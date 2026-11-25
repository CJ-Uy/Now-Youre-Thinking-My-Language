"""AI-assisted pilot series (decision H-0046) on one GPU: train the five matched conditions, run a quick
development check, then the full development sweep. Serial; stops on the first failure; refuses to start
beside another GPU process or in a used pipeline directory.

Usage from the repository root:
    .venv/Scripts/python.exe -m scripts.run_aiassist_series artifacts/conditions/opus55-ai-assisted-20261120-final
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from research import ROOT

CONDITIONS = ["original", "english-shortest", "english-feedback", "multilingual-shortest", "multilingual-feedback"]
CONFIG = "configs/pilot-opus55.json"
PIPELINE = Path("artifacts/pipeline/opus55-aiassist-laptop-20261120")
RUNS = "artifacts/runs/opus55-aiassist-laptop"


def steps(conditions):
    py = [sys.executable, "-m", "research", "--config", CONFIG]
    out = [(f"train-{c}", py + ["train", "--conditions", conditions, "--condition", c, "--allow-unreviewed",
                                "--output", f"{RUNS}-{c}"]) for c in CONDITIONS]
    out.append(("quick-unchanged", py + ["evaluate", "--budget", "256", "--limit", "50", "--output", f"{RUNS}-unchanged-quick"]))
    out += [(f"quick-{c}", py + ["evaluate", "--adapter", f"{RUNS}-{c}/adapter", "--budget", "256", "--limit", "50",
                                 "--output", f"{RUNS}-{c}-quick"]) for c in CONDITIONS]
    out.append(("dev-unchanged", py + ["evaluate", "--output", f"{RUNS}-unchanged-dev"]))
    out += [(f"dev-{c}", py + ["evaluate", "--adapter", f"{RUNS}-{c}/adapter", "--output", f"{RUNS}-{c}-dev"])
            for c in CONDITIONS]
    return out


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def main(conditions):
    root = ROOT / PIPELINE
    root.mkdir(parents=True, exist_ok=False)
    busy = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"], text=True).strip()
    status = {"started": now(), "conditions": conditions, "config": CONFIG, "steps": []}
    if busy:
        status["state"] = f"refused: GPU busy ({busy})"
        (root / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
        raise SystemExit(status["state"])
    files = [ROOT / CONFIG, *sorted((ROOT / conditions).glob("*.json*")), *sorted((ROOT / "research").glob("*.py"))]
    status["inputs_sha256"] = {str(f.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    status["source_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    status["git_dirty"] = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
    (root / "nvidia-smi-start.txt").write_text(subprocess.check_output(["nvidia-smi"], text=True), encoding="utf-8")
    for name, command in steps(conditions):
        entry = {"name": name, "command": command[1:], "start": now()}
        status["state"] = f"running {name}"
        status["steps"].append(entry)
        (root / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
        with (root / f"{name}.out").open("w", encoding="utf-8") as log:
            rc = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        entry.update(end=now(), returncode=rc)
        if rc:
            status["state"] = f"failed at {name}"
            (root / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
            raise SystemExit(status["state"])
        if name == f"quick-{CONDITIONS[-1]}":
            status["quick_done"] = now()
    status["state"] = "done"
    status["finished"] = now()
    (root / "nvidia-smi-end.txt").write_text(subprocess.check_output(["nvidia-smi"], text=True), encoding="utf-8")
    (root / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
