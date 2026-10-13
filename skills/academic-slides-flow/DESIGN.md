# academic-slides-flow — design record

Status: MVP implemented 2026-10-09. Visual components, nine deck themes,
outline time budget and speaker guide added 2026-10-13
(`odd/tasks/visual-components-and-flow.md` in the repo). `SKILL.md` is the
runtime contract; this file stays the design record.

## Goal

Produce university **presentation decks** and **study guides** with a consistent,
proven visual style, reusing themes and components that already worked in class
instead of designing from scratch each time.

Sibling of `academic-report-flow`, but deliberately lighter: a deck fails by being
messy or inconsistent, not by lacking citations. No rubric TDD, no judge loop.

## Two deliverable modes

| | `deck` (exposición) | `guide` (guía de estudio) |
|---|---|---|
| Purpose | Projected, spoken over | Read alone, reviewed for exams |
| Density | Low: one idea per slide | High: cards, tables, quiz |
| Canvas | 1920×1080 px | 297×167 mm (16:9, printable) |
| Interaction | Keyboard nav, speaker notes (`N`), live demos | Internal PDF links: map → card, question ↔ answer |
| Companion | `guia-expositores` (who says what, timing) | Spaced-review sheet (days 1/3/7/14) |
| Output | `.html` (present) + `.pdf` (`?print`) | `.pdf` (+ source `.html`) |

## Proven references (the "models that already worked")

1. **Theme `deportivo`** — Simulación, Semana 2 deck. Loved by the class.
   - Source: `~/Documents/Universidad/Ciclo-5/simulacion/unidad-1/exposicion-semana-2-tipos-de-simulacion/`
   - Fonts: Graduate (display), Barlow (text); local in `assets/fonts/` (works offline).
   - Tokens: `--blue #3D6BFF`, `--blue-l #7395FF`, `--yellow #FFD600`, `--gold #D9A800`,
     `--coal #131316`, `--ink #17181C`, `--paper #F4F4F7`, `--muted #6B6E7A`.
   - Slide variants: `slide`, `slide dark`, `slide blue`, `slide yellow`.
   - Wins: live simulations with configurable seed, speaker notes, keyboard
     nav, `?print` mode for PDF, separate presenter guide.
2. **Theme `metro`** — Redes study guide "El viaje del paquete". User loved typography,
   order, and the terminal/code block.
   - Source: `~/Documents/Universidad/Ciclo-5/fundamentos-de-redes/estudio/viaje-del-paquete/`
   - Fonts: Space Grotesk (display), IBM Plex Sans (text), IBM Plex Mono (code/labels).
   - Tokens: `--paper #F3EFE6`, `--paper-2 #E9E3D6`, `--ink #1B1B1F`, `--muted #6A665E`,
     `--rule #CFC7B6`; four category colors `--a #E4572E`, `--b #1F9E8F`,
     `--c #6C4FD1`, `--d #E9A21B`.
   - Wins: category color = meaning, metro-map index, mono kickers, numbered steps.

## Deck themes and the token contract (2026-10-13)

Deck themes sit on `themes/deck-base.css`, which owns the deck chrome (stage,
slide, notes, print) and reads only tokens:

| Token | Meaning |
|---|---|
| `--bg` `--fg` `--muted` | slide surface, text, secondary text |
| `--a1` `--a2` `--a3` | three named accents (category colors) |
| `--alt-bg` `--alt-fg` | inverse slide (`.slide.alt`): cover, section, question |
| `--display` `--body` `--mono` | font stacks |
| `--dw` `--tt` `--ls` | display weight, title transform, title tracking |

A theme file sets the tokens and its decoration. Deck components style
themselves with `:where(...)` selectors (specificity 0) and tokens only, so any
theme can override them and every component works in every deck theme.

| Theme | Status | Source |
|---|---|---|
| `deportivo` | proven | Simulación Semana 2 deck (self-contained; maps its tokens to the contract) |
| `metro-deck` | proven look | the metro guide palette on the deck canvas |
| `pizarra`, `editorial`, `terminal`, `bauhaus`, `cuaderno`, `pop`, `retro` | experimental | picked by the user from `proposals/slide-themes.html` (repo) |

An experimental theme becomes proven when a real deck in it passes gate 2.
`metro.css` stays the guide theme.

## Visual deck components (2026-10-13)

Default density: 3 items and 20 words per slide, checked by `check_deck.py`;
`data-dense` or `--max-items` / `--max-words` lift it when the user or the
content needs more. New components, all deck, all themes: `big-number`,
`icon-row` (+ `icon-sprite`, 28 stroke icons), `flow-steps`, `question-hook`,
`recap`, `figure-full`, `formula-hero` (local KaTeX). `cover` and
`section-divider` gained a token-based deck variant.

## Flow tools (2026-10-13)

- `tools/build_catalog.py` → `catalog/<theme>.html` + `catalog/index.html`, so
  components are picked by sight at gate 1.
- `tools/outline.py` → reads `component | message | visual | spoken note
  [| speaker [| m:ss]]` plus `# duration:` / `# speakers:` and prints the
  time and speaker plan (about one slide per minute).
- `tools/speaker_guide.py` → the guía de expositores as a separate guide
  document (theme `metro`): who speaks, which slide, how long, what they say.

## Folder layout (original MVP target)

```
academic-slides-flow/
├── SKILL.md                  # activation, flow, hard rules (≤ 80 lines)
├── themes/
│   ├── deportivo.css         # tokens + base slide variants
│   └── metro.css
├── components/               # one HTML snippet + CSS per proven pattern
│   ├── cover.html
│   ├── section-divider.html
│   ├── terminal-block.html   # command + highlighted output + concept tags (favorite)
│   ├── concept-card.html     # definition + "Imaginalo" analogy + "Ojo" trap
│   ├── vs-pair.html          # A vs B + one-line rule
│   ├── timeline-steps.html   # numbered journey/process
│   ├── metro-index.html      # clickable map of topics
│   ├── quiz-linked.html      # question ↔ answer anchors
│   ├── live-demo.html        # seeded simulation widget (deck only)
│   └── nav-footer.html
├── shells/
│   ├── deck.html             # keyboard nav, notes overlay, ?print mode
│   └── guide.html            # @page 297x167mm, anchors
├── tools/
│   ├── render.sh             # Brave/Chrome headless → PDF, then pdftoppm thumbnails
│   └── check_deck.py         # mechanical checks (see Hard rules)
└── references/
    ├── flow.md               # step-by-step for each mode
    ├── writing.md            # tone, density, "extra" marking
    └── profiles → ../academic-report-flow/references/profiles  (reuse, do not copy)
```

## Flow (two human gates only)

1. **Intake** — mode (`deck`/`guide`), subject, topic, audience, duration or term list,
   source material (teacher slides, video notes). Load the matching course profile
   from `academic-report-flow/references/profiles/` when one exists.
2. **Theme** — propose one theme with a reason; the user may pick another.
   Never invent a new theme silently: a new theme is an explicit experiment.
3. **Outline → GATE 1** — one line per slide/page: component + key message.
   Correct factual errors in the source material here and list them for the user.
4. **Build** — assemble shell + theme + components. No ad-hoc CSS outside the
   theme unless it becomes a new component.
5. **Render + self-check** — `tools/render.sh`, then `check_deck.py`, then inspect
   thumbnails; fix overflow and empty pages before showing anything.
6. **Visual review → GATE 2** — the user reviews the PDF.
7. **Harvest** — if the user praises a specific element, extract it into
   `components/` (or tokens into `themes/`) and note the source deck. This is
   how the library grows.

## Hard rules (lessons already paid for)

- Body text ≥ 10.5 pt on the 297×167 mm guide canvas; ≥ 28 px on 1920×1080 decks.
  Smaller text leaves pages visually empty.
- Color is never decorative: every accent maps to a category the reader can name.
- Terms or concepts not in the user's source list are marked `TIP`/extra.
- Fonts are local (`assets/fonts/`); never depend on Google Fonts at render time.
- PDF must keep internal links (Chromium headless preserves `<a href="#id">`).
- Correct inaccurate source definitions before styling them; flag each correction.
- Artifact language follows the course repo `AGENTS.md` (UNL courses: Spanish).
- Course-specific rules from profiles win (e.g. Simulación: bibliography = slides only).

## `check_deck.py` (MVP scope)

- Page/slide count matches the approved outline.
- No element overflows its page (render-time bounding box check via headless DOM).
- Minimum font size per mode.
- Every `href="#x"` has a matching `id="x"`.
- Fonts resolved locally (no `fonts.googleapis.com` in the HTML).

## Out of scope for the MVP

- PPTX export (add later via a separate converter if a teacher demands it).
- Automatic image generation; use `academic-visual-builder` when figures are needed.
- New themes beyond the nine deck themes and the metro guide theme.

## MVP implementation order (done 2026-10-09)

1. Extract `deportivo.css` and `metro.css` from the two source files.
2. Extract components, starting with `terminal-block`, `concept-card`, `vs-pair`.
3. Build `shells/guide.html` and rebuild the Redes guide from components (proof of parity).
4. Build `shells/deck.html` from the Simulación deck and rebuild one slide set.
5. Write `render.sh` and `check_deck.py`.
6. Write `SKILL.md` (use `skill-creator`), then register via `skill-registry`.
