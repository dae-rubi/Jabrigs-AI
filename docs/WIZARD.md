# ⚡ JABRIG — Wizard Instalasi

Versi: 3.0 | 2026-09-27

---

## 📋 Prasyarat

- Python 3.8+
- Terminal / command line
- (Optional) Termux:API di HP Android
- (Optional) ADB di PC

---

## 🚀 Instalasi Cepat

### 1. Clone / Download

```bash
git clone https://github.com/dae-rubi/Jabrigs-AI.git
cd Jabrigs-AI
```

### 2. Pasang Dependensi

```bash
pip install -r requirements.txt
```

Atau manual:

```bash
pip install fastapi uvicorn httpx "python-jose[cryptography]" passlib[bcrypt]
```

### 3. Konfigurasi API Key

Edit `config/api_keys.json`:

```json
{
  "gemini_api_key": "GEMINI_API_KEY_ANDA_DI_SINI",
  "router_url": "http://localhost:20128",
  "router_api_key": ""
}
```

### 4. Jalankan

```bash
python main.py
```

Atau:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Buka Browser

```
http://localhost:8000
```

---

## 📱 HP Android (Termux)

### Persiapan

1. Install Termux dari **F-Droid** (bukan Play Store)
2. Install Termux:API dari F-Droid
3. Buka Termux:API dan berikan izin

### Verifikasi

```bash
termux-notification --help
termux-screenshot --help
termux-open-url --help
```

Kalau perintah di atas berjalan, Termux:API siap.

### Jalankan di Termux

```bash
cd Jabrigs-AI
pip install -r requirements.txt
python main.py
```

---

## 💻 PC / Laptop

### Python

Pastikan Python 3.8+ terpasang:

```bash
python --version
```

### Pasang Dependensi

```bash
pip install -r requirements.txt
```

### ADB (Opsional)

Jika ingin kendali perangkat via ADB:

1. Install adb (Platform Tools)
2. Sambungkan perangkat Android
3. `adb devices` — pastikan perangkat muncul

### Jalankan

```bash
python main.py
```

Akan muncul pertanyaan:

```
Aktifkan kendali via ADB? (y/n):
```

Ketik `y` jika ingin aktifkan, `n` untuk tunda.

---

## 🔌 API Key

### Gemini

Dapatkan API key di [Google AI Studio](https://aistudio.google.com/apikey).

Isi di `config/api_keys.json`:

```json
"gemini_api_key": "AIza..."
```

### 9Router

Jika sudah punya 9Router instance:

```json
"router_url": "http://localhost:20128",
"router_api_key": "API_KEY_9ROUTER"
```

---

## 🐳 Docker

### Build

```bash
docker build -t jabrig .
```

### Run

```bash
docker run -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/memory:/app/memory \
  jabrig
```

### Environment Variables

```bash
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=AIza... \
  -e ROUTER_URL=http://localhost:20128 \
  -e ROUTER_API_KEY=xyz \
  jabrig
```

---

## 🌐 Deployment

### Systemd (Linux)

```bash
sudo cp infra/jabrig.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jabrig
sudo systemctl start jabrig
```

### Watchdog

```bash
chmod +x infra/jabrig-watchdog.sh
./infra/jabrig-watchdog.sh start
```

### Cron (Tugas Berkala)

```bash
sudo cp infra/jabrig-cron.service infra/jabrig-cron.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jabrig-cron.timer
sudo systemctl start jabrig-cron.timer
```

### Caddy (Reverse Proxy + HTTPS)

```bash
chmod +x infra/setup-caddy.sh
./infra/setup-caddy.sh
```

---

## ✅ Verifikasi

Setelah jalan, buka:

```
http://localhost:8000
```

Coba perintah:
- `halo` → sapaan
- `status` → status sistem
- `buka youtube` → buka aplikasi (jika ada)

---

## 🐛 Troubleshooting

### `ModuleNotFoundError`

Pastikan pakai environment yang sama dan dependensi terpasang.

### Port 8000 dipakai

Ganti port:

```bash
uvicorn main:app --port 8080
```

Atau ubah di `main.py` (bagian `uvicorn.run`).

### Screenshot gagal di HP

Pastikan Termux:API terpasang dan ADA izin notifikasi.

### Aplikasi tidak bisa dibuka

- HP: cek Termux:API
- PC: cek `adb devices`

---

## 📞 Butuh Bantuan?

Lihat `docs/DUKUNGAN.md` atau buat issue di GitHub.
