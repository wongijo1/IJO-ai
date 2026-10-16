import os, socket, subprocess, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8765
URL = "http://127.0.0.1:%d" % PORT

# pastikan server aktif
def server_ready():
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect(("127.0.0.1", PORT))
        s.close()
        return True
    except Exception:
        return False

if not server_ready():
    try:
        subprocess.Popen(["pythonw", "server.py"], cwd=BASE_DIR,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception:
        subprocess.Popen(["python", "server.py"], cwd=BASE_DIR,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    for _ in range(20):
        time.sleep(0.5)
        if server_ready():
            break

# cari browser untuk mode aplikasi
browser_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
browser = None
for p in browser_paths:
    if os.path.exists(p):
        browser = p
        break

if browser:
    subprocess.Popen([browser, "--app=%s" % URL, "--start-maximized",
                      "--window-name=IJO PC Assistant"], cwd=BASE_DIR)
else:
    import webbrowser
    webbrowser.open(URL)
