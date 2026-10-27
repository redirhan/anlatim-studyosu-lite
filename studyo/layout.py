"""Slayt yerleşim motoru: deck.json'daki her slaytı şablona göre şekil listesine çevirir.

Aynı şekil listesi iki yere çizilir: PPTX (pptx_out.py, düzenlenebilir metin kutuları ve şekiller) ve PIL önizleme
(preview.py, LibreOffice yoksa). Birim inç; slayt 13,333 × 7,5 (16:9).

Metin sığdırma: her kutu için en büyük punto aranır; satır sarma PPTX fontunun ölçü uyumlu eşiyle ölçülür
(fonts.py). PowerPoint'in "otomatik sığdır" özelliğine güvenilmez; punto dosyaya açıkça yazılır.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .fonts import metric_font

SW, SH = 13.333, 7.5
PX = 4.0                     # ölçüm: punto başına piksel
LINE_K = 1.2                 # tek satır aralığında satır yüksekliği / punto
TYPES = ["title", "section", "agenda", "bullets", "two_col", "process", "compare", "term", "key_fact",
         "questions", "image", "summary", "sources"]


# ---------------------------------------------------------------- şekiller
@dataclass
class Run:
    text: str
    bold: bool = False
    color: tuple | None = None
    italic: bool = False


@dataclass
class Para:
    runs: list
    bullet: str | None = None          # None | "char" | "num"
    align: str = "l"                   # l | c | r
    space_after: float = 0.35          # punto cinsinden değil: punto × bu oran
    rel: float = 1.0                   # kutu puntosuna göre oran (ör. alt satır 0,8)

    @property
    def text(self):
        return "".join(r.text for r in self.runs)


@dataclass
class TextBox:
    x: float
    y: float
    w: float
    h: float
    paras: list
    face: str = "Arial"
    color: tuple = (0, 0, 0)
    max_size: float = 24
    min_size: float = 12
    valign: str = "t"                  # t | m | b
    spacing: float = 1.0               # satır aralığı çarpanı
    bullet_char: str = "•"
    bullet_color: tuple | None = None
    name: str = "Metin"
    max_lines: int = 0                 # 0 = sınırsız; >0 ise toplam satır bu sayıyı aşamaz
    size: float = 0.0                  # sığdırma sonrası
    overflow: bool = False
    lines: int = 0


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float
    fill: tuple | None = None
    line: tuple | None = None
    line_w: float = 0.75
    radius: float = 0.0                # inç
    shape: str = "rect"                # rect | oval | rarrow
    name: str = "Kutu"
    text: TextBox | None = None        # şeklin içindeki metin (ortalanmış)


@dataclass
class Line:
    x1: float
    y1: float
    x2: float
    y2: float
    color: tuple
    width: float = 1.0                 # punto
    name: str = "Çizgi"


@dataclass
class Pic:
    path: str
    x: float
    y: float
    w: float
    h: float
    alt: str = ""
    name: str = "Görsel"


@dataclass
class Table:
    x: float
    y: float
    w: float
    rows: list                         # [[str]]; ilk satır başlık
    col_w: list
    face: str
    size: float
    ink: tuple
    head_fill: tuple
    head_ink: tuple
    label_fill: tuple
    line: tuple
    row_h: list = field(default_factory=list)
    name: str = "Tablo"

    @property
    def h(self):
        return sum(self.row_h)


@dataclass
class Slide:
    bg: tuple
    shapes: list
    notes: str = ""
    kind: str = ""
    warnings: list = field(default_factory=list)


# ---------------------------------------------------------------- metin ölçümü
def _wrap_count(text: str, f, max_px: float) -> tuple[int, float]:
    """(satır sayısı, en geniş satır px). Tek kelime sığmıyorsa geniş satır max_px'i aşar."""
    lines, widest = 0, 0.0
    for chunk in text.split("\n"):
        words, cur = chunk.split(" "), ""
        n = 0
        for w in words:
            t = (cur + " " + w).strip()
            if f.getlength(t) <= max_px or not cur:
                cur = t
            else:
                widest = max(widest, f.getlength(cur))
                n += 1
                cur = w
        widest = max(widest, f.getlength(cur))
        lines += n + 1
    return lines, widest


def line_k(f, size_pt: float, px_per_pt: float = PX) -> float:
    """Satır yüksekliği / punto: fontun kendi ölçüsünden (Calibri ~1,23, Georgia ~1,28), en az 1,17."""
    a, d = f.getmetrics()
    return max(1.17, (a + d) / (size_pt * px_per_pt)) * 1.03


def measure(tb: TextBox, size: float):
    """Kutunun bu puntoda kapladığı yükseklik (inç), satır sayısı, taşma (genişlik)."""
    total_pt, lines, too_wide = 0.0, 0, False
    w_pt = tb.w * 72 * 0.95                     # iç kenar + güvenlik payı
    for i, p in enumerate(tb.paras):
        s = size * p.rel
        bold = all(r.bold for r in p.runs) if p.runs else False
        f = metric_font(tb.face, bold, s, PX)
        indent = (s * 1.25) if p.bullet else 0
        avail = (w_pt - indent) * PX
        n, widest = _wrap_count(p.text, f, avail)
        if widest > avail * 1.001:
            too_wide = True
        lines += n
        total_pt += n * s * line_k(f, s) * tb.spacing
        if i + 1 < len(tb.paras):
            total_pt += s * p.space_after
    return total_pt / 72, lines, too_wide


def fit(tb: TextBox) -> TextBox:
    s = tb.max_size
    while s >= tb.min_size:
        hh, n, wide = measure(tb, s)
        if hh <= tb.h * 0.96 and not wide and (not tb.max_lines or n <= tb.max_lines):
            tb.size, tb.lines = s, n
            return tb
        s -= 0.5 if s <= 14 else 1
    tb.size = tb.min_size
    hh, tb.lines, _ = measure(tb, tb.min_size)
    tb.overflow = True
    return tb


def text_height(tb: TextBox) -> float:
    return measure(tb, tb.size or tb.max_size)[0]


# ---------------------------------------------------------------- yardımcılar
def _runs(s: str, t: dict, color=None) -> list:
    """'**kalın** normal' biçimini destekler; 'Terim: açıklama' ise terim kalın."""
    out = []
    parts = re.split(r"(\*\*[^*]+\*\*)", s)
    for p in parts:
        if not p:
            continue
        if p.startswith("**") and p.endswith("**"):
            out.append(Run(p[2:-2], True, color))
        else:
            out.append(Run(p, False, color))
    return out


def _item(it) -> tuple[str, str]:
    if isinstance(it, dict):
        return it.get("label", "") or "", it.get("text", "") or ""
    return "", str(it)


def _item_runs(it, t, color=None):
    label, text = _item(it)
    runs = []
    if label:
        runs.append(Run(label.rstrip(":") + ": ", True, t["title"] if t["name"] != "modern_koyu" else t["accent"]))
    runs += _runs(text, t, color)
    return runs


class Ctx:
    def __init__(self, deck: dict, t: dict, sources: dict, idx: int, n: int):
        self.deck, self.t, self.sources, self.idx, self.n = deck, t, sources, idx, n
        self.L = 1.05 if t.get("band") else 0.75
        self.R = SW - 0.75
        self.W = self.R - self.L
        self.kaynak = deck.get("kaynak_line", True)
        self.top = 1.72
        self.bottom = 6.38 if self.kaynak else 6.8


def chrome(c: Ctx, s: dict, shapes: list, title=True):
    t = c.t
    if t.get("band"):
        shapes.append(Box(0, 0, 0.32, SH, fill=t["band"], name="Şerit"))
        shapes.append(Box(0.32, 0, 0.06, SH, fill=t["accent2"], name="Şerit2"))
    if title and s.get("title"):
        tb = fit(TextBox(c.L, 0.42, c.W, 1.05, [Para([Run(s["title"], True)])], t["head_font"], t["title"],
                         t["title_size"], 22, valign="b", name="Başlık"))
        shapes.append(tb)
        if t.get("title_rule"):
            shapes.append(Line(c.L, 1.5, c.R, 1.5, t["line"], 1.25, "Başlık çizgisi"))
        elif t["name"] == "modern_koyu":
            shapes.append(Box(c.L, 1.52, 0.9, 0.06, fill=t["accent"], name="Vurgu çizgisi"))
        elif t["name"] == "renkli_lise":
            pal = t["palette"]
            for k in range(4):
                shapes.append(Box(c.L + k * 0.34, 1.52, 0.26, 0.07, fill=pal[k], radius=0.03, name="Renk çizgisi"))
    # alt bilgi: kaynak satırı + sayfa numarası (+ kurum)
    if c.kaynak and s.get("type") not in ("title", "sources", "section"):
        cites = cite_line(s, c.sources)
        if cites:
            shapes.append(fit(TextBox(c.L, 6.55, c.W - 0.9, 0.62, [Para(cites)], t["body_font"], t["muted"], 12, 9,
                                      valign="t", name="Kaynak")))
        elif s.get("type") not in ("agenda", "questions"):
            s.setdefault("_warn", []).append("kaynak satırı boş (sources alanı yok)")
    if s.get("type") != "title":
        shapes.append(fit(TextBox(SW - 1.25, 6.95, 0.75, 0.32, [Para([Run(str(c.idx + 1))], align="r")],
                                  t["body_font"], t["muted"], 11, 9, name="Sayfa no")))
        org = c.deck.get("org") or ""
        if t["name"] == "kurumsal_egitim" and org:
            shapes.append(fit(TextBox(c.L, 6.98, 6, 0.3, [Para([Run(org)])], t["body_font"], t["muted"], 10, 8,
                                      name="Kurum")))


def cite_line(s: dict, sources: dict) -> list:
    ids = s.get("sources", []) or []
    shorts = []
    for i in ids:
        src = sources.get(i)
        shorts.append(src.get("short") or src.get("title", i) if src else f"[{i}?]")
    runs = []
    if shorts:
        runs = [Run("Kaynak: " if len(shorts) == 1 else "Kaynaklar: ", True), Run("; ".join(shorts) + ".")]
    img = s.get("image")
    if isinstance(img, dict) and img.get("credit"):
        runs += [Run("  Görsel: ", True), Run(img["credit"])]
    return runs


def bullets_box(c: Ctx, items, x, y, w, h, numbered=False, max_size=28, min_size=15):
    t = c.t
    paras = [Para(_item_runs(it, t), "num" if numbered else "char", space_after=0.55) for it in items]
    return fit(TextBox(x, y, w, h, paras, t["body_font"], t["ink"], max_size, min_size, spacing=1.05,
                       bullet_char=t["bullet"], bullet_color=t["accent"], name="Maddeler"))


def _on(col):
    """Rozet rengi üstünde okunur metin rengi (açık renkte koyu, koyu renkte beyaz)."""
    lum = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
    return (40, 36, 60) if lum > 170 else (255, 255, 255)


def badge_rows(c: Ctx, items, x, y, w, h, max_size=27, min_size=15):
    """Numaralı rozet + metin satırları (renkli lise, modern koyu). Satırlar eşit yükseklikte."""
    t, shapes = c.t, []
    n = max(1, len(items))
    gap = 0.15
    bd = 0.6
    pad = 0.13
    tw = w - bd - 0.5 - 0.2
    size = max_size
    while True:
        tbs = [TextBox(x + bd + 0.45, 0, tw, 10, [Para(_item_runs(it, t))], t["body_font"], t["ink"], size, size,
                       valign="m", name=f"Madde {i + 1}") for i, it in enumerate(items)]
        for tb in tbs:
            tb.size = size
        row = max(max(text_height(tb) for tb in tbs) + 2 * pad, bd + 2 * 0.14)
        total = row * n + gap * (n - 1)
        if total <= h or size <= min_size:
            break
        size -= 1
    yy = y + max(0, (h - total) / 2) * 0.35
    pal = t["palette"]
    for i, tb in enumerate(tbs):
        col = pal[i % len(pal)]
        line = t["line"] if t["name"] == "renkli_lise" else None
        shapes.append(Box(x, yy, w, row, fill=t["card"], line=line, line_w=1, radius=t["radius"], name="Satır kutusu"))
        num = fit(TextBox(0, 0, bd, bd, [Para([Run(str(i + 1), True, _on(col))], align="c")], t["head_font"], _on(col),
                          20, 12, valign="m", name="Rozet no"))
        shapes.append(Box(x + 0.2, yy + (row - bd) / 2, bd, bd, fill=col, shape="oval", name=f"Rozet {i + 1}", text=num))
        tb.y, tb.h = yy + 0.05, row - 0.1
        shapes.append(tb)
        yy += row + gap
    return shapes, size


def place_image(path: Path, x, y, w, h):
    from PIL import Image
    with Image.open(path) as im:
        ar = im.width / im.height
    iw = min(w, h * ar)
    ih = iw / ar
    return Pic(str(path), x + (w - iw) / 2, y + (h - ih) / 2, iw, ih)


# ---------------------------------------------------------------- slayt tipleri
def s_title(c: Ctx, s: dict):
    t, sh = c.t, []
    d = c.deck
    style = t["cover_style"]
    tx = c.L
    tw = c.W
    if style == "band":
        sh.append(Box(0, 0, 4.1, SH, fill=t["band"], name="Kapak paneli"))
        sh.append(Box(4.1, 0, 0.09, SH, fill=t["accent2"], name="Kapak çizgisi"))
        label = d.get("org") or s.get("kicker") or d.get("kicker")
        if label:
            sh.append(fit(TextBox(0.55, 0.7, 3.2, 1.6, [Para([Run(label, True)])], t["head_font"], (255, 255, 255),
                                  22, 12, name="Kurum")))
            if not d.get("org"):
                s = dict(s, kicker="")
                d = dict(d, kicker="")
        tx, tw = 4.75, SW - 4.75 - 0.75
    elif style == "blobs":
        pal = t["palette"]
        sh.append(Box(10.2, -1.3, 4.4, 4.4, fill=t["soft"], shape="oval", name="Süs"))
        sh.append(Box(11.35, 0.55, 1.5, 1.5, fill=pal[0], shape="oval", name="Süs"))
        sh.append(Box(10.55, 2.35, 0.7, 0.7, fill=pal[1], shape="oval", name="Süs"))
        sh.append(Box(-0.9, 6.1, 2.6, 2.6, fill=pal[2], shape="oval", name="Süs"))
        sh.append(Box(1.95, 6.75, 0.45, 0.45, fill=pal[3], shape="oval", name="Süs"))
        tw = 9.0
    elif style == "accent_bar":
        sh.append(Box(c.L, 2.05, 0.14, 2.55, fill=t["accent"], name="Vurgu"))
        tx, tw = c.L + 0.45, c.W - 0.45
    kicker = s.get("kicker") or d.get("kicker")
    y = 1.85
    if kicker:
        sh.append(fit(TextBox(tx, y - 0.55, tw, 0.45, [Para([Run(kicker.upper(), True)])], t["body_font"],
                              t["accent2"] if style != "accent_bar" else t["accent"], 15, 11, name="Üst başlık")))
    title = s.get("title") or d.get("title", "")
    tb = fit(TextBox(tx, y, tw, 2.1, [Para([Run(title, True)])], t["head_font"], t["title"], 54, 28, valign="m",
                     name="Sunum başlığı"))
    sh.append(tb)
    y2 = y + 2.2
    sub = s.get("subtitle") or d.get("subtitle")
    if sub:
        sh.append(fit(TextBox(tx, y2, tw, 0.9, [Para([Run(sub)])], t["body_font"], t["muted"], 24, 14, name="Alt başlık")))
    if style == "rule":
        sh.append(Line(tx, y2 - 0.08, tx + 2.2, y2 - 0.08, t["accent2"], 3, "Kapak çizgisi"))
    meta = [x for x in (d.get("author") and f"Hazırlayan: {d['author']}", d.get("org") if style != "band" else None,
                        d.get("date")) if x]
    if meta:
        sh.append(fit(TextBox(tx, 5.75, tw, 0.8, [Para([Run(" · ".join(meta))])], t["body_font"], t["muted"], 18, 12,
                              name="Hazırlayan")))
    chrome(c, s, sh, title=False)
    return sh


def s_section(c: Ctx, s: dict):
    t, sh = c.t, []
    chrome(c, s, sh, title=False)
    num = s.get("number")
    if num:
        sh.append(fit(TextBox(c.L, 2.0, 3, 1.3, [Para([Run(str(num), True)])], t["head_font"], t["accent"], 72, 40,
                              name="Bölüm no")))
    sh.append(fit(TextBox(c.L, 3.25, c.W, 1.4, [Para([Run(s.get("title", ""), True)])], t["head_font"], t["title"], 44,
                          26, name="Bölüm başlığı")))
    if s.get("subtitle"):
        sh.append(fit(TextBox(c.L, 4.7, c.W, 0.8, [Para([Run(s["subtitle"])])], t["body_font"], t["muted"], 22, 14,
                              name="Bölüm alt başlığı")))
    return sh


def s_bullets(c: Ctx, s: dict, numbered=False):
    t, sh = c.t, []
    chrome(c, s, sh)
    items = s.get("bullets") or s.get("items") or []
    y0, h = c.top, c.bottom - c.top
    x, w = c.L, c.W
    img = s.get("image")
    if img:
        ip = Path(img["path"] if isinstance(img, dict) else img)
        if not ip.is_absolute():
            ip = Path(c.deck.get("_root", ".")) / ip
        if ip.is_file():
            iw = c.W * 0.4
            sh.append(place_image(ip, c.R - iw, y0, iw, h))
            w = c.W - iw - 0.4
        else:
            s.setdefault("_warn", []).append(f"görsel bulunamadı: {ip}")
    if s.get("lead"):
        lb = fit(TextBox(x, y0, w, 0.9, [Para(_runs(s["lead"], t))], t["body_font"], t["muted"], 20, 14, name="Giriş"))
        sh.append(lb)
        lh = text_height(lb) + 0.2
        y0, h = y0 + lh, h - lh
    if t["badges"] and not img and 2 <= len(items) <= 5:
        shapes, _ = badge_rows(c, items, x, y0, w, h)
        sh += shapes
    else:
        sh.append(bullets_box(c, items, x, y0, w, h, numbered))
    return sh


def s_two_col(c: Ctx, s: dict):
    t, sh = c.t, []
    chrome(c, s, sh)
    cols = s.get("columns") or [s.get("left", {}), s.get("right", {})]
    gap = 0.4
    cw = (c.W - gap) / 2
    h = c.bottom - c.top
    pal = t["palette"]
    heads, boxes = [], []
    for j, col in enumerate(cols[:2]):
        x = c.L + j * (cw + gap)
        heads.append(fit(TextBox(x + 0.35, c.top + 0.3, cw - 0.7, 0.75, [Para([Run(col.get("heading", ""), True)])],
                                 t["head_font"], t["title"] if t["name"] != "modern_koyu" else t["accent"], 26, 16,
                                 name="Sütun başlığı")))
        boxes.append(bullets_box(c, col.get("bullets", []), x + 0.35, c.top + 1.15, cw - 0.7, h - 1.4, max_size=26))
    size = min(b.size for b in boxes)
    for b in boxes:
        b.max_size = size
        fit(b)
    body_h = max(text_height(b) for b in boxes)
    box_h = min(h, 1.15 + body_h + 0.45)
    for j, (hb, b) in enumerate(zip(heads, boxes)):
        x = c.L + j * (cw + gap)
        fill = t["soft"] if t["name"] != "modern_koyu" else t["card"]
        sh.append(Box(x, c.top, cw, box_h, fill=fill, line=None, radius=t["radius"] or 0.0, name=f"Sütun {j + 1}"))
        sh.append(Box(x, c.top, cw, 0.09, fill=pal[j % len(pal)], name="Sütun çizgisi"))
        sh.append(hb)
        b.h = box_h - 1.15 - 0.2
        sh.append(b)
    return sh


def s_process(c: Ctx, s: dict):
    t, sh = c.t, []
    chrome(c, s, sh)
    steps = (s.get("steps") or [])[:5]
    n = max(1, len(steps))
    gap = 0.55
    bw = (c.W - gap * (n - 1)) / n
    top = c.top + 0.1
    note = s.get("note")
    avail = (c.bottom - top) - (0.75 if note else 0)
    pal = t["palette"]
    bd = 0.52
    k = 1.0
    while True:
        labels, texts = [], []
        for i, st in enumerate(steps):
            labels.append(TextBox(0, 0, bw - 0.3, 1.0, [Para([Run(st.get("label", ""), True)], align="c")],
                                  t["head_font"], t["title"] if t["name"] != "modern_koyu" else t["ink"], 26 * k, 14,
                                  valign="t", name="Adım adı"))
            texts.append(TextBox(0, 0, bw - 0.3, avail - 1.6, [Para(_runs(st.get("text", ""), t), align="c")],
                                 t["body_font"], t["ink"], 20 * k, 12, valign="t", name="Adım metni"))
        ls = min(fit(b_).size for b_ in labels) if labels else 20
        ts = min(fit(b_).size for b_ in texts) if texts else 16
        for b_ in labels:
            b_.max_size = ls
            fit(b_)
        for b_ in texts:
            b_.max_size = ts
            fit(b_)
        lab_h = max((text_height(b_) for b_ in labels), default=0.5) * 1.08 + 0.1
        txt_h = max((text_height(b_) for b_ in texts), default=0.5) * 1.08 + 0.15
        need = 0.22 + bd + 0.14 + lab_h + 0.08 + txt_h + 0.25
        if need <= avail or k < 0.6:
            break
        k -= 0.06
    box_h = min(avail, need)
    y = top + (avail - box_h) / 2
    for i, st in enumerate(steps):
        x = c.L + i * (bw + gap)
        col = pal[i % len(pal)]
        fill = t["card"] if t["name"] in ("modern_koyu", "renkli_lise") else t["soft"]
        sh.append(Box(x, y, bw, box_h, fill=fill, line=t["line"] if t["name"] != "modern_koyu" else None, line_w=1,
                      radius=t["radius"] or 0.0, name=f"Adım {i + 1}"))
        num = fit(TextBox(0, 0, bd, bd, [Para([Run(str(i + 1), True, _on(col))], align="c")],
                          t["head_font"], _on(col), 20, 12, valign="m", name="Adım no"))
        sh.append(Box(x + (bw - bd) / 2, y + 0.22, bd, bd, fill=col, shape="oval", name=f"Adım rozeti {i + 1}", text=num))
        lb = labels[i]
        lb.x, lb.y, lb.h = x + 0.15, y + 0.22 + bd + 0.14, lab_h
        sh.append(lb)
        tb = texts[i]
        tb.x, tb.y, tb.h = x + 0.15, lb.y + lab_h + 0.08, txt_h
        sh.append(tb)
        if i > 0:
            ax = x - gap + 0.1
            sh.append(Box(ax, y + box_h / 2 - 0.2, gap - 0.2, 0.4, fill=t["accent2"], shape="rarrow", name="Ok"))
    if note:
        sh.append(fit(TextBox(c.L, c.bottom - 0.68, c.W, 0.66, [Para(_runs(note, t), align="c")], t["body_font"],
                              t["muted"], 18, 12, valign="m", name="Not")))
    return sh


def s_compare(c: Ctx, s: dict):
    t, sh = c.t, []
    chrome(c, s, sh)
    cols = s.get("columns", [])
    rows = s.get("rows", [])
    data = [[s.get("corner", "")] + cols] + [[r.get("label", "")] + list(r.get("cells", []))[:len(cols)] for r in rows]
    nc = len(cols) + 1
    lab_w = min(3.0, c.W * 0.24)
    col_w = [lab_w] + [(c.W - lab_w) / max(1, len(cols))] * len(cols)
    h_avail = c.bottom - c.top
    size = 22
    while size >= 11:
        rh = _table_rows(data, col_w, t, size)
        if sum(rh) <= h_avail:
            break
        size -= 1
    rh = _table_rows(data, col_w, t, size)
    tb = Table(c.L, c.top, c.W, data, col_w, t["body_font"], size, t["ink"], t["accent"], t["on_accent"],
               t["soft"] if t["name"] != "modern_koyu" else t["card"], t["line"], rh)
    if sum(rh) > h_avail:
        s.setdefault("_warn", []).append("tablo sığmadı — hücre metinlerini kısalt")
    sh.append(tb)
    return sh


def _table_rows(data, col_w, t, size):
    out = []
    for i, row in enumerate(data):
        hmax = 0.0
        for j, cell in enumerate(row):
            tb = TextBox(0, 0, col_w[j] - 0.2, 10, [Para([Run(str(cell), i == 0 or j == 0)])], t["body_font"], t["ink"],
                         size, size)
            hmax = max(hmax, measure(tb, size)[0])
        out.append(hmax + 0.22)
    return out


def s_term(c: Ctx, s: dict):
    t, sh = c.t, []
    chrome(c, s, sh)
    x, w = c.L + 0.6, c.W - 1.2
    avail = c.bottom - c.top
    k = 1.0
    while True:
        parts = [fit(TextBox(x + 0.5, 0, w - 1.0, 1.3, [Para([Run(s.get("term", ""), True)])], t["head_font"],
                             t["accent"] if t["name"] == "modern_koyu" else t["title"], 56 * k, 30, name="Terim"))]
        if s.get("origin"):
            parts.append(fit(TextBox(x + 0.5, 0, w - 1.0, 0.6, [Para(_runs(s["origin"], t))], t["body_font"],
                                     t["muted"], 20 * k, 13, name="Köken")))
        parts.append(fit(TextBox(x + 0.5, 0, w - 1.0, 2.0, [Para(_runs(s.get("definition", ""), t))], t["body_font"],
                                 t["ink"], 30 * k, 16, name="Tanım")))
        if s.get("example"):
            parts.append(fit(TextBox(x + 0.5, 0, w - 1.0, 1.2, [Para([Run("Örnek: ", True)] + _runs(s["example"], t))],
                                     t["body_font"], t["muted"], 23 * k, 13, name="Örnek")))
        hs = [text_height(p) + 0.18 for p in parts]
        total = sum(hs) + 0.8
        if total <= avail or k < 0.6:
            break
        k -= 0.06
    y = c.top + max(0, (avail - total) / 2)
    sh.append(Box(x, y, w, total, fill=t["soft"] if t["name"] != "modern_koyu" else t["card"], radius=t["radius"],
                  name="Terim kartı"))
    sh.append(Box(x, y, 0.12, total, fill=t["accent2"], name="Terim çizgisi"))
    yy = y + 0.4
    for p, hh in zip(parts, hs):
        p.y, p.h = yy, hh
        sh.append(p)
        yy += hh
    return sh


def s_key_fact(c: Ctx, s: dict):
    t, sh = c.t, []
    chrome(c, s, sh)
    x, w = c.L + 0.6, c.W - 1.2
    stmt = s.get("statement", s.get("text", ""))
    col = t["title"] if t["name"] != "modern_koyu" else t["ink"]
    big = None
    if len(stmt) <= 70:            # kısa ifade (denklem, slogan): önce tek satır dene
        big = fit(TextBox(x, c.top + 0.3, w, 2.6, [Para(_runs(stmt, t), align="c")], t["head_font"], col, 44, 28,
                          valign="m", max_lines=1, name="Ana fikir"))
        if big.overflow:
            big = None
    if big is None:
        big = fit(TextBox(x, c.top + 0.3, w, 2.6, [Para(_runs(stmt, t), align="c")], t["head_font"], col, 40, 22,
                          valign="m", name="Ana fikir"))
    sh.append(big)
    sh.append(Box(SW / 2 - 0.6, c.top + 3.15, 1.2, 0.07, fill=t["accent2"], name="Ayraç"))
    if s.get("detail"):
        sh.append(fit(TextBox(x, c.top + 3.45, w, c.bottom - c.top - 3.5, [Para(_runs(s["detail"], t), align="c")],
                              t["body_font"], t["muted"], 24, 14, name="Açıklama")))
    return sh


def s_image(c: Ctx, s: dict):
    t, sh = c.t, []
    chrome(c, s, sh)
    img = s.get("image") or {}
    ip = Path(img.get("path", "") if isinstance(img, dict) else img)
    if not ip.is_absolute():
        ip = Path(c.deck.get("_root", ".")) / ip
    cap_h = 0.6 if s.get("caption") else 0
    if ip.is_file():
        sh.append(place_image(ip, c.L, c.top, c.W, c.bottom - c.top - cap_h))
    else:
        s.setdefault("_warn", []).append(f"görsel bulunamadı: {ip}")
    if s.get("caption"):
        sh.append(fit(TextBox(c.L, c.bottom - 0.55, c.W, 0.55, [Para(_runs(s["caption"], t), align="c")],
                              t["body_font"], t["muted"], 18, 12, name="Açıklama")))
    return sh


def s_sources(c: Ctx, s: dict):
    t, sh = c.t, []
    s = dict(s)
    s.setdefault("title", "Kaynakça")
    chrome(c, s, sh)
    paras = []
    for src in c.sources.values():
        if src.get("type") == "user_notes" and not src.get("in_bibliography", True):
            continue
        paras.append(Para([Run(apa(src))], space_after=0.5))
    sh.append(fit(TextBox(c.L, c.top, c.W, c.bottom - c.top + 0.4, paras, t["body_font"], t["ink"], 18, 9,
                          spacing=1.0, name="Kaynakça")))
    return sh


def apa(src: dict) -> str:
    if src.get("apa"):
        return src["apa"]
    who = src.get("author") or src.get("org") or ""
    year = src.get("year") or "t.y."
    title = src.get("title", "")
    pub = src.get("publisher") or src.get("site") or ""
    url = src.get("url") or ""
    acc = src.get("accessed")
    s = f"{who} ({year}). {title}."
    if pub and pub != who:
        s += f" {pub}."
    if url:
        s += f" {url}"
        if acc:
            s += f" (Erişim: {acc})"
    return " ".join(s.split())


BUILDERS = {"title": s_title, "section": s_section, "bullets": s_bullets, "summary": s_bullets,
            "agenda": lambda c, s: s_bullets(c, s, numbered=True), "questions": lambda c, s: s_bullets(c, s, numbered=True),
            "two_col": s_two_col, "process": s_process, "compare": s_compare, "term": s_term, "key_fact": s_key_fact,
            "image": s_image, "sources": s_sources}


def build(deck: dict, t: dict, sources: dict) -> list[Slide]:
    out = []
    slides = deck.get("slides", [])
    for i, s in enumerate(slides):
        s = dict(s)
        s["_warn"] = []
        kind = s.get("type", "bullets")
        if kind not in BUILDERS:
            raise SystemExit(f"slayt {i + 1}: bilinmeyen tip '{kind}' ({', '.join(BUILDERS)})")
        c = Ctx(deck, t, sources, i, len(slides))
        shapes = BUILDERS[kind](c, s)
        warns = list(s["_warn"])
        for sh in shapes:
            tb = sh.text if isinstance(sh, Box) else sh
            if isinstance(tb, TextBox) and tb.overflow:
                warns.append(f"'{tb.name}' en küçük puntoda bile taşıyor — metni kısalt")
        out.append(Slide(t["bg"], shapes, s.get("notes", ""), kind, warns))
    return out
