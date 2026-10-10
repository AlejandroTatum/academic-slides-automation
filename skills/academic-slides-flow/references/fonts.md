# Fonts

All render fonts are files in `assets/fonts/`. Do not add a Google Fonts stylesheet.

`deportivo`: Graduate and Barlow, copied from the Semana 2 simulación deck (already local there).

`metro`: Space Grotesk, IBM Plex Sans, and IBM Plex Mono, Latin woff2 from Fontsource (OFL). Weights used: Space Grotesk 400/500/700, IBM Plex Sans 400/500/600 plus 400 italic, IBM Plex Mono 400/600.

`check_deck.py` fails if the HTML or a linked stylesheet mentions `fonts.googleapis.com` or `fonts.gstatic.com`, or if a `url(...)` font file is missing relative to the CSS file.
