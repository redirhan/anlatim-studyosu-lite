"""Özet PDF (reportlab, tarayıcı yok): ana fikirler, süreç kutuları, anahtar terimler, kendini dene, kaynakça.

Önce tek sayfaya sığdırmayı dener (punto ölçeği küçülterek); sığmazsa okunaklı puntoyla iki sayfaya akar.
"""
from __future__ import annotations

import io
from pathlib import Path

from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import layout
from .fonts import register_reportlab


def C(rgb, a=1.0):
    return Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha=a)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _hex(c):
    return "#%02X%02X%02X" % tuple(c)


def _label(t):
    t = (t or "").strip()
    return t if t[-1:] in "?!:." else t + ":"


def _colors(t):
    """Koyu şablonda PDF yine açık zeminli; bant için şablonun zemini, vurgu için accent2/accent."""
    if sum(t["bg"]) < 200:
        return {"band": t["bg"], "ink": (30, 34, 45), "acc": (25, 140, 130), "acc2": t["accent2"], "soft": (238, 242, 247),
                "line": (205, 212, 224)}
    return {"band": t["title"], "ink": t["ink"], "acc": t["accent2"], "acc2": t["accent"], "soft": t["soft"],
            "line": t["line"]}


def build(deck: dict, t: dict, sources: dict, out: Path, purpose_line: str = ""):
    register_reportlab()
    col = _colors(t)
    title = deck.get("title", "")
    sub = " · ".join(x for x in (deck.get("subtitle"), "Özet") if x)
    slides = deck.get("slides", [])
    content = [s for s in slides if s.get("type") in layout.BUILDERS and s.get("type") not in
               ("title", "sources", "section", "agenda", "questions")]
    proc = next((s for s in slides if s.get("type") == "process"), None)
    terms = [s for s in slides if s.get("type") == "term"]
    kws = list(deck.get("keywords", []))
    qs = next((s for s in slides if s.get("type") == "questions"), None)
    w, h = A4

    def on_page(c, doc):
        band = 30 * mm
        c.setFillColor(C(col["band"]))
        c.rect(0, h - band, w, band, stroke=0, fill=1)
        c.setFillColor(C(col["acc"]))
        c.rect(0, h - band - 1.6 * mm, w * 0.22, 1.6 * mm, stroke=0, fill=1)
        c.setFillColor(C((255, 255, 255)))
        size = 21
        while pdfmetrics.stringWidth(title, "Brico-Bold", size) > w - 36 * mm and size > 12:
            size -= 1
        c.setFont("Brico-Bold", size)
        c.drawString(18 * mm, h - 15 * mm, title)
        c.setFont("Outfit", 10)
        c.drawString(18 * mm, h - 22.5 * mm, sub)
        c.setFont("Outfit", 7.6)
        c.setFillColor(C(col["ink"], 0.6))
        c.drawString(18 * mm, 9 * mm, purpose_line[:150])
        c.drawRightString(w - 18 * mm, 9 * mm, f"sayfa {doc.page}")

    def story(scale):
        sh = ParagraphStyle("h", fontName="Brico-Bold", fontSize=13 * scale, leading=16.5 * scale,
                            textColor=C(col["ink"]), spaceBefore=4 * scale, spaceAfter=4 * scale)
        si = ParagraphStyle("i", fontName="Outfit", fontSize=10.4 * scale, leading=14 * scale, textColor=C(col["ink"]),
                            leftIndent=15, firstLineIndent=-15, spaceAfter=4.5 * scale)
        sm = ParagraphStyle("m", fontName="Outfit", fontSize=8.4 * scale, leading=11 * scale,
                            textColor=C(col["ink"], 0.85), leftIndent=12, firstLineIndent=-12, spaceAfter=2.5 * scale)
        st = [Paragraph("Ana fikirler", sh)]
        acc = _hex(col["acc"])
        for i, s in enumerate(content, 1):
            text = s.get("summary") or s.get("statement") or s.get("definition") or \
                " ".join(layout._item((s.get("bullets") or [""])[0]))
            st.append(Paragraph(f"<font name='Outfit-SemiBold' color='{acc}'>{i}.</font>&nbsp; "
                                f"<font name='Outfit-SemiBold'>{esc(_label(s.get('title', '')))}</font> {esc(text)}", si))
        if proc:
            steps = proc.get("steps", [])
            st += [Spacer(1, 3 * scale), Paragraph(esc(proc.get("title", "Süreç")), sh)]
            usable = w - 36 * mm
            n = max(1, len(steps))
            bw = (usable - (n - 1) * 8 * mm) / n
            cst = ParagraphStyle("c", fontName="Outfit", fontSize=8.4 * scale, leading=10.8 * scale,
                                 textColor=C(col["ink"]))
            cells, widths = [], []
            for k, stp in enumerate(steps):
                cells.append(Paragraph(f"<font name='Brico-Bold' size='{9.6 * scale:.1f}'>{k + 1}. "
                                       f"{esc(stp.get('label', ''))}</font><br/>{esc(stp.get('text', ''))}", cst))
                widths.append(bw)
                if k + 1 < n:
                    cells.append(Paragraph(f"<font color='{acc}' size='13'>→</font>",
                                           ParagraphStyle("a", fontName="Outfit", fontSize=13, leading=15)))
                    widths.append(8 * mm)
            tb = Table([cells], colWidths=widths)
            style = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5),
                     ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]
            for k in range(0, len(cells), 2):
                style += [("BACKGROUND", (k, 0), (k, 0), C(col["soft"])), ("BOX", (k, 0), (k, 0), 0.7, C(col["line"]))]
            tb.setStyle(TableStyle(style))
            st.append(tb)
        if terms or kws:
            st += [Spacer(1, 3 * scale), Paragraph("Anahtar terimler", sh)]
            for s in terms:
                st.append(Paragraph(f"<font name='Outfit-SemiBold'>{esc(s.get('term', ''))}:</font> "
                                    f"{esc(s.get('definition', ''))}", si))
            if kws:
                st.append(Paragraph(" &nbsp;·&nbsp; ".join(esc(k) for k in kws),
                                    ParagraphStyle("k", fontName="Outfit-Medium", fontSize=9.8 * scale,
                                                   leading=14 * scale, textColor=C(col["ink"]))))
        if qs:
            st += [Spacer(1, 3 * scale), Paragraph(esc(qs.get("title", "Kendini dene")), sh)]
            for i, it in enumerate(qs.get("bullets") or qs.get("items") or [], 1):
                st.append(Paragraph(f"<font name='Outfit-SemiBold' color='{acc}'>{i}.</font>&nbsp; "
                                    f"{esc(' '.join(layout._item(it)).strip())}", si))
        if sources:
            st += [Spacer(1, 3 * scale), Paragraph("Kaynaklar", sh)]
            for s in sources.values():
                st.append(Paragraph("• " + esc(layout.apa(s)), sm))
        return st

    def make(scale):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=38 * mm,
                                bottomMargin=16 * mm, title=f"{title} — özet", author=deck.get("author", ""))
        doc.build(story(scale), onFirstPage=on_page, onLaterPages=on_page)
        return buf.getvalue(), doc.page

    for scale in (1.25, 1.18, 1.12, 1.06, 1.0, 0.95, 0.9, 0.86):
        data, pages = make(scale)
        if pages == 1:
            break
    else:
        data, pages = make(1.0)
    Path(out).write_bytes(data)
    return {"pages": pages, "scale": scale if pages == 1 else 1.0}
