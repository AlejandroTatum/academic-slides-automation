#!/usr/bin/env python3
"""Mechanical checks for an academic-slides-flow deck or study guide.

Does not modify the HTML. Findings go to stdout, one per line. Exit 0 only
when every check passes. Exit 2 is usage. Exit 1 is a failed check.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

MIN_GUIDE_PT = 10.5
MIN_DECK_PX = 28.0
PT_PER_PX = 72.0 / 96.0
REMOTE_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")
CHROME_CLASSES = {
    "kicker",
    "foot",
    "code",
    "term",
    "note",
    "when",
    "go",
    "back",
    "mbar",
    "howto",
}
CHROME_TAGS = {"small"}
BODY_TAGS = {"html", "body", "p", "h1", "h2", "h3"}
BODY_CLASSES = {"title", "what", "lead"}
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
LENGTH = re.compile(r"(\d*\.?\d+)\s*(px|pt)\b", re.I)
URL = re.compile(r"url\(\s*['\"]?([^)'\"]+)", re.I)
USAGE = (
    "usage: check_deck.py HTML --mode deck|guide (--expect N | --outline FILE) [--dom]"
    " [--max-items N] [--max-words N]"
)
DOM_SCOPE = "page-boundary overflow only; not inter-element overlaps, composition, or visual quality"
MAX_ITEMS = 3
MAX_WORDS = 30
# Text inside these never counts toward slide density: it is spoken, chrome, or code.
DENSITY_SKIP_CLASSES = {"notes", "kicker", "foot", "katex"}
DENSITY_SKIP_TAGS = {"pre", "code", "script", "style", "svg", "math"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
WORD = re.compile(r"\w+", re.U)


class Density(HTMLParser):
    """Visible items and words per deck slide. An item is an <li> or a .item element."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[dict] = []
        self._stack: list[tuple[str, bool, bool]] = []  # tag, opens slide, skipped

    def _skipping(self) -> bool:
        return any(skip for _, _, skip in self._stack)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {key: value or "" for key, value in attrs}
        classes = set(ad.get("class", "").split())
        opens = "slide" in classes
        if opens:
            self.slides.append(
                {"id": ad.get("id", ""), "dense": "data-dense" in ad, "items": 0, "words": 0}
            )
        skip = bool(classes & DENSITY_SKIP_CLASSES) or tag in DENSITY_SKIP_TAGS
        if self.slides and self._in_slide(opens) and not skip and not self._skipping():
            if tag == "li" or "item" in classes:
                self.slides[-1]["items"] += 1
        if tag not in VOID_TAGS:
            self._stack.append((tag, opens, skip))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS and self._stack:
            self._stack.pop()

    def _in_slide(self, opening: bool = False) -> bool:
        return opening or any(opens for _, opens, _ in self._stack)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index][0] == tag:
                del self._stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if self.slides and self._in_slide() and not self._skipping():
            self.slides[-1]["words"] += len(WORD.findall(data))


def density_lines(html: str, max_items: int, max_words: int) -> list[str]:
    parser = Density()
    parser.feed(html)
    failures: list[str] = []
    counts: list[str] = []
    dense = 0
    for number, slide in enumerate(parser.slides, start=1):
        name = f"slide {number}" + (f" (#{slide['id']})" if slide["id"] else "")
        exempt = " (data-dense exempt)" if slide["dense"] else ""
        counts.append(f"density: {name}: {slide['items']} items, {slide['words']} words{exempt}")
        if slide["dense"]:
            dense += 1
            continue
        if slide["items"] > max_items:
            failures.append(f"density: {name} has {slide['items']} items (max {max_items})")
        if slide["words"] > max_words:
            failures.append(f"density: {name} has {slide['words']} words (max {max_words})")
    if failures:
        return counts + failures
    if dense:
        plural = "slide" if dense == 1 else "slides"
        return counts + [f"density: pass ({dense} dense {plural} allowed)"]
    return counts + ["density: pass"]


def positive(text: str) -> int:
    value = int(text)
    if value < 1:
        raise ValueError(text)
    return value


class Collected(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.slides = 0
        self.pages = 0
        self.styles: list[str] = []
        self.links: list[str] = []
        self._in_style = False
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {key: value or "" for key, value in attrs}
        if ad.get("id"):
            self.ids.add(ad["id"])
        if tag == "a" and ad.get("href"):
            self.hrefs.append(ad["href"])
        classes = set(ad.get("class", "").split())
        if "slide" in classes:
            self.slides += 1
        if "page" in classes:
            self.pages += 1
        if tag == "link" and "stylesheet" in ad.get("rel", "").split() and ad.get("href"):
            self.links.append(ad["href"])
        if tag == "style":
            self._in_style = True
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "style" and self._in_style:
            self.styles.append("".join(self._buf))
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self._buf.append(data)


def outline_count(path: Path) -> int:
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text and not text.startswith("#"):
            count += 1
    return count


def is_chrome(selector: str) -> bool:
    classes = set(re.findall(r"\.([A-Za-z_][\w-]*)", selector))
    tags = set(re.findall(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)", selector))
    return bool(classes & CHROME_CLASSES or {tag.lower() for tag in tags} & CHROME_TAGS)


def is_body(selector: str) -> bool:
    if is_chrome(selector):
        return False
    classes = set(re.findall(r"\.([A-Za-z_][\w-]*)", selector))
    tags = {tag.lower() for tag in re.findall(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)", selector)}
    return bool(tags & BODY_TAGS or classes & BODY_CLASSES)


def length_tokens(body: str) -> list[tuple[float, str]]:
    found: list[tuple[float, str]] = []
    for match in re.finditer(r"(?:^|;)\s*font-size\s*:\s*([^;]+)", body, re.I):
        found.extend((float(n), unit.lower()) for n, unit in LENGTH.findall(match.group(1)))
    for match in re.finditer(r"(?:^|;)\s*font\s*:\s*([^;]+)", body, re.I):
        found.extend((float(n), unit.lower()) for n, unit in LENGTH.findall(match.group(1)))
    return found


def to_pt(value: float, unit: str) -> float:
    return value if unit == "pt" else value * PT_PER_PX


def to_px(value: float, unit: str) -> float:
    return value if unit == "px" else value / PT_PER_PX


def font_findings(css: str, mode: str) -> list[str]:
    declared = False
    failures: list[str] = []
    for selector, body in RULE.findall(css):
        sizes = length_tokens(body)
        if not sizes:
            continue
        body_selectors = [part.strip() for part in selector.split(",") if is_body(part)]
        if not body_selectors:
            continue
        declared = True
        label = ", ".join(body_selectors)
        for value, unit in sizes:
            if mode == "guide":
                size = to_pt(value, unit)
                if size + 1e-6 < MIN_GUIDE_PT:
                    failures.append(
                        f"font-size: {label} is {value:g}{unit}, minimum {MIN_GUIDE_PT:g}pt"
                    )
            else:
                size = to_px(value, unit)
                if size + 1e-6 < MIN_DECK_PX:
                    failures.append(
                        f"font-size: {label} is {value:g}{unit}, minimum {MIN_DECK_PX:g}px"
                    )
    if not declared:
        return ["font-size: missing body size"]
    return failures or ["font-size: pass"]


def local_sheets(html_path: Path, doc: Collected) -> tuple[str, list[str]]:
    chunks = list(doc.styles)
    findings: list[str] = []
    for href in doc.links:
        if href.startswith(("http://", "https://", "//")):
            continue
        css_path = (html_path.parent / urllib.parse.unquote(href.split("?", 1)[0])).resolve()
        if not css_path.is_file():
            findings.append(f"fonts: missing {href}")
            continue
        text = css_path.read_text(encoding="utf-8")
        chunks.append(text)
        findings.extend(font_file_findings(css_path, text))
    for style in doc.styles:
        findings.extend(font_file_findings(html_path, style))
    return "\n".join(chunks), findings


def font_file_findings(base: Path, css: str) -> list[str]:
    findings: list[str] = []
    for raw in URL.findall(css):
        url = raw.strip()
        if url.startswith("data:"):
            continue
        if url.startswith(("http://", "https://", "//")):
            findings.append(f"fonts: remote {url}")
            continue
        target = (base.parent / urllib.parse.unquote(url.split("?", 1)[0])).resolve()
        if not target.is_file():
            findings.append(f"fonts: missing {url}")
    return findings


def font_lines(html: str, file_findings: list[str]) -> list[str]:
    hosts = [host for host in REMOTE_HOSTS if host in html]
    remote = [f"fonts: remote {host}" for host in hosts]
    remote.extend(item for item in file_findings if item.startswith("fonts: remote ") and item not in remote)
    missing = sorted({item for item in file_findings if item.startswith("fonts: missing ")})
    if remote or missing:
        return remote + missing
    return ["fonts: local"]


def anchor_lines(doc: Collected) -> list[str]:
    missing = []
    for href in doc.hrefs:
        if not href.startswith("#") or href == "#":
            continue
        target = urllib.parse.unquote(href[1:])
        if target not in doc.ids:
            missing.append(f"anchors: missing id for #{target}")
    return sorted(set(missing)) or ["anchors: pass"]


def dom_overflow(html_path: Path) -> list[str]:
    script = """
<script>
addEventListener('load', () => {
  const mode = document.documentElement.dataset.mode || '';
  const rootSel = mode === 'deck' ? '.slide' : '.page';
  const issues = [];
  const label = mode === 'deck' ? 'slide' : 'page';
  document.querySelectorAll(rootSel).forEach((root, index) => {
    const box = root.getBoundingClientRect();
    for (const el of root.querySelectorAll('*')) {
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 && rect.height === 0) continue;
      const dx = Math.max(box.left - rect.left, rect.right - box.right, 0);
      const dy = Math.max(box.top - rect.top, rect.bottom - box.bottom, 0);
      if (dx > 1 || dy > 1) {
        const cls = (el.getAttribute('class') || '').trim().split(/\\s+/).filter(Boolean).join('.');
        const name = el.id ? '#' + el.id : el.tagName + (cls ? '.' + cls : '');
        issues.push(label + ' ' + (index + 1) + ' ' + name + ' exceeds page');
      }
    }
  });
  const pre = document.createElement('pre');
  pre.id = 'check-report';
  pre.textContent = JSON.stringify(issues);
  document.body.appendChild(pre);
});
</script>
"""
    text = html_path.read_text(encoding="utf-8")
    # The copy lives in a temp dir; <base> keeps relative stylesheets, fonts and images resolving.
    base = f'<base href="{html_path.resolve().parent.as_uri()}/">'
    head = re.search(r"<head[^>]*>", text, re.I)
    text = text[: head.end()] + base + text[head.end():] if head else base + text
    if "</body>" in text:
        text = text.replace("</body>", script + "</body>", 1)
    else:
        text += script
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "check.html"
        copy.write_text(text, encoding="utf-8")
        try:
            proc = subprocess.run(
                [
                    "brave",
                    "--headless=new",
                    "--disable-gpu",
                    "--virtual-time-budget=4000",
                    "--dump-dom",
                    copy.as_uri(),
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return [f"overflow: error {exc.__class__.__name__}"]
    if proc.returncode != 0 and "check-report" not in proc.stdout:
        return [f"overflow: error brave exit {proc.returncode}"]
    match = re.search(r'<pre id="check-report">(.*?)</pre>', proc.stdout, re.S)
    if not match:
        return ["overflow: error no report"]
    import json

    issues = json.loads(match.group(1))
    if not issues:
        return ["overflow: pass"]
    return [f"overflow: {item}" for item in issues]


def passing(line: str) -> bool:
    if line.startswith("density: pass") or re.fullmatch(
        r"density: slide \d+(?: \(#[\s\S]*\))?: \d+ items, \d+ words(?: \(data-dense exempt\))?", line
    ):
        return True
    if line == f"overflow: scope: {DOM_SCOPE}":
        return True
    return line in {
        "count: pass",
        "anchors: pass",
        "fonts: local",
        "font-size: pass",
        "overflow: pass",
        "overflow: skipped",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="check_deck.py", usage=USAGE, add_help=False)
    parser.add_argument("html")
    parser.add_argument("--mode", choices=("deck", "guide"))
    parser.add_argument("--expect", type=int)
    parser.add_argument("--outline")
    parser.add_argument("--dom", action="store_true")
    parser.add_argument("--max-items")
    parser.add_argument("--max-words")
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args(argv)
    if args.help or not args.mode or (args.expect is None and not args.outline) or not args.html:
        print(USAGE, file=sys.stderr)
        if args.help:
            print(f"--dom: checks {DOM_SCOPE}", file=sys.stderr)
        return 2
    limits_given = args.max_items is not None or args.max_words is not None
    if limits_given and args.mode != "deck":
        print(USAGE, file=sys.stderr)
        return 2
    try:
        max_items = positive(args.max_items) if args.max_items is not None else MAX_ITEMS
        max_words = positive(args.max_words) if args.max_words is not None else MAX_WORDS
    except ValueError:
        print(USAGE, file=sys.stderr)
        return 2
    html_path = Path(args.html)
    expected = args.expect
    if args.outline:
        outlined = outline_count(Path(args.outline))
        if expected is not None and expected != outlined:
            print(USAGE, file=sys.stderr)
            return 2
        expected = outlined
    html = html_path.read_text(encoding="utf-8")
    doc = Collected()
    doc.feed(html)
    found = doc.slides if args.mode == "deck" else doc.pages
    lines = [f"count: pass" if found == expected else f"count: expected {expected}, found {found}"]
    lines.extend(anchor_lines(doc))
    css, file_findings = local_sheets(html_path, doc)
    lines.extend(font_lines(html + "\n" + css, file_findings))
    lines.extend(font_findings(css, args.mode))
    if args.mode == "deck":
        lines.extend(density_lines(html, max_items, max_words))
    if args.dom:
        lines.append(f"overflow: scope: {DOM_SCOPE}")
        lines.extend(dom_overflow(html_path))
    else:
        lines.append("overflow: skipped")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0 if all(passing(line) for line in lines) else 1


if __name__ == "__main__":
    sys.exit(main())
