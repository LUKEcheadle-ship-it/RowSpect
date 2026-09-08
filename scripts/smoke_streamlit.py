from __future__ import annotations

import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for(url: str, timeout: float = 30.0) -> bytes:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
        time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def main() -> int:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("RowSpect UI smoke: Streamlit is not installed.", file=sys.stderr)
        return 2

    port = _free_port()
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "app.py"),
        "--server.headless=true",
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_for(f"http://127.0.0.1:{port}/_stcore/health")
        root = _wait_for(f"http://127.0.0.1:{port}/")
        if not root:
            raise RuntimeError("Streamlit root page returned an empty response.")
        print(f"RowSpect UI smoke PASS on 127.0.0.1:{port}")
        return 0
    except Exception as exc:
        print(f"RowSpect UI smoke FAIL: {exc}", file=sys.stderr)
        if process.stdout:
            output = process.stdout.read()
            if output:
                print(output[-4000:], file=sys.stderr)
        return 1
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
