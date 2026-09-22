"""Exercise the bundled windowed executable without touching hardware state."""

import subprocess
import sys
from pathlib import Path


def main():
    executable = Path(sys.argv[1]).resolve()
    cases = (
        ("--help", 0, "Usage:"),
        ("--invalid-option", 2, "Unknown option:"),
        ("--status", 0, "Background service:"),
    )
    for option, expected, message in cases:
        result = subprocess.run(
            [str(executable), option], capture_output=True, text=True, timeout=20
        )
        if result.returncode != expected or message not in result.stdout:
            raise SystemExit(
                f"{option}: expected exit {expected} and {message!r}; "
                f"got exit {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        print(f"{option}: exit {result.returncode}")


if __name__ == "__main__":
    main()
