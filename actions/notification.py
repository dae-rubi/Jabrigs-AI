"""
Action: kirim notifikasi ke HP (hanya melalui Termux:API).
Jika tidak ada Termux:API, beri tahu bahwa notifikasi tidak tersedia.
"""

import subprocess
import os

_NOTIF_SLOT = "jabrig-app"


def _kirim_notifikasi_termux(judul: str, isi: str) -> dict:
    try:
        subprocess.run(
            ["termux-notification",
             "--title", judul,
             "--content", isi,
             "--id", _NOTIF_SLOT],
            capture_output=True,
            timeout=10,
        )
        return {"ok": True, "pesan": "Notifikasi dikirim ✅"}
    except Exception as e:
        return {"ok": False, "pesan": f"Gagal kirim notifikasi lewat Termux:API — {str(e)[:80]}"}


def _kirim_notifikasi_adb(judul: str, isi: str) -> dict:
    # Android tidak menyediakan perintah adb langsung untuk push notification
    # tanpa akses UI/notifikasi service. Beri tahu bahwa fitur ini terbatas.
    return {"ok": False, "pesan": "Notifikasi hanya tersedia lewat Termux:API, bukan ADB."}


def _kirim_notifikasi_pc(judul: str, isi: str) -> dict:
    return {"ok": False, "pesan": "Notifikasi hanya tersedia di HP (Termux:API). Di PC fitur ini belum didukung."}


def _notification(parameters: dict, **ctx) -> dict:
    judul = (parameters.get("judul") or parameters.get("title") or "JABRIG").strip()
    isi = (parameters.get("isi") or parameters.get("message") or "Pesan dari JABRIG").strip()

    if "com.termux" in os.environ.get("PREFIX", ""):
        return _kirim_notifikasi_termux(judul, isi)

    return _kirim_notifikasi_adb(judul, isi)


TOOL = {
    "name": "kirim_notifikasi",
    "description": (
        "Kirim notifikasi ke HP Android (Termux:API). "
        "Tidak tersedia di PC atau via ADB."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "judul": {"type": "string", "description": "Judul notifikasi."},
            "title": {"type": "string", "description": "Alias untuk 'judul'."},
            "isi": {"type": "string", "description": "Isi notifikasi."},
            "message": {"type": "string", "description": "Alias untuk 'isi'."},
        },
        "required": ["isi"],
    },
    "handler": _notification,
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}
