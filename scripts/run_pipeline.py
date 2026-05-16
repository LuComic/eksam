from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)


def main() -> int:
    run("fetch_materials.py")
    run("extract_tasks.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
