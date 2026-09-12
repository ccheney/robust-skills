"""Resolve a local Google key without printing or persisting its secret value."""

import json
import os
import subprocess
from pathlib import Path

from evals.providers import EvalUnavailable


def from_gcloud(config_path: Path):
    if not config_path.exists():
        return None
    try:
        config = json.loads(config_path.read_text())
        project, account, key_id = (
            config["gcloud_project"],
            config["gcloud_account"],
            config["gcloud_key"],
        )
        if not all(
            isinstance(v, str) and v.strip() for v in (project, account, key_id)
        ):
            raise ValueError("Missing project/account/key")
    except (OSError, ValueError, KeyError, TypeError):
        raise EvalUnavailable(
            "Local configuration needs gcloud_project, gcloud_account, and gcloud_key"
        ) from None
    env = os.environ.copy()
    if config.get("gcloud_version"):
        env["ASDF_GCLOUD_VERSION"] = str(config["gcloud_version"])
    common = ["--project=" + project, "--account=" + account, "--quiet"]

    def run(command):
        try:
            process = subprocess.run(
                ["gcloud", *command, *common],
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise EvalUnavailable(
                "Unable to run gcloud; check its installation and the configured account login"
            ) from None
        if process.returncode:
            raise EvalUnavailable(
                "Google credential/billing lookup failed; check gcloud auth login for the configured account"
            )
        return process.stdout

    try:
        billing = json.loads(
            run(["billing", "projects", "describe", project, "--format=json"])
        )
        if not isinstance(billing, dict) or billing.get("billingEnabled") is not False:
            raise EvalUnavailable(
                "The configured Google project does not have verified disabled billing"
            )
    except ValueError:
        raise EvalUnavailable(
            "Could not verify Google project billing status"
        ) from None
    key = run(
        ["services", "api-keys", "get-key-string", key_id, "--format=value(keyString)"]
    ).strip()
    if not key:
        raise EvalUnavailable("Google returned an empty API key")
    return {
        "key": key,
        "source": {"method": "gcloud", "project": project, "billing_enabled": False},
    }
