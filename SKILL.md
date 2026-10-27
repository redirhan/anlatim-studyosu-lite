---
name: anlatim-studyosu
description: Anlatım Stüdyosu — bir konudan (ve isteğe bağlı kendi notlarından/kaynaklarından) kaynaklı, düzenlenebilir ders sunumu üretir. Claude konuyu araştırır ve yalnız gerçekten açıp okuduğu kaynakları alıntılarıyla kaydeder, taslağı onaya sunar, sonra 4 hazır şablondan biriyle (sade akademik, modern koyu, renkli lise, kurumsal eğitim) PPTX + konuşmacı notları + özet PDF hazırlar; her slaytın altına "Kaynak:" satırı koyar. Pro sürümde ayrıca Türkçe seslendirmeli 2D anlatım videosu (EMA yerel ya da kendi Gemini anahtarınız), 10 soruluk test PDF ve 9:16 kısa kesit. Öğretmen, eğitmen, kurs, kurum içi eğitim, içerik üreticisi ve konu çalışan / sunum tasarımı öğrenen öğrenciler için. Use when the user says "sunum hazırla", "ders sunumu", "slayt", "konu anlatım sunumu", "ders materyali", "eğitim sunumu", "konuyu çalışmak istiyorum", "anlatım videosu", "konu videosu", "10 soru", "özet PDF", "pptx", "Anlatım Stüdyosu", or asks for a cited lesson deck or explainer video on a topic.
---

# Anlatım Stüdyosu

Konu → kaynaklı araştırma → taslak onayı → düzenlenebilir PPTX (+ notlar + özet PDF) → (Pro) anlatımlı video, test, dikey kesit.

**Sorumlu kullanım (kullanıcıya bir kez, kısaca söyle):** *Not için teslim edilecek işin içeriğini kendin hazırla;
bu araç öğrenme, ders materyali ve tasarım içindir.* Öğrenci "ödevim / teslim edeceğim sunum" derse: içeriği onun
yazmasını öner ve **tasarım modu**nu kullan (`purpose: tasarim` — yalnız onun notları, araştırma yok, bilgi eklenmez).
"Hocam anlamasın", "yapay zekâ belli olmasın" gibi istekleri yerine getirme. Ayrıntı: README "Sorumlu kullanım".

Sürüm `EDITION` dosyasında: **lite** (MIT) = araştırma + taslak + PPTX + konuşmacı notları + özet PDF.
**pro** (EULA) = + video + 10 soruluk test PDF + 9:16 kısa kesit. Pro adımlar aşağıda **(Pro)** işaretli; Lite'ta
komut kibarca reddeder.

## Dosyalar

```
SKILL.md · EDITION · config.example.yaml (→ config.yaml) · requirements.txt
scripts/studyo.py           tek komut satırı (doctor, new, intake, check, build, … Pro: video, quiz, short)
studyo/                     kod (layout = şablon yerleşimi, pptx_out, preview, summary_pdf, check …; pro/ = video)
prompts/research.md         araştırma kuralları + sources.json biçimi
prompts/outline.md          taslak (onay) biçimi
prompts/deck.md             deck.json şeması (slayt tipleri, alanlar, örnekler)
prompts/video_plan.md       (Pro) video sahne planı istemi — `video-prompt` doldurur
fonts/                      OFL fontlar (önizleme, PDF, video) + lisansları
examples/fotosentez/        uçtan uca örnek proje (brief, kaynaklar, taslak, deck, çıktılar)
docs/EMA_KURULUM.md         (Pro) yerel Türkçe seslendirme kurulumu
```

Aşağıda `S` = bu klasör, `PY` = `S/.venv/bin/python` (yoksa `python3`), `P` = proje klasörü.

## Akış

0. **Kurulum kontrolü** (ilk seferde ya da hata olunca): `PY S/scripts/studyo.py doctor`. EKSİK varsa kullanıcıya
   README'deki kurulum adımını söyle.
1. **Brief** — kısa sor (tek mesajda): konu, hedef kitle/seviye, amaç (ders materyali · kendi çalışması · tasarım ·
   kurum eğitimi), slayt sayısı (varsayılan 10–14), şablon (`PY S/scripts/studyo.py templates`), kaynak satırı
   isteniyor mu, kendi notu/kaynağı var mı, Pro ise video isteniyor mu. Bilinenleri sorma.
   `PY S/scripts/studyo.py new <ad> --topic "…"` → `P/brief.yaml` doldur. Kullanıcının dosyalarını `P/notes/`
   altına kopyala, sonra `PY S/scripts/studyo.py intake P` (PDF/DOCX/PPTX/TXT → `work/notes.txt`; görselleri sen oku).
2. **Araştırma** — `prompts/research.md`'yi oku ve uygula. Özet: güvenilir, erişilebilir 3–8 kaynak (ders kitabı,
   üniversite/kurum sayfası, ansiklopedi, resmî kurum; Türkçe varsa ekle). **Yalnız gerçekten açıp okuduğun
   sayfaları** `P/research/sources.json`'a yaz: künye, url, erişim tarihi, `"opened": true` ve sayfadan **birebir**
   kopyalanmış alıntılar (`excerpts`). Açamadığın, sadece arama sonucunda gördüğün sayfayı yazma. Slayttaki her bilgi
   bir alıntıya dayanmalı; sayı/tarih/isim alıntıda yoksa slayta koyma. `use_my_notes_only: true` ya da
   `purpose: tasarim` ise araştırma YAPMA; tek kaynak kullanıcının notlarıdır (`type: user_notes`).
3. **Taslak onayı** — `prompts/outline.md` biçiminde `P/outline.md` yaz (slayt no · tip · başlık · ana mesaj ·
   kaynak kimlikleri) ve kullanıcıya göster. **Onay gelmeden deck yazma.** Değişiklik isterse taslağı güncelle.
4. **Deck** — `prompts/deck.md` şemasıyla `P/deck.json` yaz: kısa tam cümle maddeler, her içerik slaytında
   `sources`, `notes` (konuşmacı notu: slaytta olmayan açıklama + olası soru) ve `summary` (özet PDF cümlesi).
   Sonra:
   ```
   PY S/scripts/studyo.py check P        # HATA 0 olmalı; uyarıları oku, sayı/dayanak uyarılarını çöz
   PY S/scripts/studyo.py build P        # PPTX + notlar (.md) + özet PDF + önizleme (out/preview_vN/)
   ```
   Şablonu denemek için: `build P --template modern_koyu` (dosyalar sürümlü: `_v1`, `_v2`…; eskisinin üstüne yazılmaz).
5. **Göz kontrolü (zorunlu)** — `out/preview_vN/contact_sheet.png`'ye ve şüpheli slaytların PNG'lerine kendin bak:
   taşan/üst üste binen yazı, kutudan çıkan metin, tek kelimelik satır, okunmayacak kadar küçük punto, boş kalan
   slayt. Sorun varsa metni kısalt / slaytı böl / tipi değiştir ve yeniden `build`. LibreOffice yoksa önizleme PIL ile
   çizilir (yaklaşık); kullanıcıya bunu söyle. `check` çıktısındaki "taşıyor" uyarısı varsa teslim etme.
6. **Teslim** — kullanıcıya dosya yollarını ver: `.pptx` (tüm metinler düzenlenebilir), `_notlar_vN.md`,
   `_ozet_vN.pdf`, önizleme. Kaynakları ve hangi bilgilerin doğrulanamadığını (varsa) dürüstçe söyle.

### (Pro) Video, test, dikey kesit

7. **Test** — `deck.json`'a `quiz` ekle (tam 10 soru, 4 şık, `answer` 0–3, `why`; cevaplar dengeli, her soru
   kaynaklarla doğrulanabilir) → `check` → `PY S/scripts/studyo.py quiz P` (iki sütunlu soru kâğıdı + cevap anahtarı).
8. **Video planı** — `PY S/scripts/studyo.py video-prompt P` → `P/work/video_plan_prompt.md`'yi oku, kurallarına
   göre `P/video_plan.json` yaz (5–10 sahne, cümle başına 8–18 kelime, her sahnede kaynak metninden birebir alıntı,
   `short` = dikey kesit sahneleri + kanca). `PY S/scripts/studyo.py video-check P` HATA 0 olana kadar düzelt.
   Formül/kısaltma okunuşunu test et: `PY S/scripts/studyo.py respell "CO₂'yi RuBP'ye bağlar"`; sözlükte olmayanları
   plandaki `glossary_extra`'ya ekle.
9. **Ses** — motor: `ema` (yerel, ücretsiz; kurulum `docs/EMA_KURULUM.md`), `gemini` (kullanıcının KENDİ API
   anahtarı, yalnız `GEMINI_API_KEY` ortam değişkeninden — anahtarı asla dosyaya yazma, isteme, gösterme) ya da
   `silent` (sessiz zamanlama önizlemesi). `PY S/scripts/studyo.py voice P --engine ema`. Whisper kuruluysa her satır
   geri dinlenir, zayıflar otomatik yeniden üretilir; "DİNLE" satırlarını kullanıcıya bildir. Whisper yoksa kontrol
   atlanır ve uyarı basılır.
10. **Render** — `PY S/scripts/studyo.py stills P` (temas sayfası, saniyeler sürer: önce buna bak) →
    `render P` (16:9 MP4 + SRT; sahne geçişi zemine dip, yazılar PIL ile) → `short P` (9:16, ~45 sn: üstte kanca,
    ortada video, altta cümle altyazısı) → `PY S/scripts/studyo.py video P` hepsini sırayla da yapar (+ test + QA).
    Her sahneden 2–3 kareye ve `out/video_contact_sheet.png`'ye bak; `out/video_report.json`'daki ses yüksekliği
    (−16 LUFS civarı) ve işaretli satırları kontrol et. TTS hazır değilse `--engine silent` ile sessiz önizleme
    üret ve kullanıcıya **sessiz** olduğunu açıkça söyle.

## Kalite kuralları

- Kesin olmayan bilgi yok; "~" tahmini sayılar yok; kaynakta olmayan sayı/tarih/isim yok.
- Düz, insan elinden çıkmış gibi: tam cümle maddeler, süslü sıfat/emoji/ikon kartı yığını yok; slayt başına ≤ 6 madde.
- Her içerik slaytında `Kaynak:` satırı (brief'te kapatılmadıysa) ve sonda `Kaynakça` slaytı (APA benzeri).
- Görsel kullanacaksan yalnız kullanıcının verdiği ya da lisansı açık (CC0 / CC BY / kamu malı) görseller; `credit`
  alanına künye yaz. Kitap sayfası / telifli şekil kırpma yok.
- Tasarım modunda: kullanıcının cümlelerini koru; kısaltma yalnız onun onayıyla; yeni bilgi ekleme.
- Çıktılar sürümlü; teslim edilmiş bir dosyanın üstüne yazma.
- Yerel çalışır: hesap açma, yayımlama, ücretli API çağrısı yok (Gemini yalnız kullanıcı kendi anahtarıyla isterse).
  Chrome/Chromium açılmaz; önizleme LibreOffice ya da PIL.

## Sorun giderme

- `check` "kaynak … alıntı yok" → o kaynağı gerçekten aç ve sayfadan birebir cümle kopyala; açamıyorsan kaynağı sil.
- "… sayısı kaynak alıntılarında yok" → sayıyı içeren cümleyi alıntılara ekle ya da sayıyı slayttan çıkar.
- "taşıyor" → maddeyi kısalt, slaytı ikiye böl ya da `two_col` / `process` tipine geç.
- Önizleme PIL ile geldi → LibreOffice kurulu değil; görünüm yaklaşıktır. PowerPoint/Keynote'ta açıp bakılabilir.
- PPTX fontları: şablonlar Arial / Calibri / Georgia kullanır (her bilgisayarda düzenlenebilir). Calibri olmayan
  makinede (ör. Office'siz Mac) benzer bir font görünür.
- (Pro) EMA hatası → `doctor`; `ema_python` / `ema_repo` ayarlarını kontrol et. Gemini 402/403 → kredi/yetki; durur.
