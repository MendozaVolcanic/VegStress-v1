# Bibliografia VegStress-v1

Indice de literatura cientifica relevante para deteccion de estres volcanico via teledeteccion.

## Documentos del proyecto

- [Discriminacion estacional vs volcanico](./seasonal_vs_volcanic.md) — estrategia formal para
  separar fenologia natural de senal volcanica. **Lectura obligatoria.**
- [Papers completos](./papers_completo.md) — bibliografia indexada por tema (54 papers).
- [Proyectos similares](./proyectos_similares.md) — sistemas/plataformas comparables (55 entradas).
- [Preguntas de busqueda](./preguntas_busqueda.md) — Fase-0 (5 preguntas con output esperado).
- [Descargas jun-2026](./descargas_2026-06.md) — **18 PDFs descargados** + estado de pendientes.
- [Hallazgos Perplexity](./perplexity_hallazgos_2026-06.md) — comparativo Deep Research.

## Estructura

```
docs/bibliografia/
├── index.md                       ← este archivo
├── seasonal_vs_volcanic.md        ← problema cientifico clave
├── papers_completo.md             ← 54 papers indexados por tema
├── proyectos_similares.md         ← 55 sistemas/plataformas comparables
├── preguntas_busqueda.md          ← Fase-0 de la busqueda
├── descargas_2026-06.md           ← log de descargas (18 PDFs)
├── perplexity_hallazgos_2026-06.md ← comparativo Perplexity
└── pdfs/                          ← 18 PDFs locales (gitignored, ~108MB)
```

## Reglas

1. **Cada idea metodologica nueva** debe citar al menos 1 paper en `papers_completo.md`.
2. **Cada cambio de algoritmo** en `change_detector.py` referencia un DOI en su docstring.
3. **PDFs** van en `pdfs/` con nombre `Autor_Anio_Tema.pdf` y NO se commitean
   (gitignored; solo metadata + DOI en los .md). Verificar magic bytes post-descarga.
4. Cuando un paper se aplica al codigo, agregar tag `[IMPLEMENTADO]` con fecha y commit hash.

## Temas indexados

1. Volcanic CO2 / SO2 vegetation stress (remote sensing)
2. Discriminacion estacional vs volcanico
3. Indices red-edge (NDRE, MCARI, REP) para deteccion precoz
4. Solar Induced Fluorescence (SIF) y volcanes
5. Especies chilenas y respuesta a CO2/SO2
6. Deep learning / ML en series temporales volcanicas
7. Marcos operacionales de monitoreo combinado
