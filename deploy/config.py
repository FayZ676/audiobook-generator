"""deploy/runpod.toml read into what RunPod should have."""

import json
import subprocess
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().parent / "runpod.toml"
OURS = ("image", "paths", "context", "dockerfile")
MANIFESTS = ", ".join(
    [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    ]
)


@dataclass(frozen=True)
class Endpoint:
    name: str
    repository: str  # e.g. ghcr.io/fayz676/tta-script
    paths: list[str]
    context: str
    dockerfile: str
    settings: dict  # the RunPod endpoint body, without name, type or image

    @property
    def tag(self) -> str:
        """The last commit that touched this image's paths: CI's tag for it."""
        sha = _git("log", "-1", "--format=%H", "--", *self.paths)
        if not sha:
            raise ValueError(f"{self.name}: no commit touches {', '.join(self.paths)}")
        return sha[:12]

    @property
    def image(self) -> str:
        return f"{self.repository}:{self.tag}"

    def body(self) -> dict:
        return {"name": self.name, "type": "QUEUE", "image": self.image, **self.settings}

    def uncommitted(self) -> bool:
        return bool(_git("status", "--porcelain", "--", *self.paths))


@dataclass(frozen=True)
class Config:
    secrets: dict[str, str]  # RunPod secret name -> local variable with its value
    endpoints: list[Endpoint]

    def endpoint(self, name: str) -> Endpoint:
        found = next((e for e in self.endpoints if e.name == name), None)
        if found is None:
            raise ValueError(f"No endpoint {name!r}; there are {', '.join(e.name for e in self.endpoints)}")
        return found


def load(path: Path = CONFIG) -> Config:
    raw = tomllib.loads(path.read_text())
    endpoints = [
        Endpoint(
            name=name,
            repository=f"{raw['registry']}/{table['image']}",
            paths=table["paths"],
            context=table["context"],
            dockerfile=table["dockerfile"],
            settings={k: v for k, v in table.items() if k not in OURS},
        )
        for name, table in raw.get("endpoints", {}).items()
    ]
    return Config(secrets=raw.get("secrets", {}), endpoints=endpoints)


def image_problem(image: str) -> str | None:
    """Why RunPod couldn't pull image from GHCR anonymously, or None if it can."""
    registry, rest = image.split("/", 1)
    repository, tag = rest.rsplit(":", 1)
    try:
        with urllib.request.urlopen(f"https://{registry}/token?scope=repository:{repository}:pull", timeout=30) as r:
            token = json.load(r)["token"]
        request = urllib.request.Request(
            f"https://{registry}/v2/{repository}/manifests/{tag}",
            headers={"Authorization": f"Bearer {token}", "Accept": MANIFESTS},
            method="HEAD",
        )
        with urllib.request.urlopen(request, timeout=30):
            return None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"{image} isn't built yet (gh run watch)"
        if e.code in (401, 403):
            return f"{image} isn't public: make the package public once on GitHub (see README)"
        return f"{image}: {e.code} from {registry}"


def read_env_file(path: Path = ROOT / ".env.local") -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip().removeprefix("export ").strip()] = value.strip().strip("\"'")
    return values


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
