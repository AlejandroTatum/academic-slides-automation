#!/usr/bin/env python3
"""Tests for icons.py. Public CLI only."""

import re
import subprocess
import sys
import unittest
from pathlib import Path

TOOL = Path(__file__).with_name("icons.py")
SPRITE = Path(__file__).resolve().parent.parent / "components" / "icon-sprite.html"


def run(*args: str):
    return subprocess.run([sys.executable, str(TOOL), *args], text=True, capture_output=True, check=False)


class SpriteTests(unittest.TestCase):
    def test_sprite_has_one_symbol_per_name_in_order(self):
        proc = run("sprite", "bot", "database", "log-in")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, "")
        out = proc.stdout
        self.assertTrue(out.startswith('<svg width="0" height="0" style="position:absolute" aria-hidden="true">\n'), out[:120])
        self.assertTrue(out.endswith("</svg>\n"))
        self.assertEqual(re.findall(r'<symbol id="(i-[\w-]+)" viewBox="0 0 24 24">', out), ["i-bot", "i-database", "i-log-in"])
        rect = re.search(r"<rect ([^>]*)/>", out).group(1)
        self.assertEqual(sorted(rect.split()), sorted('width="16" height="12" x="4" y="8" rx="2"'.split()))

    def test_duplicate_names_appear_once(self):
        proc = run("sprite", "bot", "bot")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.count('id="i-bot"'), 1)

    def test_unknown_name_fails_and_suggests(self):
        proc = run("sprite", "bot", "robott")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, "")
        self.assertTrue(proc.stdout.startswith("icons: unknown robott"), proc.stdout)
        self.assertNotIn("<svg", proc.stdout)


class SearchTests(unittest.TestCase):
    def test_search_matches_names_and_tags(self):
        proc = run("search", "robot")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        names = proc.stdout.split()
        self.assertIn("bot", names)  # matched by tag
        self.assertLessEqual(len(names), 20)

    def test_search_with_several_words_needs_all(self):
        proc = run("search", "database", "search")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("database-search", proc.stdout.split())
        self.assertNotIn("bot", proc.stdout.split())

    def test_search_without_hits(self):
        proc = run("search", "zzzqqq")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "icons: no match for zzzqqq\n")


class UsageAndSpriteFileTests(unittest.TestCase):
    def test_usage(self):
        for args in ((), ("sprite",), ("search",), ("nope", "bot")):
            proc = run(*args)
            self.assertEqual(proc.returncode, 2, args)
            self.assertEqual(proc.stdout, "")
            self.assertIn("usage:", proc.stderr)

    def test_default_sprite_component_is_generated_from_lucide(self):
        text = SPRITE.read_text(encoding="utf-8")
        ids = re.findall(r'<symbol id="i-([\w-]+)"', text)
        self.assertGreaterEqual(len(ids), 40)
        fresh = run("sprite", *ids)
        self.assertEqual(fresh.returncode, 0, fresh.stdout)
        self.assertIn(fresh.stdout.strip(), text)


if __name__ == "__main__":
    unittest.main()
