# ⚡ JABRIG — Spesifikasi Teknis

Versi: 3.0 | 2026-09-27

---

## 📋 Spesifikasi Singkat

- **Bahasa**: Python 3.8+
- **Framework**: FastAPI + Uvicorn
- **AI**: Gemini 2.0 Flash → 9Router cadangan
- **Supervisor**: JEV (TypeSafe System One, opsional)
- **Router**: HERMES (custom)
- **Memori**: File-based (long_term.json)
- **Action**: Auto-discovery dari folder actions/
- **Plugin**: Auto-discovery dari folder plugins/
- **Antarmuka**: Web UI (HTML/JS) + REST API

---

## 📦 Dependensi

### Requirements.txt

```txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
httpx>=0.24.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

### Impor Utama

```python
import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
```

---

## 🏗 Struktur Projek

```
jabrig/
├── main.py               ← 800+ baris, inti sistem
├── requirements.txt      ← 7 baris
├── Dockerfile            ← 37 baris
│
├── actions/              ← 5 file
│   ├── __init__.py       ← action loader (berbasis Mark-LV)
│   ├── open_app.py
│   ├── close_app.py
│   ├── screenshot.py
│   ├── notification.py
│   └── system_status.py
│
├── plugins/              ← 1 file contoh
│   ├── __init__.py       ← plugin loader
│   └── contoh_sapaan.py
│
├── memory/               ← 2 file
│   ├── __init__.py
│   └── memory_manager.py ← 200+ baris
│
├── config/               ← 2 file
│   ├── __init__.py
│   └── api_keys.json
│
├── docs/                 ← 5 file
│   ├── README.md
│   ├── WIKI.md
│   ├── DUKUNGAN.md
│   ├── SPESIFIKASI.md
│   └── WIZARD.md
│
├── infra/                ← 6 file
│   ├── jabrig.service
│   ├── jabrig-watchdog.sh
│   ├── jabrig-cron.service
│   ├── jabrig-cron.timer
│   ├── jabrig-cron-task.sh
│   └── setup-caddy.sh
│
├── ALLINONE.md
├── INSTALL.md
├── WIZARD_FULL.sh
└── .gitignore
```

---

## 🔗 Komponen & Integrasi

### HERMES

- **Tujuan**: Router pesan
- **Input**: Teks dari pengguna
- **Output**: Tujuan (JARVIS/ULTRON/BRAHMA/JEV/GEMINI)
- **Kata kunci**: 4 kategori + default

### JEV (TypeSafe System One)

- **Tujuan**: Supervisor kurasi & safety gate
- **API**: `https://api.typesafe.ai/v1/systemone`
- **Endpoint**: `/v1/evaluate`
- **Mode**: Fail-open (kalau error, sistem tetap jalan)
- **Integrasi**: Semua pesan ke AI melewati JEV

### Gemini → 9Router

- **Gemini**: Utama, `gemini-2.0-flash`
- **9Router**: Cadangan, `localhost:20128`
- **Fallback**: Gemini → 9Router → lokal

### Action Discovery

- **Folder**: `actions/`
- **Cara**: Scan `*.py`, cari dict `TOOL`
- **Validasi**: Nama, deskripsi, parameter, handler

### Plugin Discovery

- **Folder**: `plugins/`
- **Cara**: Scan `*.py`, cari dict `PLUGIN` + fungsi `run()`
- **Validasi**: Nama, deskripsi, parameter, run

### Memory

- **File**: `memory/long_term.json`
- **Kategori**: identity, preferences, projects, relationships, wishes, notes
- **Budget**: Prompt core 900 karakter, index 420 karakter
- **Search**: Pencarian teks sederhana

---

## 🌐 API

### Endpoint

| Method | Path | Keterangan |
|--------|------|-----------|
| GET | `/` | Halaman utama (HTML) |
| POST | `/perintah` | Kirim perintah |
| GET | `/status` | Status sistem (JSON) |

### Request/Response

#### POST /perintah

Request:
```json
{"teks": "string"}
```

Response:
```json
{
  "jawab": "string",
  "jalur": "string",
  "sumber": "string"
}
```

#### GET /status

Response:
```json
{
  "perangkat": "string",
  "mode_kendali": "string",
  "kendali_aktif": "boolean",
  "gemini_siap": "boolean",
  "router_siap": "boolean",
  "jev_aktif": "boolean",
  "action_count": "integer",
  "plugin_count": "integer",
  "memory_categories": ["string"]
}
```

---

## ⚡ Performa

- **HTTP Client**: Reuse (singleton)
- **Timeout**: 2 detik per request AI
- **JEV Timeout**: 2 detik
- **Startup**: Discovery action + plugin + cek AI source
- **Auto-skip**: Perintah cepat tidak perlu ke AI

---

## 🔒 Keamanan

- **JWT**: Opsional (belum diimplementasi di v3.0)
- **CORS**: All origins (development only)
- **API Key**: File config (jangan commit ke repo publik)
- **Fail-open**: JEV & AI fallback lokal

---

## 🐛 Known Issues

- JEV tidak aktif secara default (butuh API key)
- Gemini tidak aktif tanpa API key
- 9Router tidak aktif tanpa instance terpisah
- CORS all origins (production harus diubah)

---

## 🔄 Changelog

### v3.0 (2026-09-27)

- Refactor struktur berbasis Mark-LV (FatihMakes)
- Action discovery otomatis dari folder actions/
- Plugin discovery otomatis dari folder plugins/
- Memory terstruktur (kategori, long_term.json, prompt budget)
- Config JSON (`config/api_keys.json`)
- Integrasi Hermes+JEV+9Router
- JEV kurasi semua pesan ke AI
- Deploy ke Koyeb/Colab/hosting gratis
- Dokumentasi lengkap (README, WIKI, DUKUNGAN, SPESIFIKASI, WIZARD)
