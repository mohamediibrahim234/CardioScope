"""Local launcher used by run.bat:  python -m app.launcher

- starts at $PORT (default 8000) and moves to the next free port if it is taken
  (other apps on this machine often sit on 8000/8001)
- opens the browser only when THIS API answers /health (not some other app)
"""
import json
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

HOST = "127.0.0.1"


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.3)
        if probe.connect_ex((HOST, port)) == 0:  # something is already answering
            return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, port))
            return True
        except OSError:
            return False


def find_free_port(start: int, tries: int = 50) -> int:
    for port in range(start, start + tries):
        if port_is_free(port):
            return port
    raise SystemExit(f"No free port found between {start} and {start + tries - 1}")


def is_our_api(url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/health", timeout=2) as r:
            body = json.loads(r.read())
        return body.get("model_loaded") is True and "test_accuracy" in body
    except Exception:
        return False


def open_when_ready(url: str, timeout: float = 300) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_our_api(url):
            print(f"\n  >>> Ready: {url}  (opening your browser)\n", flush=True)
            webbrowser.open(url)
            return
        time.sleep(0.5)
    print("\n  [warning] the API did not become ready; check the messages above.\n", flush=True)


def main() -> None:
    wanted = int(os.getenv("PORT", "8000"))
    port = find_free_port(wanted)
    if port != wanted:
        print(f"  Port {wanted} is used by another program -> using port {port} instead.")
    url = f"http://{HOST}:{port}"
    print(f"  Starting CardioScope on {url}   (press Ctrl+C to stop)", flush=True)

    if os.getenv("NO_BROWSER") != "1":
        threading.Thread(target=open_when_ready, args=(url,), daemon=True).start()

    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=port, workers=1)


if __name__ == "__main__":
    sys.exit(main())
