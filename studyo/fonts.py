"""Pakette gelen fontlar (fonts/, OFL-1.1). PIL ölçümü/önizleme, reportlab PDF ve video için.

PPTX dosyaları sistem fontlarını adıyla kullanır (Arial, Calibri, Georgia) — sunum her bilgisayarda düzenlenebilir
kalsın diye. Satır sarma ölçümü bu fontların ölçü uyumlu açık kaynak eşleriyle yapılır:
Arial ≈ Arimo, Calibri ≈ Carlito, Georgia ≈ Gelasio.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

from .config import SKILL

FONT_DIR = SKILL / "fonts"
# PPTX font adı -> (normal, kalın) ölçü eşleri
METRIC = {
    "Arial": ("Arimo-Regular.ttf", "Arimo-Bold.ttf"),
    "Calibri": ("Carlito-Regular.ttf", "Carlito-Bold.ttf"),
    "Georgia": ("Gelasio-Regular.ttf", "Gelasio-Bold.ttf"),
}
# video / PDF aileleri
FAMILY = {
    "outfit": {w: f"Outfit-{w}.ttf" for w in ("Regular", "Medium", "SemiBold", "Bold")},
    "bricolage": {w: f"BricolageGrotesque-{w}.ttf" for w in ("SemiBold", "Bold", "ExtraBold")},
}
REQUIRED = sorted({f for a, b in METRIC.values() for f in (a, b)} |
                  {f for fam in FAMILY.values() for f in fam.values()})


def path_for(name: str) -> Path:
    p = FONT_DIR / name
    if not p.is_file():
        raise SystemExit(f"font eksik: {p} — paketi yeniden açın (fonts/ klasörü gerekli)")
    return p


@lru_cache(maxsize=512)
def metric_font(face: str, bold: bool, size_pt: float, scale: float = 1.0) -> ImageFont.FreeTypeFont:
    """PPTX fontunun ölçü eşi; size_pt punto, scale = piksel/punto."""
    reg, bd = METRIC.get(face, METRIC["Arial"])
    return ImageFont.truetype(str(path_for(bd if bold else reg)), max(1, int(round(size_pt * scale))))


@lru_cache(maxsize=512)
def font(size: float, fam: str = "outfit", weight: str = "Regular") -> ImageFont.FreeTypeFont:
    table = FAMILY[fam]
    if weight not in table:
        weight = {"Regular": "SemiBold", "Medium": "SemiBold"}.get(weight, "Bold") if fam == "bricolage" else "Bold"
    return ImageFont.truetype(str(path_for(table[weight])), max(1, int(size)))


def missing() -> list[str]:
    return [f for f in REQUIRED if not (FONT_DIR / f).is_file()]


_RL = False


def register_reportlab():
    """reportlab için Türkçe karakterli fontları kaydet (Outfit, Bricolage)."""
    global _RL
    if _RL:
        return
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for name, f in (("Outfit", "Outfit-Regular.ttf"), ("Outfit-Medium", "Outfit-Medium.ttf"),
                    ("Outfit-SemiBold", "Outfit-SemiBold.ttf"), ("Outfit-Bold", "Outfit-Bold.ttf"),
                    ("Brico-Bold", "BricolageGrotesque-Bold.ttf"), ("Brico-ExtraBold", "BricolageGrotesque-ExtraBold.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(path_for(f))))
    _RL = True
