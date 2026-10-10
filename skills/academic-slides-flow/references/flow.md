# Flow

Two gates. Do not build before gate 1. Do not claim approval before gate 2.

## Intake

Record mode (`deck` or `guide`), subject, audience, duration or term list, source files, and the destination folder. If the user did not name the mode or the folder, ask and stop.

Load `references/profiles/` when a profile `match:` fits the subject. Profile rules win. Simulación bibliography is the teacher slides only when that profile says so.

Do not overwrite an existing HTML or PDF in that folder unless the user explicitly asks.

## Theme

`deck` defaults to `deportivo` (projected, high contrast, live demo). `guide` defaults to `metro` (read alone, category color, terminal block). Propose that default with one reason. If the user names the other theme, use it. Do not invent a third theme.

## Gate 1 — outline

One line per slide or page: component name + the one message. Components live in `components/`. Correct factual errors in the source here and list each correction before styling. Terms that are not in the user's list are `TIP`, on that line.

Stop. Wait for an explicit approval. Silence is not approval.

## Assemble

Copy into the destination, keeping this layout:

```
destination/
├── index.html          # shells/deck.html or shells/guide.html
├── themes/<theme>.css
├── assets/fonts/       # the whole directory
└── outline.txt         # one approved message per line
```

Change the stylesheet href to `themes/deportivo.css` or `themes/metro.css`. Font URLs inside the theme are relative to the CSS file (`../assets/fonts/`). Do not rewrite them if `themes/` and `assets/` stay siblings.

Paste the component `<style>` once and the markup per item. No ad-hoc CSS. A new visual pattern becomes a file in `components/` first.

`deck`: one idea per slide, speaker notes in `.notes`, keyboard nav already in the shell (`N` notes, arrows, `?print` for PDF). `guide`: map links to cards, quiz links to answers, spaced-review page for days 1/3/7/14 when the user asked for a study guide.

## Render and check

From the skill directory:

```
tools/render.sh destination/index.html
python3 tools/check_deck.py destination/index.html --mode deck|guide --outline destination/outline.txt --dom
```

`check_deck.py` writes findings to stdout and does not modify the HTML. Exit 0 is required before showing the PDF. Then look at the thumbnails. Fix overflow and empty pages. A checker pass is not visual approval.

## Gate 2 — visual review

Show the PDF path and the checker stdout. Stop. Only an explicit review continues.

## Harvest

If the user praises one element, extract it into `components/` (or tokens into `themes/`) and name the source deck in the component comment.
