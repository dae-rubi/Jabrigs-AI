# ⚡ JABRIG — Wiki Komprehensif

Versi: 3.0 | 2026-09-27

---

## 📑 Daftar Isi

1. [Pendahuluan](#pendahuluan)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [HERMES — Pengarah Alur](#hermes--pengarah-alur)
4. [JARVIS — Wajah Ramah](#jarvis--wajah-ramah)
5. [ULTRON — Kendali Perangkat](#ultron--kendali-perangkat)
6. [BRAHMA AI — Memori](#brahma-ai--memori)
7. [Gemini → 9Router — AI Engine](#gemini--9router--ai-engine)
8. [JEV — Supervisor](#jev--supervisor)
9. [Action System](#action-system)
10. [Plugin System](#plugin-system)
11. [Memory System](#memory-system)
12. [Config](#config)
13. [Web UI](#web-ui)
14. [API Reference](#api-reference)
15. [Deployment](#deployment)
16. [Troubleshooting](#troubleshooting)

---

## Pendahuluan

JABRIG adalah asisten AI terpadu yang berjalan di HP Android (Termux) dan PC.  
Dibangun dengan filosofi: **satu berkas inti + modul terpisah otomatis**.

### Filosofi Desain

- **Sederhana**: `python main.py` langsung jalan
- **Modular**: action & plugin ter-discovery otomatis
- **Tangguh**: fail-open, fallback lokal
- **Cepat**: timeout pendek, HTTP client reuse

---

## Arsitektur Sistem

```
┌──────────────────────────────────────────────────────────┐
│                    PENGGUNA                              │
│  (Web UI / API / CLI)                                   │
└─────────────────────┬────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────┐
│                    HERMES                                │
│  (Router pesan: JARVIS / ULTRON / BRAHMA / JEV / GEMINI)│
└───┬───────────┬───────────┬───────────┬──────────────────┘
    │           │           │           │
    ▼           ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  JARVIS │ │  ULTRON │ │ BRAHMA  │ │  JEV    │
│ (sapaan)│ │(perangkat│ │ (memori)│ │(supervis│
│         │ │  control)│ │         │ │  or)    │
└─────────┘ └────┬─────┘ └─────────┘ └─────────┘
                 │
        ┌────────▼────────┐
        │     GEMINI      │ → 9Router (cadangan)
        │  (AI Utama)     │
        └─────────────────┘
```

---

## HERMES — Pengarah Alur

HERMES adalah celah otak JABRIG: terima pesan dari pengguna, tentukan ke siapa pesan dikirim.

### Logika Routing

```
1. Perintah perangkat → ULTRON
2. Sapaan/identitas → JARVIS
3. Memori/ingatan → BRAHMA
4. Supervisor check → JEV (opsional)
5. Pertanyaan umum → GEMINI → 9Router
```

### Kata Kunci

| Tujuan | Kata Kunci |
|--------|-----------|
| JARVIS | halo, hai, selamat, pagi, siang, sore, malam |
| ULTRON | buka, tutup, matikan, jalankan, nyalakan, ambil layar, screenshot, notifikasi, status |
| BRAHMA | ingat, simpan, hapus ingatan, apakah kamu tahu, apa yang kamu tahu |
| JEV | jev, supervisor, anjuran, kurasi, aman, selamat |
| GEMINI (default) | semua yang tidak masuk kategori di atas |

---

## JARVIS — Wajah Ramah

JARVIS adalah lapisan responsif yang memberikan sapaan hangat dan bantuan awal.

### Contoh Respons

```
Pengguna: "Halo"
JARVIS: "Halo! 👋 Saya JABRIG — siap membantu. Ketik pertanyaan atau perintahmu."
```

---

## ULTRON — Kendali Perangkat

ULTRON eksekutor fisik: membuka/tutup aplikasi, mengambil layar, kirim notifikasi.

### Mode Operasi

| Mode | Platform | Cara |
|------|----------|------|
| Termux:API | HP Android | termux-open-url, am force-stop, termux-screenshot, termux-notification |
| ADB | PC (opsional) | adb shell am start, adb shell am force-stop, adb shell screencap |
| Tidak aktif | PC (default) | Fitur perangkat tidak tersedia |

### Daftar Aplikasi

| Nama | Paket Android |
|------|--------------|
| whatsapp | com.whatsapp |
| telegram | org.telegram.messenger |
| youtube | com.google.android.youtube |
| pengaturan | com.android.settings |
| kamera | com.android.camera |
| galeri | com.android.gallery3d |
| kalkulator | com.android.calculator2 |

---

## BRAHMA AI — Memori

BRAHMA adalah memori jangka panjang JABRIG.

### Kategori Memori

| Kategori | Keterangan |
|----------|----------|
| identity | Identitas pengguna |
| preferences | Preferensi |
| projects | Proyek |
| relationships | Hubungan |
| wishes | Keinginan |
| notes | Catatan, ringkasan sesi |

### Cara Kerja

- Setiap sesi: ringkasan disimpan di `notes.last_session`
- Setiap 10 pesan: ringkasan otomatis disimpan
- Prompt AI: hanya inti memori masuk (budget terbatas)
- Pencarian: `search_memory()` saat pengguna bertanya tentang ingatan

---

## Gemini → 9Router — AI Engine

### Gemini (Utama)

- Model: Gemini 2.0 Flash
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- Key: `config/api_keys.json` → `gemini_api_key`

### 9Router (Cadangan)

- Endpoint: `config/api_keys.json` → `router_url` (default: `http://localhost:20128`)
- Key: `config/api_keys.json` → `router_api_key`

### Alur Fallback

```
Gemini (kunci ada, siap) → jawab
    ↓ gagal / tidak siap
9Router (kunci ada, siap) → jawab
    ↓ gagal / tidak siap
Fallback lokal → pesan info
```

---

## JEV — Supervisor

JEV adalah supervisor opsional berbasis TypeSafe System One.

### Fungsi

- Evaluasi pesan sebelum dikirim ke AI
- Safety gate: tolak pesan yang berpotensi berbahaya
- Kurasi: berikan anjuran

### Mode Operasi

- **Aktif**: kalau ada kunci JEV, kirim pesan ke JEV API
- **Fail-open**: kalau JEV error/tidak aktif, sistem lanjut ke AI tanpa gangguan

### Config

```bash
JEV_API_BASE=https://api.typesafe.ai/v1/systemone
JEV_API_KEY=...
```

---

## Action System

Action adalah fungsi kendali perangkat yang di-discovery otomatis dari folder `actions/`.

### Struktur Action

```python
def _action_name(parameters: dict, **ctx) -> dict:
    # logic
    return {"ok": True, "pesan": "Selesai ✅"}

TOOL = {
    "name": "action_name",
    "description": "Deskripsi",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "param1": {"type": "string"}
        },
        "required": ["param1"]
    },
    "handler": _action_name,
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}
```

### Field TOOL

| Field | Keterangan |
|-------|----------|
| `name` | Nama unik action (identifier valid) |
| `description` | Deskripsi untuk AI routing |
| `parameters` | Skema parameter (JSON Schema OBJECT) |
| `handler` | Fungsi callable |
| `behavior` | `BLOCKING` / `NON_BLOCKING` |
| `scheduling` | `WHEN_IDLE` / `SILENT` / `INTERRUPT` |

### Action yang Tersedia

| Nama | Fungsi |
|------|--------|
| `open_app` | Buka aplikasi |
| `close_app` | Tutup aplikasi |
| `ambil_layar` | Ambil tangkapan layar |
| `kirim_notifikasi` | Kirim notifikasi |
| `system_status` | Cek status sistem |

---

## Plugin System

Plugin adalah ekstensi yang di-discovery otomatis dari folder `plugins/`.

### Struktur Plugin

```python
PLUGIN = {
    "name": "plugin_name",
    "description": "Deskripsi",
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
    # logic
    return "Hasil plugin"
```

---

## Memory System

### Penyimpanan

File: `memory/long_term.json`

Format:
```json
{
  "identity": {},
  "preferences": {},
  "projects": {},
  "relationships": {},
  "wishes": {},
  "notes": {
    "last_session": {"value": "...", "updated": "2026-09-27T10:00:00"},
    "sesi_count": 5
  }
}
```

### Fungsi

| Fungsi | Keterangan |
|--------|----------|
| `load_memory()` | Baca memori dari file |
| `save_memory(m)` | Simpan memori ke file |
| `update_memory(cat, key, value)` | Update entri |
| `format_memory_for_prompt()` | Format untuk prompt AI |
| `search_memory(query)` | Cari di memori |
| `save_session_summary(s)` | Simpan ringkasan sesi |
| `get_memory_categories()` | List kategori |

---

## Config

File: `config/api_keys.json`

```json
{
  "gemini_api_key": "AIza...",
  "router_url": "http://localhost:20128",
  "router_api_key": ""
}
```

### Environment Variables (Opsional)

| Variabel | Keterangan |
|----------|----------|
| `GEMINI_API_KEY` | Override config |
| `ROUTER_URL` | Override config |
| `ROUTER_API_KEY` | Override config |
| `JEV_API_BASE` | Base URL JEV |
| `JEV_API_KEY` | Key JEV |

---

## Web UI

URL: `http://localhost:8000`

### Halaman Utama

- Status sistem (perangkat, mode kendali, Gemini/9Router/HERMES/JEV)
- Kotak teks input perintah
- Output jawaban

### Endpoint

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/` | Halaman utama |
| POST | `/perintah` | Kirim perintah |
| GET | `/status` | Status sistem (JSON) |

---

## API Reference

### POST /perintah

Request:
```json
{"teks": "buka youtube"}
```

Response:
```json
{
  "jawab": "Membuka youtube ✅",
  "jalur": "ULTRON",
  "sumber": "ULTRON"
}
```

### GET /status

Response:
```json
{
  "perangkat": "HP Android (Termux)",
  "mode_kendali": "termux_api",
  "kendali_aktif": true,
  "gemini_siap": true,
  "router_siap": false,
  "jev_aktif": false,
  "action_count": 5,
  "plugin_count": 1,
  "memory_categories": ["notes"]
}
```

---

## Deployment

### Local

```bash
python main.py
```

### Systemd

Lihat `infra/jabrig.service`.

### Watchdog

```bash
./infra/jabrig-watchdog.sh start
```

### Cron

```bash
sudo systemctl enable jabrig-cron.timer
sudo systemctl start jabrig-cron.timer
```

### Caddy

```bash
./infra/setup-caddy.sh
```

### Docker

```bash
docker build -t jabrig .
docker run -p 8000:8000 jabrig
```

---

## Troubleshooting

### Gemini error

- Cek `gemini_api_key` di `config/api_keys.json`
- Cek koneksi internet

### 9Router error

- Pastikan 9Router berjalan
- Cek `router_api_key`

### Aplikasi tidak bisa dibuka (HP)

- Install Termux:API dari F-Droid
- Berikan izin notifikasi

### Action/Plugin tidak muncul

- Pastikan file `.py` ada di folder `actions/` atau `plugins/`
- Cek log startup di console

### Memory tidak menyimpan

- Pastikan folder `memory/` bisa ditulis
- Cek `memory/long_term.json` tidak di-lock

---

## Versi

- **v3.0** (2026-09-27): Struktur ulang berbasis Mark-LV, action/plugin discovery, memori terstruktur, config JSON, tetap 9Router/HERMES/JEV.
