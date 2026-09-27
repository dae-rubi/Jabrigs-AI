# JABRIG v3.0 — Wiki Komprehensif

Wiki ini menjelaskan arsitektur, komponen, alur kerja, dan cara penggunaan JABRIG secara mendalam.

---

## Daftar Isi

1. [Pengenalan](#pengenalan)
2. [Peran Komponen](#peran-komponen)
3. [Arsitektur Sistem](#arsitektur-sistem)
4. [Alur Percakapan](#alur-percakapan)
5. [Kendali Perangkat](#kendali-perangkat)
6. [Ingatan BRAHMA](#ingatan-brahma)
7. [Sumber Kecerdasan](#sumber-kecerdasan)
8. [Endpoint API](#endpoint-api)
9. [Keamanan](#keamanan)
10. [Environment Variables](#environment-variables)
11. [Pertanyaan Umum](#pertanyaan-umum)

---

## Pengenalan

JABRIG adalah sistem kecerdasan terpadu yang menyatukan tiga inti dalam satu berkas Python:

- **JARVIS** — antarmuka percakapan yang ramah dan membantu
- **ULTRON** — sistem kendali perangkat (buka/tutup aplikasi, screenshot, notifikasi)
- **BRAHMA AI** — sistem ingatan dan pemahaman yang menyimpan percakapan

**HERMES** adalah pengarah alur yang menerima pesan pengguna dan menentukan ke komponen mana pesan tersebut harus dikirim.

Sumber kecerdasan utama adalah **Gemini 2.0 Flash**, dengan **9Router** sebagai cadangan jika Gemini tidak tersedia.

---

## Peran Komponen

### JARVIS

JARVIS adalah wajah sistem — ia menyambut pengguna, memperkenalkan diri, dan memberikan bimbingan. JARVIS merespons kata kunci seperti "halo", "hai", "selamat", "siapa kamu", "perkenalkan", "bantu".

Respons JARVIS bersifat ramah, jelas, dan tawarkan bantuan.

### ULTRON

ULTRON adalah tangan dan mata sistem — ia menerima perintah kendali perangkat dan mengeksekusinya. ULTRON mendeteksi kata kunci seperti "buka", "tutup", "ambil layar", "tangkapan", "status", "cek sistem", "notifikasi".

ULTRON dapat:
- Membuka aplikasi (melalui Termux:API atau ADB)
- Menutup aplikasi (force-stop)
- Mengambil tangkapan layar
- Mengirim notifikasi (hanya melalui Termux:API)

### BRAHMA AI

BRAHMA AI adalah sistem ingatan dan pemahaman. Setiap pesan pengguna dan jawaban sistem disimpan di BRAHMA. Saat pengguna mengirim pesan baru, BRAHMA dapat memeriksa apakah pesan tersebut merujuk percakapan sebelumnya dan menggabungkan konteks sebelum dikirim ke AI.

BRAHMA menyimpan:
- Riwayat percakapan per session
- Metadata tentang sumber jawaban (Gemini, 9Router, ULTRON, JARVIS, atau sistem)
- Ringkasan konteks untuk prompt AI

### HERMES

HERMES adalah pengarah lalu lintas — ia menerima pesan dari pengguna dan menentukan ke komponen mana pesan tersebut harus dikirim berdasarkan analisis kata kunci.

Urutan prioritas HERMES:
1. Jika pesan mengandung kata kunci JARVIS → kirim ke JARVIS
2. Jika pesan mengandung kata kunci ULTRON → kirim ke ULTRON
3. Jika tidak, kirim ke Gemini → 9Router
4. BRAHMA menyimpan hasil akhir percakapan

---

## Arsitektur Sistem

```
Pengguna
    │
    ▼
HERMES (pengarah alur)
    │
    ├──▶ JARVIS (sambutan & bantuan)
    │
    ├──▶ ULTRON (kendali perangkat)
    │
    ├──▶ Gemini 2.0 Flash (kecerdasan utama)
    │                          │
    │                          ▼ (jika gagal)
    │                    9Router (kecerdasan cadangan)
    │
    └──▶ BRAHMA AI (ingatan & pemahaman)
              │
              ▼
         Penyimpanan percakapan (memori)
```

---

## Alur Percakapan

### Contoh 1: Perintah Kendali Perangkat

```
Pengguna: "Buka YouTube"
    │
    ▼
HERMES: Menganalisis → "Ini perintah perangkat"
    │
    ▼
ULTRON: Mengeksekusi → hp.buka_aplikasi("youtube")
    │
    ▼
HERMES: Menyusun jawaban → "✅ Membuka YouTube"
    │
    ▼
BRAHMA: Menyimpan → (pesan_user: "Buka YouTube", hasil: "✅ Membuka YouTube")
```

### Contoh 2: Pertanyaan Umum

```
Pengguna: "Jelaskan kecerdasan buatan"
    │
    ▼
HERMES: Menganalisis → "Ini pertanyaan umum"
    │
    ▼
Gemini 2.0 Flash: Menghasilkan jawaban
    │
    ▼ (jika Gemini gagal)
9Router: Menghasilkan jawaban
    │
    ▼
HERMES: Menyajikan jawaban
    │
    ▼
BRAHMA: Menyimpan percakapan
```

### Contoh 3: Sambutan

```
Pengguna: "Halo"
    │
    ▼
HERMES: Menganalisis → "Ini sambutan"
    │
    ▼
JARVIS: Menyambut → "Halo! Saya JARVIS, antarmuka percakapan JABRIG..."
    │
    ▼
BRAHMA: Menyimpan
```

---

## Kendali Perangkat

### Mode Operasi

| Mode | Keterangan |
|---|---|
| `TERMUX_API` | Menggunakan Termux:API di HP Android (tanpa root, tanpa ADB) |
| `ADB` | Menggunakan ADB di PC/Laptop |
| `TIDAK_AKTIF` | Kendali perangkat tidak diaktifkan |

### Deteksi Otomatis

- Jika dijalankan di Termux (HP Android) → otomatis menggunakan Termux:API
- Jika dijalankan di PC → ditanya apakah ingin aktifkan ADB

### Aplikasi yang Dikenali

| Nama | Paket Android |
|---|---|
| whatsapp | com.whatsapp |
| telegram | org.telegram.messenger |
| youtube | com.google.android.youtube |
| pengaturan | com.android.settings |
| kamera | com.android.camera |
| galeri | com.android.gallery3d |
| kalkulator | com.android.calculator2 |

### Perintah Termux:API

| Tindakan | Perintah |
|---|---|
| Buka aplikasi | `termux-open-url <nama>://` |
| Tutup aplikasi | `am force-stop <paket>` |
| Ambil layar | `termux-screenshot -o ~/jabrig_layar.png` |
| Kirim notifikasi | `termux-notification --title <judul> --content <isi>` |

### Perintah ADB

| Tindakan | Perintah |
|---|---|
| Buka aplikasi | `adb shell am start -n <paket>/<paket>.MainActivity` |
| Tutup aplikasi | `adb shell am force-stop <paket>` |
| Ambil layar | `adb shell screencap -p /sdcard/jabrig_layar.png` lalu `adb pull` |
| Kirim notifikasi | Melalui ADB intent (tergantung implementasi) |

---

## Ingatan BRAHMA

### Struktur Session

BRAHMA AI mengelola session percakapan:

- Setiap session memiliki ID unik
- Session aktif secara default bernama "utama"
- Setiap session menyimpan daftar pesan (user & assistant)
- Pesan mencakup: ID, timestamp, peran, isi, sumber, jalur

### Operasi BRAHMA

| Operasi | Keterangan |
|---|---|
| `simpan(peran, isi, metadata)` | Simpan pesan ke session aktif |
| `dapat_konteks(limit)` | Ambil riwayat terbaru |
| `katabuka()` | Ringkasan singkat untuk prompt AI |
| `alih_session(sid)` | Ganti session aktif |
| `daftar_session()` | List semua session |
| `hapus_session(sid)` | Hapus session |

### Penggunaan Konteks

Saat pengguna mengirim pesan, BRAHMA mengambil konteks percakapan sebelumnya (hingga 4 pesan terakhir) dan menyertakannya dalam prompt ke AI, sehingga AI dapat memberikan jawaban yang lebih mengacu konteks.

---

## Sumber Kecerdasan

### Gemini 2.0 Flash

URL: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
Kunci: dari variabel lingkungan `GEMINI_API_KEY`

Gemini adalah sumber utama — dijalankan pertama kali jika kunci tersedia.

### 9Router

URL: dari variabel lingkungan `ROUTER_API_URL` (default: `http://localhost:20128`)
Kunci: dari variabel lingkungan `ROUTER_API_KEY`

9Router adalah sumber cadangan — dijalankan jika Gemini gagal atau tidak ada kunci.

### Fallback Lokal

Jika kedua sumber tidak tersedia, JABRIG memberikan respons lokal yang informatif, menjelaskan bahwa kunci API diperlukan dan memberikan contoh perintah yang dapat digunakan.

---

## Endpoint API

### Web UI

| Metode | Endpoint | Keterangan |
|---|---|---|
| GET | `/` | Halaman utama HTML — chat interaktif |
| POST | `/perintah` | Terima pesan, dapat jawaban |

### API Status & Monitoring

| Metode | Endpoint | Keterangan |
|---|---|---|
| GET | `/status` | Status sistem lengkap (JSON) |
| GET | `/health` | Health check sederhana |
| GET | `/brahma/konteks` | Konteks percakapan BRAHMA |
| GET | `/brahma/session` | Daftar session BRAHMA |

### Format Respons `/perintah`

```json
{
  "jalur": "GEMINI_UTAMA",
  "sumber": "Gemini",
  "jawab": "Jawaban dari AI...",
  "waktu_ms": 1234.56
}
```

Jalur yang mungkin:
- `JARVIS` — respons dari JARVIS
- `ULTRON` — respons dari ULTRON
- `GEMINI_UTAMA` — respons dari Gemini
- `9ROUTER_CADANGAN` — respons dari 9Router
- `FALLBACK_LOKAL` — respons fallback
- `ERROR` — error

---

## Keamanan

### JWT Authentication

JABRIG menggunakan JWT untuk autentikasi opsional:

- Kunci rahasia disimpan di `jabrig_kunci.json` (dihasilkan otomatis)
- Token berlaku selama 24 jam
- Akun default: `admin` / `jabrig2026` (dapat diganti via `JABRIG_USER` / `JABRIG_PASS`)

### Termux:API Permissions

Pastikan Termux:API memiliki izin yang diperlukan:
- Notifikasi
- Akses ke aplikasi (untuk membuka/tutup aplikasi)
- Akses layar (untuk screenshot)

---

## Environment Variables

| Variabel | Keterangan | Default |
|---|---|---|
| `GEMINI_API_KEY` | Kunci Google AI Studio untuk Gemini | (kosong) |
| `ROUTER_API_KEY` | Kunci untuk 9Router | (kosong) |
| `ROUTER_API_URL` | URL 9Router | `http://localhost:20128` |
| `JABRIG_USER` | Nama pengguna admin | `admin` |
| `JABRIG_PASS` | Kata sandi admin | `jabrig2026` |
| `PORT` | Port server | `8000` (hardcoded) |

---

## Pertanyaan Umum

### Apakah JABRIG memerlukan root?
Tidak. JABRIG berjalan tanpa root, menggunakan Termux:API di HP.

### Apakah JABRIG memerlukan ADB?
Tidak wajib. ADB adalah opsi tambahan untuk PC. Di HP, JABRIG menggunakan Termux:API.

### Apa perbedaan JARVIS, ULTRON, dan BRAHMA?
- **JARVIS**: wajah & sambutan
- **ULTRON**: kendali perangkat
- **BRAHMA**: ingatan & pemahaman

Semua bekerja di bawah koordinasi HERMES.

### Bagaimana cara menambah aplikasi yang dikenali?
Edit daftar `APLIKASI_DAFTAR` di `main.py` dengan menambahkan entri: `"nama": "com.paket.app"`.

### Apakah percakapan tersimpan secara permanen?
Tidak, percakapan disimpan di memori selama server berjalan. Setelah server dihentikan, percakapan hilang. Untuk penyimpanan permanen, perlu ekstensi untuk menyimpan ke berkas atau database.
