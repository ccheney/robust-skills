"""Execute SQL fixtures in a disposable, unprivileged, network-isolated PostgreSQL database."""

import subprocess
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from evals.checks import finish

IMAGE = "postgres:18.6-alpine@sha256:d3e1620b530c944afa6e887d22eb899824da68e19c52024bf98f5220c88a65b2"


def grade_sql(root, case, candidate):
    name = "skill-pg-" + uuid.uuid4().hex[:16]
    assertions = []
    try:
        if subprocess.run(
            ["docker", "image", "inspect", IMAGE], capture_output=True, timeout=10
        ).returncode:
            return {
                "status": "blocked",
                "detail": "Pull postgres:18.6-alpine with python3 -m evals.prepare",
            }
        started = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                name,
                "--network=none",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--memory=256m",
                "--cpus=1",
                "--pids-limit=128",
                "--user=postgres",
                "--tmpfs",
                "/var/lib/postgresql/data:rw,uid=70,gid=70,mode=0700",
                "--tmpfs",
                "/var/run/postgresql:rw,uid=70,gid=70,mode=0775",
                "--tmpfs",
                "/tmp:rw,size=32m",
                "-e",
                "PGDATA=/var/lib/postgresql/data",
                "-e",
                "POSTGRES_HOST_AUTH_METHOD=trust",
                "-e",
                "POSTGRES_DB=eval",
                IMAGE,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if started.returncode:
            return {"status": "blocked", "detail": "PostgreSQL container did not start"}
        ready = False
        for _ in range(40):
            process = subprocess.run(
                ["docker", "exec", name, "cat", "/proc/1/comm"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if (
                process.stdout.strip() == "postgres"
                and subprocess.run(
                    [
                        "docker",
                        "exec",
                        name,
                        "pg_isready",
                        "-q",
                        "-U",
                        "postgres",
                        "-d",
                        "eval",
                    ],
                    capture_output=True,
                    timeout=2,
                ).returncode
                == 0
            ):
                ready = True
                break
            time.sleep(0.1)
        if not ready:
            return {"status": "blocked", "detail": "PostgreSQL did not become ready"}

        def sql(text, role="candidate"):
            return subprocess.run(
                [
                    "docker",
                    "exec",
                    "-i",
                    name,
                    "psql",
                    "-X",
                    "-qAt",
                    "-U",
                    role,
                    "-d",
                    "eval",
                    "-v",
                    "ON_ERROR_STOP=1",
                    "-v",
                    "VERBOSITY=sqlstate",
                    "-P",
                    "null=NULL",
                ],
                input=text,
                capture_output=True,
                text=True,
                timeout=8,
            )

        bootstrap = "CREATE ROLE candidate LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT; CREATE ROLE app_user LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT; GRANT ALL ON SCHEMA public TO candidate;"
        boot = sql(bootstrap, "postgres")
        if boot.returncode:
            return {
                "status": "error",
                "detail": "Fixture database bootstrap failed: " + boot.stderr[-500:],
            }
        setup = (root / "evals" / case["runtime"]["setup"]).read_text()
        if sql(setup, "candidate").returncode:
            return {"status": "error", "detail": "Trusted SQL fixture setup failed"}
        script = candidate.strip()
        if case["runtime"].get("query"):
            script = "CREATE VIEW result AS " + script.rstrip(";") + ";"
        try:
            applied = sql(script)
        except subprocess.TimeoutExpired:
            return finish(
                [
                    {
                        "id": "sql-applies",
                        "passed": False,
                        "detail": "Candidate SQL exceeded execution deadline",
                    }
                ]
            )
        assertions.append(
            {
                "id": "sql-applies",
                "passed": applied.returncode == 0,
                "detail": applied.stderr[-500:],
            }
        )
        if applied.returncode:
            return finish(assertions)
        for rule in case["runtime"]["checks"]:
            try:
                if rule.get("before"):
                    before = sql(rule["before"], rule.get("as_role", "candidate"))
                    if before.returncode:
                        raise ValueError("Fixture mutation failed")
                if "parallel" in rule:
                    with ThreadPoolExecutor(max_workers=len(rule["parallel"])) as pool:
                        runs = list(
                            pool.map(
                                lambda statement: sql(
                                    statement, rule.get("as_role", "candidate")
                                ),
                                rule["parallel"],
                            )
                        )
                    rows = sorted(r.stdout.strip().splitlines() for r in runs)
                    passed = all(r.returncode == 0 for r in runs) and rows == sorted(
                        rule["rows"]
                    )
                    detail = str(rows)
                else:
                    run = sql(rule["sql"], rule.get("as_role", "candidate"))
                    rows = run.stdout.strip().splitlines()
                    if rule.get("error"):
                        passed = run.returncode != 0 and rule["error"] in run.stderr
                    else:
                        passed = run.returncode == 0 and (
                            "rows" not in rule or rows == rule["rows"]
                        )
                    detail = str(rows) if run.returncode == 0 else run.stderr[-500:]
                assertions.append(
                    {"id": rule["id"], "passed": passed, "detail": detail}
                )
            except subprocess.TimeoutExpired:
                assertions.append(
                    {
                        "id": rule["id"],
                        "passed": False,
                        "detail": "SQL execution exceeded the deadline",
                    }
                )
        return finish(assertions)
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "blocked", "detail": "PostgreSQL infrastructure unavailable"}
    finally:
        try:
            subprocess.run(
                ["docker", "rm", "-f", "-v", name], capture_output=True, timeout=10
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
