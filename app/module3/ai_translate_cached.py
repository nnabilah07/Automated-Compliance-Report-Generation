import os
import json
import hashlib
from groqai_client import get_ai_client

MODEL = "llama-3.3-70b-versatile"
BASE_CACHE = "cache"


# =========================
# UTILITIES
# =========================
def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _hash_json(data):
    raw = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _hash_text(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _cache_path(category, key):
    folder = os.path.join(BASE_CACHE, category)
    _ensure_dir(folder)
    return os.path.join(folder, f"{key}.cache")


# =========================
# DEFECT TRANSLATION (JSON)
# =========================
def translate_defects_cached(defects, language="ms", role="Homeowner"):
    if not defects or language not in ("ms", "en"):
        return defects

    key = f"{language}_{role}_{_hash_json(defects)}"
    cache_file = _cache_path("defects", key)

    # 🔁 cache hit
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    client = get_ai_client()

    target = (
        "Bahasa Malaysia formal pentadbiran Tribunal"
        if language == "ms"
        else "English formal administrative legal style"
    )

    prompt = f"""
Terjemahkan data JSON berikut ke {target}.

PERATURAN WAJIB:
1. Struktur JSON KEKAL
2. Jangan tambah atau buang medan
3. Kekalkan ID, nombor, tarikh, unit
4. Terjemahkan SEMUA teks sahaja

DATA:
{json.dumps(defects, ensure_ascii=False)}
"""

    res = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "Anda penterjemah dokumen rasmi Tribunal TTPM."},
            {"role": "user", "content": prompt}
        ]
    )

    translated = json.loads(res.choices[0].message.content)

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    return translated


# =========================
# AI REPORT TRANSLATION
# =========================
def translate_report_cached(report_text, language="ms", role="Homeowner"):
    if not report_text or language not in ("ms", "en"):
        return report_text

    key = f"{language}_{role}_{_hash_text(report_text)}"
    cache_file = _cache_path("reports", key)

    # 🔁 cache hit
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()

    client = get_ai_client()

    target = (
        "Bahasa Malaysia formal Tribunal"
        if language == "ms"
        else "Formal English Tribunal style"
    )

    prompt = f"""
Terjemahkan teks berikut ke {target}.
Kekalkan format perenggan dan penomboran.

TEKS:
{report_text}
"""

    res = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "Anda penterjemah dokumen rasmi Tribunal."},
            {"role": "user", "content": prompt}
        ]
    )

    translated = res.choices[0].message.content.strip()

    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(translated)

    return translated
