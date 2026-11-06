# Referencia controlada: préstamo bibliotecario

Esta fixture de cuatro diapositivas explora el mismo caso ilustrativo con mapa, comparación, proceso y código anotado. No reproduce una presentación de usuario ni aporta mediciones o evidencia externa. Las notas distinguen ejemplos de afirmaciones; el esquema aprobado para esta fixture no aprueba un esquema de usuario.

Usa `../../themes/` y sus fuentes locales, sin copiar recursos. El HTML incorpora los estilos de los componentes para funcionar como presentación independiente; al cambiar un componente se debe contrastar su copia aquí. El tema deportivo es solo la base de esta fixture, no una selección entre las propuestas nuevas.

Desde la raíz del repositorio:

```sh
python3 skills/academic-slides-flow/tools/outline.py skills/academic-slides-flow/examples/quality-reference/outline.txt
skills/academic-slides-flow/tools/render.sh skills/academic-slides-flow/examples/quality-reference/index.html /tmp/quality-reference.pdf
python3 skills/academic-slides-flow/tools/check_deck.py skills/academic-slides-flow/examples/quality-reference/index.html --mode deck --outline skills/academic-slides-flow/examples/quality-reference/outline.txt --dom
```

Inspeccionar cada página del PDF y sus miniaturas: jerarquía, relación entre título y ejemplo, espacio intencional y recortes. La revisión visual del PDF sigue siendo una puerta humana, no una aprobación automática del checker.
