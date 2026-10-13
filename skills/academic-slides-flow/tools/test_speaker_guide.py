#!/usr/bin/env python3
"""Tests for speaker_guide.py. Public CLI only."""

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).parent
TOOL = TOOLS / "speaker_guide.py"
CHECK = TOOLS / "check_deck.py"

OUTLINE = """# Planificación de procesos
# duration: 10 min
# speakers: Ana, Luis
cover | Planificación de procesos | portada | Presentamos el tema.
icon-row | Qué decide el planificador | 3 íconos | Entra, dura, espera.
flow-steps | Ciclo de un proceso | 3 pasos | Nuevo, listo, ejecución.
big-number | El quantum | número | Diez a cien milisegundos.
recap | Para llevarse | 3 ideas | Repaso y preguntas.
"""


def deck(notes: list[str]) -> str:
    slides = "\n".join(
        f'<section class="slide"><h1 class="title">S{i}</h1>'
        + (f'<aside class="notes">{note}</aside>' if note else "")
        + "</section>"
        for i, note in enumerate(notes, start=1)
    )
    return f'<!DOCTYPE html><html data-mode="deck"><head></head><body><div id="stage">{slides}</div></body></html>'


DECK_NOTES = ["Hola, somos el grupo tres.", "", "El proceso cambia de estado.", "", "Cerramos con tres ideas."]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SpeakerGuideTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.deck = self.root / "index.html"
        self.outline = self.root / "outline.txt"
        self.deck.write_text(deck(DECK_NOTES), encoding="utf-8")
        self.outline.write_text(OUTLINE, encoding="utf-8")
        self.out = self.root / "guia-expositores.html"

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *extra: str):
        return subprocess.run([sys.executable, str(TOOL), str(self.deck), str(self.outline), *extra],
                              text=True, capture_output=True, check=False)

    def test_writes_a_separate_guide_that_passes_the_guide_checker(self):
        before = digest(self.deck), digest(self.outline)
        proc = self.run_tool()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(proc.stderr, "")
        self.assertEqual(
            proc.stdout,
            f"copied: themes/metro.css\ncopied: assets/fonts (9 files)\n"
            f"speaker-guide: 5 slides, 2 speakers, 3 pages -> {self.out}\n",
        )
        self.assertEqual(before, (digest(self.deck), digest(self.outline)))
        html = self.out.read_text(encoding="utf-8")
        self.assertIn('data-mode="guide"', html)
        self.assertIn('href="themes/metro.css"', html)
        check = subprocess.run([sys.executable, str(CHECK), str(self.out), "--mode", "guide", "--expect", "3"],
                               text=True, capture_output=True, check=False)
        self.assertEqual(check.returncode, 0, check.stdout)

    def test_guide_says_who_which_slide_how_long_and_what(self):
        self.assertEqual(self.run_tool().returncode, 0)
        html = self.out.read_text(encoding="utf-8")
        for text in ("Ana", "Luis", "0:00–2:00", "8:00–10:00", "Planificación de procesos", "Para llevarse"):
            self.assertIn(text, html)
        # deck notes win over outline notes; outline note fills a slide without deck notes
        self.assertIn("Hola, somos el grupo tres.", html)
        self.assertNotIn("Presentamos el tema.", html)
        self.assertIn("Entra, dura, espera.", html)
        # the split: Ana has 3 slides (6:00), Luis 2 (4:00)
        self.assertIn("Ana</b> · 3 diapositivas · 6:00", html)
        self.assertIn("Luis</b> · 2 diapositivas · 4:00", html)

    def test_existing_guide_is_not_overwritten_without_force(self):
        self.out.write_text("mine", encoding="utf-8")
        proc = self.run_tool()
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, f"speaker-guide: {self.out} exists (use --force)\n")
        self.assertEqual(self.out.read_text(encoding="utf-8"), "mine")
        self.assertEqual(self.run_tool("--force").returncode, 0)
        self.assertIn("Guía de expositores", self.out.read_text(encoding="utf-8"))

    def test_slide_count_mismatch_writes_nothing(self):
        self.deck.write_text(deck(DECK_NOTES[:4]), encoding="utf-8")
        proc = self.run_tool()
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "speaker-guide: deck has 4 slides, outline has 5\n")
        self.assertFalse(self.out.exists())
        self.assertFalse((self.root / "themes").exists())

    def test_outline_errors_are_reported_and_nothing_is_written(self):
        self.outline.write_text(OUTLINE.replace("recap |", "nope |"), encoding="utf-8")
        proc = self.run_tool()
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "outline: line 8 unknown component nope\n")
        self.assertFalse(self.out.exists())

    def test_custom_out_path(self):
        target = self.root / "ensayo" / "guia.html"
        proc = self.run_tool("--out", str(target))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(target.is_file())
        self.assertTrue((target.parent / "themes" / "metro.css").is_file())

    def test_reuses_the_theme_folder_the_deck_links(self):
        shared = self.root / "shared" / "themes"
        shared.mkdir(parents=True)
        (shared / "metro.css").write_text("html, body { font-size: 10.5pt; }", encoding="utf-8")
        text = deck(DECK_NOTES).replace("<head></head>", '<head><link rel="stylesheet" href="shared/themes/deck-base.css"></head>')
        self.deck.write_text(text, encoding="utf-8")
        proc = self.run_tool()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertNotIn("copied:", proc.stdout)
        self.assertFalse((self.root / "themes").exists())
        self.assertIn('href="shared/themes/metro.css"', self.out.read_text(encoding="utf-8"))

    def test_usage(self):
        proc = subprocess.run([sys.executable, str(TOOL), str(self.deck)], text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")
        self.assertIn("usage:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
