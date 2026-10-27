#!/usr/bin/env python3
"""Geliştirici aracı: fonts/src/*-VF.ttf değişken fontlarından sabit (static) kesimler üretir -> fonts/.

Paket kullanıcısının bunu çalıştırması gerekmez; fonts/ klasörü hazır gelir. Kaynak: github.com/google/fonts
(OFL-1.1, lisans metinleri fonts/ altında). Gerekli: pip install fonttools
"""
from pathlib import Path
import shutil
import urllib.request
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parents[1] / "fonts"
SRC = ROOT / "src"
JOBS = {
    "Outfit-VF.ttf": [("Outfit", w) for w in ("Regular", "Medium", "SemiBold", "Bold")],
    "Bricolage-VF.ttf": [("BricolageGrotesque", w) for w in ("SemiBold", "Bold", "ExtraBold")],
    "Arimo-VF.ttf": [("Arimo", w) for w in ("Regular", "Bold")],
    "Gelasio-VF.ttf": [("Gelasio", w) for w in ("Regular", "Bold")],
}
G = "https://github.com/google/fonts/raw/main/ofl/"
DOWNLOADS = {
    "Outfit-VF.ttf": "outfit/Outfit%5Bwght%5D.ttf", "OFL-Outfit.txt": "outfit/OFL.txt",
    "Bricolage-VF.ttf": "bricolagegrotesque/BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf",
    "OFL-BricolageGrotesque.txt": "bricolagegrotesque/OFL.txt",
    "Carlito-Regular.ttf": "carlito/Carlito-Regular.ttf", "Carlito-Bold.ttf": "carlito/Carlito-Bold.ttf",
    "OFL-Carlito.txt": "carlito/OFL.txt",
    "Arimo-VF.ttf": "arimo/Arimo%5Bwght%5D.ttf", "OFL-Arimo.txt": "arimo/OFL.txt",
    "Gelasio-VF.ttf": "gelasio/Gelasio%5Bwght%5D.ttf", "OFL-Gelasio.txt": "gelasio/OFL.txt",
}
SRC.mkdir(parents=True, exist_ok=True)
for name, rel in DOWNLOADS.items():
    if not (SRC / name).is_file():
        urllib.request.urlretrieve(G + rel, SRC / name)
WGHT = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700, "ExtraBold": 800}

for src, outs in JOBS.items():
    for fam, w in outs:
        vf = TTFont(str(SRC / src))
        axes = {a.axisTag: a.defaultValue for a in vf["fvar"].axes}
        axes["wght"] = WGHT[w]
        st = instancer.instantiateVariableFont(vf, axes, updateFontNames=False)
        out = ROOT / f"{fam}-{w}.ttf"
        st.save(str(out))
        print(out.name, out.stat().st_size // 1024, "KB")
for f in ("Carlito-Regular.ttf", "Carlito-Bold.ttf"):
    shutil.copy(SRC / f, ROOT / f)
for lic in SRC.glob("OFL-*.txt"):
    shutil.copy(lic, ROOT / lic.name)
