"""
Action: status sistem (perangkat, mode, ketersediaan komponen).
Bisa dipanggil dari HERMES/9Router/JEV.
"""

import os


def _get_perangkat_status() -> dict:
    is_termux = "com.termux" in os.environ.get("PREFIX", "")
    perangkat = "HP Android (Termux)" if is_termux else "PC / Laptop"
    return {"perangkat": perangkat, "is_termux": is_termux}


def _system_status(parameters: dict, **ctx) -> dict:
    status = {
        "perangkat": "",
        "is_termux": False,
        "mode_kendali": "tidak_aktif",
        "tersedia": False,
        "termasuk": {
            "termux_api": False,
            "adb": False,
        },
    }
    is_t = _get_perangkat_status()
    status["perangkat"] = is_t["perangkat"]
    status["is_termux"] = is_t["is_termux"]

    if is_t["is_termux"]:
        status["mode_kendali"] = "termux_api"
        try:
            result = subprocess.run(
                ["termux-notification", "--help"],
                capture_output=True, text=True, timeout=3,
            )
            status["tersedia"] = result.returncode == 0
            status["termasuk"]["termux_api"] = status["tersedia"]
        except Exception:
            status["tersedia"] = False
    else:
        # Untuk PC, asumsi tersedia jika ada adb
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True, text=True, timeout=5,
            )
            ada_adb = "device" in result.stdout
            status["mode_kendali"] = "adb" if ada_adb else "tidak_aktif"
            status["tersedia"] = ada_adb
            status["termasuk"]["adb"] = ada_adb
        except Exception:
            status[" tersedia"] = False

    return status


TOOL = {
    "name": "system_status",
    "description": (
        "Ambil status sistem: perangkat (HP/PC), mode kendali (termux-api/adb/tidak_aktif), "
        "dan ketersediaan komponen untuk kendali perangkat."
    ),
    "parameters": {"type": "OBJECT", "properties": {}},
    "handler": _system_status,
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}
