# server.py — jalankan UI web IJO di browser
# Jalankan:  python server.py   (lalu browser terbuka otomatis)

import http.server
import socketserver
import json
import os
import threading
import webbrowser

from ijo_core import Brain, process_message, NAME, VERSION

APP_PASSWORD = "456710"
APP_TOKEN = "IJO_AUTH_456710_SECRET"

PORT = 8765
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

brain = Brain()

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}

class Handler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self, relpath):
        path = os.path.join(STATIC_DIR, relpath.lstrip("/"))
        if not os.path.isfile(path):
            self.send_error(404, "Not found")
            return
        ext = os.path.splitext(path)[1].lower()
        ctype = MIME.get(ext, "application/octet-stream")
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        from urllib.parse import urlsplit
        path = urlsplit(self.path).path
        if path == "/" or path == "/index.html":
            self._serve_static("index.html")
            return
        if path.startswith("/static/"):
            self._serve_static(path[len("/static/"):])
            return
        if path == "/api/info":
            if self.headers.get("Authorization") != f"Bearer {APP_TOKEN}":
                self._send_json({"error": "unauthorized"}, 401)
                return
            self._send_json({"name": NAME, "version": VERSION, "mode": brain.mode})
            return
        # allow /assets alias
        self._serve_static(path.lstrip("/"))

    def do_POST(self):
        from urllib.parse import urlsplit
        path = urlsplit(self.path).path
        if path == "/api/login":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b""
            try:
                body = json.loads(raw.decode("utf-8") if raw else {})
            except Exception:
                self._send_json({"error": "bad json"}, 400)
                return
            if (body.get("password") or "") == APP_PASSWORD:
                self._send_json({"ok": True, "token": APP_TOKEN})
            else:
                self._send_json({"error": "unauthorized"}, 401)
            return
        if self.headers.get("Authorization") != f"Bearer {APP_TOKEN}":
            self._send_json({"error": "unauthorized"}, 401)
            return
        if path == "/api/send":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b""
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                self._send_json({"error": "bad json"}, 400)
                return
            text = (body.get("message") or "").strip()
            image = body.get("image")
            reply, status = process_message(text, brain, image=image)
            self._send_json({
                "reply": reply,
                "status": status,
                "mode": brain.mode,
            })
            return
        if path == "/api/reset":
            brain.history.clear()
            self._send_json({"ok": True})
            return
        self.send_error(404, "Not found")

    def log_message(self, fmt, *args):
        # keep quiet
        pass

def _hotkey_listener():
    """Tahan tombol Insert selama 2 detik untuk memanggil IJO (Windows)."""
    if os.name != "nt":
        return
    try:
        import ctypes, time, subprocess
    except Exception:
        return
    VK_INSERT = 0x2D
    held = 0.0
    triggered = False
    while True:
        try:
            pressed = (ctypes.windll.user32.GetAsyncKeyState(VK_INSERT) & 0x8000) != 0
        except Exception:
            return
        if pressed:
            held += 0.1
            if held >= 2.0 and not triggered:
                triggered = True
                try:
                    subprocess.Popen(["python", "launch_app.py"], cwd=BASE_DIR,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                except Exception:
                    pass
        else:
            held = 0.0
            triggered = False
        time.sleep(0.1)

def main():
    os.chdir(BASE_DIR)
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler)
    httpd.allow_reuse_address = True
    url = f"http://127.0.0.1:{PORT}"
    print(f"IJO Web UI berjalan di {url}")
    print("Tahan Insert 2 detik untuk memanggil IJO. Tekan Ctrl+C untuk menghentikan.")
    threading.Thread(target=_hotkey_listener, daemon=True).start()
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDihentikan.")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    main()
