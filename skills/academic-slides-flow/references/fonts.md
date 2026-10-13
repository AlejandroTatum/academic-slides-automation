# Fonts

All render fonts are files in `assets/fonts/`. Do not add a Google Fonts stylesheet.

`deportivo`: Graduate and Barlow, copied from the Semana 2 simulación deck (already local there).

`metro`: Space Grotesk, IBM Plex Sans, and IBM Plex Mono, Latin woff2 from Fontsource (OFL). Weights used: Space Grotesk 400/500/700, IBM Plex Sans 400/500/600 plus 400 italic, IBM Plex Mono 400/600.

New deck themes use Latin-subset woff2 files built from the system font packages by `scripts/vendor_fonts.sh` (repo root): C059 400/700 + italics (`pizarra`, `editorial`; URW, font exception), Caladea 400/700 + 400 italic (`pizarra`, `cuaderno`; Apache), Inter 400/600 (`editorial`; OFL), Fira Code 400/500/700 (`terminal`; OFL), Iosevka Term 400/700 (`retro`; OFL), DejaVu Sans 400/700 (`retro`). `pop` and `bauhaus` reuse Barlow and Space Grotesk.

KaTeX (`formula-hero`) lives in `assets/katex/` with its own woff2 fonts, vendored by `scripts/vendor_katex.sh` (MIT).

`check_deck.py` fails if the HTML or a linked stylesheet mentions `fonts.googleapis.com` or `fonts.gstatic.com`, or if a `url(...)` font file is missing relative to the CSS file.
