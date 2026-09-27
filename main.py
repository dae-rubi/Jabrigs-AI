#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
  JABRIG • SISTEM KECERDASAN TERPADU
  Versi: 3.0 | Tanggal: 2026-09-27
  Perangkat: Vivo Y19s / Android Termux / PC
  Tanpa Root • Tanpa ADB Wajib • Termux:API
====================================================================

  ARSITEKTUR:
    ANTARMUKA PENGGUNA
    ├── JARVIS   → Wawancara, interaksi bahasa, respons ramah
    ├── ULTRON   → Kontrol perangkat, eksekusi perintah, status sistem
    └── BRAHMA AI → Pemahaman mendalam, analisis, penyimpanan pengetahuan

    PENGELOLA ALUR
    └── HERMES   → Pengarah pesan, putuskan siapa yang menjawab, koordinasi

    SUMBER KECERDASAN
    ├── GEMINI 2.0 FLASH  → Utama, cepat, percakapan umum
    └── 9ROUTER           → Cadangan, lokal, jika Gemini tidak tersedia

  ALUR CHAT:
    1. PENGGUNA mengirim pesan
    2. HERMES menerima → analisis jenis pesan
       ├── Perintah perangkat → ULTRON
       ├── Percakapan/pertanyaan → GEMINI → 9ROUTER
       ├── Butuh pengetahuan mendalam → BRAHMA AI
       └── Sambutan/perkenalan → JARVIS
    3. Hasil dikembalikan ke HERMES → susun jawaban → tampilkan
    4. BRAHMA AI menyimpan percakapan untuk ingatan

  DIPASANG SECARA OTOMATIS:
    - Deteksi HP Termux / PC
    - Termux:API tanpa root dan tanpa ADB wajib
    - Kendali perangkat: buka/tutup aplikasi, layar, notifikasi
    - AI: Gemini (utama) → 9Router (cadangan)
    - Web UI sederhana berjalan di http://localhost:8000
====================================================================
"""

# ─────────────────────────────────────────────────────────────
#  IMPOR & KONSTAN GLOBAL
# ─────────────────────────────────────────────────────────────
import os
import sys
import time
import json
import secrets
import re
import subprocess
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import asyncio
import httpx

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from jose import jwt
from passlib.context import CryptContext

import uvicorn

# ─────────────────────────────────────────────────────────────
#  DETEKSI & KONFIGURASI PLATFORM OTOMATIS
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 64)
print("  ⚡ JABRIG — SISTEM KECERDASAN TERPADU  v3.0")
print("=" * 64)
print()

TERMITUS_PREFIX = os.environ.get("PREFIX", "")
IS_TERMUX = "com.termux" in TERMITUS_PREFIX
MODE: str = "HP_ANDROID" if IS_TERMUX else "PC"
print(f"  📱 Perangkat  : {MODE} {' (Termux)' if IS_TERMUX else ' (PC/Laptop)'}")

KENDALI: str = "TERMUX_API" if IS_TERMUX else None
if not IS_TERMUX:
    jawab = input("  Aktifkan kendali perangkat via ADB? (y/n): ").strip().lower()
    KENDALI = "ADB" if jawab.startswith("y") else "TIDAK_AKTIF"

print(f"  🎮 Kendali    : {KENDALI}")
print("=" * 64)
print()

# Kunci API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ROUTER_API_URL = os.getenv("ROUTER_API_URL", "http://localhost:20128")
ROUTER_API_KEY = os.getenv("ROUTER_API_KEY", "")

# Paket aplikasi yang dikenali
APLIKASI_DAFTAR: Dict[str, str] = {
    "whatsapp":    "com.whatsapp",
    "telegram":    "org.telegram.messenger",
    "youtube":     "com.google.android.youtube",
    "pengaturan":  "com.android.settings",
    "kamera":      "com.android.camera",
    "galeri":      "com.android.gallery3d",
    "kalkulator":  "com.android.calculator2",
}

# ─────────────────────────────────────────────────────────────
#  🔐 SISTEM KEAMANAN (opsional, untuk API auth)
# ─────────────────────────────────────────────────────────────
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

RAHASIA_JWT: Optional[str] = None
if os.path.exists("./jabrig_kunci.json"):
    with open("./jabrig_kunci.json") as f:
        RAHASIA_JWT = json.load(f).get("kunci", "")

if not RAHASIA_JWT:
    RAHASIA_JWT = secrets.token_hex(32)
    with open("./jabrig_kunci.json", "w") as f:
        json.dump({"kunci": RAHASIA_JWT}, f)


def buat_token(nama: str) -> str:
    return jwt.encode(
        {"sub": nama, "exp": datetime.utcnow() + timedelta(hours=24)},
        RAHASIA_JWT, algorithm="HS256"
    )


def baca_token(t: str) -> Optional[str]:
    try:
        return jwt.decode(t, RAHASIA_JWT, ["HS256"]).get("sub")
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
#  📱 KENDALI PERANGKAT — ULTRON
# ─────────────────────────────────────────────────────────────
class KendaliPerangkat:
    """
    ULTRON: Tangan & mata sistem.
    Buka/tutup aplikasi, ambil layar, kirim notifikasi.
    """

    def __init__(self):
        self.mode = KENDALI
        self.tersedia = self._cek_koneksi()
        self.aplikasi = dict(APLIKASI_DAFTAR)

    def _cek_koneksi(self) -> bool:
        if self.mode == "TIDAK_AKTIF":
            return False
        if self.mode == "TERMUX_API":
            try:
                r = subprocess.run(
                    ["termux-notification", "--title", "tes"],
                    capture_output=True, timeout=3
                )
                return r.returncode == 0
            except Exception:
                return False
        if self.mode == "ADB":
            try:
                r = subprocess.run(
                    ["adb", "devices"], capture_output=True,
                    text=True, timeout=5
                )
                return "device" in r.stdout
            except Exception:
                return False
        return False

    def _cari_paket(self, nama: str) -> Optional[str]:
        t = nama.strip().lower()
        if t in self.aplikasi:
            return self.aplikasi[t]
        for k, v in self.aplikasi.items():
            if k in t or t in k:
                return v
        return None

    def buka_aplikasi(self, nama: str) -> Dict:
        paket = self._cari_paket(nama)
        if not paket:
            return {
                "ok": False,
                "pesan": f"Aplikasi '{nama}' tidak terdaftar",
                "pengeksekusi": "ULTRON",
            }
        if self.mode == "TERMUX_API":
            try:
                subprocess.run(
                    ["termux-open-url", f"{nama.strip().lower()}://"],
                    capture_output=True, timeout=5
                )
                return {
                    "ok": True,
                    "pesan": f"✅ Membuka {nama}",
                    "detail": f"Via Termux:API — skema {nama.strip().lower()}://",
                    "pengeksekusi": "ULTRON",
                }
            except Exception as e:
                return {
                    "ok": False,
                    "pesan": f"❌ Gagal: {str(e)}",
                    "pengeksekusi": "ULTRON",
                }
        if self.mode == "ADB":
            try:
                subprocess.run(
                    [
                        "adb", "shell", "am", "start",
                        "-n", f"{paket}/{paket}.MainActivity",
                    ],
                    capture_output=True, timeout=5
                )
                return {
                    "ok": True,
                    "pesan": f"✅ Membuka {nama}",
                    "detail": f"Via ADB — paket {paket}",
                    "pengeksekusi": "ULTRON",
                }
            except Exception as e:
                return {
                    "ok": False,
                    "pesan": f"❌ Gagal: {str(e)}",
                    "pengeksekusi": "ULTRON",
                }
        return {
            "ok": False,
            "pesan": "❌ Kendali perangkat tidak diaktifkan",
            "pengeksekusi": "ULTRON",
        }

    def tutup_aplikasi(self, nama: str) -> Dict:
        paket = self._cari_paket(nama)
        if not paket:
            return {
                "ok": False,
                "pesan": f"Aplikasi '{nama}' tidak terdaftar",
                "pengeksekusi": "ULTRON",
            }
        try:
            if self.mode == "TERMUX_API":
                subprocess.run(
                    ["am", "force-stop", paket],
                    capture_output=True, timeout=5
                )
            elif self.mode == "ADB":
                subprocess.run(
                    ["adb", "shell", "am", "force-stop", paket],
                    capture_output=True, timeout=5
                )
            else:
                return {
                    "ok": False,
                    "pesan": "❌ Kendali tidak diaktifkan",
                    "pengeksekusi": "ULTRON",
                }
            return {
                "ok": True,
                "pesan": f"✅ Menutup {nama}",
                "pengeksekusi": "ULTRON",
            }
        except Exception as e:
            return {
                "ok": False,
                "pesan": f"❌ Gagal: {str(e)}",
                "pengeksekusi": "ULTRON",
            }

    def ambil_layar(self) -> Dict:
        if self.mode == "TIDAK_AKTIF":
            return {
                "ok": False,
                "pesan": "❌ Kendali tidak diaktifkan",
                "pengeksekusi": "ULTRON",
            }
        try:
            jalur = os.path.expanduser("~/jabrig_layar.png")
            if self.mode == "TERMUX_API":
                subprocess.run(
                    ["termux-screenshot", "-o", jalur],
                    capture_output=True, timeout=10
                )
            else:  # ADB
                tmp = "/sdcard/jabrig_layar.png"
                subprocess.run(
                    ["adb", "shell", "screencap", "-p", tmp],
                    capture_output=True, timeout=10
                )
                subprocess.run(
                    ["adb", "pull", tmp, jalur],
                    capture_output=True, timeout=10
                )
                subprocess.run(
                    ["adb", "shell", "rm", "-f", tmp],
                    capture_output=True, timeout=5
                )
            return {
                "ok": True,
                "pesan": f"✅ Tangkapan layar disimpan",
                "berkas": jalur,
                "pengeksekusi": "ULTRON",
            }
        except Exception as e:
            return {
                "ok": False,
                "pesan": f"❌ Gagal: {str(e)}",
                "pengeksekusi": "ULTRON",
            }

    def kirim_notifikasi(self, judul: str, isi: str) -> Dict:
        if self.mode != "TERMUX_API":
            return {
                "ok": False,
                "pesan": "❌ Notifikasi hanya tersedia lewat Termux:API",
                "pengeksekusi": "ULTRON",
            }
        try:
            subprocess.run(
                [
                    "termux-notification",
                    "--title", judul,
                    "--content", isi,
                ],
                capture_output=True, timeout=5
            )
            return {
                "ok": True,
                "pesan": f"✅ Notifikasi dikirim: {judul}",
                "pengeksekusi": "ULTRON",
            }
        except Exception as e:
            return {
                "ok": False,
                "pesan": f"❌ Gagal: {str(e)}",
                "pengeksekusi": "ULTRON",
            }

    def daftar_aplikasi(self) -> List[str]:
        return list(self.aplikasi.keys())


hp = KendaliPerangkat()

# ─────────────────────────────────────────────────────────────
#  🧠 BRAHMA AI — INGATAN & PEMAHAMAN
# ─────────────────────────────────────────────────────────────
class BrahmanAI:
    """
    BRAHMA AI: Ingatan & Pemahaman.
    Menyimpan percakapan, membaca konteks, mempersiapkan
    konteks untuk respons AI yang lebih baik.
    """

    def __init__(self):
        self.indeks: Dict[str, List[Dict]] = {}  # id_session -> list pesan
        self.daftar_session: List[str] = []
        self.session_aktif: str = self._buat_session("utama")

    def _buat_session(self, label: str = "utama") -> str:
        sid = secrets.token_urlsafe(8)
        self.indeks[sid] = []
        self.daftar_session.append(sid)
        return sid

    def simpan(self, peran: str, isi: str, metadata: Optional[Dict] = None) -> Dict:
        """Simpan satu pesan ke session aktif."""
        catatan = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.utcnow().isoformat(),
            "peran": peran,      # 'user' / 'assistant' / 'system'
            "isi": isi,
            "sumber": metadata.get("sumber", "") if metadata else "",
            "jalur": metadata.get("jalur", "") if metadata else "",
        }
        self.indeks[self.session_aktif].append(catatan)
        return {"session": self.session_aktif, "catatan": catatan}

    def dapat_konteks(self, limit: int = 8) -> List[Dict]:
        """Kembalikan riwayat terbaru dari session aktif."""
        if self.session_aktif not in self.indeks:
            return []
        pesan = self.indeks[self.session_aktif][-limit:]
        return pesan

    def katabuka(self) -> str:
        """Ringkasan singkat session aktif untuk prompt AI."""
        pesan = self.dapat_konteks(limit=4)
        if not pesan:
            return "Belum ada percakapan sebelumnya."
        baris = []
        for p in pesan[-4:]:
            peran = p["peran"].upper()
            isi_pesan = p["isi"]
            baris.append(f"[{peran}] {isi_pesan}")
        return "\n".join(baris)

    def alih_session(self, sid: str) -> bool:
        if sid in self.indeks:
            self.session_aktif = sid
            return True
        return False

    def daftar_session(self) -> List[Dict]:
        return [
            {"id": sid, "jumlah": len(self.indeks.get(sid, []))}
            for sid in self.daftar_session
        ]

    def hapus_session(self, sid: str) -> bool:
        if sid in self.indeks:
            del self.indeks[sid]
            self.daftar_session.remove(sid)
            if self.session_aktif == sid:
                self.session_aktif = self._buat_session("utama")
            return True
        return False

    def simpan_hasil(self, pesan_user: str, hasil_ai: Dict) -> None:
        """BRAHMA menyimpan hasil akhir percakapan."""
        self.simpan("user", pesan_user)
        teks = hasil_ai.get("jawab", "") or hasil_ai.get("pesan", "")
        konteks_AI = {
            "sumber":    hasil_ai.get("sumber", ""),
            "jalur":     hasil_ai.get("jalur", ""),
            "pengeksekusi": hasil_ai.get("pengeksekusi", ""),
        }
        self.simpan("assistant", teks, konteks_AI)


brahma = BrahmanAI()

# ─────────────────────────────────────────────────────────────
#  🤖 JARVIS — Wajah & Sambutan
# ─────────────────────────────────────────────────────────────
class Jarvis:
    """
    JARVIS: Wajah ramah. Sambutan, perkenalan, bimbingan.
    """

    def __init__(self):
        self.pemicu = [
            "halo", "hai", "selamat", "pagi", "siang", "sore", "malam",
            "perkenalkan", "bantu", "help", "help me", "tolong",
            "siapa kamu", "apa kabar", "hai jabrig",
        ]

    def cocok(self, pesan: str) -> bool:
        t = pesan.strip().lower()
        return any(kata in t for kata in self.pemicu)

    def respons(self, pesan: str) -> Dict:
        waktu = datetime.utcnow().strftime("%H:%M")
        salam = (
            "Selamat pagi" if 5 <= datetime.utcnow().hour < 12
            else "Selamat siang" if 12 <= datetime.utcnow().hour < 15
            else "Selamat sore" if 15 <= datetime.utcnow().hour < 18
            else "Selamat malam"
        )

        perkenalan = (
            "Saya JARVIS, antarmuka percakapan JABRIG.\n"
            "Ada ULTRON untuk kendali perangkat dan BRAHMA AI\n"
            "untuk ingatan serta pemahaman. Kami siap membantu Anda."
        )

        return {
            "sumber": "JARVIS",
            "jalur":  "JARVIS",
            "jawab": (
                f"👋 {salam}! ({waktu})\n\n"
                f"{perkenalan}\n\n"
                f"Contoh perintah:\n"
                f"  •  buka youtube\n"
                f"  •  tutup whatsapp\n"
                f"  •  ambil layar\n"
                f"  •  notifikasi Halo Dunia\n"
                f"  •  status\n"
                f"  •  siapa kamu"
            ),
        }


jarvis = Jarvis()

# ─────────────────────────────────────────────────────────────
#  ⚙️ ULTRON — Kontrol Perangkat (telah terdefinisi di atas)
# ─────────────────────────────────────────────────────────────
# Kelas KendaliPerangkat berperan sebagai ULTRON

class UltronAPI:
    """
    Pembungkus ULTRON yang menyesuaikan respons menjadi
    bentuk standar yang diharapkan HERMES.
    """

    def __init__(self):
        self.hp = hp

    def cocok(self, pesan: str) -> bool:
        t = pesan.strip().lower()
        kata_kunci = [
            "buka", "tutup", "tutupkan", "matikan",
            "ambil layar", "tangkapan", "screenshot", "foto layar",
            "notifikasi", "kirim pesan", "beri tahu",
            "status", "cek sistem", "cek", "lihat sistem",
        ]
        return any(k in t for k in kata_kunci)

    def eksekusi(self, pesan: str) -> Dict:
        t = pesan.strip().lower()
        # notifikasi
        if any(k in t for k in ["notifikasi", "kirim pesan", "beri tahu"]):
            isi = re.sub(
                r"(notifikasi|kirim pesan|beri tahu)\s*",
                "", pesan, flags=re.IGNORECASE
            ).strip()
            judul = "JABRIG"
            isi_final = isi or "Pesan dari JABRIG ✅"
            hasil = self.hp.kirim_notifikasi(judul, isi_final)
            return {
                "sumber": "ULTRON",
                "jalur":  "ULTRON",
                "jawab":  hasil["pesan"],
                **{k: v for k, v in hasil.items() if k not in ["ok", "pesan"]},
            }
        # status
        if any(k in t for k in ["status", "cek sistem", "cek", "lihat sistem"]):
            return {
                "sumber": "ULTRON",
                "jalur":  "ULTRON",
                "jawab":  self._status_teks(),
            }
        # buka
        if "buka" in t:
            for nama in self.hp.daftar_aplikasi():
                if nama in t:
                    hasil = self.hp.buka_aplikasi(nama)
                    return {
                        "sumber": "ULTRON",
                        "jalur":  "ULTRON",
                        "jawab":  hasil["pesan"],
                        "ok":     hasil["ok"],
                    }
        # tutup
        if any(k in t for k in ["tutup", "tutupkan", "matikan"]):
            for nama in self.hp.daftar_aplikasi():
                if nama in t:
                    hasil = self.hp.tutup_aplikasi(nama)
                    return {
                        "sumber": "ULTRON",
                        "jalur":  "ULTRON",
                        "jawab":  hasil["pesan"],
                        "ok":     hasil["ok"],
                    }
        # layar
        if any(k in t for k in ["layar", "tangkapan", "screenshot", "foto layar"]):
            hasil = self.hp.ambil_layar()
            return {
                "sumber": "ULTRON",
                "jalur":  "ULTRON",
                "jawab":  hasil["pesan"],
                "berkas": hasil.get("berkas"),
                "ok":     hasil["ok"],
            }
        return {
            "sumber": "ULTRON",
            "jalur":  "ULTRON",
            "jawab":  "❌ Perintah perangkat tidak dikenali",
        }

    def _status_teks(self) -> str:
        baris = [
            "📊 STATUS SISTEM ULTRON",
            "",
            f"  Perangkat : {MODE}",
            f"  Kendali   : {KENDALI} "
            f"({'✅ aktif' if hp.tersedia else '⚠️ tidak aktif'})",
            f"  AI        : Gemini (utama) → 9Router (cadangan)",
            "",
            "  Aplikasi yang dikenali:",
        ]
        for a in hp.daftar_aplikasi():
            baris.append(f"    • {a}")
        if hp.tersedia:
            baris.append("")
            baris.append("  ULTRON siap menerima perintah.")
        else:
            baris.append("")
            baris.append("  ULTRON: Kendali perangkat tidak diaktifkan.")
        return "\n".join(baris)


ultron = UltronAPI()

# ─────────────────────────────────────────────────────────────
#  🧭 HERMES — Pengelola Alur
# ─────────────────────────────────────────────────────────────
class HermesPengarah:
    """
    HERMES: Pengarah lalu lintas.
    Terima pesan → tentukan ke inti mana → eksekusi → BRAHMA simpan.
    """

    def __init__(self):
        self.jarvis = jarvis
        self.ultron = ultron
        self.brahma = brahma
        self.ai = None  # akan di-set setelah PengelolaAI dibuat

    def set_ai(self, ai):
        self.ai = ai

    def arahkan(self, pesan: str) -> Dict:
        """
        Menganalisis pesan dan memilih inti yang sesuai.
        Urutan prioritas:
          1. JARVIS — sambutan / sapa / bantuan
          2. ULTRON — perintah perangkat / status
          3. GEMINI / 9ROUTER — pertanyaan umum / analisis
        Setelah jawaban diterima, BRAHMA mencatatnya.
        """

        t = pesan.strip().lower()

        # --- JARVIS --------------------------------------------------
        if self.jarvis.cocok(pesan) and not any(
            k in t for k in [
                "buka", "tutup", "notifikasi", "layar",
                "tangkapan", "screenshot", "status", "cek",
            ]
        ):
            hasil = self.jarvis.respons(pesan)
            self.brahma.simpan_hasil(pesan, hasil)
            return hasil

        # --- ULTRON --------------------------------------------------
        if self.ultron.cocok(pesan):
            hasil = self.ultron.eksekusi(pesan)
            self.brahma.simpan_hasil(pesan, hasil)
            return hasil

        # --- GEMINI / 9ROUTER ----------------------------------------
        if self.ai is not None:
            hasil = asyncio.run(self.ai.tanya(pesan))
            self.brahma.simpan_hasil(pesan, hasil)
            return hasil

        # fallback
        fallback = {
            "sumber": "SYSTEM",
            "jalur":  "FALLBACK_LOKAL",
            "jawab":  (
                "Diterima: " + pesan + "\n\n"
                "⚠️  Sistem AI belum siap.\n"
                "   Isi GEMINI_API_KEY atau hubungkan 9Router."
            ),
        }
        self.brahma.simpan_hasil(pesan, fallback)
        return fallback


hermes = HermesPengarah()

# ─────────────────────────────────────────────────────────────
#  🧭 SUMBER KECERDASAN: GEMINI → 9ROUTER
# ─────────────────────────────────────────────────────────────
class PengelolaAI:
    """
    Mengirim pertanyaan ke Gemini; jika gagal, mencoba 9Router.
    Jika keduanya tidak siap, fallback ke respons lokal.
    """

    def __init__(self):
        self.sumber: Dict[str, Dict] = {
            "Gemini": {
                "url":     "https://generativelanguage.googleapis.com"
                          "/v1beta/models/gemini-2.0-flash:generateContent",
                "kunci":   GEMINI_API_KEY,
                "timeout": 10.0,
            },
            "9Router": {
                "url":     ROUTER_API_URL,
                "kunci":   ROUTER_API_KEY,
                "timeout": 15.0,
            },
        }
        self.status: Dict[str, bool] = {}

    async def cek_sumber(self) -> None:
        print("\n  🧭 Memeriksa sumber AI …")
        for nama, cfg in self.sumber.items():
            siap = bool(cfg["kunci"])
            if siap and nama == "9Router":
                try:
                    async with httpx.AsyncClient(timeout=3.0) as c:
                        await c.get(
                            f"{cfg['url']}/status",
                            headers={
                                "Authorization": f"Bearer {cfg['kunci']}"
                            },
                        )
                except Exception:
                    siap = False
            self.status[nama] = siap
            ikon = "✅ SIAP" if siap else "⚠️ Tidak diatur"
            print(f"    {nama:10} → {ikon}")
        print()

    async def tanya(self, pesan: str) -> Dict:
        mulai = time.time()

        # Siapkan konteks dari BRAHMA
        konteks_brahma = brahma.katabuka()
        prompt = (
            f"Percakapan sebelumnya:\n{konteks_brahma}\n\n"
            f"Pesan pengguna:\n{pesan}\n\n"
            f"Jawab dalam bahasa Indonesia dengan ramah dan jelas."
        )

        for nama in ["Gemini", "9Router"]:
            if not self.status.get(nama, False):
                continue
            hasil = await self._kirim_ke_ai(nama, prompt)
            if hasil["sukses"]:
                return {
                    "sumber":   nama,
                    "jawab":    hasil["teks"],
                    "jalur":    (
                        "GEMINI_UTAMA" if nama == "Gemini"
                        else "9ROUTER_CADANGAN"
                    ),
                    "waktu_ms": round((time.time() - mulai) * 1000, 2),
                }

        # fallback lokal
        balik = (
            f"Diterima: {pesan}\n\n"
            "⚠️  Isi GEMINI_API_KEY atau ROUTER_API_KEY\n"
            "    untuk jawaban AI yang lengkap.\n\n"
            "Contoh perintah lokal:\n"
            "  • 'siapa kamu'      → profil JABRIG\n"
            "  • 'status'         → status sistem\n"
            "  • 'buka youtube'   → buka aplikasi\n"
            "  • 'tutup whatsapp' → tutup aplikasi\n"
            "  • 'ambil layar'    → tangkapan layar\n"
            "  • 'notifikasi halo' → kirim notifikasi"
        )
        return {
            "sumber":   "lokal",
            "jawab":    balik,
            "jalur":    "CADANGAN_LOKAL",
            "waktu_ms": round((time.time() - mulai) * 1000, 2),
        }

    async def _kirim_ke_ai(self, nama: str, pesan: str) -> Dict:
        cfg = self.sumber[nama]
        try:
            async with httpx.AsyncClient(timeout=cfg["timeout"]) as c:
                if nama == "Gemini":
                    resp = await c.post(
                        f"{cfg['url']}?key={cfg['kunci']}",
                        json={
                            "contents": [{
                                "parts": [{"text": pesan}]
                            }]
                        },
                    )
                    if resp.status_code == 200:
                        d = resp.json()
                        teks = d["candidates"][0]["content"]["parts"][0]["text"]
                        return {"sukses": True, "teks": teks}
                    else:
                        return {
                            "sukses": False,
                            "teks":    f"Gemini HTTP {resp.status_code}",
                        }
                elif nama == "9Router":
                    resp = await c.post(
                        f"{cfg['url']}/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {cfg['kunci']}"
                        },
                        json={
                            "model":     "auto",
                            "messages":  [{"role": "user", "content": pesan}],
                            "max_tokens": 1024,
                        },
                    )
                    if resp.status_code == 200:
                        d = resp.json()
                        teks = d["choices"][0]["message"]["content"]
                        return {"sukses": True, "teks": teks}
                    else:
                        return {
                            "sukses": False,
                            "teks":    f"9Router HTTP {resp.status_code}",
                        }
        except httpx.TimeoutException:
            return {"sukses": False, "teks": f"{nama}: waktu habis"}
        except Exception as e:
            return {
                "sukses": False,
                "teks": f"{nama}: {type(e).__name__}: {str(e)[:40]}",
            }


ai = PengelolaAI()

# Hubungkan HERMES ke AI
hermes.set_ai(ai)

# ─────────────────────────────────────────────────────────────
#  🌐 ANTARMUKA WEB — FASTAPI
# ─────────────────────────────────────────────────────────────
app = FastAPI(title="JABRIG v3.0", version="3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await ai.cek_sumber()


# ------------------------------------------------------------
#  GET  /   → halaman utama HTML
# ------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def halaman_utama():
    status_ai_html = ""
    for nama, siap in ai.status.items():
        warna = "#00ff9d" if siap else "#ff6b6b"
        teks  = "✅ SIAP" if siap else "⚠️ TIDAK DIATUR"
        status_ai_html += (
            f'<div class="card-ai"><b>{nama}</b> '
            f'<span style="color:{warna}">{teks}</span></div>'
        )

    kontrol_teks = (
        "❌ Tidak Aktif" if KENDALI == "TIDAK_AKTIF" else KENDALI
    )
    kontrol_warna = (
        "#ff6b6b" if KENDALI == "TIDAK_AKTIF" else "#00ff9d"
    )

    apl = ", ".join(hp.daftar_aplikasi()) if hp.tersedia else "—"

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JABRIG v3.0 — JARVIS • ULTRON • BRAHMA AI</title>
<style>
:root {{
  --bg: #03040a;
  --b:  #4285f4;
  --e:  #00ff9d;
  --r:  #ff6b6b;
  --t:  #e8eaf6;
  --m:  #7a7f9a;
  --k:  #1a1d2e;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: var(--bg);
  color: var(--t);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  max-width: 720px;
  margin: 0 auto;
  padding: 18px 16px 30px;
  line-height: 1.6;
  min-height: 100vh;
}}
h1 {{
  background: linear-gradient(90deg, var(--b), var(--e));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 1.7rem;
  margin-bottom: 2px;
  text-align: center;
}}
.subtitle {{
  text-align: center;
  color: var(--m);
  margin-bottom: 18px;
  font-size: .9rem;
}}
.kotak {{
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(66,133,244,.18);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
}}
.kotak h3 {{
  color: var(--e);
  font-size: 1rem;
  margin-bottom: 10px;
  border-bottom: 1px solid rgba(66,133,244,.15);
  padding-bottom: 6px;
}}
.grid-2 {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}}
.grid-3 {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}}
.card {{
  background: rgba(66,133,244,.07);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: .9rem;
}}
.card b {{ font-size: .95rem; }}
.card-ai {{
  background: rgba(0,255,157,.06);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: .9rem;
}}

textarea {{
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(66,133,244,.3);
  background: rgba(0,0,0,.35);
  color: var(--t);
  font-size: 1rem;
  resize: vertical;
  outline: none;
  transition: border-color .2s;
  font-family: inherit;
}}
textarea:focus {{ border-color: var(--b); }}

button {{
  background: linear-gradient(90deg, var(--b), var(--e));
  border: none;
  padding: 10px 22px;
  border-radius: 10px;
  font-weight: 600;
  font-size: .95rem;
  cursor: pointer;
  margin-top: 10px;
  color: #03040a;
  letter-spacing: .2px;
  transition: filter .15s;
}}
button:hover {{ filter: brightness(1.1); }}

.hasil {{
  margin-top: 14px;
  white-space: pre-wrap;
  line-height: 1.65;
  color: var(--t);
  background: rgba(0,0,0,.25);
  border-radius: 10px;
  padding: 12px 14px;
  min-height: 48px;
  border: 1px solid rgba(66,133,244,.12);
  font-size: .95rem;
}}
.hasil b {{ color: var(--e); }}
.hasil .tag {{
  display: inline-block;
  background: rgba(66,133,244,.2);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: .75rem;
  margin-right: 4px;
  color: var(--b);
  font-weight: 600;
}}

.foot {{
  color: var(--m);
  font-size: .8rem;
  margin-top: 22px;
  text-align: center;
  border-top: 1px solid rgba(66,133,244,.1);
  padding-top: 12px;
}}
.legend {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}}
.legend span {{
  font-size: .75rem;
  background: rgba(255,255,255,.05);
  border-radius: 4px;
  padding: 3px 8px;
  color: var(--m);
}}
</style>
</head>
<body>

<h1>⚡ JABRIG</h1>
<p class="subtitle">JARVIS • ULTRON • BRAHMA AI  |  v3.0  |  {MODE}</p>

<div class="kotak">
  <h3>🧭 Status Sistem</h3>
  <div class="grid-2">
    <div class="card"><b>Perangkat</b><br>{MODE}</div>
    <div class="card"><b>Kendali HP</b><br>
      <span style="color:{kontrol_warna}">{kontrol_teks}</span></div>
  </div>
  <div style="margin-top:10px">
    <b style="color:var(--m)">Sumber AI:</b>
    <div style="margin-top:6px">{status_ai_html}</div>
  </div>
</div>

<div class="kotak">
  <h3>🤖 Tiga Inti JABRIG</h3>
  <div class="grid-3">
    <div class="card"><b>🤖 JARVIS</b><br>Wajah & sup bpmtam<br>Sambutan & bantuan</div>
    <div class="card"><b>⚙️ ULTRON</b><br>Tangan & mata<br>Kontrol perangkat</div>
    <div class="card"><b>🧠 BRAHMA AI</b><br>Ingatan & pemahaman<br>Penyimpanan percakapan</div>
  </div>
  <div class="legend">
    <span>[PENGARAH] HERMES</span>
    <span>[GEMINI 2.0] Utama</span>
    <span>[9ROUTER] Cadangan</span>
  </div>
</div>

<div class="kotak">
  <h3>💬 Kirim Pesan ke HERMES</h3>
  <textarea id="p" rows="3"
    placeholder="Contoh: halo / buka youtube / status / siapa kamu / jelaskan AI"></textarea>
  <button onclick="kirim()">Kirim →</button>
  <div id="h" class="hasil"></div>
</div>

<p class="foot">
  JABRIG v3.0 — TANPA ROOT — Termux:API / ADB / Web — Gemini → 9Router<br>
  BRAHMA AI menyimpan setiap percakapan untuk ingatan berikutnya.
</p>

<script>
async function kirim() {{
  var p = document.getElementById('p');
  var h = document.getElementById('h');
  var teks = p.value.trim();
  if (!teks) {{
    h.innerHTML = '<b>⚠️</b>  Ketik pesan terlebih dahulu.';
    return;
  }}
  h.innerHTML = '<span class="tag">HERMES</span> <b>⏳</b> Memproses …';
  try {{
    var r = await fetch('/perintah', {{
      method : 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body   : JSON.stringify({{ pesan: teks }})
    }});
    var d = await r.json();
    var jawab = d.jawab || d.pesan || JSON.stringify(d, null, 2);
    var src = (d.jalur || d.sumber || '???').toUpperCase().replace(/_/g, ' ');
    h.innerHTML = '<span class="tag">' + src + '</span><br><br>' + jawab;
  }} catch (e) {{
    h.innerHTML = '<span class="tag">ERROR</span> <b>❌</b> ' + e.message;
  }}
}}
</script>

</body>
</html>"""


# ------------------------------------------------------------
#  POST /perintah → pesan ke HERMES, dapat jawaban
# ------------------------------------------------------------
@app.post("/perintah")
async def perintah(data: dict):
    pesan = (data.get("pesan") or data.get("teks", "")).strip()
    if not pesan:
        return JSONResponse(
            status_code=400,
            content={"jalur": "ERROR", "pesan": "Harap isi pesan"},
        )

    hasil = hermes.arahkan(pesan)

    return {
        "jalur":     hasil.get("jalur", ""),
        "sumber":    hasil.get("sumber", ""),
        "jawab":     hasil.get("jawab", ""),
        "pesan":     hasil.get("pesan", ""),
        "ok":        hasil.get("ok"),
        "berkas":    hasil.get("berkas"),
        "detail":    hasil.get("detail"),
    }


# ------------------------------------------------------------
#  Endpoint tambahan
# ------------------------------------------------------------
@app.get("/status")
async def status_sistem():
    return {
        "perangkat":    MODE,
        "kendali":      {
            "mode":      KENDALI,
            "tersedia":  hp.tersedia,
            "aplikasi":  hp.daftar_aplikasi(),
        },
        "ai":           {k: {"siap": v} for k, v in ai.status.items()},
        "session_brahma": {
            "aktif": brahma.session_aktif,
            "jumlah_pesan": len(brahma.dapat_konteks(limit=100)),
            "semua_session": brahma.daftar_session(),
        },
        "timestamp":    datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health():
    return {"status": "OK", "versi": "3.0"}


@app.get("/brahma/konteks")
async def brahma_konteks():
    return {"konteks": brahma.dapat_konteks(limit=8)}


@app.get("/brahma/session")
async def brahma_session():
    return {"sessions": brahma.daftar_session()}


# ─────────────────────────────────────────────────────────────
#  7. JALANKAN SERVER
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n")
    print("  ═══════════════════════════════════════════════════")
    print("    🚀 JABRIG v3.0 — Siap Di Jalankan")
    print("  ═══════════════════════════════════════════════════")
    print(f"\n  📱 Perangkat     : {MODE}")
    print(f"  🎮 Kendali HP    : {KENDALI} "
          f"{'✅ tersedia' if hp.tersedia else '⚠️ tidak aktif'}")
    print(f"  🧠 Inti sistem   : JARVIS + ULTRON + BRAHMA AI")
    print(f"  🧭 Pengarah      : HERMES")
    print(f"  🌐 Web UI        : http://localhost:8000")
    print(f"  📡 API status    : http://localhost:8000/status")
    print(f"  📡 API health    : http://localhost:8000/health")
    print(f"  📡 Brahma konteks: http://localhost:8000/brahma/konteks")
    print(f"\n  💡 Tips:")
    print(f"     • Isi GEMINI_API_KEY untuk jawaban AI Gemini")
    print(f"     • Isi ROUTER_API_KEY + ROUTER_API_URL untuk 9Router")
    print(f"     • Di HP, pasang Termux:API dari F-Droid")
    print(f"\n  ⏹️  Hentikan : tekan Ctrl + C")
    print("\n")
    asyncio.run(ai.cek_sumber())
    uvicorn.run(app, host="0.0.0.0", port=8000)
