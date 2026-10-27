"""Slayt önizlemesi: LibreOffice varsa PPTX → PDF → PNG (gerçek görünüm); yoksa aynı şekil listesinden PIL çizimi.

Chrome/Chromium kullanılmaz. Çıktı: out/preview_vN/slide_01.png … + contact_sheet.png
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from .config import expand, load_config
from .fonts import font, metric_font
from .layout import SH, SW, Box, Line, Pic, Table, TextBox, line_k

DPI = 96          # PIL önizleme: 1280 × 720


def find_soffice() -> str | None:
    cfg = load_config()
    if cfg.get("soffice"):
        p = expand(cfg["soffice"])
        return str(p) if p and p.exists() else None
    for name in ("soffice", "libreoffice"):
        w = shutil.which(name)
        if w:
            return w
    mac = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    return str(mac) if mac.exists() else None


def via_libreoffice(pptx: Path, out_dir: Path) -> list[Path]:
    so = find_soffice()
    if not so:
        raise RuntimeError("LibreOffice yok")
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="anlatim_lo_") as tmp:
        prof = Path(tmp) / "profile"
        r = subprocess.run([so, f"-env:UserInstallation=file://{prof}", "--headless", "--convert-to", "pdf",
                            "--outdir", tmp, str(pptx)], capture_output=True, text=True, timeout=300)
        pdf = Path(tmp) / (pptx.stem + ".pdf")
        if not pdf.is_file():
            raise RuntimeError("LibreOffice PDF üretmedi: " + (r.stderr or r.stdout)[-400:])
        shutil.copy(pdf, out_dir / "slides.pdf")
        if shutil.which("pdftoppm"):
            subprocess.run(["pdftoppm", "-png", "-scale-to", "1280", str(pdf), str(out_dir / "slide")], check=True)
            files = sorted(out_dir.glob("slide-*.png"))
            outs = []
            for i, f in enumerate(files, 1):
                dst = out_dir / f"slide_{i:02d}.png"
                f.rename(dst)
                outs.append(dst)
            return outs
        try:
            import fitz  # pymupdf, isteğe bağlı
        except ImportError:
            raise RuntimeError("PDF → PNG için pdftoppm (poppler) ya da pymupdf gerekli")
        doc = fitz.open(str(pdf))
        outs = []
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(dpi=96)
            dst = out_dir / f"slide_{i:02d}.png"
            pix.save(str(dst))
            outs.append(dst)
        return outs


# ---------------------------------------------------------------- PIL çizimi
def _px(v):
    return v * DPI


def _wrap(text, f, max_px):
    lines = []
    for chunk in text.split("\n"):
        cur = ""
        for w in chunk.split(" "):
            t = (cur + " " + w).strip()
            if f.getlength(t) <= max_px or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def draw_text(d: ImageDraw.ImageDraw, tb: TextBox, ox=0.0, oy=0.0):
    size = tb.size or tb.max_size
    scale = DPI / 72
    x0, y0 = _px(tb.x + ox) + 4, _px(tb.y + oy) + 2
    w = _px(tb.w) - 8
    blocks = []
    num = 0
    for p in tb.paras:
        s = size * p.rel
        bold = bool(p.runs) and all(r.bold for r in p.runs)
        f = metric_font(tb.face, bold, s, scale)
        ind = s * 1.25 * scale if p.bullet else 0
        lines = _wrap(p.text, f, w - ind)
        blocks.append((p, f, s, ind, lines))
    total = sum(len(b[4]) * b[2] * line_k(b[1], b[2], scale) * tb.spacing * scale for b in blocks) + \
        sum(b[2] * b[0].space_after * scale for b in blocks[:-1])
    h = _px(tb.h) - 4
    y = y0 + {"t": 0, "m": max(0, (h - total) / 2), "b": max(0, h - total)}[tb.valign]
    for p, f, s, ind, lines in blocks:
        lh = s * line_k(f, s, scale) * tb.spacing * scale
        col = (p.runs[0].color if p.runs and p.runs[0].color else None) or tb.color
        if p.bullet:
            num += 1
            mark = f"{num}." if p.bullet == "num" else tb.bullet_char
            fm = metric_font("Arial", p.bullet == "num", s * (1 if p.bullet == "num" else 0.8), scale)
            d.text((x0, y + lh * 0.12), mark, font=fm, fill=tb.bullet_color or col)
        for ln in lines:
            lw = f.getlength(ln)
            xx = x0 + ind + {"l": 0, "c": (w - ind - lw) / 2, "r": (w - ind - lw)}[p.align]
            # karışık kalın/normal: ilk run kalınsa ve metin onunla başlıyorsa iki parça çiz
            if len(p.runs) > 1 and p.runs[0].bold and not all(r.bold for r in p.runs) and ln.startswith(p.runs[0].text.strip()[:3]):
                head = p.runs[0].text
                fb = metric_font(tb.face, True, s, scale)
                cut = head if ln.startswith(head) else head.strip()
                d.text((xx, y), cut, font=fb, fill=p.runs[0].color or col)
                rest = ln[len(cut):]
                rc = p.runs[1].color or tb.color
                d.text((xx + fb.getlength(cut), y), rest, font=f, fill=rc)
            else:
                d.text((xx, y), ln, font=f, fill=col)
            y += lh
        y += s * p.space_after * scale


def render_pil(slide, path: Path):
    im = Image.new("RGB", (int(_px(SW)), int(_px(SH))), tuple(slide.bg))
    d = ImageDraw.Draw(im)
    for sh in slide.shapes:
        if isinstance(sh, Box):
            box = [_px(sh.x), _px(sh.y), _px(sh.x + sh.w), _px(sh.y + sh.h)]
            fill = tuple(sh.fill) if sh.fill else None
            out = tuple(sh.line) if sh.line else None
            if sh.shape == "oval":
                d.ellipse(box, fill=fill, outline=out)
            elif sh.shape == "rarrow":
                x0, y0, x1, y1 = box
                ym = (y0 + y1) / 2
                hx = x1 - (y1 - y0) * 0.7
                d.polygon([(x0, y0 + (y1 - y0) * 0.25), (hx, y0 + (y1 - y0) * 0.25), (hx, y0), (x1, ym), (hx, y1),
                           (hx, y1 - (y1 - y0) * 0.25), (x0, y1 - (y1 - y0) * 0.25)], fill=fill)
            elif sh.radius > 0:
                d.rounded_rectangle(box, radius=_px(sh.radius), fill=fill, outline=out, width=max(1, int(sh.line_w)))
            else:
                d.rectangle(box, fill=fill, outline=out)
            if sh.text:
                t = sh.text
                t.x, t.y, t.w, t.h = sh.x, sh.y, sh.w, sh.h
                draw_text(d, t)
        elif isinstance(sh, TextBox):
            draw_text(d, sh)
        elif isinstance(sh, Line):
            d.line([_px(sh.x1), _px(sh.y1), _px(sh.x2), _px(sh.y2)], fill=tuple(sh.color),
                   width=max(1, int(sh.width * DPI / 72)))
        elif isinstance(sh, Pic):
            with Image.open(sh.path) as p:
                p = p.convert("RGBA").resize((int(_px(sh.w)), int(_px(sh.h))), Image.LANCZOS)
                im.paste(p, (int(_px(sh.x)), int(_px(sh.y))), p)
        elif isinstance(sh, Table):
            y = sh.y
            for i, row in enumerate(sh.rows):
                x = sh.x
                for j, cw in enumerate(sh.col_w):
                    head, lab = i == 0, j == 0 and i > 0
                    fill = sh.head_fill if head else sh.label_fill if lab else ((255, 255, 255) if sum(sh.ink) < 384
                                                                                 else (28, 37, 56))
                    d.rectangle([_px(x), _px(y), _px(x + cw), _px(y + sh.row_h[i])], fill=tuple(fill),
                                outline=tuple(sh.line))
                    from .layout import Para, Run
                    tb = TextBox(x + 0.06, y, cw - 0.12, sh.row_h[i], [Para([Run(str(row[j]) if j < len(row) else "",
                                                                                head or lab)])],
                                 sh.face, sh.head_ink if head else sh.ink, sh.size, sh.size, valign="m")
                    tb.size = sh.size
                    draw_text(d, tb)
                    x += cw
                y += sh.row_h[i]
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return path


def via_pil(slides, out_dir: Path) -> list[Path]:
    return [render_pil(s, out_dir / f"slide_{i:02d}.png") for i, s in enumerate(slides, 1)]


def contact_sheet(pngs: list[Path], out: Path, title: str = "", cols: int = 3):
    tw, th, pad, lab = 560, 315, 18, 30
    rows = (len(pngs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + lab + pad) + pad + 56), (244, 244, 246))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 14), title, font=font(28, "bricolage", "Bold"), fill=(30, 30, 40))
    for i, p in enumerate(pngs):
        x = pad + (i % cols) * (tw + pad)
        y = 56 + pad + (i // cols) * (th + lab + pad)
        with Image.open(p) as im:
            sheet.paste(im.convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + lab))
        d.rectangle([x - 1, y + lab - 1, x + tw, y + lab + th], outline=(200, 200, 210))
        d.text((x, y + 2), f"{i + 1}", font=font(20, "outfit", "SemiBold"), fill=(90, 90, 110))
    sheet.save(out)
    return out


def preview(pptx: Path, slides, out_dir: Path, mode: str = "auto"):
    used = "pil"
    pngs = []
    if mode in ("auto", "libreoffice") and find_soffice():
        try:
            pngs = via_libreoffice(pptx, out_dir)
            used = "libreoffice"
        except Exception as e:
            if mode == "libreoffice":
                raise
            print("  LibreOffice önizlemesi olmadı, PIL'e geçiliyor:", e)
    if not pngs:
        pngs = via_pil(slides, out_dir)
    sheet = contact_sheet(pngs, out_dir / "contact_sheet.png", pptx.stem)
    return {"engine": used, "slides": [str(p) for p in pngs], "contact_sheet": str(sheet)}
