# Ficha: PD-014

**Archivo PDF**: `pdfs/DeSchutter_2015_OldoinyoLengai_ashfall_vegetation.pdf` (18 pp, OA)
**Título**: Ash fall impact on vegetation: a remote sensing approach of the Oldoinyo Lengai 2007–08 eruption
**Autores**: Ann De Schutter, Matthieu Kervyn, Frank Canters, Sonja A. Bosshard-Stadlin, Majura A. M. Songo, Hannes B. Mattsson
**Afiliación 1er autor**: Dept. of Geography, Earth System Science, Vrije Universiteit Brussel, Bélgica (p.1; Kervyn es autor de correspondencia)
**Año**: 2015 · **Revista**: Journal of Applied Volcanology · **DOI**: 10.1186/s13617-015-0032-z
**OA**: sí (CC-BY 4.0) · **Leído**: ✅ (vía markitdown `md/AshFall_2015_vegetation_remotesensing.md`, 2026-06-07)

> ⚠️ El nombre del archivo dice "AshFall_2015"; el 1er autor real es **De Schutter** (no Kervyn, que es correspondiente).

## Metodología
Serie temporal NDVI de **MODIS MOD13Q1** (composite 16-días, 250 m) 2005–2013 sobre Oldoinyo Lengai (Tanzania), erupción 2007–08. **Índice = NDVI** (eligen NDVI por robustez en recuperación post-fuego, p.4). Decorrelan la lluvia con regresión polinómica de 2º orden NDVI~precipitación antecedente por clase vegetación-elevación (NDVIdif = observado − esperado). Mapean la zona afectada con **análisis bi-temporal + PCA**; cuantifican recuperación con índices (LG, Tc, SRI, VRR, **ARI**) y regresión logarítmica de la pendiente de recuperación vs. tiempo.

## Hallazgos clave (para el pipeline)
- **Índice usado: NDVI** (no SAVI ni EVI); justifican que NDVI no es superado por SAVI para recuperación de vegetación (p.4, Veraverbeke et al. 2012).
- **Umbral de ceniza ~3 cm**: espesor mínimo para perturbar el estado de la vegetación de forma detectable por el análisis de cambio. Bajo 3 cm la recuperación es <1 año; sobre ~8–10 cm se requieren varios años para *empezar* a recuperar (p.11, p.15).
- **Relación espesor↔daño = no lineal, power-law débil** entre espesor de ceniza medido en campo y pendiente de recuperación. Mejor ajuste con el índice **ARI (R²=0.28)**, seguido de Tc (R²=0.25) (p.10). Gran dispersión → espesor es solo uno de varios factores; relación posiblemente controlada por umbrales.
- **Tiempos de recuperación**: de >5 años (proximal, ceniza gruesa) a <6 meses (distal) con la distancia al volcán (abstract; p.12).
- **Decorrelación de lluvia con regresión polinómica de 2º orden** por sub-región vegetación-elevación; el lag óptimo de lluvia antecedente fue 48 días para herbáceas 1500–2100 m (p.5, Fig.4).
- Vegetación baja (pastizal/matorral) **más vulnerable que el bosque**; bosques en las tierras altas no fueron afectados significativamente (p.14).

## Citas útiles (con página)
- "3 cm of ash is the threshold thickness above which all vegetation types in the study area showed a significant recovery trend" (p.11) — umbral de daño detectable.
- "The estimated recovery time varies from more than 5 years to less than 6 months with increasing distance from the volcano" (abstract).
- "the statistically best fit is found for the Ash Recovery Index (R²=0.28)" (p.10) — espesor↔recuperación es débil/no lineal.

## Relevancia para VegStress
Caso análogo de **caída de ceniza → browning** (lo opuesto al CO2-greening de Guinn PD-001): aquí el mecanismo SÍ es daño/browning por enterramiento. Aporta (1) un **umbral físico (~3 cm de ceniza)** bajo el cual el cambio NDVI no es atribuible al volcán, útil para calibrar el ΔNDVI de alerta; (2) que la relación espesor↔daño es **no lineal y ruidosa** → no esperar una función simple; (3) confirma la **decorrelación de lluvia** como paso obligatorio antes de atribuir cambio.

## Dónde aplica (mapeo a código/doc)
- `change_detector.py` — el escenario browning-por-ceniza valida la lógica clásica de alerta (complementa a Guinn que la invierte para CO2).
- `seasonal_vs_volcanic.md` — su regresión polinómica de 2º orden NDVI~lluvia es una estrategia concreta de control climático (paralela a CAMELS-CL, PD-012).
- `BIBLIOGRAPHY_SYNTHESIS.md §umbrales` — umbral 3 cm como referencia de "ceniza mínima detectable".

## Flags
Afiliación verificada (p.1). 1er autor = De Schutter (no el nombre del archivo). Caso africano (savana), no chileno → extrapolar umbrales a bosque andino con cautela (los propios autores advierten que no probaron bosque, p.15).
