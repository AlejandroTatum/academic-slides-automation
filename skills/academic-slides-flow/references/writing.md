# Writing

`deck`: one idea per slide. The spoken sentence is the `.notes` text, not a paragraph on the slide. Title carries the point. No source dump.

## Deck density (default, not a limit)

By default a deck slide shows at most **3 items** and **30 words**. Visual first, with words that guide the speaker:

- Title carries the point. One optional `.lead` line under it (≤ 12 words) gives the context.
- Each icon or step has a 1–3 word label and an optional `.desc` line (≤ 6 words): the cue for what to say, not the speech.
- Recap lines are one short sentence each.
- The full spoken text stays in `.notes`. Bare labels with no guide are too thin; paragraphs are too much.

- An item is an `<li>` or an element with class `item`. Words are the visible text outside `.notes`, `.kicker`, `.foot`, `pre`, `code`, `svg`, and math.
- When the user asks for more, or the content needs it (a comparison table, a dense recap), mark that slide `data-dense`. Say why in the outline line.
- When the user wants a denser deck overall, run the checker with `--max-items N` and/or `--max-words N`. Record the values in the outline header.
- Never shrink text to fit the default. Split the slide, move text to `.notes`, or mark it dense.

`guide`: dense, but each card is definition + analogy + trap. The analogy is one concrete image. The trap is the confusion a classmate actually makes.

Color is a category the reader can name. In `metro`, `--a` `--b` `--c` `--d` are four lines. Do not use a line color on a term from another line. In `deportivo`, yellow is the accent on coal or blue; it is not a fifth meaning.

`TIP` marks a term or aside that was not in the user's source list. Put `TIP` in the kicker or beside the term. Do not smuggle extra examinable definitions.

Correct a wrong source definition before it becomes a card. Tell the user what changed and why, in the outline, not only inside the card.

Body text is `p`, `h1`–`h3`, `.title`, `.what`, `.lead`: ≥ 10.5 pt on a guide, ≥ 28 px on a deck. Kicker, footer, mono labels, and terminal chrome may be smaller. Do not shrink body text to fit; cut the sentence or add a page.

UNL course artifacts are Spanish unless that course repo says otherwise. Keep commands and identifiers in their real spelling.
