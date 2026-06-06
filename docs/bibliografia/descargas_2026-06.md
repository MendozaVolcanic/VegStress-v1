# Descargas bibliográficas — ronda junio 2026

Búsqueda con APIs gratis (arXiv/Crossref/OpenAlex/Semantic Scholar) vía 2 subagentes
paralelos + Perplexity Pro Deep Research vía Chrome (comparativo, lección AP20).
PDFs en `docs/bibliografia/pdfs/`. Verificación magic bytes §5.4 aplicada.

## ✅ Descargados y verificados (PDF válido, %PDF- + tamaño OK)

| # | Archivo | Tema | DOI | Fuente |
|---|---|---|---|---|
| 1 | `Jakubik_2023_Prithvi_geospatial_FM.pdf` | 5-Mejoras/ML | 10.48550/arXiv.2310.18660 | arXiv |
| 2 | `Coppola_2020_MIROVA_thermal_volcano.pdf` | 5-Multisensor | 10.3389/feart.2019.00362 | Frontiers |
| 3 | `Theys_2019_TROPOMI_SO2_degassing.pdf` | 5-Multisensor | 10.1038/s41598-019-39279-y | Nature SciRep |
| 4 | `CordonCaulle_2016_NHESS_eruption.pdf` | 6-Chile | 10.5194/nhess-16-675-2016 | Copernicus |
| 5 | `Biass_2022_CordonCaulle_Vegetation_Tephra_ML.pdf` | 3-CO2/Chile/ML | 10.5194/nhess-22-2829-2022 | Copernicus |
| 6 | `AshFall_2015_vegetation_remotesensing.pdf` | 6-Chile | 10.1186/s13617-015-0032-z | BMC AppliedVolc |
| 7 | `CawseNicholson_2018_AirborneRS_CO2.pdf` | 1/3-CO2/RS | 10.5194/bg-15-7403-2018 | Copernicus BG |
| 8 | `USGS_1996_Mammoth_CO2_TreeKill.pdf` | 3-CO2 Mammoth | 10.3133/fs17296_1996 | USGS |
| 9 | `SoilPlant_2022_ash_vegetation_recovery.pdf` | 6-Chile | 10.1007/s11104-022-05322-7 | Springer (OA) |
| 10 | `AlvarezGarreton_2018_CAMELS_CL.pdf` | 5-Clima/Chile | 10.5194/hess-22-5817-2018 | Copernicus HESS |
| 11 | `Eitel_2010_rededge_drought.pdf` | 4-Red-edge | 10.1093/jxb/erq201 | OUP (OA) |
| 12 | `Zamorano_2011_Araucaria_discriminacion.pdf` | 6-Especies | 10.4067/s0717-92002011000200002 | SciELO Chile |
| 13 | `Zamorano_2015_Araucaria_fragmentation.pdf` | 6-Especies | 10.3832/ifor1399-008 | iForest |

## ⏳ Pendientes — descarga MANUAL vía navegador (editorial bloquea curl)

Estos están detrás de Akamai/Cloudflare/anti-bot. Son OA o gratis pero requieren
abrir en Chrome (lección §5.1, §5.7). Ruta sugerida: EO Browser / login institucional.

| Autor año | Título | DOI | Por qué manual |
|---|---|---|---|
| Magney 2019 | SIF mechanistic tracking photosynthesis | 10.1073/pnas.1900278116 | PNAS bloquea curl (PMC6575166) |
| Magney 2018 | Global SIF retrievals | 10.1029/2018GL079031 | Wiley/AGU pdfdirect bloquea curl |
| Bogue 2023 | Plant responses to volatile emissions (tree rings) | 10.1029/2023GC010938 | Wiley/AGU bloquea curl |
| ZalazarTobar 2013 | Araucaria growth patterns | 10.1111/aec.12054 | Wiley bloquea curl |
| Bea 2024 (McGill) | **Vegetation-based proxies for satellite detection** | tesis | escholarship landing, requiere navegar |
| iScience 2024 | **Hazardous volcanic CO2 diffuse degassing — review** | 10.1016/j.isci.2024.110990 | Cell Press bloquea curl (CC-BY) |
| SIF-vs-VI 2025 | Normalized SIF responde antes que VIs | 10.1109/TGRS.2025.3561216 | IEEE paywall |
| GRL 2025 | SIF como early warning operacional | 10.1029/2025GL119408 | AGU (verificar OA) |
| SIF-NDVI 2024 | Comparación SIF satelital vs NDVI | 10.3390/rs16101735 | MDPI (Akamai bloquea curl) |
| Coppola 2019 | Global volcano monitoring multisensor Sentinel | 10.3390/rs11131528 | MDPI (Akamai) |

## ❌ Paywall real (sin OA verde — requiere VPN SERNAGEOMIN/biblioteca)

Confirmado por Unpaywall/OpenAlex que NO tienen copia OA. Son los **seminales clave**
de detección de cambios y CO2 — vale conseguirlos por VPN institucional.

| Autor año | Título | DOI | Rol |
|---|---|---|---|
| Farrar 1995 | Forest-killing diffuse CO2 Mammoth Mountain | 10.1038/376675a0 | **Seminal CO2-vegetación** |
| Houlié 2006 | Early detection eruptive dykes via NDVI | 10.1016/j.epsl.2006.03.039 | **Seminal NDVI-volcán** |
| Verbesselt 2010 | BFAST — trend & seasonal change | 10.1016/j.rse.2009.08.014 | **Seminal estacional** |
| Verbesselt 2012 | BFAST Monitor — near real-time | 10.1016/j.rse.2012.02.022 | **Seminal NRT** |
| Zhu 2014 | CCDC — continuous change detection | 10.1016/j.rse.2014.01.011 | **Seminal CCDC** |
| Kennedy 2010 | LandTrendr | 10.1016/j.rse.2010.07.008 | **Seminal LandTrendr** |
| Frampton 2013 | Sentinel-2 red-edge biophysical | 10.1016/j.isprsjprs.2013.04.007 | Red-edge S2 |
| Claverie 2018 | HLS surface reflectance | 10.1016/j.rse.2018.09.002 | HLS (probar HAL green) |
| Lewicki 2014 | Multi-scale magmatic CO2 Mammoth | 10.1016/j.jvolgeores.2014.07.011 | CO2 flux |
| Lucas 2014 | Tree rings CO2 magmatic fluids | 10.1016/j.epsl.2013.12.035 | Tree-ring CO2 |
| Pizarro 2018 | Ash deposits 2011 Puyehue-CC | 10.1016/j.jvolgeores.2018.01.020 | Chile ash |

## Hallazgos NUEVOS de esta ronda (no estaban en papers_completo.md)

1. **Bea 2024 (tesis McGill)** — "Developing vegetation-based proxies for satellite
   detection" — casi seguro detección de vegetación en disturbios volcánicos. **Máxima prioridad.**
2. **iScience 2024 review** — revisión sistemática de áreas de desgasificación CO2 difusa
   peligrosas (CC-BY). Ancla de síntesis que faltaba.
3. **Cawse-Nicholson 2018** (Biogeosciences, OA) — espectroscopía aerotransportada de
   respuesta de ecosistema a CO2 elevado. Precedente publicado más cercano a AVUELO. ✅ descargado.
4. **SIF responde antes que NDVI (TGRS 2025 + GRL 2025)** — validan directamente la
   hipótesis central de VegStress (SIF precede a NDVI). Paywall, conseguir vía IEEE/AGU.
5. **HLS v2.0 (2025)** supersede a Claverie 2018 — relevante para el pipeline.
6. **CR2MET (Zenodo) + CAMELS-CL** — controles de confusión sequía/clima para Chile. ✅ CAMELS descargado.

## Perplexity Pro (comparativo) — ver `perplexity_hallazgos_2026-06.md`

Aportó 2 hallazgos que las APIs gratis NO encontraron (valida AP20):
1. **Etna RSE 2024** "Monitoring volcanic CO2 flux by remote sensing of vegetation
   on Mt. Etna" (`S0034425724004346`) — caso operacional MÁS cercano a VegStress.
   Preprint SSRN gratis (abstract 4762417) → descarga manual.
2. **Bogue 2023 green-OA** en Chapman (la versión Wiley estaba bloqueada).
