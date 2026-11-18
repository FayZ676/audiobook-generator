import pytest

from tta_narration.models import kokoro


@pytest.fixture(name="machine")
def fake_machine(monkeypatch):
    monkeypatch.delenv("TTA_KOKORO_COPIES", raising=False)

    def machine(cpus, free_gb):
        monkeypatch.setattr(kokoro, "_cpus", lambda: cpus)
        monkeypatch.setattr(kokoro, "_free_gpu_gb", lambda: free_gb)

    return machine


def test_gpu_memory_decides_when_cores_are_plenty(machine):
    machine(cpus=32, free_gb=15.5)  # a 16 GB card

    copies, why = kokoro.copies_for_this_machine()

    assert copies == int((15.5 - kokoro.GPU_HEADROOM_GB) // kokoro.GPU_GB_PER_COPY)
    assert "GPU memory decides" in why


def test_cores_decide_when_they_are_scarcer(machine):
    machine(cpus=6, free_gb=23.5)

    assert kokoro.copies_for_this_machine()[0] == 6


def test_without_a_gpu_each_copy_gets_several_cores(machine):
    machine(cpus=10, free_gb=None)

    assert kokoro.copies_for_this_machine()[0] == 10 // kokoro.CPU_CORES_PER_COPY_WITHOUT_GPU


def test_always_at_least_one(machine):
    machine(cpus=1, free_gb=0.5)

    assert kokoro.copies_for_this_machine()[0] == 1


@pytest.mark.parametrize(
    "files, cpus",
    [
        ({"cpu.max": "900000 100000\n"}, 9.0),  # cgroup v2: a 9 vCPU RunPod worker
        ({"cpu.max": "max 100000\n"}, None),  # no limit
        ({"cpu/cpu.cfs_quota_us": "1200000\n", "cpu/cpu.cfs_period_us": "100000\n"}, 12.0),  # cgroup v1
        ({"cpu/cpu.cfs_quota_us": "-1\n", "cpu/cpu.cfs_period_us": "100000\n"}, None),
        ({}, None),  # not in a container, e.g. a Mac
    ],
)
def test_a_containers_cpu_quota_is_read(tmp_path, files, cpus):
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(exist_ok=True)
        (tmp_path / name).write_text(text)

    assert kokoro._cgroup_cpus(str(tmp_path)) == cpus  # pylint: disable=protected-access


def test_the_quota_caps_the_cores_the_host_shows(monkeypatch):
    monkeypatch.setattr(kokoro, "_cgroup_cpus", lambda: 9.0)
    monkeypatch.setattr(kokoro.os, "sched_getaffinity", lambda _: set(range(48)), raising=False)

    assert kokoro._cpus() == 9  # pylint: disable=protected-access


def test_the_environment_overrides_it(machine, monkeypatch):
    machine(cpus=32, free_gb=80)
    monkeypatch.setenv("TTA_KOKORO_COPIES", "3")

    assert kokoro.copies_for_this_machine() == (3, "TTA_KOKORO_COPIES")
