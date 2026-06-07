# Bibliografia VegStress-v1

Indice de literatura cientifica relevante para deteccion de estres volcanico via teledeteccion.

## Documentos del proyecto

- [**BIBLIOGRAPHY_SYNTHESIS.md**](./BIBLIOGRAPHY_SYNTHESIS.md) — **fuente de verdad**: solo
  umbrales/fórmulas/coeficientes accionables para el pipeline (modelo VRP Chile). **Empezar acá.**
- [Discriminacion estacional vs volcanico](./seasonal_vs_volcanic.md) — estrategia formal para
  separar fenologia natural de senal volcanica. **Lectura obligatoria.**
- [Fichas](./fichas/INDICE_FICHAS.md) — una ficha por paper usado (sistema PD-/V2-, modelo Educación).
- [GAPS](./GAPS.md) — lista viva de evidencia que falta (prioridad alta/media/baja).
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

## Reglas (adoptadas de VRP Chile + Educación y riesgos)

1. **Síntesis "solo números"**: todo umbral/fórmula/coeficiente que entra al código va a
   `BIBLIOGRAPHY_SYNTHESIS.md` con DOI + página. La prosa/contexto va en la ficha, no ahí.
2. **Una ficha por paper usado** (`fichas/PD-XXX_*.md`), con la plantilla `_PLANTILLA.md`.
   Los de solo-contexto NO necesitan ficha (basta `papers_completo.md`).
3. **Mapeo a código**: cada ficha declara "Dónde aplica" (qué archivo/función). Permite
   consulta bidireccional: "¿qué papers sostienen este umbral?".
4. **Trazabilidad código↔DOI**: `change_detector.py` cita en docstring el DOI del umbral
   que implementa. Tag `[IMPLEMENTADO: fecha + commit]` cuando un paper pasa al código.
5. **Anti-alucinación**: nunca inventar un número que el paper no da. Sin leerlo →
   `[PENDIENTE DE LECTURA]`. Afiliación no confirmada en footer → `[VERIFICAR-AFILIACION]`.
   Evidencia faltante → anotar en `GAPS.md`.
6. **Canonicidad de autores**: antes de citar como autoridad, verificar afiliación
   (ver `BIBLIOGRAPHY_SYNTHESIS.md §7`). No todo paper del tema es la misma escuela.
7. **PDFs** en `pdfs/` con nombre `Autor_Anio_Tema.pdf`, gitignored, verificar magic bytes.

## Temas indexados

1. Volcanic CO2 / SO2 vegetation stress (remote sensing)
2. Discriminacion estacional vs volcanico
3. Indices red-edge (NDRE, MCARI, REP) para deteccion precoz
4. Solar Induced Fluorescence (SIF) y volcanes
5. Especies chilenas y respuesta a CO2/SO2
6. Deep learning / ML en series temporales volcanicas
7. Marcos operacionales de monitoreo combinado
