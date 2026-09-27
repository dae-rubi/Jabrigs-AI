"""
Memory manager berbasis pola Mark-LV:
- Kategori: identity, preferences, projects, relationships, wishes, notes
- Penyimpanan: memory/long_term.json
- Prompt budget: hanya inti yang masuk system prompt, sisanya dicari saat perlu.
"""
from __future__ import annotations

import json
from datetime import datetime
from threading import Lock
from pathlib import Path
import sys

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
MEMORY_PATH = BASE_DIR / "memory" / "long_term.json"
_lock = Lock()

MEMORY_MAX_CHARS = 200_000
PROMPT_CORE_CHARS = 900
PROMPT_MAX_PER_CATEGORY = 6

def _empty_memory() -> dict:
    return {
        "identity": {},
        "preferences": {},
        "projects": {},
        "relationships": {},
        "wishes": {},
        "notes": {},
    }

def load_memory() -> dict:
    if not MEMORY_PATH.exists():
        return _empty_memory()
    with _lock:
        try:
            data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                base = _empty_memory()
                for key in base:
                    if key not in data:
                        data[key] = {}
                return data
            return _empty_memory()
        except Exception:
            return _empty_memory()

def _all_entries(memory: dict) -> list[tuple]:
    entries = []
    for cat, items in memory.items():
        if not isinstance(items, dict):
            continue
        for key, entry in items.items():
            if isinstance(entry, dict) and "value" in entry:
                entries.append((cat, key, entry))
    return entries

_trim_notifier = None

def set_trim_notifier(fn) -> None:
    global _trim_notifier
    _trim_notifier = fn

def _trim_to_limit(memory: dict) -> dict:
    if len(json.dumps(memory, ensure_ascii=False)) <= MEMORY_MAX_CHARS:
        return memory
    entries = _all_entries(memory)
    entries.sort(key=lambda t: t[2].get("updated", "0000-00-00"))
    while len(json.dumps(memory, ensure_ascii=False)) > MEMORY_MAX_CHARS and entries:
        cat, key, entry = entries.pop(0)
        if cat in memory and key in memory[cat]:
            del memory[cat][key]
            if _trim_notifier:
                _trim_notifier(f"Memori '{key}' (kategori {cat}) dihapus karena batas penyimpanan.")
    return memory

def save_memory(memory: dict) -> None:
    with _lock:
        memory = _trim_to_limit(memory)
        MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_PATH.write_text(
            json.dumps(memory, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

def update_memory(category: str, key: str, value: str, remember: bool = True) -> dict:
    memory = load_memory()
    now = datetime.now().isoformat(timespec="seconds")
    memory.setdefault(category, {})[key] = {"value": value, "updated": now}
    if remember:
        save_memory(memory)
    return memory

def format_memory_for_prompt(memory: dict | None = None, include_index: bool = True) -> str:
    if memory is None:
        memory = load_memory()
    lines = []
    core_chars = PROMPT_CORE_CHARS
    index_lines = []
    for cat, items in memory.items():
        if not isinstance(items, dict) or not items:
            continue
        cat_lines = []
        cat_chars = 0
        n = 0
        for key, entry in sorted(items.items(), key=lambda t: t[1].get("updated", ""), reverse=True):
            if not isinstance(entry, dict) or "value" not in entry:
                continue
            if n >= PROMPT_MAX_PER_CATEGORY:
                break
            line = f"{cat}: {key} = {entry['value']}"
            cat_lines.append(line)
            cat_chars += len(line)
            n += 1
        if cat_lines:
            block = "\n".join(cat_lines)
            if core_chars > 0 and cat_chars <= core_chars:
                lines.append(block)
                core_chars -= cat_chars
            else:
                index_lines.append(f"{cat}: {len(items)} entri")
    out = []
    if lines:
        out.append("=== MEMORI LANJUTAN ===")
        out.extend(lines)
    if include_index and index_lines:
        out.append("")
        out.append("=== INDEKS MEMORI ===")
        out.extend(index_lines)
        out.append("(lihat panel memori untuk detail)")
    return "\n".join(out)

def search_memory(query: str) -> list[dict]:
    if not query.strip():
        return []
    memory = load_memory()
    q = query.lower()
    results = []
    for cat, items in memory.items():
        if not isinstance(items, dict):
            continue
        for key, entry in items.items():
            if isinstance(entry, dict) and "value" in entry:
                hay = f"{cat} {key} {entry['value']}".lower()
                if q in hay:
                    results.append({
                        "kategori": cat,
                        "kunci": key,
                        "isi": entry["value"],
                        "perbarui": entry.get("updated", ""),
                    })
    return results

def save_session_summary(summary: str) -> None:
    memory = load_memory()
    session_count = memory.get("notes", {}).get("sesi_count", 0)
    memory.setdefault("notes", {})["last_session"] = {
        "value": summary,
        "updated": datetime.now().isoformat(timespec="seconds"),
    }
    memory["notes"]["sesi_count"] = session_count + 1
    save_memory(memory)

def pop_last_session() -> str | None:
    memory = load_memory()
    notes = memory.get("notes", {})
    last = notes.pop("last_session", None)
    if last and isinstance(last, dict):
        save_memory(memory)
        return last.get("value")
    return None

def get_memory_categories() -> dict:
    memory = load_memory()
    out = {}
    for cat, items in memory.items():
        if not isinstance(items, dict):
            continue
        out[cat] = []
        for key, entry in items.items():
            if isinstance(entry, dict) and "value" in entry:
                out[cat].append({
                    "kunci": key,
                    "isi": entry["value"],
                    "perbarui": entry.get("updated", ""),
                })
    return out
