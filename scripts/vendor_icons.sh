#!/usr/bin/env bash
# Vendor the Lucide icon set into the skill as compact JSON data.
#
#   ./scripts/vendor_icons.sh [version]     # default 1.56.0
#
# Keeps icon-nodes.json (every icon's SVG elements) and tags.json (search
# words), minified, plus the ISC license. tools/icons.py builds deck sprites
# from this data, so no per-icon SVG files are needed.

set -euo pipefail

VERSION="${1:-1.56.0}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO_ROOT/skills/academic-slides-flow/assets/icons/lucide"
DL="$(mktemp -d)"
trap 'rm -rf "$DL"' EXIT

(cd "$DL" && npm pack --silent "lucide-static@$VERSION" >/dev/null && tar -xzf lucide-static-*.tgz)
PKG="$DL/package"

rm -rf "$OUT"
mkdir -p "$OUT"
for name in icon-nodes tags; do
  python3 -c 'import json, sys; json.dump(json.load(open(sys.argv[1])), open(sys.argv[2], "w"), separators=(",", ":"), sort_keys=True)' \
    "$PKG/$name.json" "$OUT/$name.json"
done
cp "$PKG/LICENSE" "$OUT/LICENSE"
printf '%s\n' "$VERSION" > "$OUT/VERSION"
echo "lucide $VERSION -> $OUT ($(du -sh "$OUT" | cut -f1))"
