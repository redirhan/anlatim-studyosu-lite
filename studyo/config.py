"""Ayarlar, sürüm (Lite/Pro) ve yollar.

Sabit mutlak yol yoktur. Sıra:
  1. ortam değişkenleri (ANLATIM_CONFIG, ANLATIM_EDITION, ANLATIM_PROJECTS_DIR, EMA_PYTHON, EMA_REPO, WHISPER_CPP_MODEL ...)
  2. SKILL.md'nin yanındaki config.yaml (config.example.yaml'dan kopyalanır)
  3. aşağıdaki varsayılanlar
"""
from __future__ import annotations

import os
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]

DEFAULTS = {
    "projects_dir": "~/anlatim-studyosu",          # `new` komutu projeleri burada açar
    "template": "sade_akademik",                    # sade_akademik | modern_koyu | renkli_lise | kurumsal_egitim
    "kaynak_line": True,                            # her içerik slaytının altında "Kaynak:" satırı
    "author": "",                                   # kapakta "Hazırlayan" (boşsa yazılmaz)
    "org": "",                                      # kurum / okul / kurs adı (kurumsal şablonda alt bilgi)
    "preview": "auto",                              # auto | libreoffice | pil  (slayt önizlemesi)
    "soffice": None,                                # LibreOffice ikilisi (boşsa PATH ve /Applications aranır)
    # ---- Pro: video
    "tts_engine": "ema",                            # ema | gemini | silent (sessiz önizleme)
    "gemini_api_key_env": "GEMINI_API_KEY",         # anahtar SADECE bu ortam değişkeninden okunur
    "gemini_models": ["gemini-3.8-flash-tts", "gemini-2.5-flash-preview-tts"],   # sırayla denenir (kota/404)
    "gemini_voice": "Kore",
    "ema_python": None,                             # EMA-TTS venv python'u  (ya da EMA_PYTHON)
    "ema_repo": None,                               # git clone https://huggingface.co/canberkkkkkk/ema-tts (ya da EMA_REPO)
    "whisper_cpp_model": None,                      # ggml modeli (ya da WHISPER_CPP_MODEL); yoksa faster-whisper/openai-whisper denenir
    "video_length_min": [3, 5],
    "music": True,
    "outro_line": "Özet PDF ve 10 soruluk test videonun yanında.",
}


def _deep_merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = _deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def config_path() -> Path | None:
    env = os.environ.get("ANLATIM_CONFIG")
    if env:
        return Path(env).expanduser()
    p = SKILL / "config.yaml"
    return p if p.exists() else None


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    p = config_path()
    if p and p.exists():
        import yaml
        cfg = _deep_merge(cfg, yaml.safe_load(p.read_text(encoding="utf-8")) or {})
    env_map = {"ANLATIM_PROJECTS_DIR": "projects_dir", "EMA_PYTHON": "ema_python", "EMA_REPO": "ema_repo",
               "WHISPER_CPP_MODEL": "whisper_cpp_model", "ANLATIM_TTS_ENGINE": "tts_engine"}
    for env, key in env_map.items():
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    return cfg


def expand(p) -> Path | None:
    if not p:
        return None
    return Path(os.path.expandvars(os.path.expanduser(str(p))))


# ---------------------------------------------------------------- sürüm
def edition() -> str:
    env = os.environ.get("ANLATIM_EDITION")
    if env:
        return env.strip().lower()
    f = SKILL / "EDITION"
    if f.exists():
        return f.read_text(encoding="utf-8").strip().lower()
    return "pro"            # kaynak deposu (geliştirme): her şey açık


def pro_available() -> bool:
    return edition() == "pro" and (SKILL / "studyo" / "pro" / "__init__.py").exists()


def require_pro(feature: str):
    if not pro_available():
        raise SystemExit(f"'{feature}' Anlatım Stüdyosu Pro özelliğidir (bu kurulum: Lite). "
                         "Lite: araştırma + taslak + PPTX + konuşmacı notları + özet PDF. Bkz. README.")
