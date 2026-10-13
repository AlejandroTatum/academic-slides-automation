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


def deck(*slides: str) -> str:
    body = "\n".join(slides)
    return DECK_OK.replace(
        '<section class="slide" id="s1"><p class="kicker">SEMANA</p><h1 class="title">Título</h1><p>Una idea.</p></section>',
        body,
    )


FOUR_ITEMS = '<section class="slide" id="s1"><h1 class="title">Lista</h1><ul><li>uno</li><li>dos</li><li>tres</li><li>cuatro</li></ul></section>'
WORDY = (
    '<section class="slide" id="s1"><h1 class="title">Título</h1><p>'
    + " ".join(f"palabra{i}" for i in range(24))
    + "</p></section>"
)


class DensityTests(unittest.TestCase):
    def test_too_many_items_fails_and_names_slide(self):
        proc, same = run(deck(FOUR_ITEMS), "--mode", "deck", "--expect", "1")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, "")
        self.assertTrue(same)
        self.assertIn("density: slide 1 (#s1) has 4 items (max 3)\n", proc.stdout)
        self.assertNotIn("density: pass", proc.stdout)

    def test_too_many_words_fails(self):
        proc, same = run(deck(WORDY), "--mode", "deck", "--expect", "1")
        self.assertEqual(proc.returncode, 1)
        self.assertTrue(same)
        self.assertIn("density: slide 1 (#s1) has 25 words (max 20)\n", proc.stdout)

    def test_three_items_twenty_words_pass(self):
        slide = (
            '<section class="slide"><h1 class="title">Tres cosas</h1>'
            "<ul><li>uno</li><li>dos</li><li>tres</li></ul>"
            "<p>" + " ".join(["w"] * 15) + "</p></section>"
        )
        proc, _ = run(deck(slide), "--mode", "deck", "--expect", "1")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("density: pass\n", proc.stdout)

    def test_unnamed_slide_uses_position_only(self):
        slide = FOUR_ITEMS.replace(' id="s1"', "")
        ok = '<section class="slide"><h1 class="title">Ok</h1></section>'
        proc, _ = run(deck(ok, slide), "--mode", "deck", "--expect", "2")
        self.assertIn("density: slide 2 has 4 items (max 3)\n", proc.stdout)

    def test_item_class_counts_as_item(self):
        slide = '<section class="slide"><div class="item">a</div><div class="item">b</div><div class="item">c</div><div class="item">d</div></section>'
        proc, _ = run(deck(slide), "--mode", "deck", "--expect", "1")
        self.assertIn("density: slide 1 has 4 items (max 3)", proc.stdout)

    def test_notes_kicker_foot_and_code_do_not_count(self):
        many = " ".join(["x"] * 40)
        slide = (
            '<section class="slide"><p class="kicker">' + many + "</p>"
            '<h1 class="title">Idea</h1><pre>' + many + "</pre><code>" + many + "</code>"
            '<aside class="notes">' + many + "<ul><li>a</li><li>b</li><li>c</li><li>d</li></ul></aside>"
            '<div class="foot"><span>' + many + "</span></div></section>"
        )
        proc, _ = run(deck(slide), "--mode", "deck", "--expect", "1")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("density: pass\n", proc.stdout)

    def test_dense_slide_is_allowed(self):
        slide = FOUR_ITEMS.replace('class="slide"', 'class="slide" data-dense')
        proc, same = run(deck(slide, WORDY.replace('id="s1"', 'id="s2" data-dense')), "--mode", "deck", "--expect", "2")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(same)
        self.assertIn("density: pass (2 dense slides allowed)\n", proc.stdout)

    def test_max_items_and_words_raise_the_default(self):
        proc, _ = run(deck(FOUR_ITEMS), "--mode", "deck", "--expect", "1", "--max-items", "4")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("density: pass\n", proc.stdout)
        proc, _ = run(deck(WORDY), "--mode", "deck", "--expect", "1", "--max-words", "25")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        proc, _ = run(deck(FOUR_ITEMS), "--mode", "deck", "--expect", "1", "--max-items", "2")
        self.assertIn("density: slide 1 (#s1) has 4 items (max 2)", proc.stdout)

    def test_raised_limit_still_fails_above_it(self):
        proc, _ = run(deck(WORDY), "--mode", "deck", "--expect", "1", "--max-words", "24")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("density: slide 1 (#s1) has 25 words (max 24)", proc.stdout)

    def test_limits_are_deck_only_and_positive(self):
        for args in (
            ("--mode", "guide", "--expect", "1", "--max-items", "5"),
            ("--mode", "deck", "--expect", "1", "--max-items", "0"),
            ("--mode", "deck", "--expect", "1", "--max-words", "-3"),
            ("--mode", "deck", "--expect", "1", "--max-words", "x"),
        ):
            proc, same = run(GUIDE_OK if "guide" in args else DECK_OK, *args)
            self.assertEqual(proc.returncode, 2, args)
            self.assertEqual(proc.stdout, "", args)
            self.assertIn("usage:", proc.stderr)
            self.assertTrue(same)

    def test_guide_output_has_no_density_line(self):
        proc, _ = run(GUIDE_OK.replace("Texto.", " ".join(["t"] * 80)), "--mode", "guide", "--expect", "1")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertNotIn("density", proc.stdout)


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

    def test_deck_pass_output_order(self):
        proc, same = run(DECK_OK, "--mode", "deck", "--expect", "1")
        self.assertTrue(same)
        self.assertEqual(
            proc.stdout,
            "count: pass\nanchors: pass\nfonts: local\nfont-size: pass\ndensity: pass\noverflow: skipped\n",
        )

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

    def test_dom_overflow_uses_the_linked_stylesheet(self):
        html = """<!DOCTYPE html><html data-mode="deck"><head>
<link rel="stylesheet" href="themes/t.css">
</head><body>
<section class="slide" id="s1"><p class="wide">Ancho.</p></section>
</body></html>"""
        css = """p { font-size: 32px; }
.slide { position: relative; width: 1920px; height: 1080px; overflow: hidden; }
.wide { width: 2600px; }"""
        proc, same = run(html, "--mode", "deck", "--expect", "1", "--dom", files={"themes/t.css": css})
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertTrue(same)
        self.assertIn("overflow: slide 1 P.wide exceeds page\n", proc.stdout)

    def test_dom_overflow_passes_when_the_linked_stylesheet_fits(self):
        html = """<!DOCTYPE html><html data-mode="deck"><head>
<link rel="stylesheet" href="themes/t.css">
</head><body>
<section class="slide" id="s1"><svg class="icon" width="2600" height="10"></svg></section>
</body></html>"""
        css = """p { font-size: 32px; }
.slide { position: relative; width: 1920px; height: 1080px; overflow: hidden; }
.icon { width: 200px; }"""
        proc, _ = run(html, "--mode", "deck", "--expect", "1", "--dom", files={"themes/t.css": css})
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("overflow: pass\n", proc.stdout)

    def test_usage_without_count(self):
        proc, _ = run(GUIDE_OK, "--mode", "guide")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("usage:", proc.stderr)
        self.assertEqual(proc.stdout, "")


if __name__ == "__main__":
    unittest.main()
