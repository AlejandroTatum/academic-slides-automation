#!/usr/bin/env bash
# Vendor the system fonts used by the new deck themes into the skill as
# Latin-subset woff2 files, so decks render offline and never hit a CDN.
#
#   ./scripts/vendor_fonts.sh
#
# Needs pyftsubset (fonttools) and woff2_compress. Sources are the Arch
# packages gsfonts (C059, URW), ttf-caladea, inter-font, ttf-fira-code,
# ttf-iosevkaterm-nerd and ttf-dejavu. All are OFL, Apache, or URW
# font-exception licensed and allow embedding.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO_ROOT/skills/academic-slides-flow/assets/fonts"
UNICODES="U+0000-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2190-2193,U+2212,U+2215,U+2248,U+2260,U+2264-2265,U+25A0-25FF,U+258C"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# output-name  source-file  [ttc-index]
FONTS=(
  "c059-400 /usr/share/fonts/gsfonts/C059-Roman.otf"
  "c059-700 /usr/share/fonts/gsfonts/C059-Bold.otf"
  "c059-400-italic /usr/share/fonts/gsfonts/C059-Italic.otf"
  "c059-700-italic /usr/share/fonts/gsfonts/C059-BdIta.otf"
  "caladea-400 /usr/share/fonts/caladea/Caladea-Regular.ttf"
  "caladea-700 /usr/share/fonts/caladea/Caladea-Bold.ttf"
  "caladea-400-italic /usr/share/fonts/caladea/Caladea-Italic.ttf"
  "inter-400 /usr/share/fonts/inter/Inter.ttc 0"
  "inter-600 /usr/share/fonts/inter/Inter.ttc 12"
  "fira-code-400 /usr/share/fonts/TTF/FiraCode-Regular.ttf"
  "fira-code-500 /usr/share/fonts/TTF/FiraCode-Medium.ttf"
  "fira-code-700 /usr/share/fonts/TTF/FiraCode-Bold.ttf"
  "iosevka-term-400 /usr/share/fonts/TTF/IosevkaTermNerdFontPropo-Regular.ttf"
  "iosevka-term-700 /usr/share/fonts/TTF/IosevkaTermNerdFontPropo-Bold.ttf"
  "dejavu-sans-400 /usr/share/fonts/TTF/DejaVuSans.ttf"
  "dejavu-sans-700 /usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
)

for entry in "${FONTS[@]}"; do
  read -r name src index <<<"$entry"
  args=("$src" "--unicodes=$UNICODES" "--layout-features=*" "--output-file=$TMP/$name.ttf")
  [[ -n "${index:-}" ]] && args+=("--font-number=$index")
  pyftsubset "${args[@]}"
  woff2_compress "$TMP/$name.ttf" >/dev/null
  mv "$TMP/$name.woff2" "$OUT/$name.woff2"
  printf '%-22s %6s bytes\n' "$name.woff2" "$(stat -c %s "$OUT/$name.woff2")"
done
