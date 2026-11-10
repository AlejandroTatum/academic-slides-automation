#!/usr/bin/env python3
"""Output-format contract: guides are A4 portrait, decks ship an animated HTML
whose print render (the PDF) stays static."""

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent


def read(rel: str) -> str:
    return (SKILL / rel).read_text(encoding="utf-8")


class GuideIsA4Portrait(unittest.TestCase):
    def test_metro_page_rule_is_a4_portrait(self):
        css = read("themes/metro.css")
        self.assertRegex(css, r"@page\s*\{\s*size:\s*210mm 297mm;")
        page = re.search(r"\.page\s*\{([^}]*)\}", css).group(1)
        self.assertIn("width: 210mm", page)
        self.assertIn("height: 297mm", page)

    def test_no_landscape_guide_canvas_is_documented(self):
        for rel in ("SKILL.md", "DESIGN.md", "references/flow.md", "tools/speaker_guide.py", "shells/guide.html"):
            self.assertNotIn("297×167", read(rel), rel)
            self.assertNotIn("297x167", read(rel), rel)


class DeckHtmlIsAnimated(unittest.TestCase):
    def test_shell_links_animation_after_the_theme_and_the_nav_script(self):
        shell = read("shells/deck.html")
        self.assertIn('<link rel="stylesheet" href="../assets/anim/anim.css">', shell)
        self.assertIn('<script src="../assets/anim/anim.js"></script>', shell)
        self.assertLess(shell.index("themes/deportivo.css"), shell.index("anim/anim.css"))
        self.assertLess(shell.index("function show("), shell.index("anim/anim.js"))

    def test_animation_is_screen_only_and_never_in_print(self):
        css = read("assets/anim/anim.css")
        self.assertNotIn("<style", css)
        self.assertIn("prefers-reduced-motion: no-preference", css)
        rules = [r for r in re.findall(r"([^{}]+)\{", css) if ".slide" in r]
        self.assertTrue(rules)
        for selector in rules:
            for part in selector.split(","):
                self.assertIn("body:not(.print)", part, part)

    def test_animation_script_is_plain_js_and_skips_print(self):
        js = read("assets/anim/anim.js")
        self.assertNotIn("<script", js)
        self.assertIn("if (PRINT) return;", js)


if __name__ == "__main__":
    unittest.main()
