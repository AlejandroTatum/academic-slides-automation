#!/usr/bin/env python3
"""Public outline and checker contracts for reusable content layouts."""
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TOOLS = SKILL / "tools"


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def classes(self, name):
        return [(tag, attrs) for tag, attrs in self.elements
                if name in attrs.get("class", "").split()]


class ContentLayouts(unittest.TestCase):
    def check_layout(self, name, required):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outline = root / "outline.txt"
            outline.write_text(f"{name} | Una idea concreta | Visual | Explicación\n", encoding="utf-8")
            plan = subprocess.run([sys.executable, str(TOOLS / "outline.py"), str(outline)], capture_output=True, text=True)
            self.assertEqual(plan.returncode, 0, plan.stdout + plan.stderr)
            self.assertEqual(plan.stderr, "")
            self.assertIn(name, plan.stdout)
            text = (SKILL / "components" / f"{name}.html").read_text(encoding="utf-8")
            parsed = Elements()
            parsed.feed(text)
            self.assertEqual(len(parsed.classes("slide")), 1)
            self.assertEqual(len(parsed.classes("notes")), 1)
            self.assertNotIn("data-dense", parsed.classes("slide")[0][1])
            for cls, count in required.items():
                self.assertEqual(len(parsed.classes(cls)), count, cls)
            deck = root / "deck.html"
            base = (SKILL / "themes" / "deck-base.css").read_text(encoding="utf-8")
            deck.write_text(f'<html data-mode="deck"><head><style>{base}</style></head><body>{text}</body></html>', encoding="utf-8")
            check = subprocess.run([sys.executable, str(TOOLS / "check_deck.py"), str(deck), "--mode", "deck", "--expect", "1"], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertEqual(check.stderr, "")
            self.assertIn("density: pass\n", check.stdout)
            self.assertIn("font-size: pass\n", check.stdout)
            self.assertIn("fonts: local\n", check.stdout)
            return parsed, text

    def assert_body_fills(self, text, body):
        """The body region grows into the space under the title instead of leaving a bottom band."""
        rule = re.search(r"\." + re.escape(body) + r"\)?\s*\{([^}]*)\}", text)
        self.assertIsNotNone(rule, body)
        self.assertRegex(rule.group(1), r"flex:\s*1\b", body)

    def test_comparison(self):
        parsed, text = self.check_layout("deck-compare", {"compare-side": 2, "compare-criterion": 1, "compare-takeaway": 1, "compare-trait": 4})
        self.assertIn("Ejemplo ilustrativo", text)
        self.assert_body_fills(text, "compare-pair")

    def test_case_relationship(self):
        parsed, text = self.check_layout("deck-case-map", {"case-node": 3, "case-link": 2, "case-role": 3})
        self.assertIn("Ejemplo ilustrativo", text)
        self.assertTrue(all(tag != "svg" for tag, _ in parsed.classes("case-node")))
        self.assert_body_fills(text, "case-map")

    def test_annotated_code(self):
        parsed, text = self.check_layout("deck-annotated-code", {"code-block": 1, "code-note": 3})
        self.assertIn("Ejemplo ilustrativo", text)
        self.assertEqual(parsed.classes("code-block")[0][0], "pre")
        lines = [attrs.get("data-line") for _, attrs in parsed.classes("code-note")]
        self.assertTrue(all(line and line.isdigit() for line in lines), lines)
        self.assertGreaterEqual(len([t for t, _ in parsed.elements if t == "span" ]), 5)
        self.assert_body_fills(text, "code-example")


if __name__ == "__main__":
    unittest.main()
