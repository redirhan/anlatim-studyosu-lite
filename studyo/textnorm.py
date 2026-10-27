"""Türkçe metin yardımcıları: küçük harf, sayıyı yazıya çevirme, harf adları, kelime bölme."""
import re

LETTER_NAMES = {
    "A": "a", "B": "be", "C": "ce", "Ç": "çe", "D": "de", "E": "e", "F": "fe", "G": "ge", "Ğ": "yumuşak ge",
    "H": "he", "I": "ı", "İ": "i", "J": "je", "K": "ke", "L": "le", "M": "me", "N": "ne", "O": "o", "Ö": "ö",
    "P": "pe", "R": "re", "S": "se", "Ş": "şe", "T": "te", "U": "u", "Ü": "ü", "V": "ve", "Y": "ye", "Z": "ze",
    "Q": "kü", "W": "çift ve", "X": "iks",
}
DIGITS = ["sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
TENS = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]


def tr_lower(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower().replace("i̇", "i")


def tr_upper(s: str) -> str:
    return s.replace("i", "İ").replace("ı", "I").upper()


def _under_thousand(n: int) -> str:
    h, r = divmod(n, 100)
    t, o = divmod(r, 10)
    parts = []
    if h:
        parts.append(("" if h == 1 else DIGITS[h] + " ") + "yüz")
    if t:
        parts.append(TENS[t])
    if o:
        parts.append(DIGITS[o])
    return " ".join(parts)


def int_to_words(n: int) -> str:
    """Tam sayıyı Türkçe yazıya çevirir (2012 → 'iki bin on iki')."""
    if n == 0:
        return "sıfır"
    if n < 0:
        return "eksi " + int_to_words(-n)
    words = []
    for value, name in ((10 ** 12, "trilyon"), (10 ** 9, "milyar"), (10 ** 6, "milyon"), (1000, "bin")):
        q, n = divmod(n, value)
        if q:
            words.append("bin" if (value == 1000 and q == 1) else f"{int_to_words(q)} {name}")
    if n:
        words.append(_under_thousand(n))
    return " ".join(words)


def number_to_words(tok: str) -> str:
    """'2012' / '3,5' / '1.000.000' (Türkçe binlik nokta) → yazı."""
    tok = tok.strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", tok):
        tok = tok.replace(".", "")
    if "," in tok:
        a, b = tok.split(",", 1)
        b_words = " ".join(DIGITS[int(c)] for c in b) if b.startswith("0") else int_to_words(int(b))
        return f"{int_to_words(int(a))} virgül {b_words}"
    return int_to_words(int(tok))


def spell_letters(abbr: str) -> str:
    """'DNA' → 'de ne a'. Rakamlar yazıyla."""
    out = []
    for ch in abbr:
        up = tr_upper(ch)
        if up in LETTER_NAMES:
            out.append(LETTER_NAMES[up])
        elif ch.isdigit():
            out.append(DIGITS[int(ch)])
    return " ".join(out)


SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+")


def words(s: str):
    """Kelimeler; kesme işaretli ek aynı kelimeye sayılır (DNA'yı = 1)."""
    return re.findall(r"[0-9A-Za-zÇĞİÖŞÜçğıöşüÂâÎîÛû]+(?:['’][a-zçğıöşüâîû]+)?", s)


def norm_tokens(s: str):
    """Karşılaştırma için: küçük harf, şapkasız, noktalamasız kelime listesi."""
    s = tr_lower(s).replace("â", "a").replace("î", "i").replace("û", "u")
    s = re.sub(r"['’`]", "", s)
    return re.sub(r"[^0-9a-zçğıöşü ]", " ", s).split()
