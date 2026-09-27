# JABRIG Wizard Instalasi

Panduan langkah demi langkah untuk menginstal dan menjalankan JABRIG v3.0.

---

## Ringkasan

JABRIG adalah satu berkas Python (`main.py`) yang berjalan di:
- **HP Android** melalui Termux (menggunakan Termux:API, tanpa root, tanpa ADB wajib)
- **PC/Laptop** (dengan opsi kendali perangkat via ADB)

Sistem mencakup tiga inti kecerdasan:
- **JARVIS** — antarmuka percakapan ramah
- **ULTRON** — kendali perangkat
- **BRAHMA AI** — ingatan & pemahaman

---

## Langkah 1: Siapkan Lingkungan

### Opsi A: HP Android (Termux)

1. Pasang **Termux** dari F-Droid (https://f-droid.org/packages/com.termux/)
2. Pasang **Termux:API** dari F-Droid (wajib untuk kendali perangkat)
3. Berikan izin Termux:API di Settings > Apps > Termux:API

```bash
pkg update && pkg upgrade -y
pkg install -y python python-pip git termux-api
```

### Opsi B: PC / Laptop

```bash
# Python 3.9+ sudah terpasang
pip install --upgrade pip
pip install fastapi uvicorn httpx "python-jose[cryptography]" "passlib[bcrypt]"
```

---

## Langkah 2: Pasang Dependensi Python

```bash
pip install fastapi uvicorn httpx "python-jose[cryptography]" "passlib[bcrypt]"
```

Dependensi yang dipasang:
- `fastapi` — framework web
- `uvicorn` — server ASGI
- `httpx` — klien HTTP async untuk panggilan AI
- `python-jose[cryptography]` — JWT untuk autentikasi
- `passlib[bcrypt]`` — hashing kata sandi

---

## Langkah 3: Unduh JABRIG

```bash
# Jika sudah di clone dari GitHub
cd /path/to/jabrig

# Atau buat direktori baru dan salin main.py
mkdir ~/jabrig
cp main.py ~/jabrig/
cd ~/jabrig
```

---

## Langkah 4: Konfigurasi (Opsional)

Buat berkas `.env` atau set variabel lingkungan:

```bash
# GEMINI_API_KEY — kunci Google AI Studio
export GEMINI_API_KEY="AIzaSy..."

# ROUTER_API_KEY & ROUTER_API_URL — untuk 9Router cadangan
export ROUTER_API_KEY="your-key"
export ROUTER_API_URL="http://localhost:20128"

# Kredensial admin (opsional — default: admin/jabrig2026)
export JABRIG_USER="admin"
export JABRIG_PASS="kata-sandi-anda"
```

---

## Langkah 5: Jalankan JABRIG

```bash
python main.py
```

Sistem akan:
1. Mendeteksi perangkat (Termux atau PC)
2. Jika PC, menanyakan apakah ingin aktifkan ADB
3. Memeriksa koneksi Termux:API atau ADB
4. Memeriksa sumber AI (Gemini & 9Router)
5. Menjalankan server web di `http://localhost:8000`

---

## Langkah 6: Gunakan

Buka browser dan akses `http://localhost:8000`. Coba perintah:

- `halo` — sambutan JARVIS
- `siapa kamu` — identitas sistem
- `status` — status sistem
- `buka youtube` — buka aplikasi
- `tutup whatsapp` — tutup aplikasi
- `ambil layar` — tangkapan layar
- `notifikasi halo dunia` — kirim notifikasi

---

## Troubleshooting

### Termux:API tidak merespons
- Pastikan Termux:API terpasang dari F-Droid
- Berikan izin notifikasi dan akses aplikasi
- restart Termux

### ADB tidak terdeteksi
- Pastikan ADB terpasang dan perangkat terkoneksi
- Aktifkan USB debugging di perangkat

### AI tidak merespons
- Isi `GEMINI_API_KEY` atau `ROUTER_API_KEY`
- Cek koneksi internet

### Port 8000 sudah dipakai
- Ubah port di bagian `__main__` di `main.py` atau gunakan variabel lingkungan `PORT`

---

## Berhenti

Tekan `Ctrl + C` di terminal untuk menghentikan server.
