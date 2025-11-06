import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    req = root / "requirements-voice.txt"
    if not req.exists():
        print("requirements-voice.txt not found")
        sys.exit(1)
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(req), "--disable-pip-version-check"]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)
    print("Voice dependencies installed.")


if __name__ == "__main__":
    main()


