# JABRIG v3.0 — Sistem Kecerdasan Terpadu

**JABRIG** adalah satu berkas Python yang menyatukan tiga inti kecerdasan dalam satu sistem: **JARVIS** (wajah & sambutan), **ULTRON** (kendali perangkat), dan **BRAHMA AI** (ingatan & pemahaman), dengan **HERMES** sebagai pengarah alur yang menghubungkan pengguna ke sumber kecerdasan yang tepat — **Gemini 2.0 Flash** (utama) dan **9Router** (cadangan).

Bekerja di **HP Android (Termux)** dan **PC/Laptop**, tanpa root dan tanpa ADB wajib.

---

## Cepat Mulai

### Di HP Android (Termux)

```bash
# 1. Pasang dependensi
pkg update && pkg upgrade -y
pkg install -y python python-pip git termux-api
pip install --upgrade pip
pip install fastapi uvicorn httpx "python-jose[cryptography]" "passlib[bcrypt]"

# 2. Pasang Termux:API dari F-Droid (wajib untuk kendali perangkat)
#    https://f-droid.org/packages/com.termux.api/

# 3. Jalankan
python main.py

# 4. Buka browser: http://localhost:8000
```

### Di PC / Laptop

```bash
# 1. Pastikan Python 3.9+ dan pip sudah terpasang
python --version
pip install fastapi uvicorn httpx "python-jose[cryptography]" "passlib[bcrypt]"

# 2. Jika ingin kendali perangkat via ADB, pastikan ADB terpasang
#    dan perangkat sudah dalam mode USB debugging

# 3. Jalankan — akan ditanya apakah ingin aktifkan ADB
python main.py

# 4. Buka browser: http://localhost:8000
```

### Variabel Lingkungan (Opsional)

```bash
export GEMINI_API_KEY="AIzaSy..."
export ROUTER_API_KEY="your-router-key"
export ROUTER_API_URL="http://localhost:20128"
export JABRIG_USER="admin"
export JABRIG_PASS="kata-sandi-anda"
```

---

## Fitur Utama

| Komponen | Peran |
|---|---|
| **JARVIS** | Wajah ramah, sambutan, perkenalan, bimbingan pengguna |
| **ULTRON** | Tangan & mata sistem — eksekusi perintah perangkat, status |
| **BRAHMA AI** | Ingatan & pemahaman — simpan percakapan, konteks, analisis |
| **HERMES** | Pengarah alur — terima pesan, putuskan ke inti mana |
| **Gemini 2.0 Flash** | Sumber kecerdasan utama — cepat, percakapan umum |
| **9Router** | Sumber cadangan — lokal, jika Gemini tidak tersedia |

### Kendali Perangkat (ULTRON)

- Buka aplikasi: WhatsApp, Telegram, YouTube, Pengaturan, Kamera, Galeri, Kalkulator
- Tutup aplikasi (force-stop)
- Ambil tangkapan layar (screenshot)
- Kirim notifikasi (hanya Termux:API)

### Perintah Cepat (tanpa AI)

Ketik langsung tanpa perlu koneksi internet:
- `halo` / `hai` → sambutan JARVIS
- `siapa kamu` → identitas sistem
- `status` → status sistem lengkap
- `buka youtube` → buka aplikasi
- `tutup whatsapp` → tutup aplikasi
- `ambil layar` → tangkapan layar
- `notifikasi halo dunia` → kirim notifikasi

---

## Akses Web

| URL | Deskripsi |
|---|---|
| `http://localhost:8000/` | Halaman utama — chat interaktif |
| `http://localhost:8000/status` | Status sistem (JSON) |
| `http://localhost:8000/health` | Health check |
| `http://localhost:8000/brahma/konteks` | Konteks percakapan BRAHMA (JSON) |
| `http://localhost:8000/brahma/session` | Daftar session (JSON) |

---

## Struktur Berkas

```
/root/
├── main.py              # Satu berkas utama JABRIG v3.0
├── jabrig_kunci.json    # Kunci JWT (dihasilkan otomatis)
├── README.md            # Dokumentasi ini
├── WIZARD.md           # Panduan wizard instalasi
├── WIKI.md             # Panduan komprehensif
├── DUKUNGAN.md         # Bantuan & troubleshooting
└── SPESIFIKASI.md      # Spesifikasi teknis lengkap
```

---

## Lisensi

MIT — bebas digunakan, dimodifikasi, dan didistribusikan.

---

## Versi

- **v3.0** (2026-09-27) — JARVIS + ULTRON + BRAHMA AI + HERMES + Gemini/9Router
- **v2.0** — Sistem otomatisasi lengkap dengan FastAPI
- **v1.0** — Fondasi awal
