# Preguntas de investigación — VegStress-v1 (Fase 0)

Definidas antes de buscar, según guía maestra §2. Cada pregunta con output esperado.

## Q1 — Proyectos/sistemas operacionales del tipo VegStress
¿Qué sistemas operacionales usan teledetección de vegetación (NDVI/red-edge/SIF) como
precursor de actividad volcánica, y qué metodología/umbral publican?
→ Output: papers seminales + reviews + sistemas con código abierto.

## Q2 — Detección de cambios en series NDVI (estacional vs anomalía real)
¿Qué algoritmos (BFAST, CCDC, LandTrendr, CVA) discriminan cambio fenológico estacional
de anomalía abrupta sobre Sentinel-2/Landsat, y cuál tiene mejor desempeño en bosque
templado húmedo del Hemisferio Sur?
→ Output: paper por algoritmo + comparativas + implementación GEE/Python.

## Q3 — Efecto del CO2/desgasificación difusa sobre vegetación
¿Qué firma espectral produce el estrés por CO2/gases volcánicos difusos en vegetación
(kill zones tipo Mammoth Mountain), y a partir de qué concentración es detectable por satélite?
→ Output: papers Farrar/Mammoth + casos análogos + umbrales de detección.

## Q4 — Índices/sensores que detectan estrés ANTES que NDVI
¿Qué índices red-edge (CIred-edge, NDRE), fluorescencia (SIF) o hiperespectrales detectan
estrés de vegetación antes que NDVI, y cuánto lead-time aportan?
→ Output: papers red-edge + SIF + comparativas de sensibilidad temprana.

## Q5 — Cómo mejorar VegStress (datos, ML, validación)
¿Qué mejoras metodológicas existen: HLS (densidad temporal), foundation models (Prithvi),
fusión multi-sensor (SO2 TROPOMI + térmico MIROVA), controles climáticos (CR2MET)?
→ Output: papers/docs técnicos de cada vía de mejora.

## Especies chilenas / Andes (transversal)
Respuesta espectral de Nothofagus, Araucaria a estrés — para calibración local.

---

## Estrategia de esta ronda
1. APIs gratis primero (arXiv MCP, Crossref, OpenAlex, Semantic Scholar, NASA ADS) — subagentes paralelos.
2. Perplexity Deep Research vía Chrome — comparativo (lección AP20).
3. Triaje → descargar solo OA con URL directa (verificar magic bytes §5.4).
4. Editoriales con paywall (MDPI/Elsevier/IEEE) → buscar preprint arXiv o marcar [MANUAL].
