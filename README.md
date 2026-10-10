# academic-slides-automation

Source of truth for the `academic-slides-flow` agent skill: university slide
decks (`deck` mode) and study guides (`guide` mode) built from the proven
`deportivo` and `metro` themes.

## Layout

- `skills/academic-slides-flow/` — the skill itself (`SKILL.md`, `DESIGN.md`,
  themes, shells, components, tools, fixtures).
- `scripts/sync_skills.sh` — publishes the skill to the Pi runtime
  (`~/.pi/agent/skills`).

## Workflow

1. Edit the skill here, never in the runtime directory.
2. Run the checks (first time: `python3 -m venv .venv && .venv/bin/pip install pytest`):

   ```sh
   .venv/bin/python -m pytest -q skills/academic-slides-flow/tools/test_check_deck.py
   .venv/bin/python skills/academic-slides-flow/tools/check_deck.py \
     skills/academic-slides-flow/examples/deck/index.html \
     --mode deck --outline skills/academic-slides-flow/examples/deck/outline.txt --dom
   ```

3. Preview with `./scripts/sync_skills.sh`, then publish with
   `./scripts/sync_skills.sh --apply`. The sync runs the tests and fixtures
   first and refuses to publish on failure.

Course profiles under `references/profiles/` mirror those of
`academic-report-flow` (repo `academic-report-automation`); change them there
first.
