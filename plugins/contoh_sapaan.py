# -*- coding: utf-8 -*-
"""
Plugin contoh: Jika pengguna meminta sapaan khusus, plugin ini membantu HERMES.
Plugin ini tidak bergantung pada komponen lain; cukup letakkan di plugins/.
"""

PLUGIN = {
    "name": "contoh_sapaan",
    "description": (
        "Jika pengguna menyapa dengan nama tertentu (mis. 'Halo Yon'), "
        "plugin ini mencatat nama tersebut ke memori dan membawanya ke respons."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "nama_pengguna": {"type": "string", "description": "Nama yang disebutkan pengguna."},
        },
        "required": [],
    },
    "behavior": "NON_BLOCKING",
    "scheduling": "SILENT",
}


def run(parameters: dict, **ctx) -> str:
    nama = parameters.get("nama_pengguna")
    if not nama:
        return ""
    # Simpan nama ke memori (kategori preferences)
    from memory import update_memory
    update_memory("preferences", "nama_pengguna", nama)
    return f"Baik, saya catat nama Anda sebagai {nama}."
