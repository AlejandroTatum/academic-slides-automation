#!/usr/bin/env python3
"""Build the component catalog: one deck per deck theme with every deck
component, plus index.html, a grid to pick components by sight at gate 1.

Reads shells/, themes/ and components/; writes only into --out
(default: catalog/ next to this tools/ folder). Exit 2 is usage.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
USAGE = "usage: build_catalog.py [--out DIR]"
# Catalog order: how a short talk usually flows.
COMPONENTS = [
    "cover", "question-hook", "icon-row", "big-number", "flow-steps",
    "figure-full", "formula-hero", "section-divider", "recap",
]
FIRST_THEMES = ["deportivo", "metro-deck"]
STYLE = re.compile(r"<style>.*?</style>", re.S)
LINK = re.compile(r'<link rel="stylesheet" href="(assets/[^"]+)">')
SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.S)
SLIDE = re.compile(r'<section class="slide[^"]*"[^>]*>.*?</section>', re.S)


class Usage(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # noqa: D401 - argparse hook
        print(USAGE, file=sys.stderr)
        sys.exit(2)


def deck_themes() -> list[str]:
    names = []
    for css in sorted((SKILL / "themes").glob("*.css")):
        if css.stem == "deck-base" or "297mm" in css.read_text(encoding="utf-8"):
            continue
        names.append(css.stem)
    return [n for n in FIRST_THEMES if n in names] + [n for n in names if n not in FIRST_THEMES]


def component_parts(name: str, prefix: str) -> tuple[str, list[str], list[str], str]:
    text = (SKILL / "components" / f"{name}.html").read_text(encoding="utf-8")
    slide = SLIDE.search(text)
    if not slide:
        raise SystemExit(f"catalog: {name} has no deck slide")
    styles = "\n".join(STYLE.findall(text))
    links = [f'<link rel="stylesheet" href="{prefix}{href}">' for href in LINK.findall(text)]
    scripts = [s.replace('src="assets/', f'src="{prefix}assets/') for s in SCRIPT.findall(text)]
    section = slide.group(0)
    section = re.sub(r'^(<section class="[^"]*")', rf'\1 data-component="{name}" data-window="{name.upper()}.EXE"', section, count=1)
    return styles, links, scripts, section


def build_deck(theme: str, prefix: str, sprite: str) -> str:
    shell = (SKILL / "shells" / "deck.html").read_text(encoding="utf-8")
    styles, links, scripts, slides = [], [], [], []
    for name in COMPONENTS:
        style, link, script, section = component_parts(name, prefix)
        styles.append(f"<!-- {name} -->\n{style}" if style else "")
        links.extend(l for l in link if l not in links)
        scripts.extend(script)
        slides.append(section)
    slides[0] = slides[0].replace('class="slide', 'class="slide active', 1)
    out = re.sub(r'<link rel="stylesheet" href="\.\./themes/deck-base\.css">\n<link rel="stylesheet" href="\.\./themes/[\w-]+\.css">',
                 f'<link rel="stylesheet" href="{prefix}themes/deck-base.css">\n'
                 f'<link rel="stylesheet" href="{prefix}themes/{theme}.css">\n' + "\n".join(links),
                 shell, count=1)
    out = out.replace("<title>Deck</title>", f"<title>Catalog · {theme}</title>", 1)
    out = out.replace("</head>", "\n".join(s for s in styles if s) + "\n</head>", 1)
    out = re.sub(r'<div id="stage">.*?<div id="notes"></div>',
                 lambda _: '<div id="stage">\n' + "\n".join(slides) + '\n  <div id="notes"></div>', out, count=1, flags=re.S)
    out = out.replace("<body>", "<body>\n" + sprite, 1)
    out = out.replace("</body>", "\n".join(scripts) + "\n</body>", 1)
    return out


def build_index(themes: list[str]) -> str:
    rows = []
    for theme in themes:
        cells = "".join(
            f'<a class="cell" href="{theme}.html#{n}" target="_blank">'
            f'<iframe src="{theme}.html#{n}" loading="lazy" tabindex="-1" title="{theme} {name}"></iframe>'
            f"<span>{n}. {name}</span></a>"
            for n, name in enumerate(COMPONENTS, start=1)
        )
        rows.append(f'<section><h2>{html.escape(theme)}</h2><div class="row">{cells}</div></section>')
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Catálogo de componentes</title>
<style>
body {{ margin: 0; background: #18181b; color: #e4e4e7; font: 15px/1.5 system-ui, sans-serif; }}
header {{ padding: 20px 28px; border-bottom: 1px solid #3f3f46; }}
h1 {{ margin: 0 0 4px; font-size: 20px; }} header p {{ margin: 0; color: #a1a1aa; }}
section {{ padding: 18px 28px; border-bottom: 1px solid #27272a; }}
h2 {{ margin: 0 0 10px; font-size: 17px; }}
.row {{ display: flex; gap: 12px; overflow-x: auto; padding-bottom: 6px; }}
.cell {{ flex: none; width: 320px; color: #a1a1aa; text-decoration: none; font-family: ui-monospace, monospace; font-size: 12px; }}
.cell iframe {{ display: block; width: 320px; height: 180px; border: 0; border-radius: 6px; pointer-events: none; background: #000; margin-bottom: 4px; }}
.cell:hover span {{ color: #fff; }}
</style></head><body>
<header><h1>Catálogo de componentes</h1>
<p>Cada fila es un tema; cada columna, un componente. Clic abre el deck en esa diapositiva (N muestra las notas).</p></header>
{"".join(rows)}
</body></html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = Usage(prog="build_catalog.py", usage=USAGE, add_help=False)
    parser.add_argument("--out", default=str(SKILL / "catalog"))
    args = parser.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    prefix = os.path.relpath(SKILL, out.resolve()).replace(os.sep, "/") + "/"
    sprite_text = (SKILL / "components" / "icon-sprite.html").read_text(encoding="utf-8")
    sprite = re.search(r'<svg [^>]*aria-hidden="true">.*?</svg>', sprite_text, re.S).group(0)
    themes = deck_themes()
    for theme in themes:
        (out / f"{theme}.html").write_text(build_deck(theme, prefix, sprite), encoding="utf-8")
    (out / "index.html").write_text(build_index(themes), encoding="utf-8")
    print(f"catalog: {len(themes)} themes, {len(COMPONENTS)} components -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
