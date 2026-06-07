# Ficha: PD-001

**Archivo PDF**: `pdfs/Guinn_2024_Etna_CO2flux_vegetation.pdf` (29 pp, SSRN preprint)
**Título**: Monitoring Volcanic CO2 Flux by the Remote Sensing of Vegetation on Mt. Etna, Italy
**Autores**: Nicole K. Guinn, Craig Glennie, Marco Liuzzo, Giovanni Giuffrida, Sergio Gurrieri
**Afiliación 1er autor**: National Center for Airborne Laser Mapping (NCALM), Univ. Houston, Texas
(co-autores INGV Catania/Palermo + Univ. Ferrara — verificado en p.1)
**Año**: 2024 · **Revista**: Remote Sensing of Environment · **DOI**: 10.1016/j.rse.2024.114408
**OA**: preprint libre SSRN (4762417); versión final RSE = paywall
**Leído**: ✅ (vía markitdown `md/Guinn_2024_Etna.md`, 2026-06-07)

## Metodología
Compara **NDVI de 4 sensores** (Landsat 8, MODIS, Sentinel-2, VIIRS) contra **flujo de CO2
del suelo** medido en **5 estaciones EtnaGas** terrestres, 2011-2018, en Mt. Etna. NDVI
inter-calibrado entre sensores con **polinomio de 2º orden (r²=0.5)**. Serie llevada a
resolución diaria por interpolación lineal. Técnica núcleo: **2ª derivada de la serie NDVI**
para detectar "eventos de recarga de magma" (picos en la tasa de cambio).

## Hallazgos clave (para el pipeline)
- **CO2 volcánico difuso → GREENING (no browning).** El CO2 fertiliza la vegetación y
  *mejora* la salud → NDVI sube. Correlación CO2↔NDVI **positiva** (abstract, líneas 121-127).
- **Detección por 2ª derivada de NDVI**, NO por umbral absoluto de ΔNDVI. Los picos de la
  2ª derivada marcaron **16 eventos de recarga de magma** coincidentes en NDVI y CO2 del
  suelo (2017-2018) (línea 125).
- **Buffer espacial de 30 m** alrededor de la falla/estructura: el CO2 difuso se disemina en
  los primeros 30 m de su fuente (líneas 1012, 1616).
- **Filtros de calidad**: NDVI < 0.4 se descarta; solo imágenes con 0% nubes; mejor-pixel/día.
- **Control de confusores**: se removió por regresión lineal la influencia de lluvia/
  temperatura/humedad cuando r² > 0.1 (línea 1360). Estaciones no impactadas: r² máx 0.03.
- Los árboles **no necesitan estar sobre la estructura** volcano-tectónica para mostrar la
  señal (análisis de flancos con árboles homogéneos dio el mismo patrón).

## Citas útiles (con línea del preprint)
- "volcanic CO2 diffusely degases during magma ascent, and the volatiles interact with the
  ecosystem on the surface through CO2 fertilization, which can improve vegetation health" (L121)
- "2nd derivative spikes showed 16 magma recharge events in both NDVI and soil CO2 signals" (L125)
- "Any NDVI values under 0.4 were removed from all datasets" (L882)

## Relevancia para VegStress
**Es el paper que redefine el enfoque correcto.** Tres implicancias mayores:
1. **El supuesto de "browning = alerta" está probablemente invertido para CO2.** El CO2
   difuso produce GREENING por fertilización. → La alerta WARNING de Borde Norte (browning
   +0.157) puede NO ser señal de CO2; y el greening del Sector Sur (que reportaste con
   actividad de CO2) **SÍ es consistente** con este mecanismo.
2. **El detector correcto es la 2ª derivada de la serie temporal NDVI**, no un umbral
   absoluto de ΔNDVI entre dos fechas. Captura el *timing* de ciclos de recarga.
3. **Buffer de 30 m** alrededor de quebradas/fallas de desgasificación → afinar `aoi_config.json`.

## Dónde aplica (mapeo a código/doc)
- `change_detector.py` — **revisar la lógica de signo de alerta** (greening vs browning) y
  considerar pasar de ΔNDVI absoluto a 2ª derivada de serie.
- `seasonal_vs_volcanic.md` — su control de confusores (regresión r²>0.1) es una estrategia concreta.
- `aoi_config.json` — `radio_m` de las AOIs: contrastar con el buffer de 30 m.
- `BIBLIOGRAPHY_SYNTHESIS.md §1, §6`.

## Flags
Afiliación verificada. Hallazgos con cita de línea del preprint. Nota: es preprint
no peer-reviewed — la versión RSE final (10.1016/j.rse.2024.114408) puede diferir en números.
