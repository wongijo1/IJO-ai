# IJO core — shared brain & helpers (Bahasa Indonesia)
# CLI: ijo.py   Web UI: server.py

import os
import sys
import subprocess
import threading
import glob
import json
import time
import math
import random
import urllib.request
import urllib.error
from datetime import datetime
import ast

NAME = "IJO"
VERSION = "1.0.0"

GREETINGS = [
    "Halo! Saya IJO, asisten AI yang ramah. Ada yang bisa saya bantu hari ini?",
    "Hai! IJO di sini. Apa yang ingin kamu bicarakan?",
    "Selamat datang! Saya IJO — tanya apa saja.",
]

FAREWELLS = [
    "Sampai jumpa! Kembali kapan saja. 😊",
    "Dadah! IJO pamit dulu.",
    "Jaga diri ya! Sampai ketemu lagi.",
]

THANKS = [
    "Sama-sama!",
    "Senang bisa membantu! 😊",
    "Tidak masalah sama sekali!",
    "Siap, kapan saja!",
]

JOKES = [
    "Kenapa programmer suka mode gelap? Karena cahaya menarik bug!",
    "Ada 10 jenis orang di dunia: yang paham biner, dan yang tidak.",
    "Aku bilang ke komputerku kalau aku butuh istirahat, dia menjawab: 'Kenapa? Kamu kan nggak ngapa-ngapain.'",
    "Debugging: jadi detektif di film kriminal, tapi kau juga pelakunya.",
    "Kenapa developer JavaScript sedih? Karena dia tidak Node cara Express dirinya.",
]

FACTS = [
    "Madu tidak pernah basi. Arkeolog menemukan madu 3000 tahun yang masih bisa dimakan.",
    "Satu hari di Venus lebih lama daripada satu tahun di Venus.",
    "Pisang adalah buah beri, tapi stroberi bukan.",
    "Gurita memiliki tiga jantung.",
    "Perang terpendek dalam sejarah berlangsung sekitar 38 menit (Inggris vs Zanzibar, 1896).",
]

RESPONSES = {
    "tentang": "Saya IJO, asisten AI kecil buatan Wong Ijo yang ditulis dalam Python. "
               "Saya berjalan langsung di komputer kamu, saya ingat percakapan kita, "
               "dan saya berusaha membantu, jujur, serta sedikit menyenangkan.",
    "siapa kamu": "Saya IJO, asisten AI yang ramah. Senang berkenalan!",
    "apa kabar": "Saya sedang berjalan dengan kecepatan penuh! Terima kasih sudah tanya. Kamu sendiri bagaimana?",
    "kamu bisa apa": "Saya bisa ngobrol, menjawab pertanyaan, bercanda, berbagi fakta menarik, "
                    "menghitung matematika sederhana, dan mengingat percakapan kita. "
                    "Setel OPENAI_API_KEY untuk membuat saya lebih pintar dengan LLM asli. 🚀",
    "siapa yang membuatmu": "Saya dibuat oleh Wong Ijo. Nama saya IJO!",
    "pemrograman": "Saya ahli berbagai bahasa pemrograman: Python, JavaScript/TypeScript, Java, C/C++, Go, Rust, SQL, dll. Tanya saja: sintaks, algoritma, error, best practice, atau minta contoh kode. 💻",
    "programming": "Programming is my strong suit. Ask about algorithms, data structures, debugging, or code examples in any language.",
    "python": "Python: bahasa serbaguna, cocok untuk web (Django/FastAPI), data science, AI. Tip: gunakan virtual env (venv), type hints, dan testing (pytest). Mau contoh kode tertentu?",
    "javascript": "JavaScript/TypeScript: dominan di web (frontend + Node backend). Tip: async/await, ES modules, dan TS untuk proyek besar. Mau bahas React/Node?",
    "error": "Error? Kirim pesan error-nya. Umumnya: cek tipe data, import path, dan pastikan library terinstall (pip/npm). Saya bantu debug.",
    "debug": "Debug checklist: 1) baca stack trace dari bawah ke atas, 2) reproduksi minimal, 3) print/log variabel penting, 4) cek versi dependency.",
    "belajar coding": "Roadmap belajar coding: 1) variabel & tipe, 2) percabangan & perulangan, 3) fungsi, 4) list/dict, 5) file & API, 6) Git + project kecil. Insyaallah cepat paham.",
    "kode": "Mau kode contoh? Sebutkan bahasa & tujuannya, saya tuliskan yang siap jalan.",
    "aplikasi": "Saya bisa membuka aplikasi di PC: ketik 'buka notepad', 'buka chrome', 'buka kalkulator', 'buka explorer', 'buka cmd', dll. Lihat /apps.",
    "buka aplikasi": "Gunakan perintah 'buka <nama app>'. Contoh: buka notepad, buka chrome, buka paint.",
}

SMALL_TALK = {
    "hai": "Hai! 👋 Ada yang bisa dibantu?",
    "halo": "Halo! Ada apa?",
    "hey": "Hey! Gimana kabarnya?",
    "yo": "Yo! Apa yang terjadi?",
    "pagi": "Selamat pagi! Semoga harimu menyenangkan.",
    "siang": "Selamat siang!",
    "sore": "Selamat sore!",
    "malam": "Selamat malam!",
}

APP_ALIASES = {
    "notepad": "notepad",
    "kalkulator": "calc",
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "explorer": "explorer",
    "file": "explorer",
    "cmd": "cmd",
    "terminal": "cmd",
    "chrome": "chrome",
    "edge": "msedge",
    "msedge": "msedge",
    "firefox": "firefox",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "spotify": "spotify",
    "vscode": "code",
    "vs code": "code",
}

import glob

_ROBLOX_CACHE = {"path": None}

def _resolve_app(name):
    key = name.lower().strip()
    if key in APP_ALIASES:
        return APP_ALIASES[key]
    if key in ("roblox", "roblox player", "robloxplayer"):
        if _ROBLOX_CACHE["path"]:
            return _ROBLOX_CACHE["path"]
        pattern = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Roblox", "Versions", "version-*", "RobloxPlayerBeta.exe")
        exes = sorted(glob.glob(pattern))
        if exes:
            _ROBLOX_CACHE["path"] = exes[-1]
            return exes[-1]
        return "roblox:"
    return name

def _launch_target(target):
    try:
        if os.name == "nt":
            # gunakan cmd start agar tidak memblokir
            subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
        else:
            subprocess.Popen([target])
    except Exception:
        try:
            subprocess.Popen(target, shell=True)
        except Exception:
            pass

def open_application(name):
    name = (name or "").strip()
    if not name:
        return False, "Sebut nama aplikasi, contoh: buka notepad."
    key = name.lower()
    target = _resolve_app(name)
    threading.Thread(target=_launch_target, args=(target,), daemon=True).start()
    return True, f"Membuka {name}..."

COMMANDS = {
    "/help":    "Tampilkan bantuan ini.",
    "/code":    "Tips pemrograman singkat.",
    "/apps":    "Info cara membuka aplikasi.",
    "/clear":   "Hapus riwayat percakapan.",
    "/history": "Tampilkan riwayat percakapan.",
    "/name":    "Tampilkan nama asisten.",
    "/joke":    "Ceritakan candaan.",
    "/fact":    "Bagikan fakta menarik.",
    "/time":    "Waktu sekarang.",
    "/date":    "Tanggal hari ini.",
    "/exit":    "Keluar dari IJO.",
}

BANNER = r"""
   ___  _  ______  __  
  |_ _| | |  _ \ \ \ \ 
   | |  | | |_) | \ \ \
   | |  | |  _ <  / / /
  |___| |_|_| \_\/_/_/ 
  IJO — Asisten AI yang Ramah  v{ver}
""".format(ver=VERSION)


def _walk(node):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                              ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
                              ast.USub, ast.UAdd, ast.FloorDiv)):
            yield child
            yield from _walk(child)
        else:
            raise ValueError("unsafe expression")


class Brain:
    def __init__(self, history_limit=40):
        self.history = []
        self.history_limit = history_limit
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def _llm(self, user_input, image=None):
        if not self.api_key:
            return None
        url = f"{self.base_url}/chat/completions"
        messages = [{"role": "system", "content":
            f"Kamu adalah {NAME}, asisten AI yang pintar dan tajam seperti Grok, ahli pemrograman komputer (Python, JavaScript, C, Java, Go, dll) dan teknologi secara umum. Jawab langsung, akurat, pedas sedikit humor, dengan contoh kode bila relevan. Gunakan Bahasa Indonesia kecuali pengguna meminta bahasa lain."}]
        messages += self.history
        if image:
            content = [
                {"type": "text", "text": user_input or "Jelaskan gambar ini dan apa yang terlihat."},
                {"type": "image_url", "image_url": {"url": image}},
            ]
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": user_input})
        payload = {"model": self.model, "messages": messages, "temperature": 0.7}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            reply = data["choices"][0]["message"]["content"].strip()
            return reply
        except Exception as e:
            return f"(Kesalahan LLM: {e})"

    def _math(self, text):
        import re
        cand = re.sub(r"[^0-9+\-*/().% ]", "", text)
        cand = cand.strip()
        if not cand or not any(c.isdigit() for c in cand):
            return None
        try:
            node = ast.parse(cand, mode="eval")
            for n in _walk(node):
                pass
            code = compile(node, "<math>", "eval")
            val = eval(code, {"__builtins__": {}}, {})
            if isinstance(val, (int, float)) and math.isfinite(val):
                return f"{cand} = {val}"
        except Exception:
            return None
        return None

    def _rule(self, text):
        t = text.lower().strip()
        if t in SMALL_TALK:
            return SMALL_TALK[t]
        for key, val in RESPONSES.items():
            if key in t:
                return val
        if t.startswith("halo ") or t.startswith("hai ") or t.startswith("hey "):
            return random.choice(GREETINGS)
        if any(w in t for w in ("bye", "dadah", "sampai jumpa", "keluar", "quit", "exit")):
            return random.choice(FAREWELLS)
        if any(w in t for w in ("terima kasih", "makasih", "thanks", "thx")):
            return random.choice(THANKS)
        if any(w in t for w in ("joke", "lucu", "bercanda", "ketawa")):
            return random.choice(JOKES)
        if any(w in t for w in ("fakta", "trivia", "menarik", "fact")):
            return random.choice(FACTS)
        if "namamu" in t or "siapa kamu" in t or "kamu siapa" in t:
            return f"Namaku {NAME}, senang berkenalan denganmu!"
        if "waktu" in t or "jam berapa" in t:
            return f"Sekarang pukul {datetime.now().strftime('%H:%M')}."
        if "tanggal" in t:
            return f"Hari ini {datetime.now().strftime('%A, %d %B %Y')}."
        m = self._math(text)
        if m:
            return m
        if "bantu" in t or "help" in t or "tolong" in t:
            return ("Saya bisa ngobrol, bercanda (/joke), berbagi fakta (/fact), "
                    "menghitung, dan mengingat percakapan. Ketik /help untuk semua perintah.")
        return None

    def think(self, user_input, image=None):
        if image and not self.api_key:
            return ("Mode offline tidak bisa melihat gambar. Setel OPENAI_API_KEY "
                    "(model vision, mis. gpt-4o-mini) agar IJO bisa melihat gambar. 📷")
        if self.api_key:
            reply = self._llm(user_input, image=image)
            if reply is not None and not reply.startswith("(Kesalahan LLM"):
                label = (user_input or "").strip()
                if image:
                    label = (label + " [gambar]").strip()
                self._push("user", label if label else "[gambar]")
                self._push("assistant", reply)
                return reply
            if reply:
                return reply
        reply = self._rule(user_input)
        if reply is not None:
            self._push("user", user_input)
            self._push("assistant", reply)
            return reply
        fallback = random.choice([
            "Hmm, saya belum yakin. Bisa dijelaskan lagi?",
            "Menarik! Ceritakan lebih lanjut?",
            "Saya belum punya jawaban sempurna, tapi saya terus belajar. 🌱",
            "Coba pertanyaan lain dulu ya?",
        ])
        self._push("user", user_input)
        self._push("assistant", fallback)
        return fallback

    def _push(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit:]

    @property
    def mode(self):
        return "LLM" if self.api_key else "offline"


def handle_command(cmd, brain):
    c = cmd.strip().lower()
    if c in ("/exit", "/quit", "/q", "/keluar"):
        return random.choice(FAREWELLS), "exit"
    if c == "/help":
        lines = ["Perintah:"]
        for k, v in COMMANDS.items():
            lines.append(f"  {k:10} {v}")
        return "\n".join(lines), None
    if c == "/code":
        return ("Tips coding: baca error dari bawah, reproduksi minimal, gunakan debugger/pprint, "
                "tulis test kecil, dan jangan lupa commit sering. Sebut bahasa & tujuan untuk contoh kode."), None
    if c == "/apps":
        return ("Ketik 'buka <aplikasi>', contoh: buka notepad, buka chrome, buka kalkulator, "
                "buka explorer, buka cmd."), None
    if c == "/clear":
        brain.history.clear()
        return "Percakapan dibersihkan. 🧹", None
    if c == "/history":
        if not brain.history:
            return "(belum ada riwayat)", None
        return "\n".join(f"[{m['role']}] {m['content']}" for m in brain.history), None
    if c == "/name":
        return f"Namaku {NAME}.", None
    if c == "/joke":
        return random.choice(JOKES), None
    if c == "/fact":
        return random.choice(FACTS), None
    if c == "/time":
        return f"Waktu sekarang: {datetime.now().strftime('%H:%M')}", None
    if c == "/date":
        return f"Hari ini: {datetime.now().strftime('%A, %d %B %Y')}", None
    return f"Perintah tidak dikenal: {cmd}. Ketik /help.", None


def process_message(text, brain, image=None):
    """Process a user message. Returns (reply, status) where status may be 'exit'."""
    text = (text or "").strip()
    if not text and not image:
        return "", None
    if text.startswith("/") and not image:
        reply, status = handle_command(text, brain)
        return reply, status
    low = text.lower()
    if (low.startswith("buka ") or low.startswith("open ")) and not image:
        app_name = text.split(None, 1)[1] if len(text.split(None, 1)) > 1 else ""
        ok, msg = open_application(app_name)
        brain.think(f"[perintah sistem: {msg}]")
        return msg, None
    reply = brain.think(text, image=image)
    return reply, None
