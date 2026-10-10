# academic-slides-flow

Implement the designed skill. Do not overwrite university decks.

## Specs

S1. Two modes from DESIGN.md: `deck` (exposición, 1920×1080 px, keyboard nav, notes, live demos, `.html` + `.pdf` via `?print`) and `guide` (guía de estudio, 297×167 mm, internal PDF links, `.pdf` + source `.html`).

S2. Themes are the proven ones only: `deportivo` tokens `--blue #3D6BFF`, `--blue-l #7395FF`, `--yellow #FFD600`, `--gold #D9A800`, `--coal #131316`, `--ink #17181C`, `--paper #F4F4F7`, `--muted #6B6E7A`; `metro` tokens `--paper #F3EFE6`, `--paper-2 #E9E3D6`, `--ink #1B1B1F`, `--muted #6A665E`, `--rule #CFC7B6`, `--a #E4572E`, `--b #1F9E8F`, `--c #6C4FD1`, `--d #E9A21B`. Never invent a new theme silently.

S3. Hard rules: body text ≥ 10.5 pt on the guide canvas and ≥ 28 px on decks; color is never decorative; terms not in the user's source list are marked `TIP`; fonts are local, never `fonts.googleapis.com`; PDF keeps internal links; correct inaccurate source definitions before styling them.

S4. `check_deck.py` checks: page/slide count matches the approved outline; no element overflows its page when `--dom` is set; minimum font size per mode; every `href="#x"` has `id="x"`; fonts resolved locally.

S5. Components start with `terminal-block`, `concept-card`, `vs-pair`, plus the rest named in DESIGN.md. Shells: `deck.html` and `guide.html`.

S6. `SKILL.md` is the runtime contract (skill-creator structure). Two human gates only: outline, then visual review. Course profiles are reused from `academic-report-flow`, not copied.

## Tasks

- [x] T1 (S1-S3, S5) Extract themes, local fonts, and components. Route: inline. Commit: n/a (skill dir is not this git repo).
- [x] T2 (S4) `render.sh` + `check_deck.py` with tests. Route: inline. Commit: n/a.
- [x] T3 (S6) `SKILL.md`, references, profile symlink, fixture that passes the checker. Route: inline. Commit: n/a.

## Log

L1. desarollemos la skill de las diapositivas que quedaron pendientes
continua

L2. Original class decks stay untouched. Parity is a skill fixture, not a rewrite of `viaje-del-paquete.html` or `tipos-de-simulacion.html`.

L3. Chrome labels in the proven decks (kicker, footer, mono code) are below the body minimum. The checker enforces the minimum on body text, not on those chrome classes.
