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

## Tasks

- [ ] T1 (S1, S2) Density rule in checker (RED tests first) + `writing.md` / `SKILL.md` wording. Route: inline. Commit: —
- [ ] T2 (S3) `big-number`, `icon-row` (+ local SVG icon set), `flow-steps`, `question-hook`, `recap`. Route: inline. Commit: —
- [ ] T3 (S3) `figure-full` + `formula-hero` with vendored local KaTeX. Route: inline. Commit: —
- [ ] T4 (S4) `catalog.html` per theme; passes `check_deck.py --dom`. Route: inline. Commit: —
- [ ] T5 (S5, S6) Outline parser for the 4-field format (backward compatible) + duration/time budget in `flow.md`. Route: inline. Commit: —
- [ ] T6 (S7) Speaker-guide generator: deck + outline → separate guide `.html`/`.pdf` on the `guide` shell; fixture + test. Route: inline. Commit: —
- [ ] T7 (all) Update `DESIGN.md` (drop stale "not yet implemented"), `flow.md`, `SKILL.md`; refresh examples; `sync_skills.sh` dry run. Route: inline. Commit: —
- [ ] T8 (S8) Turn the user-picked proposals into `themes/*.css` (vendored local woff2 fonts), status `experimental` until a real deck passes gate 2. Picked (L10): pizarra, editorial, terminal, bauhaus, cuaderno, pop, retro. Route: inline. Commit: —

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
