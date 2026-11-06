# Flow

Two gates. Do not build before gate 1. Do not claim approval before gate 2.

## Intake

Record mode (`deck` or `guide`), subject, audience, duration or term list, source files, and the destination folder. If the user did not name the mode or the folder, ask and stop.

Load `references/profiles/` when a profile `match:` fits the subject. Profile rules win. Simulación bibliography is the teacher slides only when that profile says so.

Do not overwrite an existing HTML or PDF in that folder unless the user explicitly asks.

## Theme

`deck` defaults to `deportivo` (projected, high contrast, live demo). `guide` defaults to `metro` (read alone, category color, terminal block). Propose that default with one reason, or a better fit from the deck themes:

| Deck theme | Status | Fits |
|---|---|---|
| `deportivo` | proven | energy, live demos |
| `metro-deck` | proven look, new on decks | the metro guide look on a deck, category color |
| `pizarra` | experimental | math, simulation, formulas |
| `editorial` | experimental | theory, readings |
| `terminal` | proven (Engram deck, 2026-10-13) | programming, commands, networks |
| `bauhaus` | experimental | strong openings, key concepts |
| `cuaderno` | experimental | reviews, intro classes |
| `pop` | experimental | waking up the room, dynamics |
| `retro` | experimental | operating systems, history of computing |
| `plano-lavanda`, `plano-durazno`, `plano-menta` | experimental | diagrams, data models, systems; one technical-sheet look, pick the palette |

Say when the proposal is experimental. If the user names a theme, use it. Do not invent another theme silently.

## Time budget

For a `deck`, turn the duration into slides: about **one slide per minute**. A 10-minute talk is about 10 slides. Note the speakers when it is a group talk.

## Gate 1 — outline

Open `catalog/index.html` (every shared deck component in every deck theme; `live-demo` is deportivo-only) so the user picks components by sight.

One line per slide or page. Components live in `components/`. Deck outlines use four fields, plus an optional speaker and time:

```
# Estados de un proceso
# duration: 10 min
# speakers: Ana, Luis
cover | Estados de un proceso | portada | Presentamos el tema y el grupo.
flow-steps | Un proceso listo espera turno de CPU | Secuencia: creación → espera → ejecución | Ejemplo ilustrativo; fuente: components/flow-steps.html, #ciclo; contrastar con diapositivas de la unidad. | Luis | 2:00
```

`component | message (≤ 8 words) | visual | spoken note [| speaker [| m:ss]]`. The spoken note becomes the slide `.notes` and the speaker guide. A line with no `|` is still a valid one-message line. The example's source path is relative to `skills/academic-slides-flow/`: it supports the illustration, not course alignment; replace or supplement it with the actual unit source and locator.

For each content slide, draft a specific sourced point, a supporting example or evidence, and the visual's explanatory purpose. Put the source file and page/section or other locator in the outline or notes without adding fields; distinguish an illustration from evidence. Choose the existing component for that purpose, not a default icon or card. If sources are insufficient, narrow the claim, mark the gap or request evidence. Covers, section pauses and conclusions serve different roles; see `writing.md` for examples and composition review.

Run `python3 tools/outline.py outline.txt`. It prints the plan (start, length, speaker per slide) and exits 1 on an unknown component, a bad time, an unknown speaker, or explicit times over the duration. `note:` lines (long message, slide count far from the duration) are advice. Show the plan with the outline at gate 1. Correct factual errors in the source here and list each correction before styling. Terms that are not in the user's list are `TIP`, on that line.

Stop. Wait for an explicit approval. Silence is not approval.

## Assemble

Copy into the destination, keeping this layout:

```
destination/
├── index.html          # shells/deck.html or shells/guide.html
├── themes/             # deck: deck-base.css + <theme>.css; guide: metro.css
├── assets/fonts/       # the whole directory
├── assets/katex/       # only when formula-hero is used
└── outline.txt         # the approved outline
```

A deck links `themes/deck-base.css` first, then `themes/<theme>.css`. A guide links `themes/metro.css`. Font URLs inside a theme are relative to the CSS file (`../assets/fonts/`). Do not rewrite them if `themes/` and `assets/` stay siblings. Deck components use the token contract in `deck-base.css`, so they work in every deck theme. Icons are Lucide (ISC). Find the icon that names the idea with `python3 tools/icons.py search WORD`, then paste the output of `python3 tools/icons.py sprite NAME...` once after `<body>`, with exactly the icons the deck uses (`components/icon-sprite.html` is a ready default set). Never draw icons by hand.

Paste the component `<style>` once and the markup per item. No ad-hoc CSS. A new visual pattern becomes a file in `components/` first.

`deck`: one idea per slide, speaker notes in `.notes`, keyboard nav already in the shell (`N` notes, arrows, `?print` for PDF). `guide`: map links to cards, quiz links to answers, spaced-review page for days 1/3/7/14 when the user asked for a study guide.

## Render and check

From the skill directory:

```
tools/render.sh destination/index.html
python3 tools/check_deck.py destination/index.html --mode deck|guide --outline destination/outline.txt --dom
```

In `deck` mode the checker also reports `density:` lines: a slide above 3 items or 30 words fails, naming the slide, unless it is marked `data-dense`. Add `--max-items N` / `--max-words N` only when the user asked for a denser deck.

`check_deck.py` writes findings to stdout and does not modify the HTML. Exit 0 is required before showing the PDF. Then inspect thumbnails for hierarchy, legibility, evidence and visual fit. Keep whitespace that focuses or separates; fix content that looks stranded or unsupported, overflow and empty pages. Do not fill space with decoration or enforce occupancy or word minima. A checker pass is neither a composition judgment nor visual approval.

## Gate 2 — visual review

Show the PDF path and the checker stdout. Stop. Only an explicit review continues.

## Speaker guide (guía de expositores)

For a group talk, after gate 2, build the speaker guide as its own document, never as an overlay inside the deck:

```
python3 tools/speaker_guide.py destination/index.html destination/outline.txt
tools/render.sh destination/guia-expositores.html
python3 tools/check_deck.py destination/guia-expositores.html --mode guide --expect N --dom
```

It is a `guide` (theme `metro`, 297×167 mm): a cast page (who, how many slides, how long, linked) and one row per slide (number, start–end, speaker, message, what they say). What they say is the slide `.notes`; the outline note fills a slide without notes. N is the page count the tool prints. It refuses to overwrite an existing guide without `--force`.

## Harvest

If the user praises one element, extract it into `components/` (or tokens into `themes/`) and name the source deck in the component comment.
