# Bibliografia VegStress-v1

Indice de literatura cientifica relevante para deteccion de estres volcanico via teledeteccion.

## Documentos del proyecto

- [Discriminacion estacional vs volcanico](./seasonal_vs_volcanic.md) — estrategia formal para
  separar fenologia natural de senal volcanica. **Lectura obligatoria.**
- [Papers completos](./papers_completo.md) — bibliografia indexada por tema
  (en construccion — generada por agente bibliografico).
- [Literatura inicial](../literatura_vegstress.md) — seed list (sera fusionada).

## Estructura

```
docs/bibliografia/
├── index.md                    ← este archivo
├── seasonal_vs_volcanic.md     ← problema cientifico clave
├── papers_completo.md          ← bibliografia exhaustiva
└── papers/                     ← PDFs locales (no commiteados)
```

## Reglas

1. **Cada idea metodologica nueva** debe citar al menos 1 paper en `papers_completo.md`.
2. **Cada cambio de algoritmo** en `change_detector.py` referencia un DOI en su docstring.
3. **PDFs** van en `papers/` y NO se commitean (solo metadata + DOI en .md).
4. Cuando un paper se aplica al codigo, agregar tag `[IMPLEMENTADO]` con fecha y commit hash.

## Temas indexados

1. Volcanic CO2 / SO2 vegetation stress (remote sensing)
2. Discriminacion estacional vs volcanico
3. Indices red-edge (NDRE, MCARI, REP) para deteccion precoz
4. Solar Induced Fluorescence (SIF) y volcanes
5. Especies chilenas y respuesta a CO2/SO2
6. Deep learning / ML en series temporales volcanicas
7. Marcos operacionales de monitoreo combinado
