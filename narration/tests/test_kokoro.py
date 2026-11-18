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


def test_the_environment_overrides_it(machine, monkeypatch):
    machine(cpus=32, free_gb=80)
    monkeypatch.setenv("TTA_KOKORO_COPIES", "3")

    assert kokoro.copies_for_this_machine() == (3, "TTA_KOKORO_COPIES")
