#!/usr/bin/env bash
# Vendor KaTeX into the skill so formula-hero renders math offline.
#
#   ./scripts/vendor_katex.sh [version]     # default 0.16.22
#
# Copies katex.min.js, katex.min.css (woff2 sources only, so every url()
# in the stylesheet exists locally) and the woff2 fonts. KaTeX is MIT.

set -euo pipefail

VERSION="${1:-0.16.22}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO_ROOT/skills/academic-slides-flow/assets/katex"
DL="$(mktemp -d)"
trap 'rm -rf "$DL"' EXIT

(cd "$DL" && npm pack --silent "katex@$VERSION" >/dev/null && tar -xzf katex-*.tgz)
PKG="$DL/package"

rm -rf "$OUT"
mkdir -p "$OUT/fonts"
cp "$PKG/dist/katex.min.js" "$OUT/"
cp "$PKG/LICENSE" "$OUT/LICENSE"
cp "$PKG/dist/fonts/"*.woff2 "$OUT/fonts/"
# Keep only the woff2 source in each @font-face.
sed -E 's/,url\(fonts\/[A-Za-z0-9_-]+\.woff\) format\("woff"\)//g; s/,url\(fonts\/[A-Za-z0-9_-]+\.ttf\) format\("truetype"\)//g' \
  "$PKG/dist/katex.min.css" > "$OUT/katex.min.css"
printf '%s\n' "$VERSION" > "$OUT/VERSION"

if grep -Eq '\.(woff|ttf)\)' "$OUT/katex.min.css"; then
  echo "!! katex.min.css still references woff/ttf files" >&2
  exit 1
fi
echo "katex $VERSION -> $OUT ($(du -sh "$OUT" | cut -f1))"
