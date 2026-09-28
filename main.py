# -*- coding: utf-8 -*-
"""
JABRIG — Sistem Kecerdasan Terpadu
Versi: 3.0 | Tanggal: 2026-09-27
Perangkat: Vivo Y19s / Android Termux / PC
Tanpa Root • Tanpa ADB Wajib • Termux:API
"""

import asyncio
import json
import logging
import os
import platform as _platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("jabrig")

# ---------------------------------------------------------------------------
# 1. Deteksi platform otomatis
# ---------------------------------------------------------------------------

IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "")
PERANGKAT = "HP Android (Termux)" if IS_TERMUX else "PC / Laptop"
logger.info("Deteksi platform: %s (%s)", PERANGKAT, "Termux" if IS_TERMUX else "non-Termux")

GUNAKAN_TERMUX_API = IS_TERMUX
GUNAKAN_ADB = False

if not IS_TERMUX:
    try:
        jawab = input("Aktifkan kendali via ADB? (y/n): ").strip().lower()
        GUNAKAN_ADB = jawab.startswith("y")
    except Exception:
        GUNAKAN_ADB = False

MODE_KENDALI = "termux_api" if GUNAKAN_TERMUX_API else ("adb" if GUNAKAN_ADB else "tidak_aktif")
logger.info("Mode kendali: %s", MODE_KENDALI)

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 2. Konfigurasi (config/) — model Mark-LV
# ---------------------------------------------------------------------------

try:
    from config import get_gemini_key, get_router_url, get_router_key
except Exception as e:
    logger.warning("Gagal import config: %s", e)

    def _dummy():
        return ""

    get_gemini_key = _dummy
    get_router_url = lambda: "http://localhost:20128"
    get_router_key = _dummy

GEMINI_API_KEY = get_gemini_key()
ROUTER_URL = get_router_url()
ROUTER_API_KEY = get_router_key()

# ---------------------------------------------------------------------------
# 3. Memory (memory/) — kategori, long_term.json, prompt budget
# ---------------------------------------------------------------------------

try:
    from memory import (
        load_memory,
        save_memory,
        update_memory,
        format_memory_for_prompt,
        search_memory,
        save_session_summary,
        get_memory_categories,
        set_trim_notifier,
    )

    def _trim_notifier(msg: str) -> None:
        logger.warning("[MEMORI] %s", msg)

    set_trim_notifier(_trim_notifier)
except Exception as e:
    logger.warning("Gagal import memory: %s", e)

    def _dummy_memory(*_a, **_k):
        return {}

    load_memory = _dummy_memory
    update_memory = _dummy_memory
    format_memory_for_prompt = lambda *a, **k: ""
    search_memory = lambda *a, **k: []
    save_session_summary = lambda *a, **k: None
    get_memory_categories = lambda: {}

# ---------------------------------------------------------------------------
# 4. Action discovery (actions/) — berbasis Model Mark-LV
# ---------------------------------------------------------------------------

from actions import discover_actions

_actions_dir = BASE_DIR / "actions"
_action_registry = discover_actions(_actions_dir, reserved_names=set())

def run_action(name: str, parameters: dict, ctx: dict | None = None) -> dict:
    try:
        raw = _action_registry.run(name, parameters, ctx)
        # Action harus mengembalikan dict; fallback jika string
        if isinstance(raw, dict):
            return raw
        return {"ok": True if raw and "Selesai" in str(raw) else False, "pesan": str(raw)}
    except Exception as e:
        logger.error("Gagal menjalankan action '%s': %s", name, e)
        return {"ok": False, "pesan": f"Gagal menjalankan {name}: {e}"}

# ---------------------------------------------------------------------------
# 5. Plugin discovery (plugins/) — berbasis Model Mark-LV
# ---------------------------------------------------------------------------

from plugins import discover_plugins

_plugins_dir = BASE_DIR / "plugins"
_plugin_registry = discover_plugins(_plugins_dir, core_tool_names=_action_registry.names())

def run_plugin(name: str, parameters: dict, ctx: dict | None = None) -> str:
    try:
        return _plugin_registry.run(name, parameters, ctx)
    except Exception as e:
        logger.error("Gagal menjalankan plugin '%s': %s", name, e)
        return f"Plugin {name} gagal: {e}"

# ---------------------------------------------------------------------------
# 6. Kontrol perangkat — wrapper terenkripsi di atas Termux:API / ADB
# ---------------------------------------------------------------------------

class KendaliPerangkat:
    def __init__(self):
        self.mode = MODE_KENDALI
        self.tersedia = self._cek_tersedia()
        self.aplikasi = {
            "whatsapp": "com.whatsapp",
            "telegram": "org.telegram.messenger",
            "youtube": "com.google.android.youtube",
            "pengaturan": "com.android.settings",
            "kamera": "com.android.camera",
            "galeri": "com.android.gallery3d",
            "kalkulator": "com.android.calculator2",
        }
        self.screenshot_dir = os.path.expanduser("~/jabrig")

    def _cek_tersedia(self) -> bool:
        if self.mode == "tidak_aktif":
            return False
        if self.mode == "termux_api":
            try:
                r = subprocess.run(["termux-notification", "--help"], capture_output=True, timeout=3)
                return r.returncode == 0
            except Exception:
                return False
        if self.mode == "adb":
            try:
                r = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
                return "device" in r.stdout
            except Exception:
                return False
        return False

    def buka_aplikasi(self, nama: str) -> dict:
        paket = self.aplikasi.get(nama.lower())
        if not paket:
            return {"ok": False, "pesan": f"Aplikasi '{nama}' tidak terdaftar"}

        if self.mode == "termux_api":
            try:
                subprocess.run(["termux-open-url", f"{nama}://"], capture_output=True)
                return {"ok": True, "pesan": f"Membuka {nama} ✅", "jalur": "Termux:API"}
            except Exception as e:
                return {"ok": False, "pesan": f"Gagal: {e}"}
        if self.mode == "adb":
            try:
                subprocess.run(
                    ["adb", "shell", "am", "start", "-n", f"{paket}/{paket}.MainActivity"],
                    capture_output=True,
                )
                return {"ok": True, "pesan": f"Membuka {nama} ✅", "jalur": "ADB"}
            except Exception as e:
                return {"ok": False, "pesan": f"Gagal: {e}"}
        return {"ok": False, "pesan": "Kendali perangkat tidak diaktifkan"}

    def tutup_aplikasi(self, nama: str) -> dict:
        paket = self.aplikasi.get(nama.lower())
        if not paket:
            return {"ok": False, "pesan": f"Aplikasi '{nama}' tidak terdaftar"}
        try:
            perintah = ["am", "force-stop", paket] if self.mode == "termux_api" else ["adb", "shell", "am", "force-stop", paket]
            subprocess.run(perintah, capture_output=True)
            return {"ok": True, "pesan": f"Menutup {nama} ✅"}
        except Exception as e:
            return {"ok": False, "pesan": f"Gagal: {e}"}

    def ambil_layar(self) -> dict:
        if self.mode == "tidak_aktif":
            return {"ok": False, "pesan": "Kendali perangkat tidak diaktifkan"}
        os.makedirs(self.screenshot_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        jalur = os.path.join(self.screenshot_dir, f"jabrig_layar_{ts}.png")
        try:
            if self.mode == "termux_api":
                subprocess.run(["termux-screenshot", "-o", jalur], capture_output=True)
            else:
                subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/jabrig_layar.png"], capture_output=True)
                subprocess.run(["adb", "pull", "/sdcard/jabrig_layar.png", jalur], capture_output=True)
            if os.path.exists(jalur):
                return {"ok": True, "pesan": "Tangkapan layar disimpan ✅", "berkas": jalur}
            return {"ok": False, "pesan": "Perintah berhasil tetapi berkas tidak ditemukan"}
        except Exception as e:
            return {"ok": False, "pesan": f"Gagal: {e}"}

    def kirim_notifikasi(self, judul: str, isi: str) -> dict:
        if self.mode != "termux_api":
            return {"ok": False, "pesan": "Notifikasi hanya tersedia lewat Termux:API"}
        try:
            subprocess.run(
                ["termux-notification", "--title", judul, "--content", isi],
                capture_output=True,
            )
            return {"ok": True, "pesan": "Notifikasi dikirim ✅"}
        except Exception as e:
            return {"ok": False, "pesan": f"Gagal: {e}"}


hp = KendaliPerangkat()

# ---------------------------------------------------------------------------
# 7. HERMES — pengarah lalu lintas
# ---------------------------------------------------------------------------

class HermesRouter:
    def __init__(self):
        self.kata_kunci = {
            "jabari": ["halo", "hai", "selamat", "pagi", "siang", "sore", "malam", "assalamualaikum", "asalamualaikum"],
            "ultron": [
                "buka", "tutup", "matikan", "hapus", "jalankan", "nyalakan",
                "ambil layar", "tangkapan layar", "screenshot", "notifikasi",
                "status sistem", "cek sistem", "status", "cek",
                "notif", "kirim pesan", "beri tahu",
            ],
            "brahma": ["ingat", "simpan", "hapus ingatan", "apakah kamu tahu", "apa yang kamu tahu", "kontext"],
            "jev": ["jev", "supervisor", "anjuran", "kurasi", "aman", "selamat"],
        }

    def arahkan(self, teks: str) -> dict:
        t = teks.lower().strip()
        if any(k in t for k in self.kata_kunci["jabari"]):
            return {"tujuan": "JARVIS", "pesan": teks}
        if any(k in t for k in self.kata_kunci["ultron"]):
            return {"tujuan": "ULTRON", "pesan": teks}
        if any(k in t for k in self.kata_kunci["brahma"]):
            return {"tujuan": "BRAHMA", "pesan": teks}
        if any(k in t for k in self.kata_kunci["jev"]):
            return {"tujuan": "JEV", "pesan": teks}
        return {"tujuan": "GEMINI", "pesan": teks}


hermes = HermesRouter()

# ---------------------------------------------------------------------------
# 8. JEV Supervisor — opsional, fail-open (TypeSafe System One)
# ---------------------------------------------------------------------------

class JevSupervisor:
    def __init__(self):
        self.active = False
        self.api_base = os.getenv("JEV_API_BASE", "https://api.typesafe.ai/v1/systemone")
        self.api_key = os.getenv("JEV_API_KEY", "")
        self.timeout = 2.0

    async def cek_kesiapan(self) -> bool:
        if not self.api_key:
            return False
        try:
            import httpx
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(
                    f"{self.api_base}/status",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                self.active = r.status_code == 200
                return self.active
        except Exception as e:
            logger.warning("[JEV] Gagal cek kesiapan: %s", e)
            self.active = False
            return False

    async def kurasi(self, pesan: str, konteks: dict | None = None) -> dict:
        if not self.active:
            return {"boleh": True, "hint": "", "catatan": "JEV tidak aktif — lanjut ke AI utama"}
        try:
            import httpx
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(
                    f"{self.api_base}/v1/evaluate",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "message": pesan,
                        "context": konteks or {},
                        "saran": True,
                    },
                )
                if r.status_code == 200:
                    data = r.json()
                    return {
                        "boleh": data.get("boleh", True),
                        "hint": data.get("hint", ""),
                        "catatan": data.get("catatan", ""),
                    }
                return {"boleh": True, "hint": "", "catatan": "JEV tidak merespons — lanjut ke AI utama"}
        except Exception as e:
            logger.warning("[JEV] Gagal kurasi: %s", e)
            return {"boleh": True, "hint": "", "catatan": f"JEV error: {e}"}


jev = JevSupervisor()
_logger_jev = logger.getChild("jev")

# ---------------------------------------------------------------------------
# 9. AI Client — Gemini utama → 9Router cadangan
# ---------------------------------------------------------------------------

class AIEngine:
    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.router_url = ROUTER_URL
        self.router_key = ROUTER_API_KEY
        self.status_gemini = bool(self.gemini_key)
        self.status_router = bool(self.router_key)
        self._client: Optional[Any] = None

    def _get_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(timeout=2.0)
        return self._client

    async def tutup(self):
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None

    async def cek_sumber(self) -> None:
        logger.info("Memeriksa sumber AI...")
        if self.gemini_key:
            try:
                async with self._get_client() as c:
                    r = await c.post(
                        f"{self.gemini_url}?key={self.gemini_key}",
                        json={"contents": [{"parts": [{"text": "test"}]}]},
                        timeout=2.0,
                    )
                    self.status_gemini = r.status_code == 200
            except Exception as e:
                logger.warning("[AI] Gemini tidak siap: %s", e)
                self.status_gemini = False
        else:
            logger.info("[AI] Gemini: tidak ada kunci")

        if self.router_key:
            try:
                async with self._get_client() as c:
                    r = await c.get(
                        f"{self.router_url}/status",
                        headers={"Authorization": f"Bearer {self.router_key}"},
                        timeout=2.0,
                    )
                    self.status_router = r.status_code == 200
            except Exception as e:
                logger.warning("[AI] 9Router tidak siap: %s", e)
                self.status_router = False
        else:
            logger.info("[AI] 9Router: tidak ada kunci")

        logger.info("[AI] Gemini: %s | 9Router: %s",
                     "SIAP" if self.status_gemini else "TIDAK SIAP",
                     "SIAP" if self.status_router else "TIDAK SIAP")

    async def tanya(self, pesan: str, konteks: dict | None = None) -> dict:
        pesan_terenkripsi = self._kanonikasi_pesan(pesan)
        mulai = time.time()

        # Coba Gemini
        if self.status_gemini:
            hasil = await self._kirim_gemini(pesan_terenkripsi)
            if hasil["sukses"]:
                return {
                    "sumber": "Gemini",
                    "teks": hasil["teks"],
                    "jalur": "GEMINI_UTAMA",
                    "waktu_ms": round((time.time() - mulai) * 1000, 2),
                }

        # Coba 9Router
        if self.status_router:
            hasil = await self._kirim_router(pesan_terenkripsi)
            if hasil["sukses"]:
                return {
                    "sumber": "9Router",
                    "teks": hasil["teks"],
                    "jalur": "9ROUTER_CADANGAN",
                    "waktu_ms": round((time.time() - mulai) * 1000, 2),
                }

        # Fallback lokal
        return {
            "sumber": "lokal",
            "teks": (
                f"Diterima: {pesan}\n\n"
                "⚠️  Belum ada kunci Gemini atau 9Router yang aktif.\n"
                "   - Set GEMINI_API_KEY di config/api_keys.json untuk jawaban AI.\n"
                "   - Atau set ROUTER_API_KEY + ROUTER_URL untuk 9Router cadangan."
            ),
            "jalur": "FALLBACK_LOKAL",
            "waktu_ms": round((time.time() - mulai) * 1000, 2),
        }

    def _kanonikasi_pesan(self, teks: str) -> str:
        return teks.strip()

    async def _kirim_gemini(self, pesan: str) -> dict:
        try:
            c = self._get_client()
            r = await c.post(
                f"{self.gemini_url}?key={self.gemini_key}",
                json={"contents": [{"parts": [{"text": pesan}]}]},
                timeout=2.0,
            )
            if r.status_code == 200:
                data = r.json()
                teks = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"sukses": True, "teks": teks}
            logger.warning("[AI] Gemini status: %s", r.status_code)
            return {"sukses": False}
        except Exception as e:
            logger.warning("[AI] Gemini gagal: %s", e)
            return {"sukses": False}

    async def _kirim_router(self, pesan: str) -> dict:
        try:
            c = self._get_client()
            r = await c.post(
                f"{self.router_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.router_key}"},
                json={
                    "model": "auto",
                    "messages": [{"role": "user", "content": pesan}],
                    "max_tokens": 1024,
                },
                timeout=2.0,
            )
            if r.status_code == 200:
                data = r.json()
                teks = data["choices"][0]["message"]["content"]
                return {"sukses": True, "teks": teks}
            logger.warning("[AI] 9Router status: %s", r.status_code)
            return {"sukses": False}
        except Exception as e:
            logger.warning("[AI] 9Router gagal: %s", e)
            return {"sukses": False}


ai = AIEngine()

# ---------------------------------------------------------------------------
# 10. Penonton (REPL / Web UI) — logika inti
# ---------------------------------------------------------------------------

class JabrigChat:
    def __init__(self):
        self.history: list[tuple[str, str]] = []

    def perintah_cepat(self, teks: str) -> Optional[dict]:
        t = teks.lower().strip()

        # Sapaan
        if any(k in t for k in ["halo", "hai", "selamat", "pagi", "siang", "sore", "malam"]):
            return {"jawab": f"Halo! 👋 Saya JABRIG — siap membantu. Ketik pertanyaan atau perintahmu."}

        # Identitas
        if any(k in t for k in ["siapa kamu", "apa kamu", "jabrig"]):
            return {
                "jawab": (
                    f"Saya JABRIG ⚡\n"
                    f"• Perangkat: {PERANGKAT}\n"
                    f"• Mode kendali: {MODE_KENDALI}\n"
                    f"• AI: Gemini → 9Router\n"
                    f"• HERMES: aktif\n"
                    f"• JEV: {'aktif' if jev.active else 'tidak aktif'}"
                )
            }

        # Status
        if any(k in t for k in ["status", "cek sistem"]):
            s = {
                "perangkat": PERANGKAT,
                "mode_kendali": MODE_KENDALI,
                "kendali_aktif": hp.tersedia,
                "gemini": ai.status_gemini,
                "router": ai.status_router,
                "jev": jev.active,
            }
            return {"jawab": "📊 Status Sistem:\n" + "\n".join(f"  • {k}: {v}" for k, v in s.items())}

        # Buka aplikasi
        for aplikasi in hp.aplikasi:
            if aplikasi in t and any(k in t for k in ["buka", "jalankan", "nyalakan"]):
                return run_action("open_app", {"nama": aplikasi})

        # Tutup aplikasi
        for aplikasi in hp.aplikasi:
            if aplikasi in t and any(k in t for k in ["tutup", "matikan"]):
                return run_action("close_app", {"nama": aplikasi})

        # Ambil layar
        if any(k in t for k in ["ambil layar", "screenshot", "tangkapan layar"]):
            return run_action("ambil_layar", {})

        # Notifikasi
        if any(k in t for k in ["notifikasi", "kirim pesan", "beri tahu"]):
            return run_action("kirim_notifikasi", {"judul": "JABRIG", "isi": "Pesan dari sistem ✅"})

        return None

    async def proses_perintah(self, teks: str) -> dict:
        # Cek perintah cepat dulu
        cepat = self.perintah_cepat(teks)
        if cepat:
            self.history.append(("user", teks))
            self.history.append(("system", cepat["jawab"]))
            return {"sumber": "langsung", "jawab": cepat["jawab"], "jalur": "CEPAT"}

        # HERMES memandu
        routing = hermes.arahkan(teks)
        tujuan = routing["tujuan"]
        pesan = routing["pesan"]

        # JEV supervisor (opsional)
        jev_hasil = {"boleh": True, "hint": "", "catatan": ""}
        if tujuan in ("GEMINI", "JEV", "BRAHMA") and teks.strip():
            jev_hasil = await jev.kurasi(pesan, {"history_len": len(self.history)})
            _logger_jev.info("[JEV] hasil: %s", jev_hasil)

        if not jev_hasil.get("boleh", True):
            return {
                "sumber": "JEV",
                "jawab": f"⛔ Batal: {jev_hasil.get('catatan', 'Tidak diizinkan oleh JEV')}",
                "jalur": "JEV_BLOCK",
            }

        # Tujuan khusus
        if tujuan == "JARVIS":
            return await self._jawab_jarvis(pesan)
        if tujuan == "ULTRON":
            return await self._jawab_ultron(pesan)
        if tujuan == "BRAHMA":
            return await self._jawab_brahma(pesan)
        if tujuan == "JEV":
            return await self._jawab_jev(pesan)

        # Default: AI (Gemini → 9Router)
        memori_teks = format_memory_for_prompt()
        prompt_lengkap = self._buat_prompt_AI(pesan, memori_teks)
        return await ai.tanya(prompt_lengkap)

    def _buat_prompt_AI(self, pesan: str, memori: str) -> str:
        if memori:
            return f"{memori}\n\nPertanyaan: {pesan}"
        return pesan

    async def _jawab_jarvis(self, pesan: str) -> dict:
        return {"sumber": "JARVIS", "jawab": "Halo! Saya JABRIG, siap membantu Anda.", "jalur": "JARVIS"}

    async def _jawab_ultron(self, pesan: str) -> dict:
        # HERMES sudah menentukan ini perintah perangkat
        return await self.proses_perintah(pesan)

    async def _jawab_brahma(self, pesan: str) -> dict:
        # Coba cari di memori
        kata_kunci = re.sub(r" ingat |simpan |hapus ", "", pesan, flags=re.I).strip()
        if kata_kunci:
            hasil = search_memory(kata_kunci)
            if hasil:
                return {
                    "sumber": "BRAHMA",
                    "jawab": "🧠 Hasil memori:\n" + "\n".join(f"• {r['kategori']}/{r['kunci']}: {r['isi']}" for r in hasil),
                    "jalur": "BRAHMA_MEMORY",
                }
        return {"sumber": "BRAHMA", "jawab": "Tidak ada ingatan yang relevan.", "jalur": "BRAHMA_EMPTY"}

    async def _jawab_jev(self, pesan: str) -> dict:
        return {
            "sumber": "JEV",
            "jawab": f"JEV: {jev_hasil.get('catatan', 'tidak ada saran')}",
            "jalur": "JEV_Saran",
        }

    def rangkum_sesi(self) -> str:
        if not self.history:
            return ""
        return " | ".join(f"{a}: {b[:40]}" for a, b in self.history[-20:])

chat = JabrigChat()

# ---------------------------------------------------------------------------
# 11. FastAPI Web UI
# ---------------------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="JABRIG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("=== JABRIG Mulai ===")
    logger.info("Perangkat : %s", PERANGKAT)
    logger.info("Kendali   : %s (%s)", MODE_KENDALI, "aktif" if hp.tersedia else "tidak aktif")
    await ai.cek_sumber()
    logger.info("HERMES    : aktif")
    logger.info("JEV       : %s", "aktif" if jev.active else "tidak aktif (fail-open)")
    logger.info("Web UI    : http://localhost:8000")
    logger.info("=== JABRIG Siap ===")


@app.get("/", response_class=HTMLResponse)
def index():
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JABRIG</title>
<style>
  html, body {{ background: #02040a; color: #e8eaf6; font-family: system-ui, sans-serif; margin: 0; }}
  .container {{ max-width: 800px; margin: 40px auto; padding: 0 20px; }}
  h1 {{ font-size: 2.2rem; background: linear-gradient(90deg, #4285f4, #00ff9d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.4rem; }}
  .sub {{ color: #7a7f9a; margin-bottom: 2rem; }}
  .panel {{ background: #0b0f1c; border: 1px solid #2a3456; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  .panel h2 {{ font-size: 1rem; color: #9aa0b8; margin: 0 0 1rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }}
  .stat {{ background: #0f1320; border-radius: 8px; padding: 0.8rem 1rem; }}
  .stat .label {{ color: #7a7f9a; font-size: 0.8rem; text-transform: uppercase; }}
  .stat .value {{ color: #e8eaf6; font-size: 1.1rem; font-weight: bold; margin-top: 0.2rem; }}
  .stat .value.ok {{ color: #00ff9d; }}
  .stat .value.warn {{ color: #ffbf00; }}
  .stat .value.bad {{ color: #ff6b6b; }}
  textarea {{ width: 100%; background: #0b0f1c; color: #e8eaf6; border: 1px solid #2a3456; border-radius: 8px; padding: 1rem; font-size: 1rem; box-sizing: border-box; resize: vertical; }}
  button {{ background: linear-gradient(90deg, #4285f4, #00ff9d); border: none; border-radius: 8px; padding: 0.8rem 1.5rem; font-size: 1rem; font-weight: bold; color: #02040a; cursor: pointer; margin-top: 0.6rem; }}
  button:hover {{ opacity: 0.92; }}
  .output {{ margin-top: 1rem; padding: 1rem; background: #0b0f1c; border-radius: 8px; white-space: pre-wrap; line-height: 1.6; }}
  .footer {{ text-align: center; color: #7a7f9a; margin-top: 2rem; font-size: 0.85rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>⚡ JABRIG</h1>
  <p class="sub">Sistem Kecerdasan Terpadu • Gemini → 9Router • HERMES • JEV</p>

  <div class="panel">
    <h2>Sistem</h2>
    <div class="grid">
      <div class="stat">
        <div class="label">Perangkat</div>
        <div class="value ok" id="perangkat">{PERANGKAT}</div>
      </div>
      <div class="stat">
        <div class="label">Mode Kendali</div>
        <div class="value {"ok" if hp.tersedia else "warn"}" id="mode">{MODE_KENDALI}</div>
      </div>
    </div>
    <div class="grid" style="margin-top:0.8rem">
      <div class="stat">
        <div class="label">Gemini</div>
        <div class="value {"ok" if ai.status_gemini else "bad"}" id="gemini">{"✅ SIAP" if ai.status_gemini else "⚠️ Tidak Aktif"}</div>
      </div>
      <div class="stat">
        <div class="label">9Router</div>
        <div class="value {"ok" if ai.status_router else "warn"}" id="router">{"✅ SIAP" if ai.status_router else "⚠️ Tidak Aktif"}</div>
      </div>
      <div class="stat" style="grid-column: span 2;">
        <div class="label">HERMES / JEV</div>
        <div class="value ok">HERMES: aktif • JEV: {"aktif" if jev.active else "tidak aktif (fail-open)"}</div>
      </div>
    </div>
  </div>

  <div class="panel">
    <h2>Kirim Perintah</h2>
    <textarea id="input" rows="3" placeholder="Contoh: buka youtube / siapa kamu / apakah kamu tahu proyek saya?"></textarea>
    <br>
    <button onclick="kirim()">Kirim</button>
    <div class="output" id="output"></div>
  </div>

  <div class="footer">
    JABRIG v3.0 — Gemini → 9Router • HERMES • JEV • tanpa root/ADB
  </div>
</div>

<script>
async function kirim() {{
  var input = document.getElementById('input');
  var output = document.getElementById('output');
  if (!input.value.trim()) return;
  output.textContent = "⏳ Memproses...";
  try {{
    var res = await fetch('/perintah', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ teks: input.value }})
    }});
    var data = await res.json();
    output.textContent = (data.jawab !== undefined ? data.jawab : JSON.stringify(data, null, 2));
    input.value = '';
  }} catch (e) {{
    output.textContent = 'Gagal terhubung ke JABRIG: ' + e.message;
  }}
}}
</script>
</body>
</html>"""


@app.post("/perintah")
async def perintah(payload: dict):
    teks = payload.get("teks", "").strip()
    if not teks:
        raise HTTPException(status_code=400, detail="teks kosong")
    hasil = await chat.proses_perintah(teks)
    # Simpan ringkasan sesi tiap 10 pesan
    if len(chat.history) % 10 == 0:
        try:
            chat.rangkum_sesi()
            save_session_summary(chat.rangkum_sesi())
        except Exception as e:
            logger.warning("[MEMORI] Gagal simpan sesi: %s", e)
    return {
        "jawab": hasil.get("jawab", hasil.get("teks", "")),
        "jalur": hasil.get("jalur", hasil.get("sumber", "tidak diketahui")),
        "sumber": hasil.get("sumber", ""),
    }


@app.get("/status")
async def status_endpoints():
    return {
        "perangkat": PERANGKAT,
        "mode_kendali": MODE_KENDALI,
        "kendali_aktif": hp.tersedia,
        "gemini_siap": ai.status_gemini,
        "router_siap": ai.status_router,
        "jev_aktif": jev.active,
        "action_count": len(_action_registry.names()),
        "plugin_count": len(_plugin_registry._plugins),
        "memory_categories": list(get_memory_categories().keys()),
    }


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("[AI] Menutup klien...")
    await ai.tutup()
    logger.info("=== JABRIG Berhenti ===")


# ---------------------------------------------------------------------------
# 12. Jalankan jika dieksekusi langsung
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
