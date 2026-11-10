#!/usr/bin/env python3
"""Build the speaker guide (guía de expositores) for a deck: a separate
study-guide document (guide mode, theme metro, A4 portrait 210x297 mm) that says who
speaks, on which slide, for how long, and what they say.

    speaker_guide.py DECK.html OUTLINE.txt [--out FILE] [--force]

The spoken text is the deck slide .notes; the outline note fills a slide
without notes. Times and speakers come from tools/outline.py. The guide is
written next to the deck as guia-expositores.html unless --out is given; it
copies themes/metro.css and its fonts beside it when they are missing. Render
the PDF with tools/render.sh. When the deck already links a themes/ folder
that holds metro.css, the guide links that one and copies nothing. Never overwrites an existing guide without
--force. Exit 1 on outline errors or a slide count mismatch, 2 for usage.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outline import Plan, clock, parse  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
USAGE = "usage: speaker_guide.py DECK OUTLINE [--out FILE] [--force]"
PAGE_WEIGHT = 6  # rows per A4 portrait page; a long note weighs more
LINES = ["a", "b", "c", "d"]
STYLE = """<style>
  .sg-cover h1 { font-family: var(--head); font-weight: 700; font-size: 40pt; line-height: .95; letter-spacing: -0.03em; margin: 6mm 0 3mm; }
  .sg-cover .lead { font-size: 12pt; color: var(--muted); }
  .sg-cast { list-style: none; margin-top: 8mm; display: grid; grid-template-columns: repeat(2, 1fr); gap: 3mm 8mm; }
  .sg-cast li { display: flex; justify-content: space-between; align-items: baseline; padding: 2.4mm 3mm; border-left: 1.4mm solid currentColor; background: #FBF9F4; }
  .sg-cast li p { color: var(--ink); }
  .sg-cast .k { font-family: var(--mono); font-size: 8pt; color: var(--muted); }
  .sg-rows { display: flex; flex-direction: column; gap: 2.6mm; }
  .sg-rows { gap: 3.4mm; }
  .sg-row { display: grid; grid-template-columns: 20mm 1fr; gap: 4mm; align-items: start; padding: 3mm 4mm; background: #FBF9F4;
    border: 0.3mm solid var(--rule); border-left: 1.4mm solid currentColor; border-radius: 1.6mm; }
  .sg-who { display: flex; justify-content: space-between; align-items: baseline; gap: 4mm; padding-bottom: 1.2mm; margin-bottom: 1.6mm; border-bottom: 0.3mm dashed var(--rule); }
  .sg-n { font-family: var(--head); font-weight: 700; font-size: 18pt; line-height: 1; color: var(--ink); }
  .sg-t { font-family: var(--mono); font-size: 8pt; color: var(--muted); display: block; margin-top: 1mm; }
  .sg-who p { font-weight: 600; }
  .sg-who .k { font-family: var(--mono); font-size: 8pt; color: var(--muted); }
  .sg-say h3 { font-family: var(--head); font-size: 12pt; line-height: 1.1; color: var(--ink); margin-bottom: 1mm; }
  .sg-say p { color: var(--ink); }
</style>"""


class Notes(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[str] = []
        self._depth = 0  # >0 while inside a .notes element
        self._stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        classes = set((dict(attrs).get("class") or "").split())
        if "slide" in classes:
            self.slides.append("")
        if tag in {"br", "img", "hr", "input", "meta", "link", "source", "wbr"}:
            return
        self._stack.append(tag)
        if "notes" in classes or self._depth:
            self._depth += 1

    def handle_endtag(self, tag):
        if tag in self._stack:
            while self._stack:
                popped = self._stack.pop()
                if self._depth:
                    self._depth -= 1
                if popped == tag:
                    break

    def handle_data(self, data):
        if self._depth and self.slides:
            self.slides[-1] += data


def deck_notes(path: Path) -> list[str]:
    parser = Notes()
    parser.feed(path.read_text(encoding="utf-8"))
    return [re.sub(r"\s+", " ", note).strip() for note in parser.slides]


def pages(rows: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    out, current, weight = [], [], 0
    for row in rows:
        w = 1 + len(row[1].split()) // 60
        if current and weight + w > PAGE_WEIGHT:
            out.append(current)
            current, weight = [], 0
        current.append(row)
        weight += w
    if current:
        out.append(current)
    return out


def color(plan: Plan, name: str) -> str:
    if name in plan.speakers:
        return LINES[plan.speakers.index(name) % len(LINES)]
    return "a"


def render(plan: Plan, notes: list[str], theme_href: str) -> tuple[str, int]:
    e = html.escape
    total = plan.duration if plan.duration is not None else plan.total
    title = plan.title or "Exposición"
    cast = []
    for name in plan.speakers:
        mine = [s for s in plan.slides if s.speaker == name]
        if not mine:
            continue
        span = f"{mine[0].number}–{mine[-1].number}" if len(mine) > 1 else f"{mine[0].number}"
        cast.append(
            f'<li class="fg-{color(plan, name)}"><a href="#s{mine[0].number}"><p><b>{e(name)}</b> · {len(mine)} diapositivas · '
            f'{clock(sum(s.seconds or 0 for s in mine))}</p></a><span class="k">{span}</span></li>'
        )
    cast_html = f'<ul class="sg-cast">{"".join(cast)}</ul>' if cast else (
        '<p class="lead">Sin reparto: agregá <b># speakers</b> al outline.</p>'
    )
    sections = [
        f'<section class="page sg-cover" id="reparto">\n'
        f'  <div class="stripe">{"".join(f"<span class=bg-{c}></span>" for c in LINES)}</div>\n'
        f'  <div class="kicker">Guía de expositores</div>\n  <h1>{e(title)}</h1>\n'
        f'  <p class="lead">{clock(total)} · {len(plan.slides)} diapositivas · {len(plan.speakers)} expositores</p>\n'
        f'  {cast_html}\n  <div class="foot"><span>Reparto</span><nav><a href="#s1">Diapositiva 1</a></nav></div>\n</section>'
    ]
    rows = []
    for slide, note in zip(plan.slides, notes):
        said = note or slide.note
        rows.append((slide.number, said))
    chunks = pages(rows)
    for index, chunk in enumerate(chunks, start=2):
        first, last = chunk[0][0], chunk[-1][0]
        items = []
        for number, said in chunk:
            s = plan.slides[number - 1]
            who = s.speaker or "—"
            end = s.start + (s.seconds or 0)
            items.append(
                f'<article class="sg-row fg-{color(plan, s.speaker)}" id="s{number}">'
                f'<div><span class="sg-n">{number:02d}</span><span class="sg-t">{clock(s.start)}–{clock(end)} · {clock(s.seconds or 0)}</span></div>'
                f'<div class="sg-say"><div class="sg-who"><p>{e(who)}</p><span class="k">{e(s.component)}</span></div>'
                f'<h3>{e(s.message)}</h3><p>{e(said)}</p></div></article>'
            )
        label = f"Diapositivas {first}–{last}" if first != last else f"Diapositiva {first}"
        sections.append(
            f'<section class="page" id="p{index}">\n'
            f'  <div class="top"><div><div class="kicker">{label}</div><h2>{e(title)}</h2></div></div>\n'
            f'  <div class="sg-rows">{"".join(items)}</div>\n'
            f'  <div class="foot"><span>{index}</span><nav><a href="#reparto">Reparto</a></nav></div>\n</section>'
        )
    doc = f"""<!DOCTYPE html>
<html lang="es" data-mode="guide">
<head>
<meta charset="utf-8">
<title>Guía de expositores · {e(title)}</title>
<link rel="stylesheet" href="{theme_href}">
{STYLE}
</head>
<body>
{chr(10).join(sections)}
</body>
</html>
"""
    return doc, len(sections)


def linked_metro(deck: Path, out_dir: Path) -> str | None:
    """metro.css in the themes/ folder the deck already links, relative to out_dir."""
    for href in re.findall(r'<link[^>]+href="([^"]*themes/)[\w-]+\.css"', deck.read_text(encoding="utf-8")):
        if href.startswith(("http:", "https:", "//")):
            continue
        candidate = (deck.parent / href / "metro.css").resolve()
        if candidate.is_file():
            return os.path.relpath(candidate, out_dir.resolve()).replace(os.sep, "/")
    return None


def ensure_theme(out_dir: Path) -> list[str]:
    copied = []
    css_target = out_dir / "themes" / "metro.css"
    source_css = SKILL / "themes" / "metro.css"
    if not css_target.is_file():
        css_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_css, css_target)
        copied.append("copied: themes/metro.css")
    fonts = sorted(set(re.findall(r"url\(\.\./assets/fonts/([^)]+)\)", source_css.read_text(encoding="utf-8"))))
    missing = [name for name in fonts if not (out_dir / "assets" / "fonts" / name).is_file()]
    if missing:
        (out_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
        for name in missing:
            shutil.copyfile(SKILL / "assets" / "fonts" / name, out_dir / "assets" / "fonts" / name)
        copied.append(f"copied: assets/fonts ({len(missing)} files)")
    return copied


class Usage(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print(USAGE, file=sys.stderr)
        sys.exit(2)


def main(argv: list[str] | None = None) -> int:
    parser = Usage(prog="speaker_guide.py", usage=USAGE, add_help=False)
    parser.add_argument("deck")
    parser.add_argument("outline")
    parser.add_argument("--out")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    deck, outline = Path(args.deck), Path(args.outline)
    if not deck.is_file() or not outline.is_file():
        print(USAGE, file=sys.stderr)
        return 2
    plan = parse(outline)
    if plan.errors:
        sys.stdout.write("\n".join(plan.errors) + "\n")
        return 1
    notes = deck_notes(deck)
    if len(notes) != len(plan.slides):
        print(f"speaker-guide: deck has {len(notes)} slides, outline has {len(plan.slides)}")
        return 1
    out = Path(args.out) if args.out else deck.parent / "guia-expositores.html"
    if out.exists() and not args.force:
        print(f"speaker-guide: {out} exists (use --force)")
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    theme_href = linked_metro(deck, out.parent)
    copied = [] if theme_href else ensure_theme(out.parent)
    doc, count = render(plan, notes, theme_href or "themes/metro.css")
    out.write_text(doc, encoding="utf-8")
    lines = copied + [f"speaker-guide: {len(plan.slides)} slides, {len(plan.speakers)} speakers, {count} pages -> {out}"]
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
