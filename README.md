# IJO — Asisten AI yang Ramah

Asisten AI kecil yang mandiri bernama **IJO**, ditulis dalam Python murni (tanpa dependensi pihak ketiga). Berbahasa Indonesia.

## Fitur

- Obrolan interaktif di terminal
- Mengingat riwayat percakapan
- Candaan, fakta menarik, obrolan ringan, matematika sederhana
- Jawaban waktu / tanggal
- Perintah: `/help`, `/clear`, `/history`, `/joke`, `/fact`, `/time`, `/date`, `/exit`
- Backend LLM asli opsional jika `OPENAI_API_KEY` (atau yang kompatibel) disetel

## Menjalankan (CLI)

```sh
python ijo.py
```

## Menjalankan (UI Web yang cantik) 🎨

```sh
python server.py
```
Browser akan terbuka otomatis di `http://127.0.0.1:8765`.

Fitur UI:
- Tampilan modern dengan animasi, avatar, dan balon chat
- Aksi cepat (candaan, fakta, waktu, tanggal, riwayat, bersihkan, bantuan)
- Saran pertanyaan & indikator mengetik
- Mode gelap premium, responsif (mobile-friendly)

## Lebih pintar dengan LLM asli

Setel variabel lingkungan, lalu jalankan:

```sh
set OPENAI_API_KEY=sk-...
set OPENAI_BASE_URL=https://api.openai.com/v1   # opsional
set OPENAI_MODEL=gpt-4o-mini                    # opsional
python ijo.py
```

## File

- `ijo.py` — seluruh asisten
