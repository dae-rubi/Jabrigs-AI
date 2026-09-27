"""
Action: buka aplikasi di HP Android (via Termux:API atau ADB), atau di PC.
Bisa dipanggil dari HERMES/9Router/JEV.
"""

import subprocess
import os
import platform as _platform

# Peta aplikasi dikenal (nama panggilan → paket Android / nama eksekutable PC)
AplikasiTerdaftar = {
    "whatsapp":    "com.whatsapp",
    "telegram":    "org.telegram.messenger",
    "youtube":     "com.google.android.youtube",
    "pengaturan":  "com.android.settings",
    "kamera":       "com.android.camera",
    "galeri":       "com.android.gallery3d",
    "kalkulator":  "com.android.calculator2",
}

# Untuk PC (opsional): nama aplikasi yang biasa dijalankan via subprocess
# (tidak wajib ada; jika tidak ada paket, action masih mencoba NamaAplikasi sebagai command).
PC_CommandPelantai = {
    "whatsapp":    ["whatsapp"],
    "telegram":    ["telegram-desktop", "telegram"],
    "youtube":     ["google-chrome-stable", "firefox", "brave-browser"],
}


def _ada_termux_api() -> bool:
    return "com.termux" in os.environ.get("PREFIX", "")


def _try_open_android(paket: str, nama_panggilan: str) -> dict:
    if _ada_termux_api():
        try:
            subprocess.run(
                ["termux-open-url", f"{nama_panggilan}://"],
                capture_output=True,
                timeout=5,
            )
            return {"ok": True, "pesan": f"Membuka {nama_panggilan} lewat Termux:API ✅", "jalur": "termux-api"}
        except Exception as e:
            return {"ok": False, "pesan": f"Gagal lewat Termux:API — {str(e)[:60]}", "jalur": "termux-api"}
    return {"ok": False, "pesan": "Termux:API tidak tersedia untuk membuka aplikasi Android."}


def _try_open_adb(paket: str, nama_panggilan: str) -> dict:
    try:
        subprocess.run(
            ["adb", "shell", "am", "start", "-n", f"{paket}/{paket}.MainActivity"],
            capture_output=True,
            timeout=10,
        )
        return {"ok": True, "pesan": f"Membuka {nama_panggilan} lewat ADB ✅", "jalur": "adb"}
    except Exception as e:
        return {"ok": False, "pesan": f"Gagal lewat ADB — {str(e)[:60]}", "jalur": "adb"}


def _try_open_pc(nama_panggilan: str) -> dict:
    perintah = PC_CommandPelantai.get(nama_panggilan)
    if not perintah:
        perintah = [nama_panggilan]
    try:
        subprocess.Popen(perintah, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"ok": True, "pesan": f"Membuka {nama_panggilan} di PC ✅", "jalur": "pc"}
    except Exception as e:
        return {"ok": False, "pesan": f"Gagal buka aplikasi di PC — {str(e)[:60]}", "jalur": "pc"}


def _open_app(parameters: dict, **ctx) -> dict:
    nama = (parameters.get("nama") or parameters.get("nama_aplikasi") or "").strip().lower()
    if not nama:
        return {"ok": False, "pesan": "Sebutkan nama aplikasi. Contoh: whatsapp, youtube, telegram."}

    paket = AplikasiTerdaftar.get(nama)

    # FC: prioritas HP via Termux:API → ADB → PC fallback
    if paket:
        r = _try_open_android(paket, nama)
        if r["ok"]:
            return r
        r = _try_open_adb(paket, nama)
        if r["ok"]:
            return r
        return {"ok": False, "pesan": f"Aplikasi {nama} dikenal tapi gagal dibuka di HP. Coba cek koneksi Termux:API/ADB.", "jalur": r.get("jalur", "tidak diketahui")}
    else:
        r = _try_open_pc(nama)
        if r["ok"]:
            return r
        return {"ok": False, "pesan": f"Aplikasi '{nama}' tidak dikenal di HP, dicoba di PC — gagal. Pastikan nama aplikasi benar."}


TOOL = {
    "name": "open_app",
    "description": (
        "Buka aplikasi di HP (Android / Termux) atau PC. "
        "Aplikasi yang dikenal: whatsapp, telegram, youtube, pengaturan, kamera, galeri, kalkulator. "
        "Jika nama tidak dikenal, action akan mencoba menjalankannya sebagai command di PC."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "nama": {
                "type": "string",
                "description": "Nama aplikasi yang akan dibuka (mis. whatsapp, youtube).",
            },
            "nama_aplikasi": {
                "type": "string",
                "description": "Alias untuk 'nama'.",
            },
        },
        "required": ["nama"],
    },
    "handler": _open_app,
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}
