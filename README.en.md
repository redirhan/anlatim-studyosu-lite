# Anlatım Stüdyosu — cited lesson decks and narrated explainer videos (Claude Code skill, Turkish)

Give a topic — and, optionally, your own notes. Claude researches it, records **only the sources it actually opened
and read** (with verbatim excerpts), shows you an outline, and after your approval builds an **editable PowerPoint**
in one of four templates, with speaker notes and a one-page summary PDF. Every content slide gets a "Kaynak:" (source)
line and the deck ends with a bibliography. The Pro edition also renders a **narrated 2D explainer video in Turkish**,
a **10-question quiz PDF** and a **9:16 short** for social media.

Output language is Turkish. For teachers and trainers (lesson materials), courses, corporate training, educational
content creators, and students who want to **study** a topic or **learn presentation design**.

> ### Responsible use
> **Prepare the content of graded work yourself; this tool is for learning, teaching materials and design.**
> It is not a "do my homework" tool: producing graded academic work for someone else is a criminal offence in Türkiye
> (Law 2547, Additional Article 47). For a deck you will submit, use **design mode** (`purpose: tasarim`): content comes
> only from your notes, nothing is added; the tool handles layout and look.

## Editions

| | **Lite** (free, MIT) | **Pro** (paid, EULA) |
|---|---|---|
| Cited research (opened sources only, verbatim excerpts) | ✓ | ✓ |
| Outline approval step | ✓ | ✓ |
| Editable PPTX — 13 slide types, 4 templates | ✓ | ✓ |
| Source line on every slide + auto bibliography | ✓ | ✓ |
| Speaker notes (PPTX notes pane + .md) | ✓ | ✓ |
| One-page summary PDF | ✓ | ✓ |
| Preview + contact sheet (LibreOffice, else PIL) | ✓ | ✓ |
| Validator: unopened sources, numbers not in sources, overflowing text | ✓ | ✓ |
| Narrated 2D explainer video (16:9 + SRT) | — | ✓ |
| TTS: local EMA (free) · your own Gemini key · silent preview | — | ✓ |
| 192-term Turkish pronunciation glossary + Whisper back-check | — | ✓ |
| 10-question quiz PDF with separate answer key | — | ✓ |
| 9:16 short cut | — | ✓ |

## Requirements

- Claude Code with a Claude Pro (or higher) plan. Claude does the research and writing in your session; the skill
  itself makes no paid API calls.
- Python 3.10+ (macOS, Linux; WSL on Windows). Optional: LibreOffice + poppler for true slide previews.
- Pro: ffmpeg; for voice either **EMA-TTS** (local, free — `docs/EMA_KURULUM.md`) or **your own Gemini API key**
  (read only from the `GEMINI_API_KEY` environment variable); optional Whisper for back-checking.
- No Chrome/Chromium needed or launched.

## Install

```bash
mkdir -p ~/.claude/skills
unzip anlatim-studyosu-lite-v1.0.zip -d ~/.claude/skills/     # or …-pro-v1.0.zip
cd ~/.claude/skills/anlatim-studyosu
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/studyo.py doctor
```

## Use

Ask in Claude Code, e.g. *"Prepare a 12-slide lesson deck on photosynthesis for 10th graders, colourful template,
cite sources on every slide."* Manual commands: `new`, `intake`, `check`, `build` (PPTX + notes + summary + preview);
Pro: `quiz`, `video-prompt`, `video-check`, `voice`, `stills`, `render`, `short`, `video`. See `SKILL.md`.

Example project: `examples/fotosentez/` (photosynthesis, five open sources, 14 slides, four template previews).

## Privacy

Runs locally. No accounts, no publishing, no telemetry. If you pick Gemini, only the narration text goes to Google
under your own key.

## Licence

Lite: MIT. Pro: commercial EULA (`EULA.md`; files shared with Lite are also MIT). Fonts: SIL OFL 1.1.
Third parties: `THIRD_PARTY_NOTICES.md`. Redirhan Studio — redirhan.com
