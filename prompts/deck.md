# deck.json şeması — Anlatım Stüdyosu

```json
{
 "title": "Sunum başlığı", "subtitle": "Alt başlık", "kicker": "Ders · seviye (kapakta üst satır)",
 "template": "sade_akademik", "author": "", "org": "", "date": "", "kaynak_line": true,
 "keywords": ["özet PDF'te anahtar terimler"],
 "slides": [ … ],
 "quiz": [ … ]          // (Pro) tam 10 soru
}
```
`template`, `author`, `org`, `date`, `kaynak_line` boşsa brief.yaml'dan, o da boşsa config'ten gelir.

## Ortak alanlar (her slayt)
- `type` (aşağıdaki tiplerden), `title` (≤ 70 karakter; kapakta sunum başlığı kullanılır)
- `sources`: ["S1", "S3"] — içerik slaytlarında zorunlu; altta "Kaynak:" satırını bunlar oluşturur
- `notes`: konuşmacı notu (3–6 cümle: slaytta yazmayan açıklama, örnek, sınıfa soru, sık yanılgı)
- `summary`: özet PDF'e girecek tek cümle (≤ 25 kelime)
- Metinde `**kalın**` kullanılabilir. Maddeler ya düz metin ya `{"label": "Terim", "text": "açıklama"}` (terim kalın).

## Slayt tipleri

| type | alanlar | not |
|---|---|---|
| `title` | (deck title/subtitle/kicker kullanılır) | kapak |
| `section` | `title`, `subtitle`, `number` | bölüm ayracı |
| `agenda` | `bullets` | numaralı içerik listesi |
| `bullets` | `bullets` (2–6), `lead` (giriş cümlesi), `image` | `image` verilirse metin solda, görsel sağda |
| `summary` | `bullets` | "Özetle" slaytı |
| `questions` | `bullets` | numaralı açık uçlu sorular ("Kendini dene"); cevapları `notes`'a |
| `two_col` | `columns: [{"heading", "bullets"}, {"heading", "bullets"}]` | iki kutu |
| `process` | `steps: [{"label", "text"}]` (2–5), `note` | numaralı kutular + oklar (düzenlenebilir şekiller) |
| `compare` | `corner`, `columns: ["A", "B"]`, `rows: [{"label", "cells": ["…", "…"]}]` | PPTX tablo |
| `term` | `term`, `definition`, `example` | tanım kartı |
| `key_fact` | `statement` (≤ 70 karakter ise tek satır denenir), `detail` | tek güçlü cümle / denklem |
| `image` | `image: {"path": "notes/sekil.png", "credit": "Yazar, CC BY 4.0"}`, `caption` | tam slayt görsel |
| `sources` | — | Kaynakça: sources.json'dan otomatik (APA benzeri) |

Görsel yolu proje klasörüne göredir. Yalnız kullanıcının verdiği ya da lisansı açık görseller; `credit` zorunlu.

## Yazım
- Madde: tam cümle, ≤ 150 karakter (tercihen ≤ 110). Slayt başına ≤ 6 madde.
- Kaynakta olmayan sayı, tarih, isim yok; "~", "yaklaşık" ile uydurma yok.
- Hedef kitleye uygun dil; terimi ilk geçtiği yerde açıkla.
- Alt/üst simge kullanılabilir (CO₂, NADP⁺) — PPTX'te doğru görünür.

## (Pro) quiz
```json
{"q": "Soru?", "options": ["A", "B", "C", "D"], "answer": 2, "why": "Bir cümle açıklama (kaynağa dayalı)."}
```
Tam 10 soru; cevaplar şıklara dengeli dağılsın (bir harf ≤ 4 kez); her soru bir slayta ve kaynağa dayansın.
