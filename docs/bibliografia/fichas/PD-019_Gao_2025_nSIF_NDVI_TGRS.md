# Ficha: PD-019

**Archivo PDF**: `pdfs/Gao_2025_nSIF_NDVI_TGRS.pdf`
**Título**: Normalized Solar-Induced Fluorescence Responds Earlier Than Vegetation Indices to the 2019 North China Plain Drought
**Autores**: Yongyuan Gao, Yelu Zeng, Nadezhda N. Voropay, Anne Gobin, Jianxi Huang, Wei Su, Xuecao Li, Shuangxi Miao, Zhe Liu, Bingbo Gao, Yachang He, Wendi Lu, Huiren Tian, Liang Zhu, Si Gao, Kai Yan, Dalei Hao · **Afiliación 1er autor**: College of Land Science and Technology, China Agricultural University, Beijing 100083, China (y Key Laboratory of Remote Sensing for Agri-Hazards, MARA) — verificado en footer p.1
**Año**: 2025 · **Revista**: IEEE Transactions on Geoscience and Remote Sensing (TGRS) 63:1-13 · **DOI**: 10.1109/TGRS.2025.3561216
**OA**: green-OA (accepted manuscript en repositorio Lirias, KU Leuven, handle 20.500.12942/763813) · **Leído**: ✅ (extracción de texto del accepted manuscript, 2026-06-13)

> NOTA de versión: el PDF descargado es el **manuscrito ACEPTADO** (TGRS-2024-07253), no
> el maquetado final IEEE. El contenido científico es el de la versión aceptada; la
> paginación 63:1-13 corresponde al published. Para cita textual con página exacta usar la
> versión publicada (paywall IEEE Xplore).

## Metodología
Compara, durante la **sequía de 2019 en la Llanura del Norte de China (NCP)**, la capacidad
de detección temprana de estrés de varios indicadores satelitales: **SIF normalizada (SIFn)**
— SIF corregida por geometría de visión (BRDF) y por fluctuaciones de PAR —, SIF cruda,
**índices de vegetación (VIs, incluido NDVI)**, y el **rendimiento cuántico de fluorescencia
(ΦF)**. Las anomalías se calculan contra líneas base históricas (promedios 2019-2021). Analiza
a escala **biquincenal (biweekly)** y mensual; cuantifica la incertidumbre por geometría de
visión y correlaciona con lluvia, PAR y humedad relativa.

## Hallazgos clave (para el pipeline)
- **SIFn muestra el descenso MÁS TEMPRANO** ante la sequía, **antes que la SIF cruda, los VIs
  (incl. NDVI) y ΦF** (abstract, p.1). → evidencia directa de la hipótesis "SIF antes que NDVI",
  ahora también para la SIF *normalizada*.
- **En las 2 primeras semanas de sequía, SIFn cayó 8.2 %, 7.0 %, 12.5 % y 8.2 %** en las 4
  subdivisiones de la NCP (abstract, p.1) → magnitud concreta de la señal temprana.
- **NDVI está limitado por saturación y por respuesta retardada a la precipitación** (intro, p.1,
  citando ref. [10]). → confirma la debilidad de NDVI que VegStress busca complementar.
- **El análisis biquincenal detecta la sequía ANTES que el mensual** y se alinea con la
  escala temporal de las respuestas de Rd (down-regulation) → relevancia fisiológica de muestrear
  más fino que mensual.
- Durante el INICIO de sequía, la correlación de NIRv (estructura del dosel) y ΦF (clorofila) con
  SIF es **débil (R: 0.16-0.32)**; al FINAL es **fuerte (R: 0.83-0.87)** → estructura y clorofila
  afectan SIF en etapas distintas (estructura/ΦF entran tarde; SIFn capta el estrés antes que ambas).
- SIFn correlaciona con anomalía de lluvia (R: 0.45-0.52), PAR (R: 0.80-0.84) y humedad relativa
  (R: 0.52-0.54).

## Citas útiles (con página)
- "SIFn provides an effective method for drought monitoring, showing the earliest decline compared
  to raw SIF, VIs, and ΦF" (abstract, p.1)
- "In the first two weeks of drought, SIFn decreased by 8.2%, 7.0%, 12.5%, and 8.2% across the four
  NCP subdivisions" (abstract, p.1)
- "the normalized difference vegetation index (NDVI) ... can be limited by saturation effect and
  delayed precipitation response" (intro, p.1)
- "SIFn ... could detect drought stress earlier than traditional VI-based methods" (conclusión)

## Relevancia para VegStress
**Segundo pilar empírico (junto con PD-018) de la hipótesis SIF-antes-que-NDVI**, y el primero
que valida la *SIF normalizada* (corregida por geometría/PAR) como el indicador más temprano,
batiendo a la SIF cruda, a los VIs y a ΦF. Refuerza el caso de explorar un canal SIF en VegStress
y aporta una lección operativa: **muestrear biquincenal (no mensual)** mejora la detección
temprana. **Caveat de transferibilidad**: es estrés HÍDRICO en cultivos de la NCP (no CO2
volcánico en bosque Nothofagus/Araucaria) y usa productos SIF satelitales cuya resolución
(TROPOMI/OCO-2/3) es gruesa para AOIs de quebrada — la misma limitación de resolución que PD-018.

## Dónde aplica (mapeo a código/doc)
- `BIBLIOGRAPHY_SYNTHESIS.md §4` — segundo paper que valida SIF→NDVI lead-time (con SIFn).
- `seasonal_vs_volcanic.md §Estrategia` — SIF normalizada como canal de respuesta más rápida.
- `change_detector.py` — lección de cadencia: muestreo biquincenal > mensual para señal temprana.
- Roadmap v2 — evaluar SIFn (corrección BRDF/PAR) y resolución de productos SIF para AOIs chicas.

## Flags
- `[VERSIÓN]` PDF = accepted manuscript (green-OA Lirias/KU Leuven), no el maquetado IEEE final.
  Páginas citadas son del manuscrito; para página exacta del published usar IEEE Xplore.
- Afiliación 1er autor (Gao, China Agricultural University) verificada en footer p.1.
- `[NOTA]` Estrés hídrico en cultivos NCP, NO CO2 volcánico. Mecanismo y bioma distintos al caso
  de VegStress; la ventaja temporal de SIFn no está validada para desgasificación difusa.
- `[NOTA]` No reporta un lead-time numérico exacto "X días antes que NDVI"; reporta "descenso más
  temprano" + caídas a 2 semanas + biquincenal > mensual. No inventar un número de días.
