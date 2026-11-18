# pylint: disable=unbalanced-tuple-unpacking  # each test expects exactly one change
import hashlib

import pytest

from deploy import plan
from deploy.config import Config, Endpoint
from deploy.plan import plan_changes

TAG = "abc123def456"


class FakeRunPod:
    def __init__(self, secrets=(), endpoints=()):
        self.listings = {"/account/secrets": list(secrets), "/serverless": list(endpoints)}

    def items(self, path):
        return self.listings[path]


def endpoint(**settings):
    return Endpoint(
        name="tta-script",
        repository="ghcr.io/me/tta-script",
        paths=["script"],
        context="script",
        dockerfile="script/Dockerfile",
        settings={"workers": {"min": 0, "max": 3}, "cpu": [{"id": "cpu5c", "vcpuCount": 2}], **settings},
    )


@pytest.fixture(autouse=True)
def committed_and_built(monkeypatch):
    monkeypatch.setattr(Endpoint, "tag", property(lambda self: TAG))
    monkeypatch.setattr(Endpoint, "uncommitted", lambda self: False)
    monkeypatch.setattr(plan, "image_problem", lambda image: None)


def fingerprint(value, variable="KEY"):
    return f"sha256:{hashlib.sha256(value.encode()).hexdigest()[:16]} (from {variable})"


def test_a_missing_endpoint_is_created_with_its_image():
    (change,) = plan_changes(FakeRunPod(), Config(secrets={}, endpoints=[endpoint()]), {})

    assert (change.method, change.path) == ("POST", "/serverless")
    assert change.body["image"] == f"ghcr.io/me/tta-script:{TAG}"
    assert change.body["type"] == "QUEUE" and change.body["workers"] == {"min": 0, "max": 3}


def test_an_endpoint_that_matches_needs_nothing_even_with_fields_runpod_adds():
    deployed = {
        "id": "ep1",
        "name": "tta-script",
        "type": "QUEUE",
        "image": f"ghcr.io/me/tta-script:{TAG}",
        "workers": {"min": 0, "max": 3, "idleTimeout": 5},
        "cpu": [{"id": "cpu5c", "vcpuCount": 2, "memory": 4}],
    }

    assert not plan_changes(FakeRunPod(endpoints=[deployed]), Config(secrets={}, endpoints=[endpoint()]), {})


def test_only_what_differs_is_sent():
    deployed = {
        "id": "ep1",
        "name": "tta-script",
        "image": "ghcr.io/me/tta-script:old",
        "workers": {"min": 0, "max": 3},
        "cpu": [{"id": "cpu5c", "vcpuCount": 4}],
    }

    (change,) = plan_changes(FakeRunPod(endpoints=[deployed]), Config(secrets={}, endpoints=[endpoint()]), {})

    assert (change.method, change.path) == ("PATCH", "/serverless/ep1")
    assert change.body == {"image": f"ghcr.io/me/tta-script:{TAG}", "cpu": [{"id": "cpu5c", "vcpuCount": 2}]}
    assert change.summary == f"~ endpoint tta-script: image → {TAG}, cpu"


def test_an_image_that_cant_be_pulled_blocks_the_change(monkeypatch):
    monkeypatch.setattr(plan, "image_problem", lambda image: f"{image} isn't built yet")

    (change,) = plan_changes(FakeRunPod(), Config(secrets={}, endpoints=[endpoint()]), {})

    assert change.blocker == f"ghcr.io/me/tta-script:{TAG} isn't built yet"


def test_uncommitted_code_blocks_a_new_image(monkeypatch):
    monkeypatch.setattr(Endpoint, "uncommitted", lambda self: True)

    (change,) = plan_changes(FakeRunPod(), Config(secrets={}, endpoints=[endpoint()]), {})

    assert "commit and push script" in change.blocker


def test_secrets_are_created_then_updated_only_when_the_value_changes():
    config = Config(secrets={"api_key": "KEY"}, endpoints=[])

    (created,) = plan_changes(FakeRunPod(), config, {"KEY": "one"})
    assert created.body == {"name": "api_key", "value": "one", "description": fingerprint("one")}

    same = FakeRunPod(secrets=[{"id": "s1", "name": "api_key", "description": fingerprint("one")}])
    assert not plan_changes(same, config, {"KEY": "one"})

    (updated,) = plan_changes(same, config, {"KEY": "two"})
    assert (updated.method, updated.path, updated.body["value"]) == ("PATCH", "/account/secrets/s1", "two")


def test_a_secret_without_a_local_value_blocks():
    (change,) = plan_changes(FakeRunPod(), Config(secrets={"api_key": "KEY"}, endpoints=[]), {})

    assert change.blocker == "KEY isn't set in .env.local"
