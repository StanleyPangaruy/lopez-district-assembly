"""
District Assembly overlay server.

Serves the OBS browser-source overlay (overlay.html) and the control panel
(control.html) from this folder, and keeps the "who is on air" state.

Run:  double-click start.bat   (or:  python server.py)
Then: control panel  -> http://127.0.0.1:8765/
      OBS overlays   -> http://127.0.0.1:8765/overlay.html?scene=2&layer=fg  (see README.md)

Only Python's standard library is used. Nothing is reachable from other
computers: the server listens on 127.0.0.1 only.
"""

import csv
import json
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("DA_PORT", "8765"))
ROSTER = HERE / "roster.csv"
STATE_FILE = HERE / "state.json"
FIELDS = ["order", "district", "kind", "name", "person", "role", "logo"]

DEFAULT_SETTINGS = {
    "event_title": "DISTRICT ASSEMBLY",
    "header1": "PROVINCE OF QUEZON",
    "header2": "THE MUNICIPALITY OF LOPEZ",
    "card_note": "Presentation of barangay and sectoral reports",
}
DEFAULT_STATE = {
    "version": 1,
    "show_lt": True,
    "speaker": {"kind": "barangay", "district": "Poblacion", "name": "Gomez",
                "person": "Kap. Juan Dela Cruz", "role": "Punong Barangay", "logo": "", "index": 0},
    "settings": dict(DEFAULT_SETTINGS),
}

lock = threading.Lock()


# --------------------------------------------------------------------------- state
def load_state():
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        s = json.loads(json.dumps(DEFAULT_STATE))
    s.setdefault("version", 1)
    s.setdefault("show_lt", True)
    s.setdefault("speaker", dict(DEFAULT_STATE["speaker"]))
    s["settings"] = {**DEFAULT_SETTINGS, **(s.get("settings") or {})}
    return s


def save_state(s):
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, STATE_FILE)


state = load_state()


# --------------------------------------------------------------------------- roster
def _read_text(path):
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp1252"):   # Excel on Windows often saves as cp1252 (e.g. ñ)
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def read_roster():
    if not ROSTER.exists():
        return []
    rows = []
    for r in csv.DictReader(_read_text(ROSTER).splitlines()):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        if not r.get("name"):
            continue
        row = {f: r.get(f, "") for f in FIELDS}
        row["kind"] = (row["kind"] or "barangay").lower()
        rows.append(row)
    return rows


def write_roster(rows):
    tmp = ROSTER.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:   # BOM so Excel shows ñ correctly
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    os.replace(tmp, ROSTER)


# --------------------------------------------------------------------------- http
class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".html": "text/html; charset=utf-8", ".js": "text/javascript",
                      ".ttf": "font/ttf", ".otf": "font/otf", ".png": "image/png",
                      ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml",
                      ".webp": "image/webp"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def log_message(self, fmt, *args):
        if args and str(args[1] if len(args) > 1 else "").startswith(("4", "5")):
            sys.stderr.write("  ! %s\n" % (fmt % args))

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.path = "/control.html"
        elif path == "/api/state":
            with lock:
                return self._json(state)
        elif path == "/api/roster":
            try:
                return self._json(read_roster())
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        return super().do_GET()

    def do_POST(self):
        global state
        path = urlparse(self.path).path
        try:
            data = self._body()
        except Exception:
            return self._json({"error": "bad JSON"}, 400)

        if path == "/api/state":
            with lock:
                if isinstance(data.get("speaker"), dict):
                    state["speaker"] = data["speaker"]
                if "show_lt" in data:
                    state["show_lt"] = bool(data["show_lt"])
                if isinstance(data.get("settings"), dict):
                    state["settings"] = {**state["settings"], **data["settings"]}
                state["version"] += 1
                save_state(state)
                return self._json(state)

        if path == "/api/roster/row":
            with lock:
                try:
                    rows = read_roster()
                    i = int(data["index"])
                    rows[i].update({k: str(data["row"].get(k, rows[i].get(k, ""))) for k in FIELDS})
                    write_roster(rows)
                except PermissionError:
                    return self._json({"error": "roster.csv is open in another program (close Excel and try again)"}, 409)
                except Exception as e:
                    return self._json({"error": str(e)}, 400)
            return self._json({"ok": True})

        return self._json({"error": "not found"}, 404)


def main():
    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print(f"\nPort {PORT} is already in use. Is the server already running in another window?")
        input("Press Enter to close...")
        return
    base = f"http://127.0.0.1:{PORT}"
    print("=" * 60)
    print("  DISTRICT ASSEMBLY overlay server is running")
    print("=" * 60)
    print(f"  Control panel : {base}/")
    print(f"  Overlay links : see 'OBS links' in the control panel")
    print(f"  Folder        : {HERE}")
    print("\n  Keep this window open while recording. Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
