# Anlatım Stüdyosu — kaynaklı ders sunumu ve anlatım videosu (Claude Code skill)

> **Pro sürümü yakında (henüz satışta değil).** Çıkınca haber almak için [Pro bekleme listesi](https://github.com/redirhan/redirhan/issues/1) konusuna 👍 bırakın ya da kısa bir yorum yazın.

Bir konu yazın — isterseniz kendi notlarınızı da ekleyin. Claude konuyu araştırır, **yalnız gerçekten açıp okuduğu
kaynakları** alıntılarıyla kaydeder, size bir taslak gösterir; onayınızdan sonra seçtiğiniz şablonla **düzenlenebilir
bir PowerPoint**, konuşmacı notları ve tek sayfalık özet hazırlar. Her slaytın altında "Kaynak:" satırı, sonda
Kaynakça vardır. Pro sürüm aynı içerikten **Türkçe seslendirmeli 2D anlatım videosu**, **10 soruluk test** ve
sosyal medya için **dikey kısa kesit** de çıkarır.

Kimler için: ders materyali hazırlayan **öğretmenler ve eğitmenler**, kurslar, kurum içi eğitim verenler, eğitim
içeriği üreten **içerik üreticileri**; konuyu **çalışmak** ya da **sunum tasarımını öğrenmek** isteyen öğrenciler.

> ### Sorumlu kullanım
> **Not için teslim edilecek işin içeriğini kendin hazırla; bu araç öğrenme, ders materyali ve tasarım içindir.**
> Anlatım Stüdyosu "ödevini yapan" bir araç değildir. Başkası adına not alacak akademik iş hazırlamak Türkiye'de
> suçtur (2547 sayılı Kanun Ek Madde 47) ve okulların disiplin kurallarına aykırıdır. Teslim edeceğiniz bir sunumda
> **tasarım modunu** kullanın: içerik yalnız sizin notlarınızdan gelir, araç bilgi eklemez; düzen, şablon ve
> görünümü hazırlar. Kendi çalışmanız için konu sunumu, özet ve test hazırlamak serbesttir.

## Sürümler

| | **Lite** (ücretsiz, MIT) | **Pro** (ücretli, EULA) |
|---|---|---|
| Kaynaklı araştırma (yalnız açılmış kaynaklar, birebir alıntı kaydı) | ✓ | ✓ |
| Taslak onayı (slayt slayt plan) | ✓ | ✓ |
| Düzenlenebilir PPTX — 13 slayt tipi, 4 şablon | ✓ | ✓ |
| Her slaytta "Kaynak:" satırı + otomatik Kaynakça | ✓ | ✓ |
| Konuşmacı notları (PPTX not bölmesi + ayrı .md) | ✓ | ✓ |
| Özet PDF (tek sayfaya sığdırılır) | ✓ | ✓ |
| Önizleme + temas sayfası (LibreOffice, yoksa PIL) | ✓ | ✓ |
| Doğrulayıcı: açılmamış kaynak, kaynakta olmayan sayı, taşan metin | ✓ | ✓ |
| Türkçe seslendirmeli 2D anlatım videosu (16:9, SRT altyazı) | — | ✓ |
| TTS: yerel EMA (ücretsiz) · kendi Gemini anahtarınız · sessiz önizleme | — | ✓ |
| 192 terimlik Türkçe okunuş sözlüğü + Whisper geri kontrolü | — | ✓ |
| 10 soruluk test PDF (cevap anahtarı ayrı sayfada) | — | ✓ |
| 9:16 kısa kesit (Reels / Shorts / TikTok) | — | ✓ |

**Şablonlar:** `sade_akademik` (beyaz, lacivert, Arial) · `modern_koyu` (koyu zemin, turkuaz/amber, Calibri) ·
`renkli_lise` (krem zemin, dört renk, numaralı rozetler) · `kurumsal_egitim` (petrol şerit, Georgia + Arial, kurum adı).
Örnek görünüm: `examples/fotosentez/out/preview_v*/contact_sheet.png`.

## Gereksinimler

- [Claude Code](https://docs.claude.com/en/docs/claude-code) — Claude Pro (ya da üstü) aboneliği. Araştırmayı ve
  yazmayı Claude sizin oturumunuzda yapar; skill kendi başına ücretli API çağırmaz.
- Python 3.10+ (macOS, Linux; Windows'ta WSL önerilir)
- İsteğe bağlı: **LibreOffice** (gerçek slayt önizlemesi; yoksa yaklaşık PIL önizlemesi) + poppler (`pdftoppm`)
- Pro: **ffmpeg**; seslendirme için **EMA-TTS** (yerel, ücretsiz — `docs/EMA_KURULUM.md`) **ya da** kendi
  **Gemini API anahtarınız**; isteğe bağlı Whisper (whisper.cpp ya da faster-whisper) geri kontrolü
- Chrome/Chromium gerekmez ve açılmaz.

## Kurulum

```bash
mkdir -p ~/.claude/skills
unzip anlatim-studyosu-lite-v1.0.zip -d ~/.claude/skills/     # ya da …-pro-v1.0.zip
cd ~/.claude/skills/anlatim-studyosu
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config.example.yaml config.yaml          # isteğe bağlı: şablon, ad, kurum, (Pro) TTS ayarları
.venv/bin/python scripts/studyo.py doctor   # TAMAM görmelisiniz
```
macOS: `brew install --cask libreoffice` · `brew install poppler ffmpeg` — Debian/Ubuntu:
`sudo apt install libreoffice-impress poppler-utils ffmpeg`.

## Kullanım

Claude Code'da doğal dille isteyin:

> 10. sınıflar için "Fotosentez nasıl çalışır?" konulu 12 slaytlık bir ders sunumu hazırla, renkli lise şablonu,
> her slaytta kaynak olsun.

> Ekteki ders notlarımdan (notlar.pdf) sade akademik bir sunum tasarla — sadece benim notlarım, bilgi ekleme.

> (Pro) Bu sunumdan 4 dakikalık anlatım videosu, 10 soruluk test ve 45 saniyelik dikey kesit çıkar.

Claude skill'i yükler, birkaç kısa soru sorar, kaynakları açıp okur, taslağı onayınıza sunar ve çıktıları
`~/anlatim-studyosu/<proje>/out/` altına sürümlü adlarla (`_v1`, `_v2` …) yazar. Elle kullanım:

```bash
S=~/.claude/skills/anlatim-studyosu; PY=$S/.venv/bin/python
$PY $S/scripts/studyo.py new fotosentez --topic "Fotosentez nasıl çalışır?"
#   Claude: research/sources.json → outline.md (onay) → deck.json
$PY $S/scripts/studyo.py check fotosentez
$PY $S/scripts/studyo.py build fotosentez                 # PPTX + notlar + özet PDF + önizleme
$PY $S/scripts/studyo.py build fotosentez --template modern_koyu
# Pro:
$PY $S/scripts/studyo.py quiz fotosentez
$PY $S/scripts/studyo.py video-prompt fotosentez         # Claude → video_plan.json
$PY $S/scripts/studyo.py video fotosentez                # kontrol → ses → render → dikey kesit → test → QA
```

## Örnek (pakette)

`examples/fotosentez/` — "Fotosentez nasıl çalışır?" (lise / üniversite giriş): 5 açık kaynak (OpenStax Biology 2e
8.1–8.3, Vikipedi, Wikipedia; hepsi açılıp okundu, alıntıları `research/sources.json`'da), taslak, 14 slaytlık deck,
dört şablonda önizleme, konuşmacı notları, özet PDF; Pro'da ayrıca 10 soruluk test ve video planı.

## Nasıl doğruluyor?

- Her kaynakta `"opened": true` ve sayfadan birebir alıntı yoksa `check` hata verir — "okumadan kaynak gösterme" engellenir.
- Slayttaki her sayı kaynak alıntılarında ya da notlarda aranır; bulunmazsa uyarı verir.
- Tasarım modunda dış kaynak eklenemez; maddeler notlarınıza dayanmalıdır.
- Metin kutuları ölçülerek sığdırılır; sığmayan metin "taşıyor" uyarısı verir. Claude önizlemeye bakmadan teslim etmez.
- Yine de: araç bir yardımcıdır. İçeriği derste kullanmadan önce okuyun; kaynak satırları sizin kontrolünüz içindir.

## Gizlilik

Her şey bilgisayarınızda çalışır. Hesap açılmaz, hiçbir şey yayımlanmaz, kullanım verisi toplanmaz. Notlarınız
yalnız Claude Code oturumunuzda işlenir. Gemini'yi seçerseniz yalnız seslendirme metni Google'a gider (kendi
anahtarınızla). Anahtar dosyaya yazılmaz, yalnız ortam değişkeninden okunur.

## Lisans

Lite: MIT (`LICENSE`). Pro: ticari EULA (`EULA.md`; Lite'la ortak dosyalar ayrıca MIT). Fontlar SIL OFL 1.1
(`fonts/OFL-*.txt`). Üçüncü taraflar: `THIRD_PARTY_NOTICES.md`. Redirhan Labs
