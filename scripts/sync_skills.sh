#!/usr/bin/env bash
# Sync the slides skill from this repo (source of truth) to the agent runtime.
#
#   ./scripts/sync_skills.sh          # show what would change
#   ./scripts/sync_skills.sh --apply  # write the changes
#
# The repo is authoritative. Anything edited directly in a runtime directory is
# overwritten, so edit here and sync outward — never the other way around.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/skills"
SKILL=academic-slides-flow

TARGETS=(
  "$HOME/.pi/agent/skills"
)

APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

if [[ $APPLY -eq 0 ]]; then
  echo "DRY RUN — nothing is written. Re-run with --apply to sync."
  RSYNC_FLAGS=(-ai --dry-run)
else
  RSYNC_FLAGS=(-ai)
fi

# Gate the sync on the checker tests and the fixtures: a skill whose own
# checker fails must never reach a runtime directory.
PY="$REPO_ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "!! .venv not found — run: python3 -m venv .venv && .venv/bin/pip install pytest" >&2
  exit 1
fi
echo "==> Running tool tests"
PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest -q -p no:cacheprovider "$SRC/$SKILL/tools"
for mode in deck guide; do
  echo "==> Checking $mode fixture"
  "$PY" "$SRC/$SKILL/tools/check_deck.py" "$SRC/$SKILL/examples/$mode/index.html" \
    --mode "$mode" --outline "$SRC/$SKILL/examples/$mode/outline.txt" --dom
done
echo "==> Checking speaker guide fixture"
"$PY" "$SRC/$SKILL/tools/outline.py" "$SRC/$SKILL/examples/deck/outline.txt" >/dev/null
"$PY" "$SRC/$SKILL/tools/check_deck.py" "$SRC/$SKILL/examples/deck/guia-expositores.html" \
  --mode guide --expect 3 --dom
GUIDE_TMP="$(mktemp -p "$SRC/$SKILL/examples/deck" .guide-check.XXXXXX.html)"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$SRC/$SKILL/tools/speaker_guide.py" "$SRC/$SKILL/examples/deck/index.html" \
  "$SRC/$SKILL/examples/deck/outline.txt" --out "$GUIDE_TMP" --force >/dev/null
if ! diff -q "$GUIDE_TMP" "$SRC/$SKILL/examples/deck/guia-expositores.html" >/dev/null; then
  rm -f "$GUIDE_TMP"
  echo "!! examples/deck/guia-expositores.html is stale — rerun tools/speaker_guide.py ... --force" >&2
  exit 1
fi
rm -f "$GUIDE_TMP"
echo "==> Checking the catalog is current"
CATALOG_TMP="$(mktemp -d -p "$SRC/$SKILL" .catalog-check.XXXXXX)"
trap 'rm -rf "$CATALOG_TMP"' EXIT
PYTHONDONTWRITEBYTECODE=1 "$PY" "$SRC/$SKILL/tools/build_catalog.py" --out "$CATALOG_TMP" >/dev/null
if ! diff -rq "$CATALOG_TMP" "$SRC/$SKILL/catalog" >/dev/null; then
  echo "!! catalog/ is stale — run: python3 skills/$SKILL/tools/build_catalog.py" >&2
  exit 1
fi
rm -rf "$CATALOG_TMP"

for target in "${TARGETS[@]}"; do
  echo "==> $target"
  if [[ ! -d "$target" ]]; then
    echo "    skipped: runtime directory does not exist"
    continue
  fi
  [[ $APPLY -eq 1 ]] && mkdir -p "$target/$SKILL"
  # --delete keeps the runtime an exact mirror, so removed files stop loading.
  rsync "${RSYNC_FLAGS[@]}" --delete \
    --exclude '__pycache__/' \
    --exclude '.pytest_cache/' \
    --exclude '*.bak-*' \
    --exclude '.catalog-check.*' \
    --exclude '.guide-check.*' \
    "$SRC/$SKILL/" "$target/$SKILL/"
done

if [[ $APPLY -eq 0 ]]; then
  echo
  echo "DRY RUN complete. Re-run with --apply to write."
fi
