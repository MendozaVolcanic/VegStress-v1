# Ficha: PD-010

**Archivo PDF**: `pdfs/Theys_2019_TROPOMI_SO2_degassing.pdf` (10 pp)
**Título**: Global monitoring of volcanic SO2 degassing with unprecedented resolution from TROPOMI onboard Sentinel-5 Precursor
**Autores**: N. Theys, P. Hedelt, I. De Smedt, C. Lerot, H. Yu, J. Vlietinck, M. Pedergnana, S. Arellano, B. Galle, D. Fernandez, C. J. M. Carlito, C. Barrington, B. Taisne, H. Delgado-Granados, D. Loyola, M. Van Roozendael
**Afiliación 1er autor**: Royal Belgian Institute for Space Aeronomy (BIRA-IASB), Bruselas, Bélgica — verificado en p.1
**Año**: 2019 · **Revista**: Scientific Reports (Nature) · **DOI**: 10.1038/s41598-019-39279-y
**OA**: sí (Scientific Reports open-access, CC-BY)
**Leído**: ✅ (vía markitdown `md/Theys_2019_TROPOMI_SO2_degassing.md`, 2026-06-07)

## Metodología
Primeras mediciones de SO2 volcánico del espectrómetro hiperespectral **TROPOMI** (Sentinel-5P,
lanzado oct-2017). Recupera columnas verticales de SO2 (VCD, en Unidad Dobson) por **DOAS** en
UV (312–326 nm). Estima flujos de SO2 (kg/s) con la técnica de "traverse" downwind. Valida contra
red terrestre **NOVAC** (DOAS de escaneo) en Mayon (Filipinas) y Popocatépetl (México).

## Hallazgos clave (para el pipeline)
- **Resolución espacial: 7 × 3.5 km²** (huella nadir) — **13 veces mejor que OMI** (13×24 km²) (p.1, abstract).
- **Límite de detección de emisiones: factor 4 mejor que OMI** (en masa de SO2). Mejor detector
  nadir UV en órbita para plumas débiles (abstract; p.6 conclusiones).
- **Revisita: 1 día** (cobertura global diaria). Tres perfiles de VCD a 0–1 km (capa límite, PBL),
  7 km y 15 km a.s.l. (cajas de 1 km de espesor) (p.2).
- **Umbral de incertidumbre del SCD:** SCDE típico **0.3 DU (TROPOMI)** vs 0.25 DU (OMI). Detección
  plausible si SCD > 3·SCDE en ≥2 píxeles dentro de radio 75 km (p.2).
- **Para flujo:** selecciona píxeles con SCD > 1 DU; máscara de pluma. **1 DU = 2.69×10¹⁶
  moléculas/cm²**. Incertidumbre total del flujo **~50%** (dominada por el viento) (p.2).
- **Resolución temporal sub-diaria:** con viento de 5 m/s zonal, cada píxel across-track (3.5 km)
  representa **~12 min de emisión** (vs ~80 min de OMI). Permite reconstruir flujo SO2 **horario
  o sub-horario** aguas abajo (p.5).
- **Detecta volcanes de baja emisión:** confiablemente 2–4× más seguido que OMI; volcanes de
  **100–200 t SO2/día** (Korovin, Tokachi) cerca del límite, ~40% de frecuencia de detección;
  58 volcanes desgasificantes detectados nov-2017 a jul-2018 (p.4-5).

## Citas útiles (con página)
- "With a spatial footprint of 7×3.5 km² (13 times better than OMI, at least)" (p.2)
- "The limit of detection for SO2 emissions is a factor of 4 better with TROPOMI than with its
  predecessor OMI" (p.6, conclusiones)
- "each satellite pixel is in principle representative for roughly 12 minutes of emission"
  (vs 80 min OMI) (p.5)
- "the near-real-time products are available in less than three hours after sensing" (p.7, Data Availability)

## Relevancia para VegStress
**Es la fuente del canal SO2 con el que VegStress cruza-valida una señal de desgasificación vegetal.**
El nexo físico: el SO2 (y CO2 asociado) que estresa la vegetación es la misma desgasificación que
TROPOMI mide en la atmósfera. Si VegStress detecta browning/anomalía NDVI en una AOI y TROPOMI
muestra **emisión de SO2 coincidente en tiempo y lugar (con viento favorable)**, la señal vegetal
queda confirmada como volcánica (no estacional). Su resolución diaria y límite de detección 4×
mejor lo hacen el co-validador atmosférico ideal. Caveat para Chile: huella de 7×3.5 km es **mucho
más gruesa** que las AOIs de VegStress (decenas de m–km) → TROPOMI valida la *fuente regional*,
no el píxel; emisiones <100 t/día pueden quedar bajo el límite.

## Dónde aplica (mapeo a código/doc)
- `BIBLIOGRAPHY_SYNTHESIS.md §5` — SO2/TROPOMI como tercer canal de fusión y cross-validación.
- `change_detector.py` — regla de cross-validación: anomalía NDVI + SO2 TROPOMI coincidente →
  elevar confianza de la alerta a "volcánica confirmada".
- `seasonal_vs_volcanic.md` — TROPOMI como discriminador independiente (estacional NO produce SO2).
- Roadmap v2 — canal SO2 con latencia NRT <3 h, compatible con cadencia de VegStress.

## Flags
Afiliación 1er autor verificada (BIRA-IASB Bruselas, p.1). Sin números inventados (todos p.1-7).
Nota: el límite "factor 4" es en masa de emisión; el "13×" es resolución espacial — no confundir.
