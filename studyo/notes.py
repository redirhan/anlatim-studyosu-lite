"""Konuşmacı notları: PPTX'in not bölmesine yazılır + ayrıca okunabilir bir Markdown dosyası."""
from __future__ import annotations

from pathlib import Path

from . import layout


def write_md(deck: dict, sources: dict, out: Path):
    lines = [f"# {deck.get('title', '')} — konuşmacı notları", ""]
    if deck.get("subtitle"):
        lines += [f"_{deck['subtitle']}_", ""]
    for i, s in enumerate(deck.get("slides", []), 1):
        title = s.get("title") or {"title": deck.get("title", "Kapak"), "sources": "Kaynakça"}.get(s.get("type"), "")
        lines.append(f"## {i}. {title}")
        if s.get("notes"):
            lines += ["", s["notes"].strip()]
        cites = layout.cite_line(s, sources)
        if cites and s.get("type") not in ("title", "sources"):
            lines += ["", "*" + "".join(r.text for r in cites).strip() + "*"]
        lines.append("")
    lines += ["---", "Kaynakça", ""]
    lines += [f"- {layout.apa(s)}" for s in sources.values()]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
