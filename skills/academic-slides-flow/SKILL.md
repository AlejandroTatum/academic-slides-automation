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
- Themes are `deportivo` and `metro` only. Propose one with a reason. A new theme is an explicit experiment, never a silent invention.
- Body text is ≥ 10.5 pt on guides and ≥ 28 px on decks. Every accent maps to a category the reader can name.
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
3. Propose the theme. Draft a one-line outline (component + message). Stop for gate 1.
4. Copy the shell, theme, `assets/fonts/`, and components into the destination. No ad-hoc CSS unless it becomes a component.
5. Run `tools/render.sh` and `tools/check_deck.py --mode … --outline … --dom`. Inspect thumbnails. Fix overflow and empty pages.
6. Show the PDF. Stop for gate 2.
7. If praised, harvest the element.

## Output Contract

Return the mode, theme, destination path, outline status, checker stdout, PDF path, and whether gate 2 is still open. Do not claim the deck is approved.

## References

- `references/flow.md` — intake, assembly, gates.
- `references/writing.md` — density, tone, `TIP`.
- `references/fonts.md` — local font files.
- `DESIGN.md` — proven theme tokens and the two source decks.
- `references/profiles/` — course profiles reused from `academic-report-flow`.
