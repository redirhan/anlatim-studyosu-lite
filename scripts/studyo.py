#!/usr/bin/env python3
"""Anlatım Stüdyosu — komut satırı.

  python scripts/studyo.py doctor                     bağımlılık kontrolü (python, paketler, fontlar, ffmpeg, LibreOffice …)
  python scripts/studyo.py templates                  şablonları listele
  python scripts/studyo.py new <proje> --topic "…"    proje klasörü: brief.yaml, notes/, research/sources.json
  python scripts/studyo.py intake <proje>             notes/ → work/notes.txt (kendi notların / kaynakların)
  python scripts/studyo.py check <proje>              deck.json + sources.json doğrula
  python scripts/studyo.py build <proje>              check → PPTX → konuşmacı notları → özet PDF → önizleme
     (tek tek: deck | notes | summary | preview)
  --- Pro ---
  python scripts/studyo.py quiz <proje>               10 soruluk test PDF (+ cevap anahtarı)
  python scripts/studyo.py video-prompt <proje>       video sahne planı istemi (work/video_plan_prompt.md)
  python scripts/studyo.py video-check <proje>        video_plan.json doğrula
  python scripts/studyo.py voice <proje> [--engine ema|gemini|silent]
  python scripts/studyo.py stills <proje>             render öncesi temas sayfası
  python scripts/studyo.py render <proje>             anlatımlı 16:9 video (+ .srt)
  python scripts/studyo.py short <proje>              9:16 kısa kesit (sosyal medya)
  python scripts/studyo.py qa <proje>                 video temas sayfası + video_report.json
  python scripts/studyo.py video <proje>              video-check → voice → render → short → quiz → qa
  python scripts/studyo.py respell "metin"            telaffuz sözlüğü testi
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from studyo import VERSION  # noqa: E402
from studyo import config as CFG  # noqa: E402

RESPONSIBLE = ("Sorumlu kullanım: not için teslim edilecek işin içeriğini kendin hazırla; bu araç öğrenme, "
               "ders materyali ve tasarım içindir.")


def _proj(p) -> Path:
    path = Path(p).expanduser()
    if not path.is_absolute() and not path.exists():
        alt = CFG.expand(CFG.load_config()["projects_dir"]) / p
        if alt.exists():
            path = alt
    return path.resolve()


# ---------------------------------------------------------------- doctor
def doctor(_a):
    import importlib
    import platform
    import shutil
    ok = True
    print(f"Anlatım Stüdyosu {VERSION} · sürüm: {CFG.edition()} · Python {platform.python_version()} · {platform.system()}")
    if sys.version_info < (3, 10):
        print("  HATA  Python 3.10+ gerekli")
        ok = False
    req = {"pptx": "python-pptx", "reportlab": "reportlab", "PIL": "Pillow", "yaml": "PyYAML"}
    opt = {"pypdf": "pypdf (PDF notları okumak)", "docx": "python-docx (Word notları okumak)"}
    if CFG.pro_available():
        req["numpy"] = "numpy"
    for mod, name in req.items():
        try:
            importlib.import_module(mod)
            print(f"  ok    {name}")
        except ImportError:
            print(f"  HATA  {name} yok → pip install -r requirements.txt")
            ok = False
    for mod, name in opt.items():
        try:
            importlib.import_module(mod)
            print(f"  ok    {name}")
        except ImportError:
            print(f"  uyarı {name} yok (isteğe bağlı)")
    from studyo import fonts
    miss = fonts.missing()
    print("  ok    fontlar (fonts/, OFL)" if not miss else f"  HATA  font eksik: {miss}")
    ok &= not miss
    from studyo.preview import find_soffice
    so = find_soffice()
    print(f"  ok    LibreOffice ({so}) — gerçek slayt önizlemesi" if so else
          "  bilgi LibreOffice yok — önizleme PIL ile çizilir (yaklaşık görünüm)")
    if so:
        print("  ok    pdftoppm" if shutil.which("pdftoppm") else "  uyarı pdftoppm yok (poppler) — pymupdf denenir")
    ff = shutil.which("ffmpeg")
    if CFG.pro_available():
        print(f"  ok    ffmpeg ({ff})" if ff else "  HATA  ffmpeg yok (video için gerekli) → brew/apt install ffmpeg")
        ok &= bool(ff)
        from studyo.pro import doctor as pdoc
        ok &= pdoc.report()
    else:
        print("  bilgi Lite sürüm: video, test ve dikey kısa Pro'da")
    cp = CFG.config_path()
    print(f"  bilgi ayarlar: {cp if cp else 'varsayılanlar (config.example.yaml → config.yaml)'}")
    print("TAMAM" if ok else "EKSİK VAR — yukarıdaki HATA satırlarını düzelt")
    return 0 if ok else 1


def templates(_a):
    from studyo.templates import TEMPLATES
    for k, t in TEMPLATES.items():
        print(f"{k:16s} {t['label']:16s} {t['desc']}")


def new(a):
    from studyo.project import new_project
    p = Path(a.project).expanduser()
    if not p.is_absolute() and len(p.parts) == 1:
        p = CFG.expand(CFG.load_config()["projects_dir"]) / p
    new_project(p.resolve(), a.topic or "")
    print(p.resolve())
    print(RESPONSIBLE)


def intake(a):
    from studyo.intake import extract
    p = _proj(a.project)
    idx = extract(p)
    if not idx:
        print("notes/ boş — sadece araştırma ile ilerlenecek")
    for f, v in idx.items():
        print(f"  {f}: {v['chars']} karakter ({v['method']}) {v['warning']}")
    print(" ", p / "work" / "notes.txt")


def _load(p):
    from studyo import project as P, templates as T
    deck = P.load_deck(p)
    t = T.get(getattr(_load, "template", None) or deck.get("template"))
    return deck, t, P.load_sources(p), P.load_brief(p)


def check(a, quiet=False):
    from studyo import check as CH, project as P
    p = _proj(a.project)
    deck, t, sources, brief = _load(p)
    notes = (p / "work" / "notes.txt").read_text(encoding="utf-8") if (p / "work" / "notes.txt").is_file() else ""
    res = CH.validate(deck, sources, brief, P.corpus(p), notes)
    from studyo import layout
    slides = layout.build(deck, t, sources)
    for i, sl in enumerate(slides, 1):
        for w in sl.warnings:
            res["warnings"].append(f"slayt {i} ({sl.kind}): {w}")
    (p / "work").mkdir(exist_ok=True)
    (p / "work" / "check.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    if not quiet or not res["ok"]:
        print(f"{res['slides']} slayt · kullanılan kaynaklar: {', '.join(res['sources_used']) or '—'} · şablon: {t['name']}")
        for e in res["errors"]:
            print("  HATA ", e)
        for w in res["warnings"]:
            print("  uyarı", w)
        print("GEÇERLİ" if res["ok"] else "GEÇERSİZ — düzelt (ya da --force)")
    return res, slides, deck, t, sources, brief


def deck_cmd(a):
    from studyo import pptx_out
    from studyo.project import next_version, slug
    p = _proj(a.project)
    res, slides, deck, t, sources, brief = check(a, quiet=True)
    if not res["ok"] and not a.force:
        sys.exit(1)
    out, v = next_version(p / "out", slug(deck.get("title", "sunum")), ".pptx")
    pptx_out.write(slides, out, deck)
    print("  PPTX:", out)
    return out, slides, deck, t, sources, brief, v


def notes_cmd(a, deck=None, sources=None):
    from studyo import notes
    from studyo.project import next_version, slug
    p = _proj(a.project)
    if deck is None:
        deck, _, sources, _ = _load(p)
    out, _ = next_version(p / "out", slug(deck.get("title", "sunum")) + "_notlar", ".md")
    notes.write_md(deck, sources, out)
    print("  notlar:", out)
    return out


def summary_cmd(a, deck=None, t=None, sources=None, brief=None):
    from studyo import summary_pdf
    from studyo.project import next_version, slug
    p = _proj(a.project)
    if deck is None:
        deck, t, sources, brief = _load(p)
    out, _ = next_version(p / "out", slug(deck.get("title", "sunum")) + "_ozet", ".pdf")
    r = summary_pdf.build(deck, t, sources, out, RESPONSIBLE)
    print(f"  özet PDF: {out} ({r['pages']} sayfa)")
    return out


def preview_cmd(a, pptx=None, slides=None, v=None):
    from studyo import layout, preview
    from studyo.project import latest, slug
    p = _proj(a.project)
    deck, t, sources, _ = _load(p)
    if pptx is None:
        pptx = latest(p / "out", slug(deck.get("title", "sunum")), ".pptx")
        if not pptx:
            raise SystemExit("önce: deck")
        v = pptx.stem.rsplit("_v", 1)[-1]
        slides = layout.build(deck, t, sources)
    mode = a.preview or CFG.load_config().get("preview", "auto")
    r = preview.preview(pptx, slides, p / "out" / f"preview_v{v}", mode)
    print(f"  önizleme ({r['engine']}): {r['contact_sheet']}")
    return r


def build(a):
    t0 = time.time()
    out, slides, deck, t, sources, brief, v = deck_cmd(a)
    notes_cmd(a, deck, sources)
    summary_cmd(a, deck, t, sources, brief)
    if not a.no_preview:
        preview_cmd(a, out, slides, v)
    print(f"bitti ({time.time() - t0:.0f} sn). {RESPONSIBLE}")


# ---------------------------------------------------------------- Pro
def pro(name):
    def run(a):
        CFG.require_pro(name)
        from studyo.pro import cli
        return cli.run(name, a, _proj(a.project) if getattr(a, "project", None) else None)
    return run


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=doctor)
    sub.add_parser("templates").set_defaults(fn=templates)
    n = sub.add_parser("new")
    n.add_argument("project")
    n.add_argument("--topic", default="")
    n.set_defaults(fn=new)
    for name, fn in (("intake", intake), ("check", lambda a: sys.exit(0 if check(a)[0]["ok"] else 1)),
                     ("deck", deck_cmd), ("notes", notes_cmd), ("summary", summary_cmd), ("preview", preview_cmd),
                     ("build", build)):
        s = sub.add_parser(name)
        s.add_argument("project")
        s.add_argument("--template", default=None, help="şablonu bu sefer için değiştir")
        s.add_argument("--force", action="store_true", help="doğrulama hatası olsa da üret")
        s.add_argument("--preview", default=None, choices=["auto", "libreoffice", "pil"])
        s.add_argument("--no-preview", action="store_true")
        s.set_defaults(fn=fn)
    for name in ("quiz", "video-prompt", "video-check", "voice", "rescore", "stills", "render", "remix", "short",
                 "qa", "video"):
        s = sub.add_parser(name)
        s.add_argument("project")
        s.add_argument("--engine", default=None, help="ema | gemini | silent")
        s.add_argument("--resume", action="store_true", help="voice: sadece işaretli satırları yeniden üret")
        s.add_argument("--force", action="store_true")
        s.add_argument("--template", default=None)
        s.add_argument("--seconds", type=float, default=None, help="short: hedef süre (varsayılan 45)")
        s.set_defaults(fn=pro(name))
    r = sub.add_parser("respell")
    r.add_argument("text")
    r.set_defaults(fn=pro("respell"), project=None)
    a = ap.parse_args()
    if getattr(a, "template", None):
        _load.template = a.template
    rc = a.fn(a)
    sys.exit(rc if isinstance(rc, int) else 0)


if __name__ == "__main__":
    main()
