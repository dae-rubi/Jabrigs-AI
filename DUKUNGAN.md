# Dukungan JABRIG v3.0

Panduan bantuan, troubleshooting, dan cara mendapatkan dukungan untuk JABRIG.

---

## Daftar Isi

1. [Mulai Cepat](#mulai-cepat)
2. [Masalah Umum](#masalah-umum)
3. [Troubleshooting Detail](#troubleshooting-detail)
4. [Kontribusi](#kontribusi)
5. [Hubungi Dukungan](#hubungi-dukungan)

---

## Mulai Cepat

### Masalah: Server tidak mau start

**Gejala:** `python main.py` langsung error atau traceback.

**Penyebab & Solusi:**

1. **Dependensi belum terpasang**
   ```
   pip install fastapi uvicorn httpx "python-jose[cryptography]" "passlib[bcrypt]"
   ```

2. **Python versi terlalu lama**
   JABRIG memerlukan Python 3.9+. Cek dengan `python --version`.

3. **Port 8000 sudah dipakai**
   Cek dengan `lsof -i :8000` atau `netstat -tlnp | grep 8000`.
   Jika dipakai, ubah port di bagian `__main__` di `main.py`.

---

### Masalah: Termux:API tidak berfungsi

**Gejala:** Perintah `buka`, `tutup`, `ambil layar`, `notifikasi` gagal dengan pesan kesalahan.

**Penyebab & Solusi:**

1. **Termux:API belum terpasang**
   Pasang dari F-Droid: https://f-droid.org/packages/com.termux.api/

2. **Izin belum diberikan**
   Pergi ke Settings > Apps > Termux:API dan beri izin notifikasi, akses aplikasi, dan akses layar.

3. **Perangkat tidak mendukung skema URL**
   Beberapa perangkat tidak mendukung `termux-open-url` dengan skema kustom.
   Pastikan aplikasi yang ingin dibuka sudah terpasang dan mendukung skema URL-nya.

---

### Masalah: ADB tidak terdeteksi (PC)

**Gejala:** Saat menjalankan di PC dan memilih `y` untuk ADB, muncul pesan "Kendali tidak diaktifkan" atau error.

**Penyebab & Solusi:**

1. **ADB belum terpasang**
   Pasang ADB dari platform-tools Android:
   ```
   # Di Linux
   sudo apt install adb

   # Di macOS (dengan Homebrew)
   brew install android-platform-tools

   # Di Windows
   Unduh dari: https://developer.android.com/studio/releases/platform-tools
   ```

2. **Perangkat tidak terkoneksi**
   - Aktifkan USB debugging di perangkat Android
   - Hubungkan perangkat via USB
   - Cek dengan `adb devices` — harus muncul perangkat

3. **Driver belum terpasang (Windows)**
   Pasang driver USB untuk perangkat Android.

---

### Masalah: AI tidak merespons

**Gejala:** Jawaban selalu fallback lokal dengan pesan "Isi GEMINI_API_KEY..."

**Penyebab & Solusi:**

1. **Kunci API belum diatur**
   ```
   export GEMINI_API_KEY="AIzaSy..."
   export ROUTER_API_KEY="your-key"
   ```

2. **Koneksi internet bermasalah**
   Pastikan perangkat terhubung ke internet. Cek dengan `ping google.com`.

3. **Kunci tidak valid**
   - Gemini: dapatkan kunci di https://aistudio.google.com/apikey
   - 9Router: pastikan 9Router berjalan di URL yang ditentukan

---

### Masalah: Web UI tidak bisa diakses

**Gejala:** Browser menampilkan "Unable to connect" atau "Connection refused".

**Penyebab & Solusi:**

1. **Server belum berjalan**
   Pastikan `python main.py` sedang berjalan di terminal lain.

2. **Salah alamat**
   Gunakan `http://localhost:8000` atau `http://127.0.0.1:8000`.

3. **Port berbeda**
   Jika server berjalan di port lain, sesuaikan URL.

4. **Akses dari perangkat lain di jaringan**
   - Gunakan alamat IP server: `http://<IP_SERVER>:8000`
   - Pastikan firewall mengizinkan akses masuk ke port 8000

---

### Masalah: Respon lambat atau timeout

**Gejala:** Permintaan AI membutuhkan waktu sangat lama atau gagal dengan timeout.

**Penyebab & Solusi:**

1. **Koneksi internet lambat**
   - Naikkan nilai timeout di `PengelolaAI` (ubah `timeout` di `__init__`)

2. **Gemini rate limit**
   - Google AI Studio memiliki batas penggunaan. Tunggu beberapa saat atau naikkan batas.

3. **9Router tidak responsif**
   - Pastikan 9Router berjalan dan merespons di URL yang ditentukan

---

### Masalah: Error saat import modul

**Gejala:** `ModuleNotFoundError: No module named 'fastapi'` atau serupa.

**Penyebab & Solusi:**

1. **Modul belum terpasang**
   ```
   pip install fastapi uvicorn httpx "python-jose[cryptography]" "passlib[bcrypt]"
   ```

2. **Membangun di lingkungan virtual yang salah**
   Pastikan menggunakan environment yang sama dengan tempat dependensi diinstal.
   ```
   source /path/to/venv/bin/activate
   python main.py
   ```

---

## Troubleshooting Detail

### Memeriksa status sistem

Setelah server berjalan, akses:
- `http://localhost:8000/status` — status lengkap sistem
- `http://localhost:8000/health` — health check sederhana
- `http://localhost:8000/brahma/konteks` — konteks BRAHMA

### Melihat log server

Terminal yang menjalankan `python main.py` akan menampilkan log:
- Status AI saat startup
- Request yang masuk
- Error jika terjadi

### Merestart server

1. Tekan `Ctrl + C` di terminal yang menjalankan server
2. Jalankan kembali `python main.py`

---

## Kontribusi

### Cara berkontribusi

1. **Fork repositori**
2. **Buat branch fitur**: `git checkout -b fitur-anda`
3. **Commit perubahan**: `git commit -m "Menambah fitur X"`
4. **Push ke branch**: `git push origin fitur-anda`
5. **Buka Pull Request**

### Area kontribusi

- **Fitur baru**: Tambahkan fungsi atau komponen baru
- **Perbaikan bug**: Perbaiki masalah yang ditemukan
- **Dokumentasi**: Perbaiki atau tambah dokumentasi
- **UI/UX**: Perbaiki tampilan atau pengalaman pengguna

---

## Hubungi Dukungan

Jika mengalami masalah yang tidak tercantum di atas:

1. **Periksa log server** untuk pesan error detail
2. **Cek 엔드포인트 status** (`/status`) untuk informasi sistem
3. **Buat issue** di repositori GitHub dengan:
   - Deskripsi masalah yang jelas
   - Langkah reproduksi
   - Output log/error
   - Informasi sistem (OS, Python version, Termux/PC)

---

## Informasi Sistem yang Dibutuhkan untuk Bug Report

Saat melaporkan bug, sertakan:

- Versi JABRIG (dari `main.py` header atau `/health`)
- Sistem operasi (Android Termux / Linux / macOS / Windows)
- Versi Python (`python --version`)
- Dependensi yang terpasang (`pip list`)
- Mode kendali (Termux:API / ADB / Tidak Aktif)
- Status AI (Gemini aktif/tidak, 9Router aktif/tidak)
- Langkah-langkah untuk mereproduksi masalah
- Output error atau log yang relevan
