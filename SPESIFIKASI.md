# SPESIFIKASI TEKNIS JABRIG v3.0

Dokumen ini menjelaskan spesifikasi teknis lengkap JABRIG v3.0 untuk pengembang, kontributor, dan auditor sistem.

---

## Informasi Umum

| Atribut | Nilai |
|---|---|
| Nama proyek | JABRIG |
| Versi | 3.0 |
| Tanggal rilis | 2026-09-27 |
| Bahasa pemrograman | Python 3.9+ |
| Lisensi | MIT |
| Repositori | https://github.com/fathan-aziz/jabrig |
| Status | Stabil |

---

## Komponen Sistem

### 1. JARVIS (Just A Rather Very Intelligent System)

**Peran:** Wajah dan antarmuka percakapan yang ramah.

**Kata kunci pemicu:**
- halo, hai, selamat, pagi, siang, sore, malam
- perkenalkan, bantu, help
- siapa kamu, apa kabar

**Fungsi utama:**
- Menyambut pengguna dengan waktu real-time (pagi/siang/sore/malam)
- Memberikan perkenalan sistem
- Menawarkan bantuan dan contoh perintah
- Menjawab pertanyaan dasar tentang sistem

**Output standar:**
- Format teks ramah dengan emoji
- Informasi waktu dan salam sesuai waktu hari
- Daftar perintah contoh

### 2. ULTRON (Unit Lengkap Teknologi Operating Network)

**Peran:** Tangan dan mata sistem — eksekusi perintah perangkat dan monitoring status.

**Kata kunci pemicu:**
- buka, bukakan
- tutup, tutupkan, matikan
- ambil layar, tangkapan, screenshot, foto layar
- notifikasi, kirim pesan, beri tahu
- status, cek sistem, cek,lihat sistem

**Sub-komponen:**
- `KendaliPerangkat`: Kelas utama untuk operasi perangkat
- `UltronAPI`: Pembungkus yang menyesuaikan respons

**Operasi yang didukung:**

| Operasi | Termux:API | ADB |
|---|---|---|
| Buka aplikasi | `termux-open-url` | `adb shell am start` |
| Tutup aplikasi | `am force-stop` | `adb shell am force-stop` |
| Ambil layar | `termux-screenshot -o` | `adb shell screencap` + `adb pull` |
| Kirim notifikasi | `termux-notification` | (terbatas) |

**Aplikasi yang dikontrol:**

| Nama | Paket Android |
|---|---|
| whatsapp | com.whatsapp |
| telegram | org.telegram.messenger |
| youtube | com.google.android.youtube |
| pengaturan | com.android.settings |
| kamera | com.android.camera |
| galeri | com.android.gallery3d |
| kalkulator | com.android.calculator2 |

**Pengecekan koneksi:**
- Termux:API: Menggunakan `termux-notification --title tes`
- ADB: Menggunakan `adb devices` dan memeriksa keberadaan "device" di output

### 3. BRAHMA AI (Bengkel Rasa Heuristic & Artificial Memory Assistant)

**Peran:** Sistem ingatan dan pemahaman — menyimpan percakapan, mengelola konteks, dan memberikan analisis mendalam.

**Struktur data:**
- Session: ID unik, daftar pesan, jumlah pesan
- Pesan: ID, timestamp, peran (user/assistant/system), isi, sumber, jalur

**Operasi:**
- `simpan(peran, isi, metadata)`: Menyimpan pesan
- `dapat_konteks(limit)`: Mengambil riwayat terbaru
- `katabuka()`: Ringkasan konteks untuk prompt AI
- `alih_session(sid)`: Mengubah session aktif
- `daftar_session()`: Daftar semua session
- `hapus_session(sid)`: Menghapus session

**Penyimpanan:**
- Bertipe in-memory (dictionary)
- Session aktif default: "utama"
- Session baru dibuat dengan ID acak (secrets.token_urlsafe)

**Fungsi konteks:**
- Menyimpan konteks percakapan untuk respons AI yang lebih baik
- Membaca konteks sebelumnya saat pengguna mengirim pesan
- Menyediakan ringkasan untuk prompt AI

### 4. HERMES (Hubung Efisien Rute & Manajemen Eksekusi Sistem)

**Peran:** Pengarah alur — menerima pesan, menentukan ke komponen mana pesan dikirim, dan mengoordinasikan respons.

**Alur keputusan:**

```
1. Terima pesan dari pengguna
2. Analisis kata kunci:
   ├── Jika cocok dengan JARVIS → kirim ke JARVIS
   ├── Jika cocok dengan ULTRON → kirim ke ULTRON
   └── Jika tidak → kirim ke Gemini → 9Router
3. Terima hasil dari komponen yang ditunjuk
4. BRAHMA menyimpan hasil akhir
5. Kembalikan respons ke pengguna
```

**Prioritas:**
1. JARVIS (sambutan dan bantuan)
2. ULTRON (perintah perangkat)
3. Gemini / 9Router (pertanyaan umum)

**Integrasi:**
- Berinteraksi dengan semua komponen melalui antarmuka yang telah ditetapkan
- Menggunakan `asyncio.run()` untuk memanggil AI secara sinkron dari konteks non-async

### 5. Sumber Kecerdasan

#### Gemini 2.0 Flash

- **URL:** `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- **Autentikasi:** Kunci API melalui parameter query `?key=...`
- **Format request:** JSON dengan struktur `contents[0].parts[0].text`
- **Timeout:** 10 detik
- **Status:** Diperiksa melalui ketersediaan kunci API

#### 9Router

- **URL:** Dari variabel `ROUTER_API_URL` (default: `http://localhost:20128`)
- **Autentikasi:** Bearer token melalui header `Authorization`
- **Format request:** Format Chat Completions API (`/v1/chat/completions`)
- **Timeout:** 15 detik
- **Status:** Diperiksa melalui endpoint `/status`

#### Fallback Lokal

Jika tidak ada sumber AI yang tersedia:
- Menampilkan pesan informatif
- Menjelaskan kunci yang diperlukan
- Memberikan contoh perintah yang dapat digunakan

---

## API Reference

### Endpoint Utama

#### GET /

Halaman utama HTML — antarmuka chat interaktif.

**Respons:** HTML lengkap dengan CSS terintegrasi.

**Konten:**
- Judul: "⚡ JABRIG"
- Subjudul: "JARVIS • ULTRON • BRAHMA AI | v3.0 | <MODE>"
- Status sistem (perangkat, kendali, sumber AI)
- Tiga inti sistem (card grid)
- Kotak input pesan dengan tombol kirim
- Script JavaScript untuk mengirim pesan dan menampilkan respons

**Gaya tampilan:**
- Latar gelap (#03040a)
- Warna utama: biru (#4285f4) ke hijau (#00ff9d)
- Teks terang (#e8eaf6)
- Responsif (mobile-friendly)
- Font system-ui

#### POST /perintah

Menerima pesan pengguna dan mengembalikan jawaban dari HERMES.

**Request body:**
```json
{
  "pesan": "string",
  "teks": "string" (alternatif)
}
```

**Respons:**
```json
{
  "jalur": "JARVIS | ULTRON | GEMINI_UTAMA | 9ROUTER_CADANGAN | FALLBACK_LOKAL | ERROR",
  "sumber": "JARVIS | ULTRON | Gemini | 9Router | lokal | SYSTEM",
  "jawab": "string",
  "pesan": "string (alternatif)",
  "ok": true/false,
  "berkas": "string (path)",
  "detail": "string",
  "waktu_ms": number
}
```

**Kode error:**
- 400: Jika pesan kosong

#### GET /status

Mengembalikan status sistem lengkap dalam format JSON.

**Respons:**
```json
{
  "perangkat": "HP_ANDROID | PC",
  "kendali": {
    "mode": "TERMUX_API | ADB | TIDAK_AKTIF",
    "tersedia": true/false,
    "aplikasi": ["whatsapp", "telegram", ...]
  },
  "ai": {
    "Gemini": {"siap": true/false},
    "9Router": {"siap": true/false}
  },
  "session_brahma": {
    "aktif": "session_id",
    "jumlah_pesan": number,
    "semua_session": [{"id": "...", "jumlah": n}]
  },
  "timestamp": "ISO8601"
}
```

#### GET /health

Health check sederhana.

**Respons:**
```json
{"status": "OK", "versi": "3.0"}
```

#### GET /brahma/konteks

Mengembalikan konteks percakapan BRAHMA.

**Respons:**
```json
{"konteks": [{"id": "...", "timestamp": "...", "peran": "...", "isi": "...", ...}]}
```

#### GET /brahma/session

Mengembalikan daftar session.

**Respons:**
```json
{"sessions": [{"id": "...", "jumlah": n}, ...]}
```

---

## Spesifikasi Teknis

### Dependensi

| Paket | Versi | Keterangan |
|---|---|---|
| fastapi | >=0.100.0 | Framework web |
| uvicorn | >=0.23.0 | Server ASGI |
| httpx | >=0.24.0 | Klien HTTP async |
| python-jose[cryptography] | >=3.3.0 | JWT dan kriptografi |
| passlib[bcrypt] | >=1.7.4 | Hashing kata sandi |

### Ketergantungan Sistem

**Termux (Android):**
- `termux-api` package (dari F-Droid atau apt Termux)
- Izin Termux:API (notifikasi, akses aplikasi, akses layar)

**PC/Laptop (untuk ADB):**
- Android Debug Bridge (adb) dalam PATH
- Perangkat Android dengan USB debugging diaktifkan

### Konfigurasi

Semua konfigurasi melalui variabel lingkungan:

| Variabel | Default | Keterangan |
|---|---|---|
| `GEMINI_API_KEY` | "" | Kunci API Gemini |
| `ROUTER_API_URL` | "http://localhost:20128" | URL 9Router |
| `ROUTER_API_KEY` | "" | Kunci 9Router |
| `JABRIG_USER` | "admin" | Nama pengguna admin |
| `JABRIG_PASS` | "jabrig2026" | Kata sandi admin |

### Port

- Default: 8000
- Server berjalan di `0.0.0.0:8000`
- Dapat diubah dengan mengedit bagian `__main__` di `main.py`

### Keamanan

#### JWT

- Algoritma: HS256
- Kunci rahasia: Dihasilkan acak (secrets.token_hex(32)) dan disimpan di `jabrig_kunci.json`
- Masa berlaku: 24 jam
- Subject: Nama pengguna

#### Hashing Kata Sandi

- Algoritma: bcrypt
- Digunakan untuk hash kata sandi admin

#### Penyimpanan Kunci

- Kunci JWT disimpan dalam berkas JSON
- Dibuat otomatis jika belum ada
- Tidak ada enkripsi tambahan pada berkas (bergantung keamanan sistem file)

### Penanganan Error

- Semua operasi perangkat berada dalam blok try-except
- Error dikembalikan sebagai respons dengan `ok: false` dan `pesan` yang menjelaskan kesalahan
- API endpoint mengembalikan JSON error dengan kode status yang sesuai
- AI calls menangani timeout dan exception dengan graceful degradation

### Async/Await

- `PengelolaAI.cek_sumber()`: async
- `PengelolaAI.tanya()`: async
- `PengelolaAI._kirim_ke_ai()`: async
- Endpoint FastAPI: async
- HERMES menggunakan `asyncio.run()` untuk memanggil AI dari konteks sinkron

---

## Alur Startup

1. **Deteksi sistem:**
   - Cek apakah berjalan di Termux (`PREFIX` environment variable)
   - Tentukan `MODE` (HP_ANDROID atau PC)
   - Jika PC, tanyakan apakah ingin aktifkan ADB

2. **Inisialisasi komponen:**
   - `KendaliPerangkat`: Sesuaikan mode dan cek koneksi
   - `BrahmanAI`: Buat session aktif
   - `PengelolaAI`: Siapkan sumber AI dan cek ketersediaan

3. **Cek sumber AI:**
   - Cek Gemini (API key tersedia?)
   - Cek 9Router (API key tersedia dan endpoint merespons?)
   - Tampilkan status di console

4. **Mulai server FastAPI:**
   - Jalankan di `0.0.0.0:8000`
   - Tampilkan informasi akses di console

---

## Struktur Kode

```
main.py (single file architecture)
├── Konstanta & import
├── Deteksi sistem & konfigurasi
├── 🔐 Sistem keamanan (JWT, hashing)
├── 📱 KendaliPerangkat (ULTRON)
│   ├── __init__ & cek koneksi
│   ├── _cari_paket
│   ├── buka_aplikasi
│   ├── tutup_aplikasi
│   ├── ambil_layar
│   ├── kirim_notifikasi
│   └── daftar_aplikasi
├── 🧠 BrahmanAI (ingatan)
│   ├── __init__ & session management
│   ├── simpan
│   ├── dapat_konteks & katabuka
│   ├── alih_session
│   ├── daftar_session & hapus_session
│   └── simpan_hasil
├── 🤖 Jarvis
│   ├── __init__ (pemicu)
│   ├── cocok
│   └── respons
├── ⚙️ UltronAPI
│   ├── __init__
│   ├── cocok
│   ├── eksekusi
│   └── _status_teks
├── 🧭 HermesPengarah
│   ├── __init__
│   ├── set_ai
│   └── arahkan
├── 🧭 PengelolaAI
│   ├── __init__
│   ├── cek_sumber
│   ├── tanya
│   └── _kirim_ke_ai
├── 🌐 FastAPI app
│   ├── on_event("startup")
│   ├── GET /
│   ├── POST /perintah
│   ├── GET /status
│   ├── GET /health
│   ├── GET /brahma/konteks
│   └── GET /brahma/session
└── __main__
    ├── Informasi console
    ├── cek_sumber async
    └── uvicorn.run
```

---

## Cara Test

### 1. Verifikasi dependensi

```bash
python -c "import fastapi, uvicorn, httpx, jose, passlib; print('OK')"
```

### 2. Verifikasi startup

```bash
python main.py
# Harus menampilkan:
# - Informasi perangkat
# - Status AI (Gemini/9Router)
# - URL server
```

### 3. Verifikasi endpoint

```bash
curl http://localhost:8000/health
# Harusnya: {"status":"OK","versi":"3.0"}

curl http://localhost:8000/status
# Harusnya: JSON status lengkap
```

### 4. Verifikasi web UI

Buka browser ke `http://localhost:8000` dan:
- Periksa tampilan status sistem
- Kirim perintah "halo" → harusnya respons JARVIS
- Kirim perintah "status" → harusnya respons ULTRON
- Kirim pertanyaan umum → harusnya respons dari Gemini/9Router

### 5. Verifikasi ingatan BRAHMA

```bash
curl http://localhost:8000/brahma/session
# Harusnya: {"sessions": [{"id": "...", "jumlah": 0}]}

curl http://localhost:8000/brahma/konteks
# Harusnya: {"konteks": []}

# Setelah mengirim pesan:
curl http://localhost:8000/brahma/konteks
# Harusnya: {"konteks": [{"id": "...", "timestamp": "...", ...}]}
```

---

## Batasan yang Diketahui

1. **Penyimpanan in-memory:** Percakapan BRAHMA tidak persisten — hilang saat server restart
2. **Tidak ada enkripsi end-to-end:** Komunikasi antara komponen within proses yang sama
3. **Tidak ada rate limiting:** API endpoint tidak dibatasi kecepatan
4. **Batas aplikasi:** Hanya 7 aplikasi yang dikenali (bisa dikembangkan)
5. **OCR tidak didukung:** Tangkapan layar disimpan sebagai berkas, tidak diproses
6. **Single session default:** BRAHMA menggunakan satu session aktif (bisa dikembangkan untuk multi-user)
7. **Terima kasih banyak**

---

## Pengembangan Masa Depan

Ide untuk versi selanjutnya:

- [ ] Penyimpanan persisten untuk BRAHMA (SQLite/JSON file)
- [ ] Multi-session dan multi-user
- [ ] More aplikasi yang didukung
- [ ] OCR untuk tangkapan layar
- [ ] integrasi dengan layanan lain (email, calendar, dll)
- [ ] Rate limiting pada API
- [ ] HTTPS support
- [ ] Dashboard admin
- [ ] Plugin system untuk ekstensi

---

## Kontak & Dukungan

- **Dokumentasi:** Lihat `WIKI.md` dan `DUKUNGAN.md`
- **Issue tracker:** https://github.com/fathan-aziz/jabrig/issues
- **Kontribusi:** Lihat bagian "Kontribusi" di `DUKUNGAN.md`

