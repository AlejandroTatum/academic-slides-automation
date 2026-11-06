# academic-slides-automation

Source of truth for the `academic-slides-flow` agent skill: university slide
decks (`deck` mode) and study guides (`guide` mode) built from nine deck themes
(`deportivo`, `metro-deck`, and seven experimental ones) and the `metro` guide theme.

## Documentation portal

The Spanish skill documentation is a Quarto website, following the reports
portal's structure. From the repository root, run `quarto preview` to browse it
locally, or `quarto render` to build `_site/index.html` (verified with Quarto
1.11.9). Start at `index.qmd`; see [portal operations](docs/portal.md) for the
explicit render scope, maintenance instructions, and GitHub Pages deployment.
The site is configured for https://alejandrotatum.github.io/academic-slides-automation/;
publication requires GitHub Pages to be enabled with GitHub Actions as its source.

## Layout

- `skills/academic-slides-flow/` — the skill itself (`SKILL.md`, `DESIGN.md`,
  themes, shells, components, tools, fixtures).
- `scripts/sync_skills.sh` — publishes the skill to the Pi runtime
  (`~/.pi/agent/skills`).
- `scripts/vendor_fonts.sh`, `scripts/vendor_katex.sh`, `scripts/vendor_icons.sh` —
  rebuild the local fonts, KaTeX and Lucide icon data inside the skill.
- `proposals/slide-themes.html` — the theme proposals the user picked from.
- `odd/tasks/` — feature plans and their log.

## Workflow

1. Edit the skill here, never in the runtime directory.
2. Run the checks (first time: `python3 -m venv .venv && .venv/bin/pip install pytest`):

   ```sh
   .venv/bin/python -m pytest -q skills/academic-slides-flow/tools
   .venv/bin/python skills/academic-slides-flow/tools/check_deck.py \
     skills/academic-slides-flow/examples/deck/index.html \
     --mode deck --outline skills/academic-slides-flow/examples/deck/outline.txt --dom
   ```

   After changing components, themes, or the shell, regenerate the catalog:
   `python3 skills/academic-slides-flow/tools/build_catalog.py`.

3. Preview with `./scripts/sync_skills.sh`, then publish with
   `./scripts/sync_skills.sh --apply`. The sync runs the tests and fixtures
   first and refuses to publish on failure.

Course profiles under `references/profiles/` mirror those of
`academic-report-flow` (repo `academic-report-automation`); change them there
first.
