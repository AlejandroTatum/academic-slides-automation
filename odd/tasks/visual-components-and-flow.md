# visual-components-and-flow

Grow `academic-slides-flow` with visual-first components and a richer flow. Decks stay visual, low text, at most three items per slide; the speaker guide is its own guide document.
Work in `skills/academic-slides-flow/` (this repo); publish only through `scripts/sync_skills.sh`.

## Specs

S1. "mas componentes y mas el flujo, yo trabajo con las diapo que se generan ahora mismo, todo visual sin tanto texto, maximo 3 cosas" + "no lo limites pero, seria el por defecto pero si pido o la tarea pide mas poder hacerlo sin ser un limitante". The **default** is at most **3 visible items** and **~20 words** per `deck` slide, spoken text in `.notes`. It is a default, not a limit: more is allowed when the user asks or the task needs it.

S2. `check_deck.py --mode deck` reports slides above the S1 default, naming the slide. A slide marked `data-dense` (per slide) or a run with `--max-items N` / `--max-words N` (whole deck) is accepted without failing. `guide` mode is unchanged.

S3. New visual components, laid out for 3 items by default and accepting more (S1) (accepted proposal): `big-number` (one huge figure + one line), `icon-row` (local SVG icons, 1–3 word labels; default 3), `flow-steps` (steps with arrows; default 3), `figure-full` (full-screen diagram/image + caption, bridge to `academic-visual-builder`), `formula-hero` (one large formula with up to 3 annotated parts, local KaTeX), `question-hook` (one big question opening a section), `recap` (closing ideas; default 3). Each works in `deportivo` and `metro`.

S4. `catalog.html` renders every component in each theme so components are chosen visually at gate 1 (accepted proposal).

S5. Outline line format (accepted proposal): `component | message (≤ 8 words) | visual | spoken note`. Existing one-message outlines keep working.

S6. Duration → slide count (~1 per minute) and a time per slide (accepted proposal).

S7. "la guia que se genere aparte como una guia mismo": the `guia-expositores` (who speaks, which slide, how long, what they say) is generated from the deck as a separate document in `guide` mode (297×167 mm, own `.html` + `.pdf`), not as an overlay inside the deck.

S8. "si faltaria agregar mas modelos de diapositivas tambien, muestrame propuestas en html para verlas y voy eligiendo yo que se tener unas 10 como maximo". New themes are shown in `proposals/slide-themes.html`; the user picks; total themes (including `deportivo` and `metro`) stay at about 10 at most. Every theme follows the shared token contract so all components work in it.

S9. "hay que mejroar esos assets estan terribles" (screenshot of the hand-drawn icon-row icons). Icons come from a professional, consistent, locally vendored set; a deck embeds only the icons it uses; icon-row gives icons visual weight.

## Tasks

- [x] T1 (S1, S2) Density rule in checker (RED tests first) + `writing.md` / `SKILL.md` wording. Route: inline. Commit: 61f2f74
- [x] T2 (S3) `big-number`, `icon-row` (+ local SVG icon set), `flow-steps`, `question-hook`, `recap`. Route: inline. Commit: a756a43
- [x] T3 (S3) `figure-full` + `formula-hero` with vendored local KaTeX. Route: inline. Commit: a900016
- [x] T4 (S4) `catalog.html` per theme; passes `check_deck.py --dom`. Route: inline. Commit: 0284695
- [x] T5 (S5, S6) Outline parser for the 4-field format (backward compatible) + duration/time budget in `flow.md`. Route: inline. Commit: 0f8cb32
- [x] T6 (S7) Speaker-guide generator: deck + outline → separate guide `.html`/`.pdf` on the `guide` shell; fixture + test. Route: inline. Commit: 9883871
- [x] T7 (all) Update `DESIGN.md` (drop stale "not yet implemented"), `flow.md`, `SKILL.md`; refresh examples; `sync_skills.sh` dry run. Route: inline. Commit: 9a79a94
- [x] T8 (S8) Turn the user-picked proposals into `themes/*.css` (vendored local woff2 fonts), status `experimental` until a real deck passes gate 2. Picked (L10): pizarra, editorial, terminal, bauhaus, cuaderno, pop, retro. Route: inline. Commit: f94f924
- [x] T9 (S9) Vendor Lucide (ISC) as icon data, `tools/icons.py` (search + sprite), rebuild `icon-sprite` from Lucide, icon tiles in `icon-row`; rebuild catalog and examples. Route: inline. Commit: da23f91

## Log

L1. vamos a trabajar y mejorar la skill tenemos muy pocos modelos y general hay que mejorarla, quiero propuestas, para la skill

L2. mas componentes y mas el flujo, yo trabajo con las diapo que se generan ahora mismo, todo visual sin tanto texto, maximo 3 cosas

L3. la guia que se genere aparte como una guia mismo. con eso arma el plan de la propuesta de lo que te acabo de decir

L4. Assumption stated to the user and not contradicted: "maximo 3 cosas" means per slide. New themes are out of scope for this feature.

L6. no lo limites pero, seria el por defecto pero si pido o la tarea pide mas poder hacerlo sin ser un limitante

L7. Decision: the 3-item / ~20-word rule is a checked default with opt-out (`data-dense` per slide, `--max-items` / `--max-words` per run); components renamed so they are not fixed at 3 (`icon-row`, `flow-steps`, `recap`).

L5. Risk to watch: T3 vendors KaTeX (dependency, delivery item 5); T5 changes the outline format the checker already consumes (must stay backward compatible).

L8. si faltaria agregar mas modelos de diapositivas tambien, muestrame propuestas en html para verlas y voy eligiendo yo que se tener unas 10 como maximo

L9. Supersedes L4 on themes: new themes are now in scope. Preview built at `proposals/slide-themes.html` with 12 proposals + 2 current, same content and components in each.

L10. Elegidos: deportivo, metro, Pizarra, Editorial, Terminal, Bauhaus, Cuaderno, Pop, Retro siste

L11. "Retro siste" read as "Retro sistema" (message truncated). Total 9 themes: 2 current + 7 new. Fonts to vendor as woff2: C059 (pizarra, editorial), Caladea (pizarra, cuaderno), Inter (editorial), Fira Code (terminal), Iosevka (retro), DejaVu Sans (retro).

L12. Decision: `deportivo` is a deck theme and `metro` a guide theme. New themes are deck themes on a shared `themes/deck-base.css` (token contract: --bg --fg --muted --a1..3 --alt-bg --alt-fg --display --body --mono --dw --tt --ls). `metro-deck.css` brings the metro look to decks; `metro.css` stays the guide theme. `deportivo.css` stays self-contained and maps its tokens to the contract. Shell links deck-base + one theme. Components (T2/T3) are deck components and must work in all 9 deck themes.

L13. Catalog lives in `catalog/` (generated by `tools/build_catalog.py`, committed so the runtime has it). The checker caught a guide-only cover style leaking into decks; guide-only style blocks are now `<style data-mode="guide">` and the generator skips them.

L14. Closed: all tasks done on branch feat/visual-components-and-flow. sync_skills.sh dry run passes (50 tests, fixtures, speaker guide, fresh catalog); not applied to the runtime (publishing is the user's call). Experimental themes become proven after a real deck passes gate 2.

L15. Independent verify (gentle-ai-verify): PASS S1-S8. Minor findings fixed in a51c63b: sync gate now rebuilds the speaker guide fixture and fails when stale; docs no longer claim live-demo is in the catalog; metro-deck documented as "proven look, new on decks"; --dot-fg added to the token contract comment.

L16. aporta RDD para la creacion de documentos, o el verify es suficiente? / entonces pasame el comando para desactivarlo solo en el repo

L17. Decision: no native review for this branch (whole-branch candidate exceeded the lens context budget); independent verify (PASS S1-S8) is the closing proof. User will disable RDD for this clone themselves.

L18. /tmp/pi-clipboard-0c407cfe-7655-48cf-846e-59f2dece8fba.png hay que mejroar esos assets estan terribles

L19. Decision: Lucide (ISC, 1879 icons, consistent 24-grid stroke style) vendored as icon-nodes.json + tags.json; sprite ids become `i-<lucide-name>` (the old hand-drawn ids were never released; PR #1 is unmerged).

L20. si me convence mas, pero siento que hay muy poquito texto si vendria bien palabras al menos para guiarme, vuelve a darme la propuesta y vamos ajusando la skill con las diapos que considero ideal

L21. si perfecto esas serian las ideales poco texto, de esa manera, actualiza la skill

L22. Decision: the Engram v2 deck is the ideal. Default density becomes 3 items / 30 words of guiding text: title, one .lead line, a .desc line (≤ 6 words) under each icon or step, one-sentence recap lines; speech stays in .notes. terminal is proven (gate 2 passed on the Engram deck).
