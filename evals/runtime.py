"""Resource-limited, credential-free executable graders."""

import json
import subprocess
import uuid
import hashlib
from pathlib import Path

IMAGE = "robust-skills-eval-runtime:1"
LABEL = "org.robust-skills.eval-runtime-sha256"


def source_hash():
    root = Path(__file__).parent / "runtime"
    digest = hashlib.sha256()
    for name in (
        "Dockerfile",
        "package.json",
        "package-lock.json",
        "run.mjs",
        "starlark.py",
    ):
        digest.update(name.encode() + b"\0" + (root / name).read_bytes() + b"\0")
    return digest.hexdigest()


def execute(payload, timeout=30):
    name = "skill-eval-" + uuid.uuid4().hex[:16]
    nonce = "result-" + uuid.uuid4().hex + ":"
    body = json.dumps({**payload, "nonce": nonce})
    try:
        exists = subprocess.run(
            ["docker", "image", "inspect", IMAGE],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if exists.returncode:
            return {
                "status": "blocked",
                "detail": "Build the local evaluation runtime: python3 -m evals.prepare",
            }
        inspected = json.loads(exists.stdout)[0]
        if (inspected.get("Config", {}).get("Labels") or {}).get(
            LABEL
        ) != source_hash():
            return {
                "status": "blocked",
                "detail": "The local grading image is stale; rebuild with python3 -m evals.prepare",
            }
        run = subprocess.run(
            [
                "docker",
                "run",
                "--name",
                name,
                "--rm",
                "-i",
                "--pull=never",
                "--network=none",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--pids-limit=256",
                "--memory=1536m",
                "--cpus=2",
                "--tmpfs",
                "/tmp:rw,size=256m",
                "--shm-size=256m",
                IMAGE,
            ],
            input=body,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        records = [
            line[len(nonce) :]
            for line in run.stdout.splitlines()
            if line.startswith(nonce)
        ]
        if run.returncode in (125, 126, 127):
            return {
                "status": "blocked",
                "detail": "The runtime container could not start",
            }
        if not records:
            return {
                "assertions": [
                    {
                        "id": "execution-completes",
                        "passed": False,
                        "detail": "No completed grader result",
                    }
                ]
            }
        measured = json.loads(records[-1])
        measured["runtime_image_id"] = inspected["Id"]
        return measured
    except FileNotFoundError:
        return {"status": "blocked", "detail": "Docker is not installed"}
    except subprocess.TimeoutExpired:
        return {
            "assertions": [
                {
                    "id": "execution-deadline",
                    "passed": False,
                    "detail": "Artifact exceeded the execution deadline",
                }
            ]
        }
    finally:
        try:
            subprocess.run(
                ["docker", "rm", "-f", name], capture_output=True, timeout=10
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
