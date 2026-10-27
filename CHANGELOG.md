# Değişiklik günlüğü / Changelog

## 1.0.0 — 2026-10-27

İlk sürüm. / First release.

- **Lite (ücretsiz, MIT):** konu → kaynaklı araştırma kuralları (yalnız açılmış kaynaklar, birebir alıntı zorunlu) →
  taslak onayı → düzenlenebilir PPTX (13 slayt tipi, 4 şablon: sade akademik, modern koyu, renkli lise, kurumsal
  eğitim), her slaytta "Kaynak:" satırı + otomatik Kaynakça, konuşmacı notları (PPTX not bölmesi + .md), tek sayfaya
  sığdırılan özet PDF, LibreOffice (yoksa PIL) önizleme + temas sayfası.
- Doğrulayıcı (`check`): kaynak açılmış mı / alıntı var mı, slayttaki sayılar kaynakta geçiyor mu, tasarım modunda
  dış kaynak yasağı, madde uzunlukları, taşan metin.
- Kullanıcı notları: PDF, DOCX, PPTX (notlar dahil), TXT/MD; görsel → tesseract varsa OCR.
- **Pro (EULA):** anlatımlı 2D video (8 sahne şablonu, şablon renkleriyle), TTS motorları `ema` (yerel, Apache-2.0
  model) / `gemini` (kendi anahtarınız, yalnız ortam değişkeni) / `silent`, 192 terimlik Türkçe okunuş sözlüğü,
  Whisper geri kontrolü (varsa) ve otomatik yeniden üretim, sentez müzik yatağı + ducking, −16 LUFS, SRT altyazı,
  10 soruluk test PDF (cevap anahtarı ayrı sayfada), 9:16 kısa kesit (kanca + altyazı).
- `doctor`, sürümlü çıktı adları (`_vN`), mutlak yol yok (config.yaml / ortam değişkenleri).
- Örnek: "Fotosentez nasıl çalışır?" (examples/fotosentez).
