"""What has to change on RunPod for it to match runpod.toml."""

import hashlib
from dataclasses import dataclass

from deploy.api import RunPod
from deploy.config import Config, Endpoint, image_problem


@dataclass(frozen=True)
class Change:
    summary: str
    method: str  # POST or PATCH
    path: str
    body: dict
    blocker: str | None = None  # why it can't be made yet


def plan_changes(runpod: RunPod, config: Config, env: dict[str, str]) -> list[Change]:
    return _secret_changes(runpod, config, env) + _endpoint_changes(runpod, config)


def _secret_changes(runpod: RunPod, config: Config, env: dict[str, str]) -> list[Change]:
    """Secret values are write-only, so each secret's description carries a
    hash of its value, to tell when the local value has changed."""
    existing = {s["name"]: s for s in runpod.items("/account/secrets")}
    changes = []
    for name, variable in config.secrets.items():
        value = env.get(variable)
        if not value:
            changes.append(Change(f"+ secret {name}", "POST", "", {}, f"{variable} isn't set in .env.local"))
            continue
        fingerprint = f"sha256:{hashlib.sha256(value.encode()).hexdigest()[:16]} (from {variable})"
        body = {"value": value, "description": fingerprint}
        if name not in existing:
            changes.append(Change(f"+ secret {name}", "POST", "/account/secrets", {"name": name, **body}))
        elif existing[name].get("description") != fingerprint:
            changes.append(Change(f"~ secret {name}: new value", "PATCH", f"/account/secrets/{existing[name]['id']}", body))
    return changes


def _endpoint_changes(runpod: RunPod, config: Config) -> list[Change]:
    existing = {e["name"]: e for e in runpod.items("/serverless")}
    changes = []
    for endpoint in config.endpoints:
        desired = endpoint.body()
        found = existing.get(endpoint.name)
        if found is None:
            changes.append(
                Change(f"+ endpoint {endpoint.name} ({endpoint.image})", "POST", "/serverless", desired, _blocker(endpoint))
            )
            continue
        # name and type can't change; everything else is sent only if it differs.
        differ = {k: v for k, v in desired.items() if k not in ("name", "type") and not _within(v, found.get(k))}
        if not differ:
            continue
        what = ", ".join(f"image → {endpoint.tag}" if k == "image" else k for k in differ)
        changes.append(
            Change(
                f"~ endpoint {endpoint.name}: {what}",
                "PATCH",
                f"/serverless/{found['id']}",
                differ,
                _blocker(endpoint) if "image" in differ else None,
            )
        )
    return changes


def _blocker(endpoint: Endpoint) -> str | None:
    if endpoint.uncommitted():
        return f"{endpoint.name}: commit and push {', '.join(endpoint.paths)} first; the image is built from main"
    return image_problem(endpoint.image)


def _within(desired: object, actual: object) -> bool:
    """Whether actual has everything desired says, allowing fields RunPod adds."""
    if isinstance(desired, dict):
        return isinstance(actual, dict) and all(_within(v, actual.get(k)) for k, v in desired.items())
    if isinstance(desired, list):
        return isinstance(actual, list) and len(desired) == len(actual) and all(map(_within, desired, actual))
    return desired == actual
