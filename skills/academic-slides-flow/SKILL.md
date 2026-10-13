---
name: academic-slides-flow
description: "Trigger: diapositivas, slides, deck, exposición, guía de estudio, study guide. Build university decks and study guides from proven themes."
license: Apache-2.0
metadata:
  author: "gentleman-programming"
  version: "1.0"
---

## Activation Contract

Use when creating or revising a university presentation deck or study guide. Do not use for reports, exercises, or figures alone (`academic-report-flow`, `academic-visual-builder`).

The user chooses the mode: `deck` (spoken, 1920×1080) or `guide` (read alone, 297×167 mm). Never infer it.

## Hard Rules

- Two human gates only: approved outline, then visual review of the PDF. Silence is not approval.
- Deck themes: proven `deportivo`, `terminal`; `metro-deck` (proven metro look, new on decks); experimental `pizarra`, `editorial`, `bauhaus`, `cuaderno`, `pop`, `retro`. Guide theme: `metro`. Propose one with a reason; say when it is experimental. Any other theme is an explicit experiment, never a silent invention.
- Body text is ≥ 10.5 pt on guides and ≥ 28 px on decks. Every accent maps to a category the reader can name.
- Decks are visual. Default: ≤ 3 items and ≤ 30 words per slide, as guiding text (title, one `.lead` line, a short `.desc` per item); the full speech goes in `.notes`. It is a default, not a limit: when the user or the content needs more, mark the slide `data-dense` or run the checker with `--max-items` / `--max-words` (`references/writing.md`).
- Mark terms absent from the user's source list as `TIP`. Correct inaccurate source definitions before styling them, and list each correction.
- Fonts are local files. Never use `fonts.googleapis.com`. Run `tools/render.sh` and `tools/check_deck.py` before showing work.
- Do not overwrite an existing deck or guide unless the user explicitly asks.
- Load a matching file in `references/profiles/` when one exists. Profile rules win.
- Artifact language follows the course repo. UNL courses are Spanish.

## Decision Gates

| Situation | Action |
|---|---|
| Mode or destination missing | Stop and ask. |
| User names a theme | Use it. |
| No theme named | Propose one with a reason; wait for accept or switch. |
| Outline not approved | Stop at gate 1. |
| Checker fails | Fix before showing the PDF. |
| PDF not reviewed | Stop at gate 2. |
| User praises an element | Harvest it into `components/` and note the source. |

## Execution Steps

1. Read `references/flow.md` and the matching profile, if any.
2. Intake: mode, subject, audience, duration or term list, sources, destination folder.
3. Deck: turn the duration into slides (about 1 per minute). Propose the theme. Show `catalog/index.html` so the user picks components by sight.
4. Draft the outline (`component | message | visual | spoken note [| speaker [| m:ss]]`), run `tools/outline.py`, show outline + plan. Stop for gate 1.
5. Copy the shell, `themes/deck-base.css` + the theme (or `metro.css` for a guide), `assets/fonts/`, `assets/katex/` if a formula is used, and the components into the destination. No ad-hoc CSS unless it becomes a component.
6. Run `tools/render.sh` and `tools/check_deck.py --mode … --outline … --dom`. Inspect thumbnails. Fix overflow, empty pages, and density.
7. Show the PDF. Stop for gate 2.
8. Group talk: build the speaker guide with `tools/speaker_guide.py` as a separate guide, render and check it.
9. If praised, harvest the element; a praised experimental theme becomes proven.

## Output Contract

Return the mode, theme (and whether it is experimental), destination path, outline status and plan, checker stdout, PDF path, speaker guide path if built, and whether gate 2 is still open. Do not claim the deck is approved.

## References

- `references/flow.md` — intake, assembly, gates.
- `references/writing.md` — density, tone, `TIP`.
- `references/fonts.md` — local font files.
- `DESIGN.md` — themes, token contract, components, tools.
- `catalog/` — every shared deck component in every deck theme (`live-demo` stays deportivo-only) (`tools/build_catalog.py` regenerates it).
- `tools/` — `check_deck.py`, `outline.py`, `icons.py` (Lucide search + sprite), `speaker_guide.py`, `build_catalog.py`, `render.sh`.
- `references/profiles/` — course profiles reused from `academic-report-flow`.
