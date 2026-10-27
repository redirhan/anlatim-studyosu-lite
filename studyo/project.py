"""Proje klasörü: brief.yaml, notes/, research/sources.json, outline.md, deck.json, (Pro) video_plan.json, work/, out/."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from .config import load_config

BRIEF_TEMPLATE = """\
# Anlatım Stüdyosu — proje özeti. Claude bu dosyayı sizinle birlikte doldurur.
# Sorumlu kullanım: Not için teslim edilecek işin içeriğini kendin hazırla; bu araç öğrenme, ders materyali ve
# tasarım içindir. Teslim edilecek bir sunum için "tasarim" modunu kullan: içerik yalnız senin notlarından gelir.

topic: "{topic}"
audience: ""            # ör. "9. sınıf", "üniversite 1. sınıf", "şirket içi yeni çalışanlar"
purpose: ders_materyali # ders_materyali | calisma | tasarim | egitim
  #   ders_materyali: öğretmen/eğitmen için ders sunumu (araştırma + kaynak)
  #   calisma:        kendi çalışman için konu sunumu + özet (teslim edilmez)
  #   tasarim:        SENİN içeriğinden tasarım (notes/ klasöründeki metin dışında bilgi eklenmez)
  #   egitim:         kurum içi eğitim / kurs materyali
language: tr
slide_count: 10         # kapak ve kaynakça dahil
template: {template}    # sade_akademik | modern_koyu | renkli_lise | kurumsal_egitim
kaynak_line: true       # her içerik slaytının altında "Kaynak:" satırı
author: "{author}"      # kapakta "Hazırlayan:" (boş bırakılabilir)
org: "{org}"            # okul / kurum / kurs adı (boş bırakılabilir)
date: ""
use_my_notes_only: false   # true: araştırma yapılmaz, yalnız notes/ klasörü kullanılır (tasarim modunda zorunlu)
# Pro (video):
video_length_min: [3, 5]
tts_engine: {engine}    # ema | gemini | silent
"""


def slug(s: str) -> str:
    s = s.lower().translate(str.maketrans("çğıöşüâîûİ", "cgiosuaiui"))
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:40] or "sunum"


def next_version(out_dir: Path, base: str, ext: str):
    v = 1
    while (out_dir / f"{base}_v{v}{ext}").exists():
        v += 1
    return out_dir / f"{base}_v{v}{ext}", v


def latest(out_dir: Path, base: str, ext: str):
    v = 1
    best = None
    while (out_dir / f"{base}_v{v}{ext}").exists():
        best = out_dir / f"{base}_v{v}{ext}"
        v += 1
    return best


def new_project(path: Path, topic: str = "") -> Path:
    cfg = load_config()
    path.mkdir(parents=True, exist_ok=True)
    for d in ("notes", "research", "work", "out"):
        (path / d).mkdir(exist_ok=True)
    b = path / "brief.yaml"
    if not b.exists():
        b.write_text(BRIEF_TEMPLATE.format(topic=topic.replace('"', "'"), template=cfg["template"],
                                           author=cfg.get("author", ""), org=cfg.get("org", ""),
                                           engine=cfg.get("tts_engine", "ema")), encoding="utf-8")
    s = path / "research" / "sources.json"
    if not s.exists():
        s.write_text(json.dumps({"sources": []}, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def load_brief(p: Path) -> dict:
    f = p / "brief.yaml"
    d = yaml.safe_load(f.read_text(encoding="utf-8")) if f.is_file() else {}
    return d or {}


def load_sources(p: Path) -> dict:
    f = p / "research" / "sources.json"
    if not f.is_file():
        return {}
    d = json.loads(f.read_text(encoding="utf-8"))
    items = d.get("sources", d) if isinstance(d, dict) else d
    return {s["id"]: s for s in items}


def load_deck(p: Path) -> dict:
    f = p / "deck.json"
    if not f.is_file():
        raise SystemExit(f"deck.json yok: {f} (prompts/deck.md şemasıyla Claude yazar)")
    d = json.loads(f.read_text(encoding="utf-8"))
    brief = load_brief(p)
    cfg = load_config()
    for k in ("template", "author", "org", "date", "kaynak_line"):
        if k not in d and brief.get(k) not in (None, ""):
            d[k] = brief[k]
        if k not in d and cfg.get(k) not in (None, ""):
            d[k] = cfg[k]
    d["_root"] = str(p)
    return d


def corpus(p: Path) -> str:
    """Doğrulama metni: kullanıcı notları + açılmış kaynaklardan kaydedilen alıntılar."""
    parts = []
    n = p / "work" / "notes.txt"
    if n.is_file():
        parts.append(n.read_text(encoding="utf-8"))
    for s in load_sources(p).values():
        for e in s.get("excerpts", []):
            parts.append(e if isinstance(e, str) else e.get("text", ""))
    return "\n".join(parts)
