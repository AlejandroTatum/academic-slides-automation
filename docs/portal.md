---
title: "Operación del portal"
---

Este sitio documenta `academic-slides-flow` con Quarto, siguiendo el patrón del portal de reportes: idioma español, tema `cosmo`, búsqueda lateral y navegación por secciones. No transforma los decks en presentaciones Quarto ni modifica el motor de render de la skill.

## Vista previa local

Con Quarto instalado, desde la raíz del repositorio:

```sh
quarto --version
quarto preview
```

Abrí la dirección que indique Quarto. Para generar el sitio sin iniciar un servidor:

```sh
quarto render
```

El resultado queda en `_site/index.html`. `_site/` y `.quarto/` son salidas locales y no se versionan. La implementación se verificó con Quarto 1.11.9.

## Archivos incluidos

`_quarto.yml` usa una lista explícita de entradas:

- `index.qmd`: inicio y rutas de lectura.
- `docs/portal.md`: operación del sitio.
- `docs/portal/*.qmd`: contexto, flujo, herramientas, temas y calidad.

Los perfiles de materias, propuestas, fixtures, planes internos y entregables de cursos no forman parte de esa lista. No los agregues como recursos globales del sitio. El portal menciona rutas fuente como texto; no copia ni publica automáticamente esos archivos.

## Mantener las páginas

1. Verificá la regla o comando en `skills/academic-slides-flow/`.
2. Actualizá la página correspondiente y la navegación si agregás una entrada.
3. Ejecutá `quarto render` y revisá advertencias, enlaces y navegación.

Las secciones siguen el patrón del portal de reportes, pero solo se incluyen las que tienen contenido real. No se agregan secciones vacías ni propuestas de cambio al funcionamiento de la skill.

## Publicación

El sitio está configurado para [GitHub Pages](https://alejandrotatum.github.io/academic-slides-automation/) con el repositorio [academic-slides-automation](https://github.com/AlejandroTatum/academic-slides-automation). Para activarlo, seleccioná **GitHub Actions** como fuente en Settings → Pages del repositorio.

El workflow de documentación renderiza las pull requests sin desplegar. Publica solo tras un push a `main` o una ejecución manual seleccionando `main`; usa el entorno `github-pages`. El despliegue comprueba el contenido de `_site` y falla ante archivos inesperados, en vez de publicar fuentes o datos por accidente. Activar Pages y publicar el repositorio son pasos separados de esta configuración.
