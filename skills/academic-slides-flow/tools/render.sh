#!/bin/sh
# Render a deck or guide HTML to PDF, then write page thumbnails.
# Usage: render.sh PATH.html [out.pdf]
set -eu
html=$(readlink -f "$1")
out=${2:-${html%.html}.pdf}
brave --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 \
  --print-to-pdf="$out" "file://${html}?print"
pdftoppm -png -r 36 "$out" "${out%.pdf}-thumb"
printf 'pdf: %s\n' "$out"
