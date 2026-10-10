#!/usr/bin/env python3
"""Tests for check_deck.py. Public CLI only."""

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).with_name("check_deck.py")


def run(html: str, *args: str, files: dict[str, str] | None = None):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / "deck.html"
        path.write_text(html, encoding="utf-8")
        for name, text in (files or {}).items():
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        proc = subprocess.run(
            [sys.executable, str(TOOL), str(path), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        return proc, before == after


GUIDE_OK = """<!DOCTYPE html>
<html data-mode="guide"><head><style>
html, body { font-size: 10.5pt; }
</style></head><body>
<section class="page" id="p1"><p>Texto.</p><a href="#p1">volver</a></section>
</body></html>
"""

DECK_OK = """<!DOCTYPE html>
<html data-mode="deck"><head><style>
p { font-size: 32px; }
.kicker { font-size: 26px; }
.title { font: 400 104px/1.02 Georgia, serif; }
</style></head><body>
<section class="slide" id="s1"><p class="kicker">SEMANA</p><h1 class="title">Título</h1><p>Una idea.</p></section>
</body></html>
"""


class CheckDeckTests(unittest.TestCase):
    def test_guide_pass_leaves_file_unchanged(self):
        proc, same = run(GUIDE_OK, "--mode", "guide", "--expect", "1")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(proc.stderr, "")
        self.assertTrue(same)
        self.assertEqual(
            proc.stdout,
            "count: pass\nanchors: pass\nfonts: local\nfont-size: pass\noverflow: skipped\n",
        )

    def test_deck_chrome_below_minimum_still_passes(self):
        proc, _ = run(DECK_OK, "--mode", "deck", "--expect", "1")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("font-size: pass", proc.stdout)

    def test_count_mismatch(self):
        proc, same = run(GUIDE_OK, "--mode", "guide", "--expect", "2")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, "")
        self.assertTrue(same)
        self.assertIn("count: expected 2, found 1", proc.stdout)
        self.assertNotIn("count: pass", proc.stdout)

    def test_deck_does_not_count_pages(self):
        html = GUIDE_OK.replace('data-mode="guide"', 'data-mode="deck"').replace(
            "10.5pt", "28px"
        )
        proc, _ = run(html, "--mode", "deck", "--expect", "1")
        self.assertIn("count: expected 1, found 0", proc.stdout)
        self.assertEqual(proc.returncode, 1)

    def test_missing_anchor(self):
        html = GUIDE_OK.replace('href="#p1"', 'href="#falta"')
        proc, _ = run(html, "--mode", "guide", "--expect", "1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("anchors: missing id for #falta", proc.stdout)

    def test_external_href_is_not_an_anchor(self):
        html = GUIDE_OK.replace(
            '<a href="#p1">volver</a>',
            '<a href="https://example.com/x#no">ext</a>',
        )
        proc, _ = run(html, "--mode", "guide", "--expect", "1")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_remote_font(self):
        html = GUIDE_OK.replace(
            "<style>",
            '<link href="https://fonts.googleapis.com/css2?family=X" rel="stylesheet"><style>',
        )
        proc, _ = run(html, "--mode", "guide", "--expect", "1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("fonts: remote fonts.googleapis.com", proc.stdout)

    def test_guide_body_below_minimum(self):
        proc, _ = run(GUIDE_OK.replace("10.5pt", "9pt"), "--mode", "guide", "--expect", "1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("font-size:", proc.stdout)
        self.assertNotIn("font-size: pass", proc.stdout)

    def test_deck_body_below_minimum(self):
        proc, _ = run(DECK_OK.replace("32px", "12px"), "--mode", "deck", "--expect", "1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("font-size:", proc.stdout)
        self.assertNotIn("font-size: pass", proc.stdout)

    def test_missing_body_size_fails(self):
        html = """<!DOCTYPE html><html><body>
<section class="slide" id="s1"><p>Una idea.</p></section>
</body></html>"""
        proc, _ = run(html, "--mode", "deck", "--expect", "1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("font-size: missing body size", proc.stdout)

    def test_outline_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            html = root / "deck.html"
            outline = root / "outline.txt"
            html.write_text(GUIDE_OK, encoding="utf-8")
            outline.write_text("# approved\n\nUna idea\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(TOOL), str(html), "--mode", "guide", "--outline", str(outline)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("count: pass", proc.stdout)

    def test_linked_font_must_exist(self):
        html = """<!DOCTYPE html><html><head>
<link rel="stylesheet" href="theme.css">
</head><body>
<section class="page" id="p1"><p>Texto.</p></section>
</body></html>"""
        css = """@font-face { font-family: "X"; src: url(fonts/missing.woff2) format("woff2"); }
html, body { font-size: 10.5pt; }"""
        proc, _ = run(html, "--mode", "guide", "--expect", "1", files={"theme.css": css})
        self.assertEqual(proc.returncode, 1)
        self.assertIn("fonts: missing fonts/missing.woff2", proc.stdout)

    def test_usage_without_count(self):
        proc, _ = run(GUIDE_OK, "--mode", "guide")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage:", proc.stderr)
        self.assertEqual(proc.stdout, "")


if __name__ == "__main__":
    unittest.main()
