"""
Konfigurasi API-key dan pengaturan umum Jabrig.
Berbasis pola Mark-LV (config/api_keys.json + config manager).
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

def load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def get_gemini_key() -> str:
    return (load_config().get("gemini_api_key") or "").strip()

def get_router_url() -> str:
    return (load_config().get("router_url") or "http://localhost:20128").strip()

def get_router_key() -> str:
    return (load_config().get("router_api_key") or "").strip()
