# Proyectos Similares a VegStress-v1

> Inventario de plataformas operacionales, repositorios y APIs relevantes para inspiracion, codigo, datos o colaboracion.
> **Fecha de compilacion:** 2026-04-25
> **Nota de confianza:** compilado desde conocimiento entrenado (corte enero 2026). Cada entrada lleva un flag:
> - **[VERIFIED]** — informacion estable, baja probabilidad de cambio.
> - **[CHECK]** — verificar URL/estado en vivo antes de citar oficialmente.
> - **[DEAD]** — proyecto sin actividad reciente, no profundizar.
>
> URLs marcadas con `*` deben confirmarse manualmente.

---

## 1. Plataformas Operacionales de Monitoreo Volcanico Satelital

### 1.1 MOUNTS — Monitoring Unrest from Space [VERIFIED]
- **URL:** http://www.mounts-project.com *
- **GitHub:** https://github.com/mounts-project *
- **Owner:** TU Berlin / Sebastien Valade (lider), con colaboradores INGV y otros.
- **Status:** Activo (publicacion clave 2019, plataforma actualizada hasta 2024-2025).
- **Que hace:** Plataforma multi-sensor que combina Sentinel-1 (InSAR), Sentinel-2 (termal/SWIR), Sentinel-5P (SO2) y deep learning para detectar anomalias en >20 volcanes globales. Genera dashboards con time-series automatizadas.
- **Que copiamos:** Arquitectura de pipeline multi-sensor; UI del dashboard volcan-por-volcan; metodologia de fusion de indices; estrategia de alertas. **Es la referencia mas directa para VegStress-v1**.
- **API/datos:** Productos visualizables; descarga programatica limitada — contactar a Valade para colaboracion academica. Codigo en GitHub (ML para SO2 y deformacion).
- **Last update:** 2024-2025.

### 1.2 MIROVA — Middle Infrared Observation of Volcanic Activity [VERIFIED]
- **URL:** https://www.mirovaweb.it
- **Owner:** Universita di Torino + INGV (Coppola, Laiolo, Cigolini).
- **Status:** Activo, scrapeado diariamente por nuestro proyecto hermano.
- **Que hace:** Detecta hotspots termicos MODIS+VIIRS en tiempo casi-real. Genera VRP (Volcanic Radiative Power) por volcan.
- **Que copiamos:** Esquema de clasificacion de actividad termica; formato de series temporales; ya integrado.
- **API/datos:** No hay API publica oficial — scraping HTML y OCR (ver Automatizacion web V5.0). Datos abiertos, no requiere auth.
- **Last update:** Continuo.

### 1.3 MODVOLC [VERIFIED]
- **URL:** http://modis.higp.hawaii.edu/
- **Owner:** HIGP — Universidad de Hawaii (Robert Wright et al.).
- **Status:** Activo desde 2000, sigue corriendo.
- **Que hace:** Algoritmo de deteccion de hotspots termicos en MODIS Terra/Aqua. Cubre todos los volcanes activos.
- **Que copiamos:** Threshold de NTI (Normalized Thermal Index); enfoque historico largo (24+ anos); cross-validacion de eventos.
- **API/datos:** Browse interface por volcan; descarga CSV de pixeles termicos. Libre, sin auth.
- **Last update:** 2024+ (continuo).

### 1.4 Smithsonian GVP — Global Volcanism Program [VERIFIED]
- **URL:** https://volcano.si.edu
- **GitHub:** algunos clientes en https://github.com/smithsonian *
- **Owner:** Smithsonian Institution.
- **Status:** Activo, base de datos canonica.
- **Que hace:** Catalogo global de volcanes, erupciones historicas, Weekly Volcanic Activity Reports en colaboracion con USGS.
- **Que copiamos:** IDs canonicos de volcanes (Smithsonian Volcano Number); metadata para nuestros 11 volcanes chilenos.
- **API/datos:** WFS/WMS publicos; CSV/JSON descargables; API REST documentada. Libre.
- **Last update:** Semanal.

### 1.5 VONA / VAACs (Volcano Observatory Notice for Aviation) [VERIFIED]
- **URL:** https://www.ssd.noaa.gov/VAAC/vaac.html (Washington VAAC); Buenos Aires VAAC: https://www.smn.gob.ar/vaac
- **Owner:** ICAO + 9 VAACs regionales (Buenos Aires cubre Andes Chile/Argentina).
- **Status:** Activo, operacional 24/7.
- **Que hace:** Emite avisos de cenizas para aviacion en formato estandarizado.
- **Que copiamos:** Formato de mensaje de alerta estandarizado (XML/text); disparadores para emision de alertas en VegStress.
- **API/datos:** Feeds RSS/text publicos.
- **Last update:** Tiempo real.

### 1.6 NASA Disasters Mapping Portal [VERIFIED]
- **URL:** https://maps.disasters.nasa.gov
- **Owner:** NASA Disasters Program.
- **Status:** Activo.
- **Que hace:** Mapas operacionales para respuesta a desastres incluyendo activaciones volcanicas (capa de cenizas, termica, deformacion).
- **Que copiamos:** Arquitectura ArcGIS Online de capas modulares; estilo de mapas de impacto.
- **API/datos:** ArcGIS REST endpoints publicos.
- **Last update:** Continuo segun eventos.

### 1.7 Copernicus Emergency Management Service (EMS) [VERIFIED]
- **URL:** https://emergency.copernicus.eu
- **Owner:** EU / DG-DEFIS, operado por consorcio (e-GEOS, SERTIT, otros).
- **Status:** Activo.
- **Que hace:** Activaciones rapidas para desastres. Tiene historico de productos para erupciones (La Palma 2021, Etna multiples, Hunga Tonga 2022).
- **Que copiamos:** Plantillas cartograficas, simbologia volcanica oficial EU.
- **API/datos:** Productos descargables PDF/SHP/GeoTIFF gratis post-activacion.
- **Last update:** Por evento.

### 1.8 ESA G-POD / Volcano Pilot [CHECK]
- **URL:** https://gpod.eo.esa.int *
- **Owner:** ESA EO Science.
- **Status:** Migrando hacia Copernicus DataSpace; algunos servicios deprecados.
- **Que hace:** Procesamiento on-demand de SAR (InSAR) para deformacion volcanica.
- **Que copiamos:** Workflows de SBAS/PSI documentados.
- **API/datos:** Acceso para usuarios registrados ESA.

### 1.9 DLR Volcano Information Service [CHECK]
- **URL:** https://atmos.eoc.dlr.de/ *
- **Owner:** DLR-EOC (Aachen/Oberpfaffenhofen).
- **Status:** Activo para SO2 (TROPOMI, GOME-2).
- **Que hace:** Productos near-real-time de SO2, ash, AAI para volcanes globales.
- **Que copiamos:** Cross-validacion de actividad: SO2 + nuestra senal NDVI.
- **API/datos:** WMS/WCS publicos, NRT en horas.

### 1.10 INGV — Productos Etna/Stromboli [VERIFIED]
- **URL:** https://www.ct.ingv.it (Catania) y https://www.ingv.it
- **Owner:** Istituto Nazionale di Geofisica e Vulcanologia.
- **Status:** Muy activo.
- **Que hace:** Boletines diarios/semanales con productos satelitales propios + termica + deformacion + gas.
- **Que copiamos:** Estructura de boletin operacional; formato de comunicacion con autoridades; podrian colaborar academicamente (lazos con MIROVA/MOUNTS).
- **API/datos:** Boletines PDF; algunos productos via WebGIS.

### 1.11 OVDAS — SERNAGEOMIN Chile [VERIFIED]
- **URL:** https://rnvv.sernageomin.cl/ y https://www.sernageomin.cl
- **Owner:** SERNAGEOMIN (Nicolas trabaja aqui).
- **Status:** Activo. RNVV = Red Nacional de Vigilancia Volcanica.
- **Que hace:** Vigilancia oficial de 90+ volcanes chilenos. Reportes semanales (REAV/RAV).
- **Que copiamos:** Formato oficial de reportes; integrar VegStress como capa adicional al sistema interno; **nuestro mejor canal de adopcion operacional**.
- **API/datos:** Datos sismicos/visuales internos; web publica con boletines.

### 1.12 Alaska Volcano Observatory (AVO) [VERIFIED]
- **URL:** https://avo.alaska.edu
- **GitHub:** https://github.com/alaska-volcano-observatory *
- **Owner:** USGS + Universidad de Alaska Fairbanks + DGGS.
- **Status:** Muy activo.
- **Que hace:** Monitoreo multi-parametro de 50+ volcanes; pioneros en uso operacional de Sentinel/Landsat para Aleutianas.
- **Que copiamos:** Codigo de procesamiento termico; experiencia con stratovolcanes glaciados (analogo a Andes Sur).
- **API/datos:** Imagenes y boletines publicos; algunos repos abiertos.

### 1.13 USGS Volcano Hazards Program [VERIFIED]
- **URL:** https://www.usgs.gov/programs/VHP
- **GitHub:** https://github.com/usgs *
- **Owner:** USGS.
- **Status:** Activo.
- **Que hace:** Coordinacion de 5 observatorios (HVO, AVO, CVO, YVO, CalVO); productos satelitales y terrestres.
- **Que copiamos:** Niveles de alerta volcanica color-coded estandar; integrar con nuestros niveles de stress.
- **API/datos:** API publica para alertas (https://volcanoes.usgs.gov/hans-public/api/volcano/*).

### 1.14 LAVA — INGV Hotsat [CHECK]
- **URL:** https://hotsat.ct.ingv.it *
- **Owner:** INGV-Catania.
- **Status:** Activo.
- **Que hace:** Plataforma termica satelital INGV, complementaria a MIROVA.
- **Que copiamos:** Algoritmos termicos para sensores SLSTR/MODIS.

---

## 2. Dashboards de Vegetacion / Fenologia (referencia UI/UX)

### 2.1 Global Forest Watch (GFW) [VERIFIED]
- **URL:** https://www.globalforestwatch.org
- **GitHub:** https://github.com/wri/gfw
- **Owner:** World Resources Institute + partners.
- **Status:** Muy activo.
- **Que hace:** Dashboard global de perdida forestal con alertas (GLAD, RADD, DETER).
- **Que copiamos:** **Mejor referencia UI/UX para nuestro dashboard.** Sistema de AOIs, alertas por email, time-series interactivas.
- **API/datos:** API REST pormenorizada (https://data-api.globalforestwatch.org); Mapbox tiles.
- **Last update:** Continuo.

### 2.2 Sentinel Hub EO Browser [VERIFIED]
- **URL:** https://apps.sentinel-hub.com/eo-browser
- **GitHub:** https://github.com/sentinel-hub/EO-Browser *
- **Owner:** Sinergise / Planet.
- **Status:** Muy activo.
- **Que hace:** Visualizador de Sentinel/Landsat/MODIS con custom scripts (evalscript).
- **Que copiamos:** Custom scripts (NDVI, NBR, BAI, evalscripts en JS) que ya usamos parcialmente; sistema de "themes" personalizables.
- **API/datos:** Sentinel Hub API + Statistical API (clave para nuestras AOIs).

### 2.3 Digital Earth Africa / Australia [VERIFIED]
- **URL:** https://www.digitalearthafrica.org y https://www.dea.ga.gov.au
- **GitHub:** https://github.com/digitalearthafrica , https://github.com/GeoscienceAustralia/dea-notebooks
- **Owner:** Geoscience Australia + DE Africa consortium.
- **Status:** Muy activo.
- **Que hace:** Open Data Cube nacional con productos analiticos listos (WOfS, GeoMAD, Fractional Cover).
- **Que copiamos:** **Arquitectura ODC (Open Data Cube)** para datacube de Andes; notebooks de geomedian; productos de coherencia temporal.
- **API/datos:** STAC API + Sandbox JupyterHub gratuito.

### 2.4 Copernicus Global Land Service (CGLS) [VERIFIED]
- **URL:** https://land.copernicus.eu/global
- **Owner:** Comision Europea / VITO.
- **Status:** Activo.
- **Que hace:** Productos NDVI, LAI, FAPAR, FCover globales 300m (Sentinel-3) y 1km (PROBA-V historico).
- **Que copiamos:** Productos NDVI 10-day como baseline regional para anomalias; metodologia de smoothing temporal.
- **API/datos:** Descargas NetCDF gratuitas con registro.

### 2.5 NASA Worldview / GIBS [VERIFIED]
- **URL:** https://worldview.earthdata.nasa.gov
- **GitHub:** https://github.com/nasa-gibs/worldview
- **Owner:** NASA EOSDIS.
- **Status:** Muy activo, opensource.
- **Que hace:** Visor global de capas EOSDIS (~1000 capas), incluye anomalias termicas MODIS/VIIRS, ash, SO2.
- **Que copiamos:** **Codigo opensource del visor (React)**; protocolo GIBS WMTS para servir tiles.
- **API/datos:** GIBS WMTS publico, sin auth.

### 2.6 Google Earth Engine Apps (varios) [VERIFIED]
- **URL ejemplos:** https://earthengine.google.com/case_studies y catalogo apps.earthengine.google.com
- **Que hace:** Apps publicas para LandTrendr-GEE (Kennedy), CCDC-GEE (Zhu), Hansen Forest, MapBiomas Chaco/Bosque Atlantico.
- **Que copiamos:** **LandTrendr-GEE y CCDC-GEE son los algoritmos clave para detectar tendencia de stress NDVI**; portar a Python para CDSE.
- **API/datos:** Earth Engine Python API (free para investigacion).

### 2.7 GEOGLAM Crop Monitor [VERIFIED]
- **URL:** https://cropmonitor.org
- **Owner:** GEO + USDA + UMD.
- **Status:** Activo.
- **Que hace:** Monitoreo mensual de cultivos globales con anomalias NDVI.
- **Que copiamos:** Esquema de "areas de preocupacion" mensual; metodologia de comparacion con baseline climatologico.

### 2.8 Phenocam Network [VERIFIED]
- **URL:** https://phenocam.nau.edu
- **GitHub:** https://github.com/khufkens/phenocamr
- **Owner:** Northern Arizona University + colaboradores.
- **Status:** Activo.
- **Que hace:** Red de camaras fenologicas con extraccion automatica de GCC/Phenology metrics.
- **Que copiamos:** Metricas de "transition dates" (SOS, EOS) para validar estacionalidad — relevante para distinguir stress estacional vs volcanico.

### 2.9 LandTrendr-GEE [VERIFIED]
- **URL:** https://emapr.github.io/LT-GEE/
- **GitHub:** https://github.com/eMapR/LT-GEE
- **Owner:** Oregon State University (Robert Kennedy lab).
- **Status:** Activo.
- **Que hace:** Algoritmo de segmentacion temporal para detectar disturbios en time-series NBR/NDVI.
- **Que copiamos:** **Logica de segmentos para distinguir disturbio gradual (stress) vs abrupto (lava/lahares)**.

### 2.10 CCDC-GEE [VERIFIED]
- **GitHub:** https://github.com/GERSL/CCDC
- **Owner:** Univ. Connecticut (Zhe Zhu).
- **Status:** Activo.
- **Que copiamos:** Continuous Change Detection — superior a metodos basados en imagen unica para nuestro problema.

### 2.11 BFAST / bfastSpatial [VERIFIED]
- **URL:** http://bfast.r-forge.r-project.org/
- **GitHub:** https://github.com/bfast2/bfast , https://github.com/loicdtx/bfastSpatial
- **Owner:** Wageningen University (Verbesselt et al.).
- **Status:** Activo (R, con port Python `bfast` por GFZ).
- **Que copiamos:** **BFASTmonitor es ideal para deteccion near-real-time de breakpoints en NDVI** — candidato fuerte para reemplazar nuestra deteccion actual.

### 2.12 VITO Terrascope [VERIFIED]
- **URL:** https://terrascope.be
- **Owner:** VITO Belgica.
- **Status:** Activo.
- **Que hace:** Plataforma de productos Sentinel + servicios on-demand (incluye world cereal).
- **Que copiamos:** Modelo de "Processing API" para correr workflows en cloud.

---

## 3. Repositorios GitHub Relevantes

### 3.1 sentinelsat [VERIFIED]
- **GitHub:** https://github.com/sentinelsat/sentinelsat
- **Status:** Mantenimiento (Copernicus migro a CDSE/STAC).
- **Que copiamos:** Patrones de paginacion y reintentos; aunque migrar a `pystac-client` + CDSE.

### 3.2 openeo-python-client [VERIFIED]
- **GitHub:** https://github.com/Open-EO/openeo-python-client
- **Owner:** OpenEO consortium.
- **Status:** Muy activo.
- **Que copiamos:** Backend-agnostic processing — podria correr nuestro pipeline en VITO/CDSE/EODC sin reescritura.

### 3.3 eo-learn [VERIFIED]
- **GitHub:** https://github.com/sentinel-hub/eo-learn
- **Owner:** Sinergise.
- **Status:** Activo.
- **Que copiamos:** Framework de EOTask/EOWorkflow — buen modelo para componer pipeline NDVI.

### 3.4 satpy [VERIFIED]
- **GitHub:** https://github.com/pytroll/satpy
- **Status:** Muy activo.
- **Que copiamos:** Lectura multi-sensor; util para integrar Sentinel-3 SLSTR/OLCI mas adelante.

### 3.5 hyp3-isce2 / MintPy [VERIFIED]
- **GitHub:** https://github.com/insarlab/MintPy , https://github.com/ASFHyP3/hyp3-isce2
- **Owner:** Caltech/JPL + ASF.
- **Status:** Muy activo.
- **Que copiamos:** Pipeline InSAR para complementar VegStress con deformacion (Sentinel-1).

### 3.6 PyVolcano / vmod [CHECK]
- **GitHub:** https://github.com/uafgeotools/vmod *
- **Owner:** UAF Geophysical Institute.
- **Que copiamos:** Modelado de fuentes de deformacion volcanica.

### 3.7 stactools-packages [VERIFIED]
- **GitHub:** https://github.com/stactools-packages
- **Que copiamos:** Plantillas STAC para nuestros productos derivados (NDVI anomalies stack).

### 3.8 awesome-earthobservation-code [VERIFIED]
- **GitHub:** https://github.com/acgeospatial/awesome-earthobservation-code
- **Que copiamos:** Lista curada; punto de partida para descubrir mas repos.

### 3.9 geemap / leafmap [VERIFIED]
- **GitHub:** https://github.com/gee-community/geemap , https://github.com/opengeos/leafmap
- **Owner:** Qiusheng Wu (UTK).
- **Status:** Muy activo.
- **Que copiamos:** **leafmap es ideal para nuestro dashboard** — Folium/ipyleaflet wrapper con widgets STAC.

### 3.10 pyroSAR / OpenSARLab [VERIFIED]
- **GitHub:** https://github.com/johntruckenbrodt/pyroSAR
- **Que copiamos:** Procesamiento SAR Sentinel-1; complemento a optical.

### 3.11 detectree2 / forestools [CHECK]
- **GitHub:** https://github.com/PatBall1/detectree2 *
- **Que copiamos:** Segmentacion de copa para refinar mascaras de vegetacion sana.

### 3.12 prithvi-100M (IBM-NASA) [VERIFIED]
- **GitHub:** https://github.com/NASA-IMPACT/hls-foundation-os
- **HuggingFace:** https://huggingface.co/ibm-nasa-geospatial/Prithvi-100M
- **Status:** Activo (2023-2025).
- **Que copiamos:** Foundation model HLS para fine-tuning de detector de stress vegetal — alta prioridad para v2.

### 3.13 TorchGeo [VERIFIED]
- **GitHub:** https://github.com/microsoft/torchgeo
- **Owner:** Microsoft Research.
- **Que copiamos:** Datasets y trainers PyTorch para EO; util si vamos a deep learning.

### 3.14 RasterVision [VERIFIED]
- **GitHub:** https://github.com/azavea/raster-vision
- **Owner:** Azavea / Element 84.
- **Que copiamos:** Framework de inferencia geospatial.

### 3.15 stackstac + odc-stac [VERIFIED]
- **GitHub:** https://github.com/gjoseph92/stackstac , https://github.com/opendatacube/odc-stac
- **Que copiamos:** **Critico** — carga lazy de stacks STAC desde Planetary Computer / CDSE / Earth Search, base de cualquier datacube moderno.

---

## 4. Citizen Science / Comunidad

### 4.1 Smithsonian "What's Erupting" + boletines [VERIFIED]
- Ya cubierto en seccion 1.4.

### 4.2 Volcano Listserv (Arizona State) [VERIFIED]
- **URL:** https://volcano.asu.edu *
- **Owner:** Arizona State University.
- **Status:** Activo (mailing list de la comunidad volcanologica).
- **Que copiamos:** Canal de difusion de VegStress al publicarlo.

### 4.3 Zooniverse — Volcano Concierto / Jungle Rhythms [CHECK]
- **URL:** https://www.zooniverse.org
- **Status:** Algunas campanas volcanicas pasadas (e.g., Mapping change). Verificar campanas activas 2026.

### 4.4 IAVCEI Working Groups [VERIFIED]
- **URL:** https://www.iavcei.org
- **Que copiamos:** WG on Remote Sensing of Volcanoes — comunidad academica para difusion y colaboracion.

### 4.5 Volcanic Ash Twitter/X community [CHECK]
- Cuentas clave: @volcanowatcher, @Culture_Volcan, @sebastien_valade (MOUNTS), @USGSVolcanoes, @sernageomin.
- Util para difusion y feedback.

### 4.6 OpenVolcano [DEAD]
- Iniciativas dispersas, sin proyecto unificado activo. Saltar.

---

## 5. APIs y Portales de Datos

### 5.1 Copernicus Data Space Ecosystem (CDSE) [VERIFIED]
- **URL:** https://dataspace.copernicus.eu
- **STAC:** https://catalogue.dataspace.copernicus.eu/stac
- **Status:** Operacional desde 2023, reemplaza SciHub.
- **Acceso:** Free con cuenta; Sentinel Hub services + openEO + S3.
- **Ya en uso.**

### 5.2 Microsoft Planetary Computer [VERIFIED]
- **URL:** https://planetarycomputer.microsoft.com
- **STAC:** https://planetarycomputer.microsoft.com/api/stac/v1
- **Status:** Activo, free para investigacion (require token signing).
- **Que copiamos:** Mejor catalogo STAC global; Sentinel-2 L2A + Landsat + MODIS + DEM.
- **Acceso:** Free, sas-token via API.

### 5.3 AWS Open Data — Sentinel-2 / Landsat / MODIS [VERIFIED]
- **URL:** https://registry.opendata.aws/sentinel-2-l2a-cogs/
- **STAC (Earth Search):** https://earth-search.aws.element84.com/v1
- **Acceso:** Free read; transferencia free dentro de AWS.

### 5.4 Google Earth Engine [VERIFIED]
- **URL:** https://earthengine.google.com
- **Acceso:** Free para investigacion no comercial; comercial via GCP.
- **Que copiamos:** Catalogos de MODIS Active Fire (FIRMS), VIIRS, GOES, datasets ECMWF para meteorologia.

### 5.5 Smithsonian GVP API [VERIFIED]
- **URL:** https://volcano.si.edu/database/webservices.cfm *
- **Acceso:** Free.

### 5.6 USGS Volcano Hazards HANS API [VERIFIED]
- **URL:** https://volcanoes.usgs.gov/hans-public/api/
- **Acceso:** Free, JSON.

### 5.7 Copernicus DEM (GLO-30) [VERIFIED]
- **URL:** https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model
- **Acceso:** Free, registro.
- **Que copiamos:** Topografia para correccion radiometrica y mascaras de pendiente.

### 5.8 ASTER GDEM v3 [VERIFIED]
- **URL:** https://earthdata.nasa.gov/learn/find-data/near-real-time/aster
- **Acceso:** Free con NASA Earthdata login.

### 5.9 NASA FIRMS — Active Fire [VERIFIED]
- **URL:** https://firms.modaps.eosdis.nasa.gov
- **API:** https://firms.modaps.eosdis.nasa.gov/api/
- **Que copiamos:** Cross-validacion de hotspots termicos (MODIS/VIIRS/Landsat).
- **Acceso:** Free, API key.

### 5.10 TROPOMI / Sentinel-5P Pre-Ops Data Hub [VERIFIED]
- **URL:** https://s5phub.copernicus.eu (legado) → ahora via CDSE.
- **Que copiamos:** SO2, NO2, CO L2 — **clave para cross-validar episodios de desgasificacion**.

### 5.11 SACS — Support to Aviation Control Service [VERIFIED]
- **URL:** https://sacs.aeronomie.be
- **Owner:** BIRA-IASB Belgica.
- **Status:** Activo.
- **Que hace:** Alertas NRT de SO2/cenizas desde TROPOMI/IASI/GOME.
- **Acceso:** Free; suscripcion email.

### 5.12 MODIS MOD13Q1 / VIIRS VNP13 NDVI [VERIFIED]
- **Acceso:** AppEEARS https://appeears.earthdatacloud.nasa.gov
- **Que copiamos:** NDVI 16-day historico (2000+) como baseline de largo plazo.

### 5.13 HLS — Harmonized Landsat Sentinel [VERIFIED]
- **URL:** https://hls.gsfc.nasa.gov
- **STAC:** disponible en Planetary Computer y NASA CMR.
- **Que copiamos:** Producto armonizado L30+S30 — **deberia ser nuestra fuente principal** para series temporales mas densas que Sentinel-2 solo.

### 5.14 ECOSTRESS / EMIT (ISS) [VERIFIED]
- **URL:** https://ecostress.jpl.nasa.gov , https://earth.jpl.nasa.gov/emit/
- **Que copiamos:** ECOSTRESS LST a ~70m — **muy relevante para stress termico vegetal**; EMIT hyperspectral para mineral mapping en zonas alteradas.
- **Acceso:** Free via NASA Earthdata.

### 5.15 PACE / OCI [CHECK]
- **URL:** https://pace.oceansciences.org
- **Status:** Lanzado 2024. Hyperspectral global ~1km.
- **Que copiamos:** PRISM-like indices vegetales mas alla de NDVI (CCI, PRI).

---

## 6. Especifico Chile / Andes

### 6.1 SERNAGEOMIN — RNVV [VERIFIED]
- Ya cubierto en 1.11. **Stakeholder #1 de VegStress.**

### 6.2 CR2 — Centro de Ciencia del Clima y la Resiliencia [VERIFIED]
- **URL:** https://www.cr2.cl
- **Data Explorer:** https://www.cr2.cl/datos-productos-grillados/
- **Owner:** Univ. Chile + UDEC + UACh.
- **Status:** Activo.
- **Que hace:** Productos grillados de precipitacion, temperatura, sequia para Chile (CR2MET).
- **Que copiamos:** **CR2MET para correlacionar anomalias NDVI con sequia regional (control esencial)**.
- **Acceso:** Free.

### 6.3 DGA Chile — Direccion General de Aguas [VERIFIED]
- **URL:** https://snia.mop.gob.cl
- **Que copiamos:** Estaciones meteorologicas e hidrometricas cercanas a volcanes para validar contexto.

### 6.4 CONAF — SIDCO [VERIFIED]
- **URL:** https://www.conaf.cl
- **Que hace:** Sistema de Deteccion de Incendios CONAF (incluye satelital).
- **Que copiamos:** Cooperacion para distinguir senales de incendio vs stress volcanico.

### 6.5 SAG Chile [VERIFIED]
- **URL:** https://www.sag.gob.cl
- **Status:** No tiene productos satelitales operacionales relevantes a volcanes. Saltar.

### 6.6 Centro de Estudios Cientificos (CECs) — Valdivia [CHECK]
- **URL:** https://www.cecs.cl
- **Que hace:** Investigacion glaciologica con foco en glaciares andinos (incluye Chillan, Villarrica, Mocho-Choshuenco).
- **Que copiamos:** Posible colaboracion para volcanes glaciados (Villarrica, Llaima, Hudson).

### 6.7 Observatorio Volcanologico de los Andes del Sur (OVDAS) [VERIFIED]
- Sub-unidad de SERNAGEOMIN, cubierto en 1.11.

### 6.8 OAVV — Observatorio Argentino de Vigilancia Volcanica [VERIFIED]
- **URL:** https://oavv.segemar.gob.ar
- **Owner:** SEGEMAR Argentina.
- **Status:** Activo.
- **Que copiamos:** Cooperacion para volcanes binacionales (Lanin, Copahue, Lascar — bueno, este es chileno). Comunicacion bilateral.

### 6.9 IGP / OVS Peru [VERIFIED]
- **URL:** https://ovs.igp.gob.pe
- **Owner:** Instituto Geofisico del Peru.
- **Status:** Activo.
- **Que copiamos:** Misma latitud, mismos sensores; cooperacion natural para Andes Centrales.

### 6.10 INPE Brasil — TerraBrasilis / DETER [VERIFIED]
- **URL:** http://terrabrasilis.dpi.inpe.br
- **Que copiamos:** **Mejor referencia regional de dashboard NRT de detecion en Sudamerica**; arquitectura de alertas DETER.

### 6.11 MapBiomas Chile / Bosque Atlantico [VERIFIED]
- **URL:** https://chile.mapbiomas.org
- **GitHub:** https://github.com/mapbiomas
- **Status:** Activo.
- **Que copiamos:** Land-cover Chile 2000-2024 — mascaras de tipos de vegetacion para nuestras AOIs.

### 6.12 IDE Chile — Infraestructura de Datos Espaciales [VERIFIED]
- **URL:** https://www.ide.cl
- **Que copiamos:** Capas oficiales (limites, riesgos) para overlay en dashboard.

### 6.13 Proyecto Riesgos GFDRR-Banco Mundial Chile [CHECK]
- Productos derivados de eventos pasados (Calbuco 2015, Chaiten 2008). Verificar disponibilidad.

---

## TOP 10 Prioridad — Estudiar/Contactar Esta Semana

1. **MOUNTS (Sebastien Valade, TU Berlin)** — referencia mas directa; contactar para colaboracion academica. Email via TU Berlin EO group.
2. **leafmap + geemap (Qiusheng Wu)** — adoptar inmediatamente para el dashboard.
3. **stackstac + odc-stac + Planetary Computer** — refactor del pipeline a STAC moderno.
4. **HLS (Harmonized Landsat-Sentinel)** — cambio de fuente principal: 2-3 dias revisit vs 5 dias.
5. **BFASTmonitor (Wageningen)** — algoritmo de breakpoint para NRT detection.
6. **CR2MET (CR2 Chile)** — incorporar como control climatico (sequia) inmediatamente.
7. **SACS (BIRA-IASB)** — suscribir alertas SO2 para cross-validacion automatica.
8. **MIROVA + MODVOLC** — ya integrado/conocido; mantener cross-check operacional.
9. **Global Forest Watch** — clonar UX de alertas y AOIs.
10. **Prithvi-100M (IBM-NASA)** — fine-tuning para v2 con foundation model.

## Posibles Colaboradores Academicos (Chile/Andes-friendly)

- **Sebastien Valade (MOUNTS, TU Berlin)** — interes explicito en multi-sensor + ML, ya tiene volcanes andinos en su sistema.
- **Diego Coppola, Marco Laiolo (UniTo / MIROVA)** — ya scrapeamos sus datos; abrir dialogo formal mejor que scraping ciego.
- **Robert Wright (HIGP Hawaii / MODVOLC)** — pionero termico; receptivo.
- **CR2 Chile (Rene Garreaud, Maisa Rojas)** — clima/vegetacion Chile; data-sharing natural.
- **OVS Peru (IGP)** — vecino regional, mismos volcanes con misma latitud.
- **AVO (Universidad Alaska Fairbanks)** — experiencia en stratovolcanes glaciados, analogo Sur Chile.
- **CECs Valdivia** — para volcanes con casquetes glaciares.
- **MapBiomas Chile** — para land-cover masking.
- **Wageningen University (Verbesselt, BFAST)** — metodologia NRT.
- **Qiusheng Wu (UT Knoxville)** — open-source community lead, util para difusion.

## Notas Finales

- Los flags **[CHECK]** deben confirmarse navegando antes de enlazar oficialmente desde el dashboard.
- Recomiendo correr una pasada manual con `WebFetch` o navegacion de browser antes de citar URLs en publicaciones.
- Marcar como **DEAD** cualquier proyecto cuyo ultimo commit/post sea anterior a 2022 al verificarlo.
- Considerar abrir un `issue` en GitHub de MOUNTS preguntando por colaboracion oficial — bajo costo, alto valor.
