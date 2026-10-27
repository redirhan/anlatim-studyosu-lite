"""deck.json + research/sources.json doğrulayıcı. Hata (ERROR) varsa deck üretilmez (--force hariç).

Kurallar:
- Sadece açılmış kaynaklar: her kaynakta "opened": true, erişim tarihi ve sayfadan BİREBİR kopyalanmış en az bir
  alıntı ("excerpts") olmalı. Alıntısız kaynak = okunmamış kaynak = kullanılamaz.
- Slaytlardaki kaynak kimlikleri sources.json'da olmalı; içerik slaytlarının kaynağı olmalı.
- Slayttaki her sayı kaynak alıntılarında ya da kullanıcı notlarında geçmeli (yoksa uyarı: doğrula ya da sil).
- "tasarim" modunda dış kaynak eklenmez; her madde kullanıcının notlarına dayanmalı.
"""
from __future__ import annotations

import re

from . import layout
from .textnorm import int_to_words, tr_lower

CONTENT = {"bullets", "two_col", "process", "compare", "term", "key_fact", "image", "summary"}
STOP = set("""ve ile bir bu şu o da de ki mi mı mu mü için gibi kadar daha çok en ise ama fakat veya ya hem ne
nasıl neden niçin olan olarak olur olup oldu olduğu olduğunu olması sonra önce şimdi peki yani bunu bunun buna
şunu onun ona onu onlar biz siz ben sen her hiç bazı birçok çünkü eğer zaman yine artık sadece bile böylece
ayrıca aslında örneğin özellikle yeni ilk iki üç dört beş tek kendi kendini olan olarak sırasında içinde
arasında tarafından""".split())
EN_NUM = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
          10: "ten", 12: "twelve", 20: "twenty", 100: "hundred"}


def norm(s: str) -> str:
    s = tr_lower(s or "")
    s = re.sub(r"[\"“”'’`«»]", "", s)
    return " ".join(re.sub(r"[^0-9a-zçğıöşüâîû]+", " ", s).split())


def slide_texts(s: dict) -> list[str]:
    out = []
    for k in ("title", "subtitle", "lead", "statement", "detail", "term", "definition", "example", "origin", "note",
              "caption"):
        if s.get(k):
            out.append(str(s[k]))
    for it in s.get("bullets", []) or s.get("items", []) or []:
        out.append(" ".join(layout._item(it)))
    for col in s.get("columns", []) if s.get("type") == "two_col" else []:
        out.append(col.get("heading", ""))
        out += [" ".join(layout._item(b)) for b in col.get("bullets", [])]
    for st in s.get("steps", []) or []:
        out += [st.get("label", ""), st.get("text", "")]
    if s.get("type") == "compare":
        out += list(s.get("columns", []))
        for r in s.get("rows", []):
            out.append(r.get("label", ""))
            out += list(r.get("cells", []))
    return [x for x in out if x]


def number_found(num: str, corpus_raw: str, corpus_n: str) -> bool:
    if re.search(rf"(?<!\d){re.escape(num)}(?!\d)", corpus_raw):
        return True
    try:
        n = int(num.replace(".", ""))
    except ValueError:
        return False
    words = [norm(int_to_words(n))]
    if n in EN_NUM:
        words.append(EN_NUM[n])
    return any(re.search(rf"\b{re.escape(w)}\b", corpus_n) for w in words)


TR_HINT = set("ve bir bu için ile da de olarak olan gibi daha çok en ise ama veya ki".split())


def turkish_share(text: str) -> float:
    """Metnin kabaca ne kadarı Türkçe: Türkçe harf ya da sık Türkçe sözcük içeren kelimelerin payı (satır bazında)."""
    lines = [ln for ln in text.splitlines() if len(ln.split()) >= 4]
    if not lines:
        return 1.0
    tr = 0
    for ln in lines:
        ws = norm(ln).split()
        hits = sum(1 for w in ws if re.search(r"[çğışöü]", w) or w in TR_HINT)
        tr += hits / max(1, len(ws)) >= 0.2
    return tr / len(lines)


def validate(deck: dict, sources: dict, brief: dict, corpus_raw: str, notes_raw: str) -> dict:
    errors, warns = [], []
    purpose = (brief.get("purpose") or "ders_materyali").strip()
    notes_only = bool(brief.get("use_my_notes_only")) or purpose == "tasarim"
    # ---- kaynaklar
    for sid, s in sources.items():
        kind = s.get("type", "web")
        if kind == "user_notes":
            if not notes_raw.strip():
                errors.append(f"kaynak {sid}: user_notes ama notes/ klasöründen metin çıkmadı (önce: intake)")
            continue
        if notes_only:
            errors.append(f"kaynak {sid}: '{purpose}' modunda / use_my_notes_only'de dış kaynak eklenmez")
        if s.get("opened") is not True:
            errors.append(f"kaynak {sid}: \"opened\": true değil — yalnız gerçekten açıp okuduğun kaynakları yaz")
        ex = [e if isinstance(e, str) else e.get("text", "") for e in s.get("excerpts", [])]
        if not ex or not any(len(e.split()) >= 5 for e in ex):
            errors.append(f"kaynak {sid}: sayfadan birebir alıntı (excerpts, ≥5 kelime) yok")
        if not s.get("url") and kind == "web":
            errors.append(f"kaynak {sid}: url yok")
        if not s.get("accessed") and kind == "web":
            warns.append(f"kaynak {sid}: erişim tarihi (accessed) yok")
        if not s.get("short"):
            warns.append(f"kaynak {sid}: kısa künye (short) yok — Kaynak satırında başlık kullanılacak")
    used = set()
    # ---- slaytlar
    slides = deck.get("slides", [])
    if not slides:
        errors.append("slayt yok")
    want = brief.get("slide_count")
    if want and abs(len(slides) - int(want)) > 2:
        warns.append(f"slayt sayısı {len(slides)} (brief: {want})")
    if slides and slides[0].get("type") != "title":
        warns.append("ilk slayt kapak (type: title) değil")
    if deck.get("kaynak_line", True) and sources and not any(s.get("type") == "sources" for s in slides):
        warns.append("Kaynakça slaytı yok (type: sources) — sona ekle")
    c_raw = corpus_raw
    c_n = norm(corpus_raw)
    stems = {w[:5] for w in c_n.split() if len(w) >= 4}
    notes_stems = {w[:5] for w in norm(notes_raw).split() if len(w) >= 4}
    tr_share = turkish_share(corpus_raw)
    lexical = notes_only or tr_share >= 0.5
    if not lexical and corpus_raw.strip():
        warns.append(f"bilgi: kaynak alıntılarının çoğu Türkçe değil (Türkçe payı %{int(tr_share * 100)}) — kelime "
                     "dayanak kontrolü atlandı; sayı kontrolü yapıldı. Her maddenin bir alıntıya dayandığını sen denetle.")
    for i, s in enumerate(slides, 1):
        kind = s.get("type", "bullets")
        tag = f"slayt {i} ({kind})"
        if kind not in layout.BUILDERS:
            errors.append(f"{tag}: bilinmeyen tip ({', '.join(layout.BUILDERS)})")
            continue
        ids = s.get("sources", []) or []
        for sid in ids:
            used.add(sid)
            if sid not in sources:
                errors.append(f"{tag}: kaynak '{sid}' sources.json'da yok")
        if kind in CONTENT and not ids:
            (warns if notes_only else errors).append(f"{tag}: kaynak kimliği yok (sources: [\"S1\", ...])")
        if kind in CONTENT and not s.get("notes"):
            warns.append(f"{tag}: konuşmacı notu yok")
        if kind in CONTENT and not s.get("summary"):
            warns.append(f"{tag}: özet cümlesi (summary) yok — özet PDF'te madde kullanılır")
        if len(s.get("title", "")) > 70:
            warns.append(f"{tag}: başlık {len(s['title'])} karakter (≤ 70 önerilir)")
        items = s.get("bullets", []) or s.get("items", []) or []
        if len(items) > 6:
            warns.append(f"{tag}: {len(items)} madde (≤ 6 önerilir)")
        for it in items:
            t = " ".join(layout._item(it))
            if len(t) > 150:
                warns.append(f"{tag}: madde {len(t)} karakter (≤ 150): \"{t[:60]}…\"")
        texts = slide_texts(s) if kind in CONTENT or kind in ("questions", "agenda") else []
        for t in texts:
            for num in re.findall(r"\d+(?:[.,]\d+)?", t):
                if not number_found(num, c_raw, c_n):
                    warns.append(f"{tag}: '{num}' sayısı kaynak alıntılarında/notlarda yok — doğrula, alıntı ekle ya da sil")
        if kind in CONTENT and lexical:
            for t in texts:
                content = [w for w in norm(t).split() if len(w) >= 5 and w not in STOP]
                if len(content) < 3:
                    continue
                base = notes_stems if notes_only else stems
                share = sum(w[:5] in base for w in content) / len(content)
                lim = 0.5 if notes_only else 0.3
                if share < lim:
                    who = "notlarında" if notes_only else "kaynak alıntılarında/notlarda"
                    warns.append(f"{tag}: içerik kelimelerinin %{int(share * 100)}'i {who} — dayanak zayıf: \"{t[:70]}\"")
    for sid in sources:
        if sid not in used and sources[sid].get("type") != "user_notes":
            warns.append(f"kaynak {sid} hiçbir slaytta kullanılmadı (kaynakçada yine görünür)")
    # ---- test (Pro)
    quiz = deck.get("quiz", [])
    if quiz:
        if len(quiz) != 10:
            errors.append(f"soru sayısı {len(quiz)} (10 olmalı)")
        for k, q in enumerate(quiz, 1):
            if len(q.get("options", [])) != 4:
                errors.append(f"soru {k}: 4 şık olmalı")
            if not 0 <= int(q.get("answer", -1)) <= 3:
                errors.append(f"soru {k}: cevap 0–3 olmalı")
            for num in re.findall(r"\d+", q.get("q", "") + " " + " ".join(q.get("options", []))):
                if not number_found(num, c_raw, c_n):
                    warns.append(f"soru {k}: '{num}' sayısı kaynaklarda yok")
        dist = [int(q.get("answer", 0)) for q in quiz]
        if quiz and max(dist.count(i) for i in range(4)) > 4:
            warns.append(f"cevap dağılımı dengesiz: {[dist.count(i) for i in range(4)]}")
    return {"ok": not errors, "errors": errors, "warnings": warns, "slides": len(slides),
            "sources_used": sorted(used)}
