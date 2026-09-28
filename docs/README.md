# ⚡ JABRIG — Sistem Kecerdasan Terpadu

Versi: 3.0 | Tanggal: 2026-09-27 | Perangkat: Vivo Y19s / Android Termux / PC  
Tanpa Root • Tanpa ADB Wajib • Termux:API

---

## 🧭 Apa itu JABRIG?

JABRIG adalah asisten AI terpadu yang berjalan di HP Android (Termux) atau PC.  
Satu perintah: `python main.py`, lalu buka `http://localhost:8000`.

---

## 🧩 Arsitektur

```
JABRIG
├── HERMES      → Pengarah alur (router pesan)
├── JARVIS      → Wajah ramah & sambutan
├── ULTRON      → Kendali perangkat (via Termux:API / ADB)
├── BRAHMA AI   → Memori jangka panjang (memory/)
├── GEMINI 2.0  → AI utama (Gemini → 9Router cadangan)
├── 9Router     → Cadangan AI lokal
├── JEV         → Supervisor opsional (fail-open, TypeSafe System One)
└── Actions/    → Kendali perangkat (oto-ditemukan)
    └── Plugins/ → Skill tambahan (drop-in)
```

---

## 🗂 Struktur Folder

```
jabrig/
├── main.py               ← inti sistem (HERMES, JEV, AI, Web UI, FastAPI)
├── requirements.txt      ← dependensi Python
├── Dockerfile            ← build image siap deploy
│
├── actions/              ← kendali perangkat (auto-ditemukan)
│   ├── __init__.py       ← action loader
│   ├── open_app.py       ← buka aplikasi
│   ├── close_app.py      ← tutup aplikasi
│   ├── screenshot.py     ← ambil layar
│   ├── notification.py   ← kirim notifikasi
│   └── system_status.py  ← cek status sistem
│
├── plugins/              ← skill tambahan (drop-in .py)
│   ├── __init__.py       ← plugin loader
│   └── contoh_sapaan.py  ← contoh plugin
│
├── memory/               ← memori jangka panjang
│   ├── __init__.py
│   └── memory_manager.py ← kategori, long_term.json, prompt budget
│
├── config/               ← konfigurasi API
│   ├── __init__.py
│   └── api_keys.json     ← GEMINI_API_KEY, ROUTER_URL, ROUTER_API_KEY
│
├── docs/                 ← dokumentasi
│   ├── README.md
│   ├── WIZARD.md
│   ├── WIKI.md
│   ├── DUKUNGAN.md
│   └── SPESIFIKASI.md
│
├── infra/                ← infrastruktur deployment
│   ├── jabrig.service        ← systemd service
│   ├── jabrig-watchdog.sh   ← watchdog start/stop/restart
│   ├── jabrig-cron.service  ← tugas berkala
│   ├── jabrig-cron.timer    ← timer 6 jam
│   ├── jabrig-cron-task.sh  ← script tugas
│   └── setup-caddy.sh       ← setup Caddy reverse proxy
│
├── ALLINONE.md           ← gambaran lengkap + quick start
├── INSTALL.md            ← install + integrasi sistem
├── WIZARD_FULL.sh        ← wizard instalasi multi-platform
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Pasang dependensi

```bash
pip install -r requirements.txt
```

Atau satu per satu:

```bash
pip install fastapi uvicorn httpx "python-jose[cryptography]" passlib[bcrypt]
```

### 2. Isi API Key

Edit `config/api_keys.json`:

```json
{
  "gemini_api_key": "GEMINI_API_KEY_ANDA_DI_SINI",
  "router_url": "http://localhost:20128",
  "router_api_key": ""
}
```

### 3. Jalankan

```bash
python main.py
```

Atau dengan uvicorn langsung:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Buka di browser

```
http://localhost:8000
```

---

## 💬 Cara Pakai

### Via Web UI

Buka `http://localhost:8000`, ketik perintah di kotak teks.

Contoh perintah:
- `"halo"` / `"hai"` → sapaan
- `"siapa kamu"` → identitas
- `"status"` → status sistem
- `"buka youtube"` → buka aplikasi
- `"tutup whatsapp"` → tutup aplikasi
- `"ambil layar"` → screenshot
- `"notifikasi test"` → kirim notifikasi
- `"ingat proyek saya Jabrig"` → simpan ke memori
- `"apa yang kamu tahu tentang Jabrig"` → cari di memori

### Via API

```bash
curl -X POST http://localhost:8000/perintah \
  -H "Content-Type: application/json" \
  -d '{"teks": "buka youtube"}'
```

Response:
```json
{
  "jawab": "Membuka youtube ✅",
  "jalur": "ULTRON",
  "sumber": "ULTRON"
}
```

Status sistem:
```bash
curl http://localhost:8000/status
```

---

## 🔌 Action & Plugin

### Menambah Action Baru

Buat file di `actions/nama_action.py`:

```python
def _nama_action(parameters: dict, **ctx) -> dict:
    # logic di sini
    return {"ok": True, "pesan": "Selesai ✅"}

TOOL = {
    "name": "nama_action",
    "description": "Deskripsi action ini",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "param1": {"type": "string"}
        },
        "required": ["param1"]
    },
    "handler": _nama_action,
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}
```

Action otomatis terdaftar saat `main.py` dijalankan.

### Menambah Plugin Baru

Buat file di `plugins/nama_plugin.py`:

```python
PLUGIN = {
    "name": "nama_plugin",
    "description": "Deskripsi plugin ini",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "param1": {"type": "string"}
        },
        "required": []
    },
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}

def run(parameters: dict, **ctx) -> str:
    # logic plugin di sini
    return "Hasil plugin"
```

Plugin otomatis terdaftar saat `main.py` dijalankan.

---

## 🤖 AI

### Gemini (Utama)

- URL: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- Kunci: `config/api_keys.json` → `gemini_api_key`

### 9Router (Cadangan)

- URL: `config/api_keys.json` → `router_url` (default: `http://localhost:20128`)
- Kunci: `config/api_keys.json` → `router_api_key`

### Alur AI

1. Cek perintah cepat (halo, status, buka/tutup app, dll)
2. HERMES arahkan ke tujuan (JARVIS / ULTRON / BRAHMA / JEV / GEMINI)
3. JEV supervisor (opsional) — kalau tidak aktif, langsung ke AI
4. Gemini utama → kalau gagal, 9Router cadangan → kalau keduanya gagal, jawaban lokal

---

## 🧠 Memori (BRAHMA AI)

Memori disimpan di `memory/long_term.json` dengan kategori:

- `identity` — identitas pengguna
- `preferences` — preferensi
- `projects` — proyek
- `relationships` — hubungan
- `wishes` — keinginan
- `notes` — catatan (termasuk ringkasan sesi)

Prompt budget: hanya inti memori yang masuk prompt AI setiap request. Sisanya dicari saat perlu via `search_memory()`.

---

## 📱 HP Android (Termux)

### Persiapan

1. Install Termux dari F-Droid
2. Install Termux:API dari F-Droid
3. Berikan izin Termux:API

### Fitur yang Tersedia

- Buka aplikasi (via `termux-open-url`)
- Tutup aplikasi (via `am force-stop`)
- Ambil layar (via `termux-screenshot`)
- Notifikasi (via `termux-notification`)

### Mode Kendali

- Otomatis deteksi Termux → gunakan Termux:API
- Jika di PC → tanya apakah ingin aktifkan ADB

---

## 🌐 Deploy

### Local / VPS

```bash
python main.py
# atau
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Systemd (auto-start)

Lihat `infra/jabrig.service` untuk konfigurasi unit systemd.

```bash
sudo cp infra/jabrig.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jabrig
sudo systemctl start jabrig
```

### Watchdog

Lihat `infra/jabrig-watchdog.sh` untuk memantau proses dan restart otomatis.

### Cron (tugas berkala)

Lihat `infra/jabrig-cron.service`, `infra/jabrig-cron.timer`, `infra/jabrig-cron-task.sh`.

### Caddy (reverse proxy + HTTPS otomatis)

Lihat `infra/setup-caddy.sh`.

### Docker

```bash
docker build -t jabrig .
docker run -p 8000:8000 jabrig
```

Atau dengan docker-compose (butuh penyesuaian environment).

---

## ⚡ Performa

- HTTP client di-reuse untuk mengurangi overhead koneksi
- Timeout pendek (2 detik) untuk respons cepat
- Auto-skip: pesan JARVIS/ULTRON yang jelas tidak perlu ke AI
- HERMES memandu alur sebelum panggil AI
- JEV opsional, fail-open — kalau error, sistem tetap jalan

---

## 🔒 Keamanan

- JWT untuk autentikasi (kalau diaktifkan)
- API key di `config/api_keys.json` (jangan dikomit ke repo publik)
- CORS diizinkan semua (untuk development; untuk production, batasi origin)

---

## 🐛 Troubleshooting

### Gemini gagal

- Pastikan `gemini_api_key` di `config/api_keys.json` benar
- Cek koneksi internet

### 9Router gagal

- Pastikan 9Router berjalan di `router_url`
- Cek `router_api_key`

### Aplikasi tidak bisa dibuka (HP)

- Pastikan Termux:API terpasang dan diberi izin
- Di PC, pastikan adb terpasang dan perangkat tersambung (`adb devices`)

### Web UI tidak muncul

- Pastikan port 8000 tidak dipakai aplikasi lain
- Cek log `main.py` saat startup

---

## 📄 Dokumentasi Lengkap

Lihat folder `docs/`:
- `WIZARD.md` — wizard instalasi
- `WIKI.md` — wiki komprehensif
- `DUKUNGAN.md` — panduan dukungan
- `SPESIFIKASI.md` — spesifikasi teknis

Atau `ALLINONE.md` untuk gambaran lengkap + quick start.
