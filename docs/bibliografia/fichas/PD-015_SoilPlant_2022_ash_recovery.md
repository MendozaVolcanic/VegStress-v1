# Ficha: PD-015

**Archivo PDF**: `pdfs/Saputra_2022_Kelud_ash_soil_recovery.pdf` (17 pp, OA)
**Título**: Recovery after volcanic ash deposition: vegetation effects on soil organic carbon, soil structure and infiltration rates
**Autores**: Danny Dwi Saputra, Kurniatun Hairiah, Didik Suprayogo, Rika Ratna Sari, Widianto, Meine van Noordwijk
**Afiliación 1er autor**: Plant Production Systems, Wageningen University & Research, Países Bajos (también Brawijaya University, Indonesia) (p.1)
**Año**: 2022 · **Revista**: Plant and Soil · **DOI**: 10.1007/s11104-022-05322-7
**OA**: sí (The Author(s) 2022) · **Leído**: ✅ (vía markitdown `md/SoilPlant_2022_ash_vegetation_recovery.md`, 2026-06-07)

## Metodología
Cronosecuencia (space-for-time) en la ladera del **Mt. Kelud (Java, Indonesia)**, erupción de feb-2014 que depositó hasta 20 cm de ceniza. 12 parcelas en 4 usos de suelo (bosque degradado DF, agroforestería compleja CAF y simple SAF, cultivos anuales CR), medidas en PRE-erupción (2007/08), 3 y 6 años post (YAE). Variables de **suelo** (no índice espectral): espesor de ceniza preservada, hojarasca, C orgánico (Corg, Walkley-Black), estabilidad de agregados (MWD), porosidad, infiltración. ANOVA + Tukey + regresión.

## Hallazgos clave (para el pipeline)
- **Tiempos de recuperación contrastados por propiedad** (núcleo del paper):
  - **Infiltración**: colapsa de 28.9 → 3.7 cm/h a 3 YAE, pero **recupera al nivel PRE en 6 años** (rápido) (p.8, Fig.4).
  - **Estabilidad de agregados (MWD)**: mínimo a 3 YAE (1.55 mm), recupera a PRE en 6 YAE (~2.67 mm) (p.9, Tabla 1).
  - **C orgánico (Corg)**: recuperación **lenta** — parte de niveles bajos en ceniza fresca y sube gradualmente (DF 0.67%/año los primeros 3 años; CAF/SAF más lento) (p.7).
  - **Hojarasca**: en CAF a 6 YAE ya supera PRE (recuperación completa) (p.7).
- **Espesor de ceniza preservada 6 YAE: 2–14 cm (media 8.5 cm)**; el original estimado fue **9.8–13.9 cm** (la ceniza se compacta/redistribuye ~40% en 2 años, Blong 2017) (p.8).
- **Hidrofobicidad inicial** de la ceniza fresca limita infiltración y agregación → "desconexión" temporal del suelo (p.2 diagrama conceptual).
- **El espesor depende de la posición de ladera, NO de la cobertura de copa** (R²=0.03 con copa vs. R²=0.28 con posición; valle 25–85% más grueso que ladera media/alta) (p.6).
- **El uso de suelo gobierna la trayectoria de recuperación**: sistemas arbóreos (DF, agroforestería) recuperan más rápido y acumulan más Corg que cultivo anual.

## Citas útiles (con página)
- "soil infiltration ... from an average of 28.9 cm hour⁻¹ in PRE plummeting to 3.7 cm hour⁻¹ in 3 YAE ... quickly recovered to its PRE condition after six years" (p.8).
- "Corg slowly increased from low levels in the fresh volcanic ash ... aggregate stability, and soil infiltration quickly recovered" (abstract).
- "no relationship between canopy cover and preserved volcanic ash thickness ... R²=0.03 ... significant relationship between volcanic ash thickness and plot position ... R²=0.28" (p.6).

## Relevancia para VegStress
Aporta la **escala temporal subyacente** al greening/browning que veremos en NDVI: tras ceniza, lo que el satélite verá como "recuperación de vigor" responde a procesos de suelo con tiempos muy distintos (infiltración/agregados en años, Corg en décadas). Importa para no confundir una recuperación NDVI rápida con recuperación ecosistémica completa, y para entender por qué la vegetación arbórea (Araucaria/Nothofagus, PD-016) puede recuperarse a ritmo distinto que pastizal. La dependencia espesor↔posición-de-ladera (no copa) sugiere que las AOIs deben considerar topografía.

## Dónde aplica (mapeo a código/doc)
- `seasonal_vs_volcanic.md` — argumento de que la recuperación post-ceniza es multi-año → ventanas temporales largas para distinguir señal de ruido estacional.
- `aoi_config.json` — la dependencia espesor↔posición topográfica apoya ponderar AOIs por ladera/valle.
- `BIBLIOGRAPHY_SYNTHESIS.md §recuperación` — tiempos de recuperación por proceso.

## Flags
Afiliación verificada (p.1). Caso tropical/agroforestal indonesio, no chileno → tiempos de recuperación NO transferibles directamente a bosque andino-patagónico templado (clima y especies distintos). Es estudio de suelo, no de teledetección: aporta contexto físico, no umbrales NDVI.
