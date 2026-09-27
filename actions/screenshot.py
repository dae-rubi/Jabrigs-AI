"""
Action: ambil tangkapan layar (screenshot).
Simpan ke berkas di folder proyek, beri tahu lokasi file.
"""

import subprocess
import os
import time
from datetime import datetime

SCREENSHOT_DIR = os.path.expanduser("~/jabrig")


def _ambil_layar_termux(path: str) -> dict:
    try:
        subprocess.run(
            ["termux-screenshot", "-o", path],
            capture_output=True,
            timeout=30,
        )
        if os.path.exists(path):
            return {"ok": True, "pesan": f"Tangkapan layar disimpan ✅", "berkas": path}
        return {"ok": False, "pesan": "Perintah berhasil tetapi berkas tidak ditemukan."}
    except Exception as e:
        return {"ok": False, "pesan": f"Gagal lewat Termux:API — {str(e)[:80]}", "jalur": "termux-api"}


def _ambil_layar_adb(path: str) -> dict:
    tmp = "/sdcard/jabrig_layar.png"
    try:
        subprocess.run(
            ["adb", "shell", "screencap", "-p", tmp],
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["adb", "pull", tmp, path],
            capture_output=True,
            timeout=30,
        )
        if os.path.exists(path):
            return {"ok": True, "pesan": "Tangkapan layar disimpan ✅", "berkas": path}
        return {"ok": False, "pesan": "Berhasil screencap, tapi pull gagal."}
    except Exception as e:
        return {"ok": False, "pesan": f"Gagal lewat ADB — {str(e)[:80]}", "jalur": "adb"}


def _ambil_layar_pc(path: str) -> dict:
    # Fallback PC: jika ada alat khusus, bisa ditambahkan di sini.
    # Untuk sekarang beri tahu bahwa fitur ini tersedia di HP/ADB.
    return {"ok": False, "pesan": "Tangkapan layar hanya tersedia di HP (Termux:API / ADB).", "jalur": "pc"}


def _screenshot(parameters: dict, **ctx) -> dict:
    nama_berkas = parameters.get("nama") or "jabrig_screenshot"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    jalur = os.path.join(SCREENSHOT_DIR, f"{nama_berkas}_{timestamp}.png")

    try:
        os.makedirs(os.path.dirname(jalur) or ".", exist_ok=True)
    except Exception:
        pass

    if _ada_termux_api():
        return _ambil_layar_termux(jalur)
    return _ambil_layar_adb(jalur)
    # Jika di PC, kembalikan pesan tidak tersedia.


TOOL = {
    "name": "ambil_layar",
    "description": (
        "Ambil tangkapan layar (screenshot) di HP Android. "
        "Gunakan Termux:API (termux-screenshot) jika tersedia, "
        "jika tidak ada, coba ADB. Simpan di folder jabrig."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "nama": {
                "type": "string",
                "description": "Awalan nama berkas screenshot (opsional).",
            },
        },
        "required": [],
    },
    "handler": _screenshot,
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}
