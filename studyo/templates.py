"""Dört hazır sunum şablonu. Renkler RGB; fontlar sistem fontu adı (PPTX her yerde düzenlenebilir kalsın).

Her şablon aynı slayt tiplerini destekler; farklar renk, font, başlık bandı, madde işareti ve kutu biçimidir.
Video (Pro) da aynı paleti kullanır: ink (metin), bg (zemin), accent / accent2 / soft (vurgu), card (kutu).
"""
from __future__ import annotations

TEMPLATES = {
    "sade_akademik": {
        "label": "Sade akademik",
        "desc": "Beyaz zemin, lacivert başlık, ince çizgi, Arial. Üniversite dersi ve seminer için.",
        "head_font": "Arial", "body_font": "Arial",
        "bg": (255, 255, 255), "ink": (34, 34, 34), "muted": (95, 95, 95), "title": (21, 61, 110),
        "accent": (21, 61, 110), "accent2": (192, 80, 46), "soft": (234, 240, 247), "card": (255, 255, 255),
        "line": (183, 195, 211), "on_accent": (255, 255, 255),
        "title_rule": True, "band": None, "radius": 0.0, "bullet": "•", "badges": False,
        "title_size": 34, "cover_style": "rule",
    },
    "modern_koyu": {
        "label": "Modern koyu",
        "desc": "Koyu lacivert zemin, turkuaz ve amber vurgular, Calibri. Atölye, eğitim videosu, ekran sunumu.",
        "head_font": "Calibri", "body_font": "Calibri",
        "bg": (18, 24, 38), "ink": (226, 231, 240), "muted": (150, 162, 184), "title": (255, 255, 255),
        "accent": (79, 209, 197), "accent2": (246, 173, 85), "soft": (31, 41, 61), "card": (28, 37, 56),
        "line": (52, 66, 94), "on_accent": (18, 24, 38),
        "title_rule": False, "band": None, "radius": 0.12, "bullet": "▪", "badges": True,
        "title_size": 36, "cover_style": "accent_bar",
    },
    "renkli_lise": {
        "label": "Renkli lise",
        "desc": "Krem zemin, dört canlı renk, numaralı rozetler, yuvarlak kutular, Calibri. Lise ve ortaokul dersi.",
        "head_font": "Calibri", "body_font": "Calibri",
        "bg": (255, 251, 242), "ink": (45, 42, 72), "muted": (110, 106, 135), "title": (45, 42, 110),
        "accent": (255, 107, 74), "accent2": (43, 179, 163), "soft": (255, 240, 214), "card": (255, 255, 255),
        "line": (238, 226, 205), "on_accent": (255, 255, 255),
        "palette": [(255, 107, 74), (43, 179, 163), (255, 185, 40), (108, 99, 255)],
        "title_rule": False, "band": None, "radius": 0.18, "bullet": "●", "badges": True,
        "title_size": 38, "cover_style": "blobs",
    },
    "kurumsal_egitim": {
        "label": "Kurumsal eğitim",
        "desc": "Beyaz zemin, solda petrol rengi şerit, Georgia başlık + Arial metin, kurum adı alt bilgide. Şirket içi eğitim, kurs.",
        "head_font": "Georgia", "body_font": "Arial",
        "bg": (255, 255, 255), "ink": (43, 43, 43), "muted": (100, 100, 100), "title": (15, 76, 92),
        "accent": (15, 76, 92), "accent2": (227, 100, 20), "soft": (236, 244, 246), "card": (255, 255, 255),
        "line": (200, 214, 218), "on_accent": (255, 255, 255),
        "title_rule": False, "band": (15, 76, 92), "radius": 0.04, "bullet": "■", "badges": False,
        "title_size": 34, "cover_style": "band",
    },
}

ALIASES = {"sade": "sade_akademik", "akademik": "sade_akademik", "koyu": "modern_koyu", "modern": "modern_koyu",
           "renkli": "renkli_lise", "lise": "renkli_lise", "kurumsal": "kurumsal_egitim", "egitim": "kurumsal_egitim"}


def get(name: str | None) -> dict:
    name = (name or "sade_akademik").strip().lower().replace(" ", "_").replace("ğ", "g").replace("ı", "i")
    name = ALIASES.get(name, name)
    if name not in TEMPLATES:
        raise SystemExit(f"bilinmeyen şablon '{name}'. Seçenekler: {', '.join(TEMPLATES)}")
    t = dict(TEMPLATES[name])
    t["name"] = name
    t.setdefault("palette", [t["accent"], t["accent2"], t["accent"], t["accent2"]])
    return t


def hexc(rgb) -> str:
    return "%02X%02X%02X" % tuple(rgb)
