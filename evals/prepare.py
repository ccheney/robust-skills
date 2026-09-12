"""Build local grading dependencies. This does not call an LLM."""

import subprocess
from pathlib import Path
from evals.runtime import IMAGE, LABEL, source_hash
from evals.postgres import IMAGE as POSTGRES_IMAGE

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [
            "docker",
            "build",
            "--label",
            LABEL + "=" + source_hash(),
            "-t",
            IMAGE,
            str(root / "evals/runtime"),
        ],
        check=True,
    )
    subprocess.run(["docker", "pull", POSTGRES_IMAGE], check=True)
