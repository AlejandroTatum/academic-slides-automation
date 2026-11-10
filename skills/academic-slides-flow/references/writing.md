# Writing

`deck`: one idea per content slide. The spoken sentence is the `.notes` text, not a paragraph on the slide. No source dump.

## Make the point visible and traceable

- Strengthen the title-as-point rule: replace a topic label with a specific claim or takeaway supported by the provided material. Qualify it where the source does; do not invent facts, measurements or certainty. Keep the title concise, but do not sacrifice meaning to meet a word target.
- Give the audience a concrete reason to believe or understand the point: a sourced observation, comparison, worked example, excerpt or labeled diagram, as appropriate. Connect it to the title in the visible content and explain the inference in `.notes`. Keep a trace to the actual file and page/section or other locator in the outline or notes; cite visibly when required. An illustrative example must be labeled as such and cannot become evidence for an unsupported claim.
- If the available sources cannot support the point, narrow it, explicitly mark the evidence as unavailable, or ask for a source; do not fabricate it. Follow profile-specific source rules.
- Choose the visual for its job: show a sequence, contrast, relationship, evidence, or a concrete case. Pick an available component that fits that job and the amount of content; do not repeat icons or cards just to decorate. A visual should add information or make a relationship easier to see, not merely restate the title.
- Covers identify the subject; section pauses orient the audience; conclusions synthesize supported takeaways. They can be intentionally sparse and need not mimic the evidence structure of a content slide.

### Example: from topic to point

The repository's `skills/academic-slides-flow/components/flow-steps.html`, markup for `#ciclo`, illustrates the sequence Nuevo → Listo → Ejecución and describes waiting for CPU. It is a component example, not a substitute for the course's unit slides. After checking those slides, a content outline could use:

```text
flow-steps | Un proceso listo espera turno de CPU | Secuencia: creación → espera → ejecución | Ejemplo ilustrativo: tras crearse, espera CPU antes de ejecutarse. Fuente: components/flow-steps.html, #ciclo; contrastar con diapositivas de la unidad.
```

Here the sequence explains the wait instead of placing three unrelated icons below “Ciclo de un proceso”. The source locator is relative to `skills/academic-slides-flow/`; replace it with the actual course source and locator when using course evidence. Do not present this illustration as a measured result.

## Review composition, not occupancy

Inspect rendered slides individually and as a sequence. Ask what should be seen first, whether the evidence and visual are legible and connected to the point, and whether the composition suits the slide's role. Whitespace can separate ideas, focus attention or give a cover or pause room to breathe. It is suspect when content appears stranded, hierarchy is unclear, a visual is too small to explain anything, or a content slide lacks the support needed to understand its point.

When space feels accidental, first check whether the message or evidence is missing; then use a better-fitting existing component, adjust the distribution within its intended design, split or combine material where appropriate. Preserve legibility and the no ad-hoc CSS rule. Do not add decorative filler, repeat content, or impose a minimum word count or canvas occupancy. A checker pass cannot judge this visual purpose.

## Deck density (default, not a limit)

By default a deck slide shows at most **3 items** and **30 words**. Visual first, with words that guide the speaker:

- One optional `.lead` line under the point-bearing title (≤ 12 words) gives the context.
- Each icon or step has a 1–3 word label and an optional `.desc` line (≤ 6 words): the cue for what to say, not the speech.
- Recap lines are one short sentence each.
- The full spoken text stays in `.notes`. Bare labels with no guide are too thin; paragraphs are too much.

- An item is an `<li>` or an element with class `item`. Words are the visible text outside `.notes`, `.kicker`, `.foot`, `pre`, `code`, `svg`, and math.
- When the user asks for more, or the content needs it (a comparison table, a dense recap), mark that slide `data-dense`. Say why in the outline line. The checker still reports its item and word counts and marks it exempt.
- When the user wants a denser deck overall, run the checker with `--max-items N` and/or `--max-words N`. Record the values in the outline header.
- Never shrink text to fit the default. Split the slide, move text to `.notes`, or mark it dense.

`guide`: dense, but each card is definition + analogy + trap. The analogy is one concrete image. The trap is the confusion a classmate actually makes.

Color is a category the reader can name. In `metro`, `--a` `--b` `--c` `--d` are four lines. Do not use a line color on a term from another line. In `deportivo`, yellow is the accent on coal or blue; it is not a fifth meaning.

`TIP` marks a term or aside that was not in the user's source list. Put `TIP` in the kicker or beside the term. Do not smuggle extra examinable definitions.

Correct a wrong source definition before it becomes a card. Tell the user what changed and why, in the outline, not only inside the card.

Body text is `p`, `h1`–`h3`, `.title`, `.what`, `.lead`: ≥ 10.5 pt on a guide, ≥ 28 px on a deck. Kicker, footer, mono labels, and terminal chrome may be smaller. Do not shrink body text to fit; cut the sentence or add a page.

UNL course artifacts are Spanish unless that course repo says otherwise. Keep commands and identifiers in their real spelling.
