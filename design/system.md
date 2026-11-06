# Sistema de diseño observado · diapositivas

Inventario de la familia de diapositivas, no una propuesta de tema nuevo. Los 80 valores siguientes son 8 roles de color por cada una de 10 fuentes; los alias repetidos se cuentan por rol, no como colores únicos. Cada fila sigue el orden `--bg`, `--fg`, `--muted`, `--a1`, `--a2`, `--a3`, `--alt-bg`, `--alt-fg`. Los acentos identifican categorías, no decoración. Las combinaciones deben comprobarse para contraste: no todas las parejas de tokens existentes son accesibles.

| Fuente | 8 roles de color, en el orden anterior |
|---|---|
| `skills/academic-slides-flow/themes/deck-base.css` | #F4F4F7, #17181C, #6B6E7A, #3D6BFF, #FFD600, #7395FF, #131316, #FFFFFF |
| `skills/academic-slides-flow/themes/bauhaus.css` | #F2EBDD, #1A1A1A, #5A554C, #E63322, #1D4DB6, #F5C400, #1D4DB6, #F2EBDD |
| `skills/academic-slides-flow/themes/cuaderno.css` | #FDFCF7, #22313F, #5E6E7C, #2C6FBB, #D1495B, #2E8B57, #D9C9A3, #22313F |
| `skills/academic-slides-flow/themes/deportivo.css` | #F4F4F7, #17181C, #6B6E7A, #3D6BFF, #D9A800, #7395FF, #131316, #FFFFFF (aliases resueltos) |
| `skills/academic-slides-flow/themes/editorial.css` | #F7F3EC, #141414, #6E665B, #C8102E, #141414, #8C7B62, #141414, #F7F3EC |
| `skills/academic-slides-flow/themes/metro-deck.css` | #F3EFE6, #1B1B1F, #6A665E, #E4572E, #1F9E8F, #6C4FD1, #1B1B1F, #F3EFE6 |
| `skills/academic-slides-flow/themes/pizarra.css` | #21402F, #EEEBE0, #B9C2B4, #F6D86B, #F49A9A, #94CCEB, #172E22, #EEEBE0 |
| `skills/academic-slides-flow/themes/pop.css` | #FFE14D, #111111, #3A3A3A, #FF3B30, #0057FF, #111111, #FF3B30, #FFFFFF |
| `skills/academic-slides-flow/themes/retro.css` | #C0C0C0, #000000, #222222, #000080, #800000, #006400, #0000AA, #FFFFFF |
| `skills/academic-slides-flow/themes/terminal.css` | #0B0F0C, #D7FFD9, #6FA77A, #39FF88, #FF4FD8, #5CC8FF, #39FF88, #0B0F0C |

`skills/academic-slides-flow/themes/metro.css` es la variante de guía, no otro tema de diapositiva: 9 roles de color: `--paper` #F3EFE6, `--paper-2` #E9E3D6, `--ink` #1B1B1F, `--muted` #6A665E, `--rule` #CFC7B6, `--a` #E4572E, `--b` #1F9E8F, `--c` #6C4FD1, `--d` #E9A21B.

## Tipografía

Tres roles de familia en cada tema: `--display`, `--body`, `--mono`. `skills/academic-slides-flow/themes/deck-base.css`: Georgia/serif, system-ui/sans-serif, ui-monospace/monospace. Los temas declaran fuentes locales: Space Grotesk y IBM Plex (`metro-deck.css`); C059 e Inter (`editorial.css`); Graduate y Barlow (`deportivo.css`); Caladea (`cuaderno.css`); C059 y Caladea (`pizarra.css`); Barlow (`pop.css`); Iosevka Term y DejaVu Sans (`retro.css`); Fira Code (`terminal.css`); Space Grotesk (`bauhaus.css`). Las vistas usan solo los stacks de sistema de deck-base: aproximan esas fuentes locales y no reproducen exactamente sus métricas. `deck-base.css` establece título 104px (variantes 86 y 128), entradilla 40px, cuerpo 32px, kicker 26px y pie 22px: 6 tamaños observados.

## Espaciado, radios y sombras

`skills/academic-slides-flow/themes/deck-base.css`: lienzo 1920 × 1080; padding 96px 140px 150px; separación de diapositiva 44px; pie a 46px del borde inferior (5 medidas). Radio de notas 18px (1). `skills/academic-slides-flow/components/flow-steps.html`: círculos de 170px con radio 50% (1). `skills/academic-slides-flow/themes/pizarra.css`: sombra de marco `inset 0 0 0 30px #6B4A2E, inset 0 0 0 36px #4E351F` (1). `skills/academic-slides-flow/themes/pop.css`: sombra de título `16px 16px 0 #111` (1). Son ejemplos observados, no una escala exhaustiva de todas las declaraciones CSS.

## Componentes y reglas

- `skills/academic-slides-flow/components/deck-case-map.html`: tres actores, dos relaciones explícitas; el préstamo vincula lector y ejemplar. No confundir obra con copia.
- `skills/academic-slides-flow/components/flow-steps.html`: secuencia numerada con transiciones; no sustituye un mapa de relaciones.
- `skills/academic-slides-flow/components/figure-full.html`: figura principal y pie; identificar ilustraciones y fuentes.
- `skills/academic-slides-flow/components/bar-rows.html`: barras para valores reales con categoría y unidad; no inventar mediciones.

Las tres vistas son composiciones propuestas, no componentes ni temas implementados. Comparten contenido ilustrativo; no representan evidencia medida.
