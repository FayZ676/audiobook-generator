"""RunPod's REST v2 management API and its serverless job API, standard library only."""

import json
import socket
import urllib.error
import urllib.request
from collections.abc import Iterator

MANAGEMENT = "https://api.runpod.io/v2"
JOBS = "https://api.runpod.ai/v2"


class RunPodError(Exception):
    pass


class RunPod:
    def __init__(self, api_key: str) -> None:
        self._key = api_key

    def get(self, path: str) -> object:
        return self._call("GET", f"{MANAGEMENT}{path}")

    def post(self, path: str, body: dict) -> object:
        return self._call("POST", f"{MANAGEMENT}{path}", body)

    def patch(self, path: str, body: dict) -> object:
        return self._call("PATCH", f"{MANAGEMENT}{path}", body)

    def delete(self, path: str) -> None:
        self._call("DELETE", f"{MANAGEMENT}{path}")

    def items(self, path: str) -> list[dict]:
        """A listing's items, whether it comes back as a list or wrapped in an object."""
        reply = self.get(path)
        if isinstance(reply, list):
            return reply
        if isinstance(reply, dict):
            return next((v for v in reply.values() if isinstance(v, list)), [])
        return []

    def job(self, endpoint_id: str, action: str, body: dict | None = None) -> dict:
        """/run, /status/<id>, /health ... on an endpoint's job API."""
        reply = self._call("POST" if body is not None else "GET", f"{JOBS}/{endpoint_id}/{action}", body)
        return reply if isinstance(reply, dict) else {}

    def events(self, path: str, idle_s: float | None) -> Iterator[dict]:
        """Server-sent events from path as dicts, until idle_s pass with none
        (None: until the server closes the stream)."""
        request = self._request("GET", f"{MANAGEMENT}{path}", None)
        try:
            with urllib.request.urlopen(request, timeout=idle_s) as response:
                for raw in response:
                    line = raw.decode().strip()
                    if line.startswith("data:"):
                        yield json.loads(line[5:])
        except (TimeoutError, socket.timeout):
            return
        except urllib.error.HTTPError as e:
            raise _error(e) from e

    def _call(self, method: str, url: str, body: dict | None = None) -> object:
        try:
            with urllib.request.urlopen(self._request(method, url, body), timeout=60) as response:
                text = response.read().decode()
        except urllib.error.HTTPError as e:
            raise _error(e) from e
        return json.loads(text) if text else None

    def _request(self, method: str, url: str, body: dict | None) -> urllib.request.Request:
        headers = {"Authorization": f"Bearer {self._key}", "Accept": "application/json, text/event-stream"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        return urllib.request.Request(url, data=data, headers=headers, method=method)


def _error(e: urllib.error.HTTPError) -> RunPodError:
    detail = e.read().decode(errors="replace")
    try:
        problem = json.loads(detail)
        detail = problem.get("detail") or problem.get("title") or detail
        if problem.get("errors"):
            detail += f" {problem['errors']}"
    except (ValueError, AttributeError):
        pass
    return RunPodError(f"{e.code} {e.url}: {detail}")
