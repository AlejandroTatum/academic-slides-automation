#!/usr/bin/env python3
"""Tests for outline.py. Public CLI only."""

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).parent
TOOL = TOOLS / "outline.py"
CHECK = TOOLS / "check_deck.py"

FOUR = """# Planificación de procesos
# duration: 10 min
# speakers: Ana, Luis
cover | Planificación de procesos | portada | Presentamos el tema.
icon-row | Qué decide el planificador | 3 íconos | Entra, dura, espera.
flow-steps | Ciclo de un proceso | 3 pasos | Nuevo, listo, ejecución.
recap | Para llevarse | 3 ideas | Repaso y preguntas.
"""


def run(text: str, *args: str):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "outline.txt"
        path.write_text(text, encoding="utf-8")
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        proc = subprocess.run([sys.executable, str(TOOL), str(path), *args], text=True, capture_output=True, check=False)
        return proc, before == hashlib.sha256(path.read_bytes()).hexdigest()


class OutlinePlanTests(unittest.TestCase):
    def test_four_field_plan_splits_duration_and_speakers(self):
        proc, same = run(FOUR)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(proc.stderr, "")
        self.assertTrue(same)
        self.assertEqual(
            proc.stdout,
            "plan: 4 slides · 10:00 · 2 speakers\n"
            "01  0:00  2:30  Ana   cover       Planificación de procesos\n"
            "02  2:30  2:30  Ana   icon-row    Qué decide el planificador\n"
            "03  5:00  2:30  Luis  flow-steps  Ciclo de un proceso\n"
            "04  7:30  2:30  Luis  recap       Para llevarse\n"
            "speaker: Ana 2 slides 5:00\n"
            "speaker: Luis 2 slides 5:00\n",
        )

    def test_explicit_speaker_and_time_win(self):
        text = FOUR.replace(
            "icon-row | Qué decide el planificador | 3 íconos | Entra, dura, espera.",
            "icon-row | Qué decide el planificador | 3 íconos | Entra, dura, espera. | Luis | 4:00",
        )
        proc, _ = run(text)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("01  0:00  2:00  Ana   cover", proc.stdout)
        self.assertIn("02  2:00  4:00  Luis  icon-row", proc.stdout)
        self.assertIn("03  6:00  2:00  Luis  flow-steps", proc.stdout)
        self.assertIn("04  8:00  2:00  Luis  recap", proc.stdout)

    def test_without_duration_each_slide_is_one_minute(self):
        text = "\n".join(l for l in FOUR.splitlines() if not l.startswith(("# duration", "# speakers"))) + "\n"
        proc, _ = run(text)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(proc.stdout.startswith("plan: 4 slides · 4:00 · 0 speakers\n"))
        self.assertIn("04  3:00  1:00  -  recap", proc.stdout)
        self.assertNotIn("speaker:", proc.stdout)

    def test_legacy_one_message_lines_still_work(self):
        proc, _ = run("# fixture\nUna idea\nOtra idea\n")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("plan: 2 slides · 2:00 · 0 speakers\n", proc.stdout)
        self.assertIn("01  0:00  1:00  -  -  Una idea\n", proc.stdout)

    def test_one_speaker_is_singular(self):
        text = FOUR.replace("# speakers: Ana, Luis", "# speakers: Ana")
        proc, _ = run(text)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(proc.stdout.startswith("plan: 4 slides · 10:00 · 1 speaker\n"), proc.stdout)
        self.assertIn("speaker: Ana 4 slides 10:00\n", proc.stdout)

    def test_long_message_and_odd_slide_count_are_notes_not_failures(self):
        text = FOUR.replace("Para llevarse", "Para llevarse estas tres ideas muy importantes del tema de hoy")
        text = text.replace("# duration: 10 min", "# duration: 20 min")
        proc, _ = run(text)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("note: line 7 message has 11 words (default 8)\n", proc.stdout)
        self.assertIn("note: 4 slides for 20:00 (about 1 per minute suggests 20)\n", proc.stdout)


class OutlineErrorTests(unittest.TestCase):
    def assertFails(self, text: str, line: str):
        proc, same = run(text)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertEqual(proc.stderr, "")
        self.assertTrue(same)
        self.assertIn(line + "\n", proc.stdout)
        self.assertNotIn("plan:", proc.stdout)

    def test_unknown_component(self):
        self.assertFails(FOUR.replace("recap |", "slideshow |"), "outline: line 7 unknown component slideshow")

    def test_wrong_field_count(self):
        self.assertFails(FOUR.replace("recap | Para llevarse | 3 ideas | Repaso y preguntas.", "recap | Para llevarse"),
                         "outline: line 7 needs 1 or 4-6 fields, found 2")

    def test_bad_time(self):
        self.assertFails(FOUR.replace("Repaso y preguntas.", "Repaso y preguntas. | Ana | dos"),
                         "outline: line 7 bad time dos")

    def test_unknown_speaker(self):
        self.assertFails(FOUR.replace("Repaso y preguntas.", "Repaso y preguntas. | Marta"),
                         "outline: line 7 speaker Marta is not in # speakers")

    def test_explicit_times_exceed_duration(self):
        self.assertFails(FOUR.replace("Repaso y preguntas.", "Repaso y preguntas. | Ana | 11:00"),
                         "outline: explicit times 11:00 exceed duration 10:00")

    def test_bad_duration(self):
        self.assertFails(FOUR.replace("# duration: 10 min", "# duration: diez"), "outline: bad duration diez")

    def test_usage(self):
        proc = subprocess.run([sys.executable, str(TOOL)], text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")
        self.assertIn("usage:", proc.stderr)


class CheckDeckOutlineTests(unittest.TestCase):
    def test_check_deck_counts_four_field_lines_and_skips_headers(self):
        slides = "".join(f'<section class="slide"><h1 class="title">S{i}</h1></section>' for i in range(4))
        html = f'<!DOCTYPE html><html data-mode="deck"><head><style>p {{ font-size: 32px; }}</style></head><body>{slides}</body></html>'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "deck.html").write_text(html, encoding="utf-8")
            (root / "outline.txt").write_text(FOUR, encoding="utf-8")
            proc = subprocess.run([sys.executable, str(CHECK), str(root / "deck.html"), "--mode", "deck",
                                   "--outline", str(root / "outline.txt")], text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("count: pass\n", proc.stdout)


if __name__ == "__main__":
    unittest.main()
