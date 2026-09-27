# Integrasi JABRIG: systemd, Watchdog, Cron, Caddy

Dokumen ini menjelaskan cara mengintegrasikan semua komponen agar JABRIG otomatis berjalan, dipantau, dan bisa diakses via HTTPS.

## Isi
1. [Sebelum mulai](#sebelum-mulai)
2. [Auto-start via systemd](#autostart-via-systemd)
3. [Watchdog otomatis](#watchdog-otomatis)
4. [Cronjob berkala](#cronjob-berkala)
5. [Caddy + HTTPS otomatis](#caddy--https-otomatis)
6. [Verifikasi](#verifikasi)
7. [Troubleshooting](#troubleshooting)

---

## Sebelum mulai

Pastikan:
- Python 3.9+ dan dependensi JABRIG terpasang
- `main.py` ada di `/root/main.py` (atau sesuaikan path)
- Anda punya akses root/sudo

---

## Auto-start via systemd

### 1. Pasang file layanan
```bash
sudo cp /root/jabrig.service /etc/systemd/system/jabrig.service
sudo systemctl daemon-reload
```

### 2. Opsional: set environment variable
Buat `/root/.jabrig-env`:
```bash
cat > /root/.jabrig-env <<EOF
GEMINI_API_KEY=AIzaSy...
ROUTER_API_KEY=...
TYPESAFE_API_KEY=...
JEV_MODEL=jev-latest
EOF
sudo chmod 600 /root/.jabrig-env
```

### 3. Aktifkan & mulai
```bash
sudo systemctl enable jabrig.service
sudo systemctl start jabrig.service
sudo systemctl status jabrig.service
```

Cek log:
```bash
journalctl -u jabrig.service -f
```

---

## Watchdog otomatis

Watchdog memantau apakah proses JABRIG masih hidup. Kalau mati, otomatis restart.

### 1. Buat file watchdog
```bash
chmod +x /root/jabrig-watchdog.sh
```

### 2. Jalankan sebagai daemon (manual)
```bash
nohup bash /root/jabrig-watchdog.sh watch &
```

### 3. Atau jalankan lewat systemctl (lebih rapi)
Buat file `/etc/systemd/system/jabrig-watchdog.service`:
```ini
[Unit]
Description=JABRIG Watchdog
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash /root/jabrig-watchdog.sh watch
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Lalu:
```bash
sudo cp /etc/systemd/system/jabrig-watchdog.service
sudo systemctl daemon-reload
sudo systemctl enable jabrig-watchdog.service
sudo systemctl start jabrig-watchdog.service
```

Cek status:
```bash
bash /root/jabrig-watchdog.sh status
```

---

## Cronjob berkala

Task berkala: kesehatan check, cleanup temp file, log ringkasan.

### Opsi A: systemd timer (direkomendasikan)
```bash
sudo cp /root/jabrig-cron.service /etc/systemd/system/
sudo cp /root/jabrig-cron.timer /etc/systemd/system/
sudo chmod +x /root/jabrig-cron-task.sh
sudo systemctl daemon-reload
sudo systemctl enable --now jabrig-cron.timer
sudo systemctl status jabrig-cron.timer
```

Lihat log task:
```bash
journalctl -u jabrig-cron.service -f
```

### Opsi B: crontab biasa
```bash
crontab -e
# Tambahkan:
0 */6 * * * /root/jabrig-cron-task.sh >> /root/jabrig-cron-task.log 2>&1
```

---

## Caddy + HTTPS otomatis

Caddy menyediakan reverse proxy + HTTPS otomatis (Let's Encrypt).

### 1. Jalankan script setup
```bash
chmod +x /root/setup-caddy.sh
sudo bash /root/setup-caddy.sh
```

Script akan:
- Install Caddy kalau belum ada
- Buat Caddyfile di `/etc/caddy/Caddyfile`
- Test konfigurasi
- Jalankan Caddy sebagai service

### 2. Ganti nama domain
Jika punya domain, edit `/etc/caddy/Caddyfile`:
```caddy
your-domain.com {
    reverse_proxy localhost:8000
}
```

Lalu reload Caddy:
```bash
sudo systemctl reload caddy
```

Caddy akan otomatis dapat sertifikat HTTPS dari Let's Encrypt.

### 3. Verifikasi
- http://localhost:80 → harusnya redirect ke HTTPS (kalau domain diatur)
- https://your-domain.com → UI JABRIG

---

## Verifikasi

### Cek semua service
```bash
systemctl status jabrig.service
systemctl status jabrig-watchdog.service
systemctl status jabrig-cron.timer
systemctl status caddy
```

### Cek log masing-masing
```bash
journalctl -u jabrig.service -f
journalctl -u jabrig-watchdog.service -f
journalctl -u jabrig-cron.service -f
journalctl -u caddy -f
```

### Cek watchdog manual
```bash
bash /root/jabrig-watchdog.sh status
```

### Cek endpoint JABRIG
```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/status
```

---

## Troubleshooting

### JABRIG tidak start
- Cek log: `journalctl -u jabrig.service -e`
- Cek env: `cat /root/.jabrig-env`
- Test manual: `python3 /root/main.py`

### Watchdog gagal restart
- Cek log: `cat /root/jabrig-watchdog.log`
- Cek PID: `cat /run/jabrig-watchdog.pid`

### Caddy gagal dapat HTTPS
- Pastikan domain sudah pointing ke IP server
- Cek log: `journalctl -u caddy -e`
- Test config: `caddy validate --config /etc/caddy/Caddyfile`

---

## Struktur file

```
/root/
├── main.py                 # JABRIG utama
├── jabrig.service         # systemd unit
├── jabrig-watchdog.sh     # watchdog script
├── jabrig-cron.service    # systemd cron task
├── jabrig-cron.timer      # systemd timer
├── jabrig-cron-task.sh    # script task berkala
├── setup-caddy.sh         # script setup Caddy
├── .jabrig-env            # env vars (opsional)
└── INSTALL.md             # ini
```

---

Jika ada yang perlu disesuaikan (mis. path berbeda, port berbeda, user bukan root), tinggal edit file yang sesuai.
