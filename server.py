"""
server.py
---------
Zero-dependency local web server for the dashboard. Serves index.html and
data/processed/market_data.json with no-cache headers, so a browser refresh
always shows the latest pipeline run.

Run:    python3 server.py
Then open the printed URL (it also opens automatically).

Port in use? Either close whatever's on 8080, or:
    DASHBOARD_PORT=8081 python3 server.py
"""

import http.server
import os
import socketserver
import sys
import webbrowser
from pathlib import Path

PORT = int(os.environ.get("DASHBOARD_PORT", 8080))
BASE_DIR = Path(__file__).resolve().parent


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # quiet by default — comment out to see every request


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True  # avoids "address already in use" on quick restarts


def main():
    os.chdir(BASE_DIR)  # serve relative to the project root, regardless of launch dir

    data_file = BASE_DIR / "data" / "processed" / "market_data.json"
    if not data_file.exists():
        print("market_data.json not found yet — run `python3 data_pipeline.py` first.")
        print("(Starting the server anyway; the dashboard will show an error until you do.)")

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
