"""
server.py
---------
Zero-dependency local web server for the dashboard. Serves index.html and
data/processed/market_data.json with no-cache headers, so a browser refresh
always shows the latest pipeline run.

A background thread also watches data/raw/ and regenerates market_data.json
automatically whenever a file in there is added or changed — that's the
piece that makes the dashboard actually self-updating rather than just
auto-polling a static file. See watch_and_regenerate() below.

Run:    python3 server.py
Then open the printed URL (it also opens automatically). market_data.json
is generated on startup and kept fresh from then on — you don't need to run
data_pipeline.py by hand unless you want a one-off regeneration.

Port in use? Either close whatever's on 8080, or:
    DASHBOARD_PORT=8081 python3 server.py

Watch interval too slow/fast? Either close whatever's on 8080, or:
    WATCH_INTERVAL_SECONDS=5 python3 server.py
"""

import http.server
import os
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

import data_pipeline

PORT = int(os.environ.get("DASHBOARD_PORT", 8080))
WATCH_INTERVAL_SECONDS = int(os.environ.get("WATCH_INTERVAL_SECONDS", 15))
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # quiet by default — comment out to see every request


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True  # avoids "address already in use" on quick restarts


def _raw_snapshot():
    """Newest mtime across files in data/raw/, or 0.0 if the folder is empty/missing."""
    if not RAW_DIR.exists():
        return 0.0
    mtimes = [p.stat().st_mtime for p in RAW_DIR.iterdir() if p.is_file()]
    return max(mtimes) if mtimes else 0.0


def watch_and_regenerate(last_seen):
    """Runs forever in a daemon thread: whenever a file in data/raw/ is added,
    removed, or modified, regenerates market_data.json to match. This is the
    self-updating half of the dashboard — the front end's 30s poll only
    refreshes what's already in market_data.json; this is what keeps that
    file itself in sync with new data. `last_seen` is the snapshot taken right
    after the startup generation in main(), so this loop only reacts to
    changes from that point on rather than re-running immediately.
    """
    while True:
        time.sleep(WATCH_INTERVAL_SECONDS)
        try:
            current = _raw_snapshot()
            if current != last_seen:
                last_seen = current
                data_pipeline.generate_market_data()
                print("data/raw/ changed — regenerated market_data.json")
        except Exception as e:
            print(f"watcher error (will retry in {WATCH_INTERVAL_SECONDS}s): {e}")


def main():
    os.chdir(BASE_DIR)  # serve relative to the project root, regardless of launch dir

    print("Generating market_data.json...")
    data_pipeline.generate_market_data()
    initial_snapshot = _raw_snapshot()

    watcher = threading.Thread(target=watch_and_regenerate, args=(initial_snapshot,), daemon=True)
    watcher.start()
    print(f"Watching data/raw/ for changes every {WATCH_INTERVAL_SECONDS}s.")

    try:
        with ReusableTCPServer(("", PORT), NoCacheHandler) as httpd:
            url = f"http://localhost:{PORT}"
            print(f"Dashboard running at {url}")
            print("Press Ctrl+C to stop.")
            webbrowser.open(url)
            httpd.serve_forever()
    except OSError as e:
        print(f"Could not start server on port {PORT}: {e}")
        print(f"Try:  DASHBOARD_PORT=8081 python3 server.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping dashboard server.")


if __name__ == "__main__":
    main()
