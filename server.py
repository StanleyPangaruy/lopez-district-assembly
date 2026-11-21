"""
District Assembly overlay server.

Serves the OBS browser-source overlay (overlay.html) and the control panel
(control.html) from this folder, and keeps the "who is on air" state.

Run:  double-click start.bat   (or:  python server.py)
Then: control panel  -> http://127.0.0.1:8765/
      OBS overlays   -> http://127.0.0.1:8765/overlay.html?scene=2&layer=fg  (see README.md)

Only Python's standard library is used. By default nothing is reachable from
other computers: the server listens on 127.0.0.1 only.

Network mode (start_lan.bat, or DA_LAN=1) also listens on the local network so
another PC (e.g. a second OBS machine) can show the Camera Only and Guest
overlays (scenes 5 and 6). Other computers get read-only access to just those
overlays, the live state they poll, and the fonts/logos/assets they draw with.
The control panel, the roster and every change stay on this computer.
"""

import csv
import json
import os
import posixpath
import socket
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("DA_PORT", "8765"))
LAN = os.environ.get("DA_LAN", "").strip() not in ("", "0")
LAN_SCENES = {"5", "6"}                                  # overlays other computers may open
LAN_DIRS = ("/fonts/", "/logos/", "/assets/")            # files those overlays load
ROSTER = HERE / "roster.csv"
STATE_FILE = HERE / "state.json"
FIELDS = ["order", "district", "kind", "name", "person", "role", "logo"]
GUESTS = HERE / "guests.csv"
GUEST_FIELDS = ["order", "title", "name", "position"]

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
    "guest": {"title": "", "name": "", "position": "", "index": -1},
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
    s.setdefault("guest", dict(DEFAULT_STATE["guest"]))
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


def read_guests():
    """Guest list for the Guest camera overlay (scene 6)."""
    if not GUESTS.exists():
        return []
    rows = []
    for r in csv.DictReader(_read_text(GUESTS).splitlines()):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        if r.get("name"):
            rows.append({f: r.get(f, "") for f in GUEST_FIELDS})
    return rows


def write_roster(rows):
    tmp = ROSTER.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:   # BOM so Excel shows ñ correctly
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    os.replace(tmp, ROSTER)


# --------------------------------------------------------------------------- network
def lan_urls():
    """This PC's addresses on the local network, as base URLs."""
    try:
        ips = socket.gethostbyname_ex(socket.gethostname())[2]
    except OSError:
        ips = []
    return [f"http://{ip}:{PORT}" for ip in ips if not ip.startswith("127.")]


def lan_allowed(raw_path):
    """What another computer may GET: the scene 5/6 overlays, the state they poll, and their fonts/images."""
    u = urlparse(raw_path)
    path = posixpath.normpath(unquote(u.path))           # so /logos/../roster.csv can't slip through
    if path == "/overlay.html":
        return parse_qs(u.query).get("scene", [""])[0] in LAN_SCENES
    return path == "/api/state" or path.startswith(LAN_DIRS)


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

    def _is_local(self):
        return self.client_address[0] in ("127.0.0.1", "::1", "::ffff:127.0.0.1")

    def _forbidden(self):
        return self._json({"error": "only the Camera Only and Guest overlays are shared on the network"}, 403)

    def do_GET(self):
        if not self._is_local() and not lan_allowed(self.path):
            return self._forbidden()
        path = urlparse(self.path).path
        if path == "/api/lan":
            return self._json({"enabled": LAN, "urls": lan_urls() if LAN else []})
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
        elif path == "/api/guests":
            try:
                return self._json(read_guests())
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        return super().do_GET()

    def do_POST(self):
        global state
        if not self._is_local():                         # changes only from this computer
            return self._forbidden()
        path = urlparse(self.path).path
        try:
            data = self._body()
        except Exception:
            return self._json({"error": "bad JSON"}, 400)

        if path == "/api/state":
            with lock:
                if isinstance(data.get("speaker"), dict):
                    state["speaker"] = data["speaker"]
                if isinstance(data.get("guest"), dict):
                    state["guest"] = data["guest"]
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
        httpd = ThreadingHTTPServer(("0.0.0.0" if LAN else "127.0.0.1", PORT), Handler)
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
    if LAN:
        print("\n  NETWORK MODE: other computers can open the Camera Only and Guest overlays:")
        for u in lan_urls() or [f"http://<this PC's IP>:{PORT}"]:
            print(f"    {u}/overlay.html?scene=5&layer=fg   (Camera Only)")
            print(f"    {u}/overlay.html?scene=6&layer=fg   (Guest)")
        print("  If Windows Firewall asks, allow Python on Private networks.")
    print("\n  Keep this window open while recording. Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
