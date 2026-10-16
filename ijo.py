# IJO — asisten AI berbasis CLI (Bahasa Indonesia)
# Jalankan dengan:  python ijo.py

import sys
from ijo_core import *

# re-export color helper
def _color(text, code):
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"

import time

def typing_print(text, delay=0.006):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    print(_color(BANNER, "35"))
    brain = Brain()
    mode = brain.mode
    print(_color(f"Mode: {mode}. Ketik /help untuk perintah, /exit untuk keluar.\n", "90"))
    print(random.choice(GREETINGS))
    while True:
        try:
            prompt = input(_color("kamu> ", "32"))
        except (EOFError, KeyboardInterrupt):
            print()
            print(random.choice(FAREWELLS))
            break
        text = prompt.strip()
        if not text:
            continue
        reply, status = process_message(text, brain)
        if text.startswith("/"):
            print(reply)
        else:
            typing_print(_color(f"{NAME}> ", "36") + reply, delay=0.004)
        if status == "exit":
            break

if __name__ == "__main__":
    main()
