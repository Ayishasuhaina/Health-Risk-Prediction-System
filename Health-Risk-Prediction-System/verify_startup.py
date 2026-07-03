"""Verify Flask app starts successfully."""

import subprocess
import sys
import time


def main():
    """Launch app.py and confirm server startup message."""
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output = ""
    deadline = time.time() + 120
    started = False

    while time.time() < deadline:
        line = process.stdout.readline()
        if line:
            output += line
            print(line, end="")
            if "Running on" in line:
                started = True
                break
        elif process.poll() is not None:
            break

    if started:
        print("\nAPP STARTUP SUCCESSFUL")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        sys.exit(0)

    process.kill()
    print("\nAPP STARTUP FAILED")
    print(output)
    sys.exit(1)


if __name__ == "__main__":
    main()
