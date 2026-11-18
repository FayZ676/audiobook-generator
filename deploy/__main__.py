"""Run the RunPod deployment from the terminal. deploy/runpod.toml is what
should exist; these commands compare RunPod with it, make it match, and use
what's there.

    python3 -m deploy plan                  # what apply would change
    python3 -m deploy apply                 # make RunPod match runpod.toml
    python3 -m deploy status                # workers, jobs and rollouts
    python3 -m deploy run tta-script job.json [--out result.json]
    python3 -m deploy logs tta-narration [--follow]
    python3 -m deploy destroy tta-script    # asks first
    python3 -m deploy images                # what CI builds, as JSON

RUNPOD_API_KEY, and the values of the secrets runpod.toml lists, come from
the environment or .env.local at the repo root.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from deploy.api import RunPod, RunPodError
from deploy.config import Config, Endpoint, load, read_env_file
from deploy.plan import Change, plan_changes

DONE = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="show what apply would change")
    commands.add_parser("apply", help="make RunPod match runpod.toml")
    commands.add_parser("status", help="workers, jobs and rollouts of each endpoint")
    run = commands.add_parser("run", help="run a job and print its output")
    run.add_argument("endpoint")
    run.add_argument("job", type=Path, help='JSON file with the job\'s input, as {"input": {...}} or just {...}')
    run.add_argument("--out", type=Path, help="write the output here instead of printing it")
    logs = commands.add_parser("logs", help="recent log lines of an endpoint's workers")
    logs.add_argument("endpoint")
    logs.add_argument("--follow", action="store_true", help="keep streaming new lines")
    logs.add_argument("--tail", type=int, default=100)
    destroy = commands.add_parser("destroy", help="delete an endpoint, its workers and its jobs")
    destroy.add_argument("endpoint")
    commands.add_parser("images", help="the images CI builds, as JSON")
    args = parser.parse_args()

    config = load()
    if args.command == "images":
        print(json.dumps([_image(e) for e in config.endpoints]))
        return
    env = {**read_env_file(), **os.environ}
    if not env.get("RUNPOD_API_KEY"):
        sys.exit("Set RUNPOD_API_KEY in .env.local at the repo root (see README)")
    runpod = RunPod(env["RUNPOD_API_KEY"])
    try:
        if args.command in ("plan", "apply"):
            deploy(runpod, config, env, apply=args.command == "apply")
        elif args.command == "status":
            status(runpod, config)
        elif args.command == "run":
            run_job(runpod, _find(runpod, config.endpoint(args.endpoint)), args.job, args.out)
        elif args.command == "logs":
            show_logs(runpod, _find(runpod, config.endpoint(args.endpoint)), args.tail, args.follow)
        elif args.command == "destroy":
            destroy_endpoint(runpod, config.endpoint(args.endpoint))
    except (RunPodError, ValueError) as e:
        sys.exit(str(e))


def deploy(runpod: RunPod, config: Config, env: dict[str, str], apply: bool) -> None:
    changes = plan_changes(runpod, config, env)
    if not changes:
        print("RunPod matches runpod.toml")
        return
    for change in changes:
        print(change.summary)
    blocked = [c.blocker for c in changes if c.blocker]
    if blocked:
        sys.exit("\n".join(["", "Can't apply yet:", *blocked]))
    if apply:
        print()
        for change in changes:
            _apply(runpod, change)
        print("\nApplied. `python3 -m deploy status` shows the rollout.")


def _apply(runpod: RunPod, change: Change) -> None:
    if change.method == "POST":
        runpod.post(change.path, change.body)
    else:
        runpod.patch(change.path, change.body)
    print(f"done: {change.summary}")


def status(runpod: RunPod, config: Config) -> None:
    deployed = {e["name"]: e for e in runpod.items("/serverless")}
    for endpoint in config.endpoints:
        found = deployed.get(endpoint.name)
        if found is None:
            print(f"{endpoint.name}: not deployed")
            continue
        health = runpod.job(found["id"], "health")
        releases = runpod.get(f"/serverless/{found['id']}/releases")
        rollout = releases.get("rollout", {}) if isinstance(releases, dict) else {}
        print(f"{endpoint.name} ({found['id']})")
        print(f"  image    {found.get('image', '?')}")
        print(f"  jobs     {_counts(health.get('jobs', {}))}")
        print(f"  workers  {_counts(health.get('workers', {}))}")
        if rollout.get("inProgress"):
            print(f"  rollout  {rollout.get('workersOnLatest')}/{rollout.get('workersTotal')} workers on the latest release")


def run_job(runpod: RunPod, endpoint_id: str, job_file: Path, out: Path | None) -> None:
    job = json.loads(job_file.read_text())
    job = job if "input" in job else {"input": job}
    started = runpod.job(endpoint_id, "run", job)
    print(f"job {started['id']}", file=sys.stderr)
    state = started
    while state.get("status") not in DONE:
        time.sleep(2)
        state = runpod.job(endpoint_id, f"status/{started['id']}")
        print(f"  {state.get('status')}", file=sys.stderr)
    if state["status"] != "COMPLETED":
        sys.exit(json.dumps({k: v for k, v in state.items() if k != "input"}, indent=1))
    output = json.dumps(state.get("output"), indent=1)
    if out:
        out.write_text(output)
        print(f"output in {out}", file=sys.stderr)
    else:
        print(output)


def show_logs(runpod: RunPod, endpoint_id: str, tail: int, follow: bool) -> None:
    workers = runpod.items(f"/serverless/{endpoint_id}/workers")
    if not workers:
        print("No workers running; logs go when a worker does.", file=sys.stderr)
        return
    if follow and len(workers) > 1:
        print(f"{len(workers)} workers; following the first", file=sys.stderr)
    for worker in workers[:1] if follow else workers:
        path = f"/serverless/{endpoint_id}/workers/{worker['id']}/logs?tail={tail}"
        for event in runpod.events(path, idle_s=None if follow else 3):
            print(f"{worker['id']} {event.get('ts', '')} {event.get('line', '')}")


def destroy_endpoint(runpod: RunPod, endpoint: Endpoint) -> None:
    endpoint_id = _find(runpod, endpoint)
    answer = input(f"Delete {endpoint.name} ({endpoint_id}), its workers and its jobs? Type its name: ")
    if answer.strip() != endpoint.name:
        sys.exit("Left as it is")
    runpod.delete(f"/serverless/{endpoint_id}")
    print(f"Deleted {endpoint.name}")


def _find(runpod: RunPod, endpoint: Endpoint) -> str:
    found = next((e for e in runpod.items("/serverless") if e["name"] == endpoint.name), None)
    if found is None:
        raise ValueError(f"{endpoint.name} isn't deployed; run `python3 -m deploy apply`")
    return found["id"]


def _image(endpoint: Endpoint) -> dict:
    return {
        "name": endpoint.name,
        "image": endpoint.image,
        "context": endpoint.context,
        "dockerfile": endpoint.dockerfile,
    }


def _counts(counts: dict) -> str:
    return ", ".join(f"{v} {k}" for k, v in counts.items() if v) or "none"


if __name__ == "__main__":
    main()
