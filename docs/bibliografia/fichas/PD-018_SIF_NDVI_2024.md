# Ficha: PD-018

**Archivo PDF**: `pdfs/SIF_NDVI_2024_comparison.pdf`
**Título**: Comparison between Satellite Derived Solar-Induced Chlorophyll Fluorescence, NDVI and kNDVI in Detecting Water Stress for Dense Vegetation across Southern China
**Autores**: Chunxiao Wang, Lu Liu, Yuke Zhou, Xiaojuan Liu, Jiapei Wu, Wu Tan, Chang Xu, Xiaoqing Xiong · **Afiliación 1er autor**: Hainan Geomatics Center of Ministry of Natural Resources, Haikou, China — verificado en p.1
**Año**: 2024 · **Revista**: Remote Sensing (MDPI) 16(10):1735 · **DOI**: 10.3390/rs16101735
**OA**: sí (CC BY 4.0, MDPI) · **Leído**: ✅ (vía markitdown `md/SIF_NDVI_2024_comparison.md`, 2026-06-07)

## Metodología
Compara tres índices satelitales — **NDVI (MODIS MOD09A1)**, **kNDVI** (kernel-NDVI con kernel
RBF Gaussiano) y **SIF (producto GOSIF**, derivado de OCO-2 + MODIS, 0.05°, mensual) — como
proxies de estrés hídrico sobre vegetación densa del sur de China (18–30°N), 2001–2020.
Benchmark: **GPP de 3 torres de flujo** (QYZ, DHS, XSBN). Atribución de drivers climáticos con
**LightGBM + SHAP**. Caso de estudio: sequía extrema 2009–2010 (SPEI < −1).

## Hallazgos clave (para el pipeline)
- **SIF cae ANTES que NDVI/kNDVI ante la sequía (LEAD-TIME ~1 mes).** En la sequía extrema
  2009–2010, la anomalía SIF empezó a bajar en **enero 2010**, mientras NDVI y kNDVI lo
  hicieron recién en **febrero 2010** (p.12, líneas 653–656). → **lead-time de ~1 mes** —
  evidencia satelital directa de la hipótesis SIF-antes-que-NDVI.
- **SIF responde con MENOR retraso (time-lag) respecto a GPP** que NDVI/kNDVI (Tabla 2, p.13):
  - Sitio QYZ: SIF–GPP **lag = 0 meses, R²=0.92**; NDVI y kNDVI alcanzan su máximo recién a
    **lag = 1 mes** (R²=0.80 y 0.81). → SIF capta el cambio de GPP **un mes antes**.
  - Sitio XSBN: SIF lag óptimo = 1 mes (R²=0.78); NDVI = 2 meses; kNDVI = 3 meses.
- **SIF es el mejor surrogate de GPP** y muestra la **mayor caída de anomalía** en abril 2010
  (mínimo común), seguido de kNDVI y luego NDVI (p.12, líneas 656–658).
- **Correlaciones SIF–GPP** (mensual, lag 0): QYZ R²=0.92→0.98 (texto p.12 reporta 0.98),
  XSBN R²=0.75. **Excepción**: sitio DHS, SIF–GPP **R²=0.18**, más débil que NDVI/kNDVI
  (p.12, líneas 663–666) → la ventaja de SIF NO es universal por sitio.
- **% de píxeles con correlación positiva vs SPEI3**: SIF 66.72% > kNDVI 65.61% > NDVI 64.29%
  (p.7, líneas 510–512).
- **VPD (déficit de presión de vapor) es el driver dominante** del estrés en los 3 índices
  (~29–30% del área, SHAP), no la precipitación (p.10, líneas 598–604).
- Modelos LightGBM con **R² > 0.96** para los tres índices (Tabla 1, p.9).

## Citas útiles (con página)
- "SIF Anomaly (SIFSA) beginning to decrease slightly earlier (January 2010) compared to NDVI
  ... and kNDVI ..., which started in February 2010" (p.12, L653–656)
- "the time-lag relationship of SIF with GPP was shorter than that of NDVI and kNDVI with GPP"
  (p.13, L688–689)
- "SIF serves as the most effective surrogate for GPP, capturing the variability of GPP during
  drought periods with minimal time lag" (abstract, p.1)

## Relevancia para VegStress
**Pilar empírico de la hipótesis SIF-antes-que-NDVI.** Es la evidencia satelital más directa
del cluster: ante estrés hídrico, **SIF anticipa a NDVI ~1 mes** y reduce el time-lag respecto
a GPP. Justifica explorar SIF (GOSIF / TROPOMI-SIF / futuro FLEX) como canal de alerta
temprana en VegStress, *complementario* al NDVI actual. **Caveat de diseño**: la ventaja es
dependiente del sitio (en DHS SIF fue peor que NDVI), y la resolución de GOSIF (0.05° ≈ 5 km)
es **demasiado gruesa** para AOIs volcánicas de quebrada/flanco — habría que evaluar
productos SIF de mayor resolución o downscaling antes de operacionalizar.

## Dónde aplica (mapeo a código/doc)
- `BIBLIOGRAPHY_SYNTHESIS.md §4` — número clave: lead-time SIF↔NDVI = ~1 mes (ene vs feb 2010).
- `seasonal_vs_volcanic.md §Estrategia` — SIF como índice de respuesta más rápida que NDVI.
- `change_detector.py` — candidato a canal SIF futuro; hoy fuera de resolución para AOIs chicas.
- Roadmap v2 — evaluar resolución SIF (GOSIF 5 km vs TROPOMI vs downscaling).

## Flags
- Afiliación 1er autor verificada (p.1). OA CC BY confirmada.
- `[NOTA]` Lead-time y caída derivan de UN evento de sequía (2009–2010) y 3 torres; ventaja
  de SIF no universal (DHS R²=0.18). No extrapolar a estrés volcánico sin validación local.
- `[NOTA]` Es sequía/déficit hídrico, no CO2 volcánico (greening) — mecanismo distinto al PD-001.
