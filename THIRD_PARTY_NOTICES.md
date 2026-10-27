# Üçüncü taraf bildirimleri / Third-party notices

## Pakette gelenler / Bundled

| Bileşen | Lisans | Kullanım |
|---|---|---|
| Outfit (fonts/Outfit-*.ttf) | SIL OFL 1.1 — `fonts/OFL-Outfit.txt` | özet PDF, test PDF, video yazıları |
| Bricolage Grotesque (fonts/BricolageGrotesque-*.ttf) | SIL OFL 1.1 — `fonts/OFL-BricolageGrotesque.txt` | başlıklar (PDF, video) |
| Arimo (fonts/Arimo-*.ttf) | SIL OFL 1.1 — `fonts/OFL-Arimo.txt` | Arial ile ölçü uyumlu: satır sarma ölçümü, PIL önizleme |
| Carlito (fonts/Carlito-*.ttf) | SIL OFL 1.1 — `fonts/OFL-Carlito.txt` | Calibri ile ölçü uyumlu: satır sarma ölçümü, PIL önizleme |
| Gelasio (fonts/Gelasio-*.ttf) | SIL OFL 1.1 — `fonts/OFL-Gelasio.txt` | Georgia ile ölçü uyumlu: satır sarma ölçümü, PIL önizleme |

Fontlar github.com/google/fonts deposundan alınmış, değişken fontlardan sabit kesimler (static instances) üretilmiştir
(`scripts/dev_make_fonts.py`). OFL gereği font dosyaları tek başına satılmaz; yazılımla birlikte dağıtılır.

## Kullanıcının kurduğu / Installed by the user (pakette yok)

| Bileşen | Lisans | Kullanım |
|---|---|---|
| python-pptx | MIT | PPTX yazma |
| reportlab | BSD | PDF |
| Pillow | MIT-CMU (HPND) | önizleme, video kareleri |
| PyYAML | MIT | ayar dosyaları |
| pypdf | BSD | PDF notlarını okuma |
| python-docx | MIT | Word notlarını okuma |
| numpy (Pro) | BSD | ses işleme, müzik yatağı |
| FFmpeg (Pro) | LGPL-2.1+ / GPL (derlemeye göre) | video/ses kodlama; ayrı komut olarak çağrılır |
| LibreOffice (isteğe bağlı) | MPL-2.0 | slayt önizlemesi; ayrı komut olarak çağrılır |
| poppler / pdftoppm (isteğe bağlı) | GPL-2.0 | PDF → PNG; ayrı komut olarak çağrılır |
| EMA-TTS (Pro, isteğe bağlı) | Apache-2.0 (model kartı) | yerel Türkçe seslendirme; kullanıcı kendisi indirir: huggingface.co/canberkkkkkk/ema-tts |
| whisper.cpp / faster-whisper (isteğe bağlı) | MIT | seslendirme geri kontrolü |
| Google Gemini API (Pro, isteğe bağlı) | Google'ın hizmet şartları | kullanıcının kendi anahtarıyla TTS |

Müzik yatağı paket içindeki kodla sentezlenir (numpy); örnek ya da kayıt içermez.
Telaffuz sözlüğü (`studyo/pro/data/glossary_tr.tsv`) Pro EULA kapsamındadır; hak sahibi Redirhan Labs.

Örnek projedeki kaynaklar (OpenStax Biology 2e — CC BY-NC-SA 4.0 · Vikipedi / Wikipedia — CC BY-SA 4.0) yalnız
atıf yapılarak, kısa alıntılarla kullanılmıştır; sunum metni kendi cümlelerimizdir. Haklar sahiplerine aittir.
