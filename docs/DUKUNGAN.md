# ⚡ JABRIG — Panduan Dukungan

Versi: 3.0 | 2026-09-27

---

## 🆘 Darurat

### JABRIG tidak jalan

1. Cek dependensi:
   ```bash
   pip install -r requirements.txt
   ```
2. Cek config:
   ```bash
   cat config/api_keys.json
   ```
3. Cek log:
   ```bash
   python main.py 2>&1 | tee jabrig.log
   ```

### Web UI tidak muncul

1. Cek port:
   ```bash
   ss -tlnp | grep 8000
   # atau
   netstat -tlnp | grep 8000
   ```
2. Coba port lain:
   ```bash
   uvicorn main:app --port 8080
   ```

### Gemini error

1. Cek API key:
   ```bash
   cat config/api_keys.json
   ```
2. Test langsung:
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIza..."
   ```

### 9Router error

1. Pastikan 9Router jalan:
   ```bash
   # Contoh: jika 9Router adalah layanan terpisah
   curl http://localhost:20128/status
   ```
2. Cek API key di config.

### HP tidak bisa buka aplikasi

1. Cek Termux:API:
   ```bash
   termux-notification --help
   ```
   Kalau error, install ulang dari F-Droid.
2. Cek izin:
   - Buka Settings → Apps → Termux → Permissions
   - Aktifkan "Notifikasi" dan "Akses file"
3. Coba perintah manual:
   ```bash
   termux-open-url whatsapp://
   ```

### Screenshot gagal

1. Cek direktori:
   ```bash
   ls -la ~/jabrig
   ```
   Kalau folder tidak ada, buat manual:
   ```bash
   mkdir -p ~/jabrig
   ```
2. Cek Termux:API (lihat poin HP di atas).

### Plugin/Action tidak terdaftar

1. Cek log saat startup — harus muncul:
   ```
   Action dimuat: nama_action (nama_file.py)
   Plugin dimuat: nama_plugin (nama_file.py)
   ```
2. Jika tidak muncul, cek:
   - File `.py` ada di folder yang benar
   - Ada dict `TOOL` (action) atau `PLUGIN` (plugin)
   - Tidak ada error sintaks

### Memori tidak menyimpan

1. Cek file:
   ```bash
   cat memory/long_term.json
   ```
2. Kalau error, hapus dan coba lagi:
   ```bash
   rm memory/long_term.json
   python main.py
   ```

---

## 📧 Contact

- Buat issue di GitHub: https://github.com/dae-rubi/Jabrigs-AI/issues
- Atau kirim email (kalau ada)

---

## ✅ Checklist Troubleshooting

| Masalah | Solusi |
|---------|--------|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Port 8000 dipakai | Ganti port di uvicorn |
| Gemini error | Cek API key |
| 9Router error | Cek 9Router running + key |
| HP aplikasi gagal | Install Termux:API + izin |
| Screenshot error | Cek folder ~/jabrig |
| Plugin tidak muncul | Cek log + struktur file |
| Memory error | Hapus long_term.json, restart |

---

## 📝 Log

Log mencetak ke stdout (terminal). Untuk menyimpan:

```bash
python main.py > jabrig.log 2>&1
```

Atau pakai `tee`:

```bash
python main.py 2>&1 | tee jabrig.log
```

---

## 🔐 Keamanan

### API Key

Jangan komit `config/api_keys.json` ke repo publik. File ini ada di `.gitignore`?

Untuk development lokal, bisa pakai env var:

```bash
export GEMINI_API_KEY=AIza...
python main.py
```

Untuk production, lebih baik pakai secret manager atau file config yang di-protect.

### CORS

Hanya untuk development: CORS diizinkan semua (`allow_origins=["*"]`).

Untuk production, batasi:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://domain.com"],
    ...
)
```

---

## 📊 Monitoring

### Status Check

```bash
curl http://localhost:8000/status | python -m json.tool
```

### Log Watching

```bash
tail -f jabrig.log
```

### Process Check

```bash
ps aux | grep uvicorn
# atau
ps aux | grep main.py
```

---

## 📥 Uninstall

1. Hentikan proses:
   ```bash
   pkill -f "uvicorn main:app"
   # atau
   pkill -f "python main.py"
   ```
2. Hapus folder:
   ```bash
   rm -rf Jabrigs-AI
   ```
3. Hapus dependensi (opsional):
   ```bash
   pip uninstall fastapi uvicorn httpx python-jose passlib
   ```

---

## 🔄 Update

```bash
git pull
pip install -r requirements.txt --upgrade
python main.py
```

---

## 🆕 Versi Terbaru

Lihat riwayat perubahan di GitHub: https://github.com/dae-rubi/Jabrigs-AI/commits/main

---

## 📖 Dokumentasi Lain

- [README](docs/README.md) — gambaran umum
- [WIZARD](docs/WIZARD.md) — instalasi
- [WIKI](docs/WIKI.md) — wiki komprehensif
- [SPESIFIKASI](docs/SPESIFIKASI.md) — spesifikasi teknis
- [ALLINONE](ALLINONE.md) — overview lengkap
