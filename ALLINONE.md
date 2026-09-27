# JABRIG — Sistem Kecerdasan Terpadu

**JABRIG** adalah satu berkas Python yang menyatukan tiga inti kecerdasan dalam satu sistem: **JARVIS** (wajah & sambutan), **ULTRON** (kendali perangkat), dan **BRAHMA AI** (ingatan & pemahaman), dengan **HERMES** sebagai pengarah alur yang menghubungkan pengguna ke sumber kecerdasan yang tepat — **Gemini 2.0 Flash** (utama) dan **9Router** (cadangan).

Bekerja di **HP Android (Termux)** dan **PC/Laptop**, tanpa root dan tanpa ADB wajib.

---

## 📊 Gambaran Lengkap

### Arsitektur Sistem

```
ANTARMUKA PENGGUNA
├── JARVIS   → Wawancara, interaksi bahasa, respons ramah
├── ULTRON   → Kontrol perangkat, eksekusi perintah, status sistem
└── BRAHMA AI → Pemahaman mendalam, analisis, penyimpanan pengetahuan

PENGELOLA ALUR
└── HERMES   → Pengarah pesan, putuskan siapa yang menjawab, koordinasi

SUMBER KECERDASAN
├── GEMINI 2.0 FLASH  → Utama, cepat, percakapan umum
├── 9ROUTER           → Cadangan, lokal, jika Gemini tidak tersedia
└── JEV (TypeSafe System One) → Opsional: routing hint, safety gate, kurasi konteks
```

### Alur Chat

1. PENGGUNA mengirim pesan
2. HERMES menerima → analisis jenis pesan
   - Perintah perangkat → ULTRON
   - Percakapan/pertanyaan → GEMINI → 9ROUTER
   - Butuh pengetahuan mendalam → BRAHMA AI
   - Sambutan/perkenalan → JARVIS
3. Hasil dikembalikan ke HERMES → susun jawaban → tampilkan
4. BRAHMA AI menyimpan percakapan untuk ingatan

### Fitur Utama

| Komponen | Peran |
|---|---|
| **JARVIS** | Wajah ramah, sambutan, perkenalan, bimbingan pengguna |
| **ULTRON** | Tangan & mata sistem — eksekusi perintah perangkat, status |
| **BRAHMA AI** | Ingatan & pemahaman — simpan percakapan, konteks, analisis |
| **HERMES** | Pengarah alur — terima pesan, putuskan ke inti mana |
| **Gemini 2.0 Flash** | Sumber kecerdasan utama — cepat, percakapan umum |
| **9Router** | Sumber cadangan — lokal, jika Gemini tidak tersedia |
| **JEV (opsional)** | Lapisan supervisi: routing hint, safety gate, kurasi konteks |

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

## 🚀 Quick Start

### Di HP Android (Termux)

```bash
# 1. Pasang dependensi
pkg update && pkg upgrade -y
pkg install -y python python-pip git termux-api
pip install --upgrade pip
pip install -r requirements.txt

# 2. Pasang Termux:API dari F-Droid (wajib untuk kendali perangkat)
#    https://f-droid.org/packages/com.termux.api/

# 3. Jalankan
python main.py

# 4. Buka browser: http://localhost:8000
```

### Di PC / Laptop (Lokal)

```bash
# 1. Pastikan Python 3.9+ dan pip sudah terpasang
python --version
pip install -r requirements.txt

# 2. Jika ingin kendali perangkat via ADB, pastikan ADB terpasang
#    dan perangkat sudah dalam mode USB debugging

# 3. Jalankan — akan ditanya apakah ingin aktifkan ADB (kalau TTY tersedia)
python main.py

# 4. Buka browser: http://localhost:8000
```

### Dengan Docker

```bash
# Bangun image
docker build -t jabrig .

# Jalankan
docker run -d \
  --name jabrig \
  -p 8000:8000 \
  -e GEMINI_API_KEY="AIzaSy..." \
  -e ROUTER_API_KEY="..." \
  jabrig

# Buka browser: http://localhost:8000
```

---

## 📦 Instalasi Per Platform

### 1. VPS (Ubuntu/Debian + systemd)

```bash
# Clone repo
git clone https://github.com/dae-rubi/Jabrigs-AI.git
cd Jabrigs-AI

# Install dependensi
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
pip3 install -r requirements.txt

# Buat .env
cat > .env <<EOF
GEMINI_API_KEY=AIzaSy...
ROUTER_API_KEY=...
TYPESAFE_API_KEY=...
JABRIG_KENDALI=TIDAK_AKTIF
EOF
chmod 600 .env

# Aktifkan service systemd
sudo cp jabrig.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jabrig.service
sudo systemctl start jabrig.service

# Cek status
sudo systemctl status jabrig.service
journalctl -u jabrig.service -f
```

### 2. Hugging Face Spaces

1. Buat Space baru → Settings → SDK: **Python**
2. Buat `requirements.txt`:
   ```
   fastapi
   uvicorn[standard]
   httpx
   python-jose[cryptography]
   passlib[bcrypt]
   ```
3. Buat `app.py` (salin isi `main.py`, tapi hapus bagian `if __name__ == "__main__":`)
4. Jalankan dengan Gunicorn atau Uvicorn:
   ```
   gunicorn app:app --timeout 9999 --workers 1
   ```
   atau
   ```
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
5. Isi Secrets di dashboard HF: `GEMINI_API_KEY`, dll.

### 3. Google Colab

```python
# Sel 1: Install
!pip install fastapi uvicorn httpx python-jose[cryptography] passlib[bcrypt] pyngrok

# Sel 2: Jalankan server di background
import subprocess, threading
subprocess.run(['python', '/content/main.py'], stdout=open('/content/jabrig-colab.log', 'w'))

# Sel 3: Ekspos dengan ngrok (atau cloudflared)
from pyngrok import ngrok
ngrok.connect(8000)
print(f"URL: {ngrok.connect(8000).url()}")
```

Alternatif tunnel: `cloudflared tunnel --url localhost:8000`

### 4. Koyeb

1. Push kode ke GitHub
2. Di Koyeb dashboard:
   - Buildpack: **Python**
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $KOYEB_APP_PORT`
   - Environment Variables: isi `GEMINI_API_KEY`, dll.
3. Deploy

Atau gunakan Dockerfile (lihat `Dockerfile` di repo ini).

### 5. Cloudflare Tunnel (VPS + Tunnel)

Jika VPS menjalankan JABRIG, gunakan Cloudflare Tunnel untuk akses HTTPS:

```bash
# Install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Buat tunnel
cloudflared tunnel --url localhost:8000
```

Catatan: Cloudflare Workers sendiri tidak cocok untuk FastAPI Python penuh. Gunakan VPS + tunnel.

### 6. VPS Lain (General)

Ikuti pola yang sama seperti VPS Ubuntu/Debian:
1. Pasang Python 3.9+
2. `pip install -r requirements.txt`
3. Isi `.env`
4. (Opsional) systemd service — lihat `jabrig.service`
5. (Opsional) Caddy/tunnel untuk HTTPS

### 7. Termux (HP Android)

Lihat Quick Start bagian HP Android di atas.

---

## 📖 Wiki Singkat

### Komponen

| Komponen | File/Class | Peran |
|---|---|---|
| JARVIS | `Jarvis` | Sambutan, bantuan, perkenalan |
| ULTRON | `KendaliPerangkat` + `UltronAPI` | Kendali perangkat (buka/tutup/notifikasi/screenshot) |
| BRAHMA AI | `BrahmanAI` | Ingatan percakapan, konteks, session |
| HERMES | `HermesPengarah` | Routing pesan ke komponen yang tepat |
| Gemini | `PengelolaAI` → Gemini | AI utama |
| 9Router | `PengelolaAI` → 9Router | AI cadangan |
| JEV (opsional) | `JevSupervisor` | Routing hint, safety gate, kurasi |

### Endpoint API

| URL | Method | Keterangan |
|---|---|---|
| `/` | GET | Halaman utama HTML (chat) |
| `/perintah` | POST | Kirim pesan, dapat jawaban |
| `/status` | GET | Status sistem (JSON) |
| `/health` | GET | Health check |
| `/brahma/konteks` | GET | Konteks percakapan |
| `/brahma/session` | GET | Daftar session |

### Lingkungan Variabel

| Nama | Keterangan | Default |
|---|---|---|
| `GEMINI_API_KEY` | Kunci Google AI Studio | (kosong) |
| `ROUTER_API_KEY` | Kunci 9Router | (kosong) |
| `ROUTER_API_URL` | URL 9Router | `http://localhost:20128` |
| `TYPESAFE_API_KEY` | Kunci JEV (opsional) | (kosong) |
| `JEV_MODEL` | Model JEV | `jev-latest` |
| `JABRIG_KENDALI` | Mode kendali: ADB / TERMUX_API / TIDAK_AKTIF | (ditentukan otomatis) |
| `JABRIG_USER` | Nama user admin | `admin` |
| `JABRIG_PASS` | Kata sandi admin | `jabrig2026` |
| `PORT` | Port server (Docker) | `8000` |

---

## 🛟 Dukungan & Troubleshooting

### JABRIG tidak start

- Cek log:
  - systemd: `journalctl -u jabrig.service -e`
  - Manual: lihat output terminal
- Cek env: `cat .env`
- Test manual: `python main.py`

### Watchdog tidak restart

- Cek log: `cat /root/jabrig-watchdog.log`
- Cek PID: `cat /run/jabrig-watchdog.pid`
- Test manual: `bash jabrig-watchdog.sh status`

### Caddy gagal dapat HTTPS

- Pastikan domain sudah pointing ke IP server
- Cek log: `journalctl -u caddy -e`
- Test config: `caddy validate --config /etc/caddy/Caddyfile`

### AI tidak merespons

- Isi `GEMINI_API_KEY` atau `ROUTER_API_KEY`
- Cek koneksi internet
- Cek status: `curl http://localhost:8000/status`

### Termux:API tidak berfungsi

- Pasang Termux:API dari F-Droid
- Berikan izin (notifikasi, akses aplikasi, akses layar)

### Error import

- Pasang ulang dependensi: `pip install -r requirements.txt`
- Pastikan pakai environment yang benar

---

## 📁 Struktur Berkas

```
/
├── main.py                 # JABRIG utama (v3.0)
├── requirements.txt         # Dependensi Python
├── Dockerfile              # Docker build
├── WIZARD_FULL.sh          # Wizard instalasi multi-platform
├── INSTALL.md              # Dokumentasi instalasi
├── jabrig.service          # systemd unit
├── jabrig-watchdog.sh      # Watchdog script
├── jabrig-cron.service     # Cron systemd service
├── jabrig-cron.timer       # Cron systemd timer
├── jabrig-cron-task.sh     # Script task cron
├── setup-caddy.sh          # Script setup Caddy
├── .gitignore              # Git ignore rules
├── README.md               # README (ringkasan)
├── WIZARD.md               # Wizard instalasi
├── WIKI.md                 # Wiki komprehensif
├── DUKUNGAN.md             # Dukungan & troubleshooting
├── SPESIFIKASI.md          # Spesifikasi teknis
├── telegram-bot/           # Telegram bot (terpisah)
└── ultron/                 # Ultron framework (terpisah)
```

---

## 🤝 Kontribusi

1. Fork repositori
2. Buat branch fitur: `git checkout -b fitur-anda`
3. Commit perubahan: `git commit -m "fitur: ..."`
4. Push ke branch: `git push origin fitur-anda`
5. Buka Pull Request

---

## 📄 Lisensi

MIT — bebas digunakan, dimodifikasi, dan didistribusikan.

---

## 🔗 Links

- **Repositori**: https://github.com/dae-rubi/Jabrigs-AI
- **Issue tracker**: https://github.com/dae-rubi/Jabrigs-AI/issues
