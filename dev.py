from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from watchfiles import watch


ROOT = Path(__file__).resolve().parent
WATCH_PATHS = [ROOT / "main.py", ROOT / "ui"]


def start_app() -> subprocess.Popen[str]:
    return subprocess.Popen([sys.executable, str(ROOT / "main.py")], cwd=ROOT)


def stop_app(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main() -> None:
    process = start_app()

    try:
        for _changes in watch(*WATCH_PATHS):
            stop_app(process)
            process = start_app()
    except KeyboardInterrupt:
        pass
    finally:
        stop_app(process)


if __name__ == "__main__":
    main()
