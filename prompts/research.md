# Araştırma kuralları — Anlatım Stüdyosu

Amaç: sunumdaki her bilginin, gerçekten açılıp okunmuş bir kaynaktaki bir cümleye dayanması.

## Ne zaman araştırma yok
- `purpose: tasarim` ya da `use_my_notes_only: true` → araştırma yapma. Tek kaynak kullanıcının notları:
  `{"id": "N1", "type": "user_notes", "title": "Kendi ders notlarım", "short": "Kendi notların", "in_bibliography": false}`
  (ya da kullanıcı notlarına bir künye verdiyse onu yaz). Slayt metni notlardaki cümlelere dayanmalı.

## Kaynak seçimi
1. Önce kullanıcının verdiği kaynaklar (notes/). Sonra 3–8 dış kaynak.
2. Tercih sırası: açık ders kitabı (ör. OpenStax), üniversite / resmî kurum / müze / bilim kuruluşu sayfası, MEB / EBA
   gibi resmî eğitim içeriği, ansiklopedi (Vikipedi kabul, ama tek kaynak olmasın), saygın bilim yayını.
   Türkçe kaynak varsa en az birini kullan; hedef kitle lise ise dil düzeyi uygun olsun.
3. Kaçın: içerik çiftlikleri, forumlar, yapay zekâ özet siteleri, kaynak göstermeyen bloglar, ödev siteleri.
4. Tartışmalı ya da güncel değişen bilgide tarihli kaynak kullan ve tarihi slayta yaz.

## Açtığını kaydet (zorunlu)
- Sayfayı WebFetch / tarayıcı aracıyla **gerçekten aç**. Arama sonucunda gördüğün özet "açılmış" sayılmaz.
- Okurken slaytta kullanacağın her bilgi için sayfadan **birebir** cümle kopyala (`excerpts`; 5–40 kelime, dilinde,
  çevirmeden). Sayı, tarih, isim içeren her bilgi bir alıntıda geçmeli.
- Açılmayan / 403 / ödeme duvarı olan sayfayı yazma; başka kaynak bul.
- Görsel kullanacaksan: lisansı (CC0 / CC BY / kamu malı) sayfasında doğrula, `credit` künyesini yaz.

## `research/sources.json` biçimi

```json
{"sources": [
  {"id": "S1", "type": "web", "opened": true, "accessed": "2026-10-27",
   "author": "Clark, M. A., Douglas, M. ve Choi, J.", "year": "2018",
   "title": "8.1 Overview of Photosynthesis. Biology 2e", "publisher": "OpenStax",
   "url": "https://openstax.org/books/biology-2e/pages/8-1-overview-of-photosynthesis",
   "short": "Clark vd. (2018), Biology 2e, 8.1",
   "excerpts": ["Plants, algae, and a group of bacteria called cyanobacteria are the only organisms capable of performing photosynthesis."]}
]}
```
Alanlar: `id` (S1, S2 … / N1 notlar), `type` (web | book | article | user_notes), `opened` (true), `accessed`
(YYYY-AA-GG), `author` ya da kurum, `year` ("t.y." = tarih yok), `title`, `publisher`/`site`, `url`, `short`
(slayt altındaki kısa künye), `excerpts` (birebir alıntılar), isteğe bağlı `apa` (hazır tam künye), `notes`.

## Sonra
- `studyo.py check P` kaynakları denetler: `opened`, alıntı, url, kullanılmayan kaynak, kaynaklarda geçmeyen sayılar.
- Kaynaklar farklı dildeyse (ör. İngilizce) kelime bazlı dayanak kontrolü atlanır: her maddenin hangi alıntıya
  dayandığını kendin denetle. Emin olmadığın maddeyi çıkar.
