#!/usr/bin/env python3
"""Tests for build_catalog.py. Public CLI only."""

import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).parent
SKILL = TOOLS.parent
BUILD = TOOLS / "build_catalog.py"
CHECK = TOOLS / "check_deck.py"
DECK_THEMES = {"deportivo", "metro-deck", "pizarra", "editorial", "terminal", "bauhaus", "cuaderno", "pop", "retro", "plano-lavanda", "plano-durazno", "plano-menta"}
COMPONENTS = [
    "cover", "question-hook", "icon-row", "big-number", "flow-steps",
    "deck-case-map", "deck-compare", "figure-full", "formula-hero",
    "deck-annotated-code", "section-divider", "recap",
    "avatar-cards", "block-opener", "demo-script", "evidence-frame",
    "pipeline-flow", "rail-timeline", "scatter-cards", "sheet-frame",
    "stair-steps", "stat-hero",
]


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def build(*args: str):
    return subprocess.run([sys.executable, str(BUILD), *args], text=True, capture_output=True, check=False)


class BuildCatalogTests(unittest.TestCase):
    def test_writes_one_deck_per_theme_and_an_index(self):
        before = tree_hash(SKILL / "components"), tree_hash(SKILL / "themes")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = build("--out", str(out))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stderr, "")
            self.assertEqual(proc.stdout, f"catalog: {len(DECK_THEMES)} themes, {len(COMPONENTS)} components -> {out}\n")
            written = {p.stem for p in out.glob("*.html")}
            self.assertEqual(written, DECK_THEMES | {"index"})
            self.assertEqual(before, (tree_hash(SKILL / "components"), tree_hash(SKILL / "themes")))

    def test_each_deck_has_every_component_in_order_and_passes_the_checker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets").symlink_to(SKILL / "assets", target_is_directory=True)
            out = root / "catalog"
            self.assertEqual(build("--out", str(out)).returncode, 0)
            for theme in DECK_THEMES:
                deck = out / f"{theme}.html"
                html = deck.read_text(encoding="utf-8")
                self.assertIn(f'themes/{theme}.css"', html)
                self.assertIn('themes/deck-base.css"', html)
                body = html.split("<body>", 1)[1]
                self.assertTrue(body.lstrip().startswith('<svg width="0" height="0"'), theme)
                self.assertEqual(body.count('<symbol id="i-'), (SKILL / "components" / "icon-sprite.html").read_text().count('<symbol id="i-'))
                ids = re.findall(r'<section class="slide[^"]*"[^>]*\bdata-component="([\w-]+)"', html)
                self.assertEqual(ids, COMPONENTS, theme)
                check = subprocess.run(
                    [sys.executable, str(CHECK), str(deck), "--mode", "deck", "--expect", str(len(COMPONENTS))],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(check.returncode, 0, f"{theme}\n{check.stdout}")

    def test_index_frames_every_slide_of_every_theme(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertEqual(build("--out", str(out)).returncode, 0)
            index = (out / "index.html").read_text(encoding="utf-8")
            for theme in DECK_THEMES:
                for number in range(1, len(COMPONENTS) + 1):
                    self.assertIn(f'src="{theme}.html#{number}"', index)
            for name in COMPONENTS:
                self.assertIn(name, index)

    def test_catalog_covers_eligible_component_files(self):
        components = SKILL / "components"
        files = {p.stem: p.read_text(encoding="utf-8") for p in components.glob("*.html")}
        # Sprite is an embedded helper; live-demo is theme-specific; reveal-steps
        # requires shell key-handler integration even though it contains an example slide.
        excluded = {"icon-sprite", "live-demo", "reveal-steps"}
        self.assertTrue(excluded <= files.keys())
        self.assertIn("deck, every theme", files["icon-sprite"].splitlines()[0])
        self.assertIn("theme: deportivo", files["live-demo"].splitlines()[0])
        self.assertIn("add revealStep() to the shell keydown handler", files["reveal-steps"])
        eligible = {
            name for name, text in files.items()
            if name not in excluded and "deck, every theme" in text.splitlines()[0]
            and re.search(r'<section class="slide(?:\s|"|$)', text)
        }
        self.assertTrue(eligible)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = build("--out", str(out))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stderr, "")
            index = (out / "index.html").read_text(encoding="utf-8")
            for theme in DECK_THEMES:
                html = (out / f"{theme}.html").read_text(encoding="utf-8")
                names = re.findall(r'<section class="slide[^"]*"[^>]*\bdata-component="([\w-]+)"', html)
                self.assertEqual(set(names), eligible, theme)
                self.assertEqual(len(names), len(eligible), theme)
                for number, name in enumerate(names, 1):
                    self.assertIn(f'<iframe src="{theme}.html#{number}" loading="lazy" tabindex="-1" title="{theme} {name}"></iframe>', index)
                    self.assertIn(f'<span>{number}. {name}</span>', index)
                self.assertTrue(excluded.isdisjoint(names), theme)
            self.assertEqual(proc.stdout, f"catalog: {len(DECK_THEMES)} themes, {len(eligible)} components -> {out}\n")

    def test_unknown_option_is_usage(self):
        proc = build("--nope")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")
        self.assertIn("usage:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
