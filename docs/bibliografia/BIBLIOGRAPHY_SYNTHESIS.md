# BIBLIOGRAPHY_SYNTHESIS — VegStress-v1

> **Fuente de verdad bibliográfica del proyecto.** Inspirado en el modelo de VRP Chile:
> NO se resume cada paper — se extrae solo lo **accionable para el pipeline**
> (umbrales, fórmulas, coeficientes, bandas, lead-time, decisiones de algoritmo).
> La prosa/contexto va en las fichas individuales (`fichas/`), no acá.
>
> **Regla de oro**: cada número que entra al código (`change_detector.py`,
> `aoi_config.json`, `spatial_mapper.py`) debe tener su origen citado acá con DOI + página.

**Última actualización**: 2026-06-07 · **PDFs en** `pdfs/` (18, gitignored) · **Fichas en** `fichas/`

---

## 0. Cómo leer este documento

| Sección | Qué contiene |
|---|---|
| §1 | Núcleo: precursor volcánico vía vegetación (qué firma, qué lead-time) |
| §2 | Detección de cambios NDVI — algoritmos y cuál elegir |
| §3 | Umbrales CO2 → estrés de vegetación (cuándo es detectable por satélite) |
| §4 | Índices que detectan ANTES que NDVI (red-edge, SIF) — lead-time |
| §5 | Mejoras de pipeline (HLS, foundation models, multisensor) |
| §6 | **Tabla canónica de umbrales VegStress** (copy-paste al código) |
| §7 | Canonicidad de autores (autoridad vs confundible) |
| §8 | Glosario |

---

## 1. Núcleo — precursor volcánico vía vegetación

### Guinn et al. 2024 — Monitoring volcanic CO2 flux by remote sensing of vegetation, Mt. Etna ⭐ LEÍDO
- **PDF**: `Guinn_2024_Etna_CO2flux_vegetation.pdf` (SSRN preprint, 29 pp) · DOI `10.1016/j.rse.2024.114408` · ficha `PD-001`
- **Rol**: caso operacional MÁS cercano a VegStress. Correlaciona NDVI satelital con flujo de CO2 del suelo (5 estaciones EtnaGas, 2011-2018).
- **HALLAZGO QUE CAMBIA EL DISEÑO**: el CO2 volcánico difuso produce **GREENING** (fertilización
  → NDVI sube), NO browning. Correlación CO2↔NDVI **positiva**.
- **Método de detección**: **2ª derivada de la serie temporal de NDVI** → picos = eventos de
  recarga de magma (16 detectados 2017-2018). NO usan umbral absoluto de ΔNDVI.
- **Números citados** (líneas del preprint):
  - Inter-calibración multi-sensor: polinomio 2º orden, **r²=0.5** (L1124)
  - Filtro de calidad: **NDVI < 0.4 se descarta** (L882); solo 0% nubes, mejor-pixel/día
  - **Buffer 30 m** alrededor de falla/quebrada (CO2 se disemina en primeros 30 m) (L1012,1616)
  - Control de confusores: remover regresión lineal de lluvia/temp/humedad cuando **r²>0.1** (L1360)
- **Aplicabilidad**: (1) revisar signo de alerta en `change_detector.py` (greening, no browning);
  (2) migrar de ΔNDVI absoluto a 2ª derivada de serie; (3) buffer 30 m en AOIs.

### Farrar et al. 1995 — Forest-killing diffuse CO2, Mammoth Mountain
- **PDF**: ❌ paywall (Nature, `10.1038/376675a0`) → VPN SERNAGEOMIN
- **Rol**: seminal. Estableció que CO2 magmático difuso mata bosque → señal de unrest.
- **Extraer**: flujo de CO2 (g·m⁻²·d⁻¹) asociado a kill zones.

### Bogue et al. 2023 — Plant responses to volatile emissions detectable from space
- **PDF**: `Bogue_2023_PlantResponses_VolatileEmissions.pdf` (Chapman green-OA) · DOI `10.1029/2023GC010938`
- **Rol**: detección satelital de respuesta vegetal a desgasificación; tree-ring + RS.
- **Extraer**: qué bandas/índices, umbral de ΔCO2 local detectable.

---

## 2. Detección de cambios NDVI — estacional vs anomalía

> El problema científico #1 de VegStress (ver `seasonal_vs_volcanic.md`).
> Los 3 algoritmos canónicos están **paywall** (Elsevier RSE) → conseguir vía VPN.

| Algoritmo | Paper seminal | DOI | PDF | Qué aporta |
|---|---|---|---|---|
| **BFAST** | Verbesselt 2010 | 10.1016/j.rse.2009.08.014 | ❌ paywall | Descompone tendencia+estacional+ruido |
| **BFAST Monitor** | Verbesselt 2012 | 10.1016/j.rse.2012.02.022 | ❌ paywall | Detección near-real-time |
| **CCDC** | Zhu 2014 | 10.1016/j.rse.2014.01.011 | ❌ paywall | Modelo armónico, predice NDVI esperado |
| **LandTrendr** | Kennedy 2010 | 10.1016/j.rse.2010.07.008 | ❌ paywall | Segmentación temporal anual |
| Comparativa | Pasquarella 2022 | 10.1016/j.jag.2022.102806 | DOAJ (pendiente) | "Demystifying LandTrendr & CCDC" |

### Biass et al. 2022 — Vulnerabilidad de vegetación a tefra, Cordón Caulle ⭐
- **PDF**: `Biass_2022_CordonCaulle_Vegetation_Tephra_ML.pdf` · DOI `10.5194/nhess-22-2829-2022`
- **Rol**: el caso chileno/andino más cercano. ML + GEE + Sentinel sobre bosque templado HS.
- **Extraer** (fichar): features usadas, qué clasificador, métricas de daño de vegetación.

---

## 3. Umbrales CO2 → estrés de vegetación

### Viveiros & Silva 2024 — Hazardous volcanic CO2 diffuse degassing: systematic review ⭐
- **PDF**: `iScience_2024_VolcanicCO2_Degassing_Review.pdf` (Cell OA, 16 pp) · DOI `10.1016/j.isci.2024.110990`
- **Rol**: síntesis ancla. Revisión de áreas de desgasificación difusa y sus impactos en vegetación.
- **Extraer** (fichar): concentraciones letales indoor/outdoor, sitios de estudio, flujos típicos.

### Cawse-Nicholson et al. 2018 — Airborne RS de ecosistema bajo CO2 elevado
- **PDF**: `CawseNicholson_2018_AirborneRS_CO2.pdf` · DOI `10.5194/bg-15-7403-2018`
- **Rol**: precedente publicado más cercano al concepto AVUELO (espectroscopía de respuesta a CO2).

### USGS 1996 — Mammoth Mountain CO2 tree-kill (fact sheet)
- **PDF**: `USGS_1996_Mammoth_CO2_TreeKill.pdf` · `10.3133/fs17296_1996`
- **Rol**: documento público base del caso Mammoth.

---

## 4. Índices que detectan ANTES que NDVI (lead-time)

### Eitel et al. 2010 — Red-edge detecta estrés antes que NDVI
- **PDF**: `Eitel_2010_rededge_drought.pdf` · DOI `10.1093/jxb/erq201`
- **Extraer** (fichar): cuánto lead-time, qué índice red-edge (NDRE/CIred-edge), magnitud de la señal.

### Köhler/Magney et al. 2018 — SIF global con TROPOMI
- **PDF**: ⏳ pendiente (lector Wiley no soltó limpio) · DOI `10.1029/2018GL079031`
- **Rol**: base de SIF satelital.

### SIF vs NDVI 2024 — comparación
- **PDF**: `SIF_NDVI_2024_comparison.pdf` · DOI `10.3390/rs16101735`

> **Hipótesis central VegStress** (validar): SIF y red-edge preceden a NDVI en detectar
> estrés. Papers TGRS 2025 (`10.1109/TGRS.2025.3561216`) y GRL 2025
> (`10.1029/2025GL119408`) lo afirman directamente — **conseguir vía IEEE/AGU** (paywall).

---

## 5. Mejoras de pipeline

| Vía | Paper | DOI | PDF | Para qué |
|---|---|---|---|---|
| **MOUNTS** (sistema ref. #1) ⭐ | Valade 2019 | 10.3390/rs11131528 | `Valade_2019_MOUNTS_monitoring_system.pdf` | Multisensor Sentinel + IA; candidato colaboración |
| **Foundation model** | Jakubik 2023 (Prithvi) | 10.48550/arXiv.2310.18660 | `Jakubik_2023_Prithvi_geospatial_FM.pdf` | Path a v2 con DL sobre HLS |
| **MIROVA térmico** | Coppola 2020 | 10.3389/feart.2019.00362 | `Coppola_2020_MIROVA_thermal_volcano.pdf` | Fusión térmico+vegetal |
| **SO2 TROPOMI** | Theys 2019 | 10.1038/s41598-019-39279-y | `Theys_2019_TROPOMI_SO2_degassing.pdf` | Cross-validación desgasificación |
| **Control sequía** | Alvarez-Garreton 2018 (CAMELS-CL) | 10.5194/hess-22-5817-2018 | `AlvarezGarreton_2018_CAMELS_CL.pdf` | Descartar confusor climático |
| **HLS** | Claverie 2018 | 10.1016/j.rse.2018.09.002 | ❌ paywall (probar HAL) | Duplica densidad temporal |

---

## 6. Tabla canónica de umbrales VegStress (copy-paste al código)

> **Estado: PROVISIONAL.** Estos umbrales se fijaron por criterio inicial, NO citados de
> paper aún. Tarea: validar/reemplazar cada uno con su DOI tras fichar §1-§4.

| Parámetro | Valor actual | Origen | Estado |
|---|---|---|---|
| Alerta WATCH (ΔNDVI) | > 0.10 | criterio propio | `[VERIFICAR: sin cita]` |
| Alerta WARNING (ΔNDVI) | > 0.15 | criterio propio | `[VERIFICAR: sin cita]` |
| Alerta CRITICAL (ΔNDVI) | > 0.25 | criterio propio | `[VERIFICAR: sin cita]` |
| NDVI bandas S2 | B08 (NIR) − B04 (Red) / suma | estándar | OK (definición) |
| Resolución espacial | 10 m/px | Sentinel-2 L2A | OK |
| Máscara nubes/nieve | SCL clases (DN) | S2 L2A ATBD | OK |
| **NDVI mínimo válido** | **> 0.4** | Guinn 2024 L882 (10.1016/j.rse.2024.114408) | ✅ citado |
| **Buffer desgasificación** | **30 m** alrededor de quebrada/falla | Guinn 2024 L1012/1616 | ✅ citado |
| **Detección** | **2ª derivada de serie NDVI** (no ΔNDVI absoluto) | Guinn 2024 L125 | ✅ citado |
| **Signo de señal CO2** | **GREENING** (NDVI↑), no browning | Guinn 2024 L121 | ✅ citado |
| **Control confusores** | regresión lineal clima si r²>0.1 | Guinn 2024 L1360 | ✅ citado |

**Conflicto detectado**: los umbrales WATCH/WARNING/CRITICAL actuales asumen **browning**
(ΔNDVI positivo = pérdida) y umbral absoluto. Guinn 2024 muestra que la señal de CO2 es
**greening** y se detecta por 2ª derivada de la serie. → Ver `GAPS.md` 🔴. Falta leer
Biass 2022 (caso Chile/tefra) para el otro mecanismo (daño por tefra = browning real).

---

## 7. Canonicidad de autores (autoridad vs confundible)

> Lección de VRP Chile (AP2): no todos los papers del mismo tema son la misma escuela.
> Antes de citar como **autoridad metodológica**, verificar afiliación en footer.

| Dominio | Autoridad (citar) | Confundible / contexto (NO como autoridad) |
|---|---|---|
| CO2-vegetación volcánico | Farrar, Bogue, Guinn, Lewicki, Cawse-Nicholson, Viveiros | Papers de CO2 agrícola/FACE genérico (otro mecanismo) |
| Detección cambios NDVI | Verbesselt (BFAST), Zhu (CCDC), Kennedy (LandTrendr) | Métodos CVA simples sin validación fenológica |
| Caso chileno/andino | Biass, Zamorano, SERNAGEOMIN/OVDAS | Estudios de bosque boreal/tropical (otro bioma) |
| Sistema operacional | Valade (MOUNTS), Coppola (MIROVA) | — |

---

## 8. Glosario

- **NDVI**: (NIR−Red)/(NIR+Red). Vigor de vegetación. S2: (B08−B04)/(B08+B04).
- **ΔNDVI**: diferencia pixel-a-pixel entre dos fechas. Base de la detección de cambios.
- **SIF**: Solar-Induced Fluorescence. Proxy de fotosíntesis; precede a NDVI en estrés.
- **Red-edge / NDRE**: índices en el borde rojo (700-740nm). Sensibles a clorofila temprano.
- **AOI**: Area of Interest. Zona circular de desgasificación definida en `aoi_config.json`.
- **HLS**: Harmonized Landsat-Sentinel. Producto fusionado, mayor densidad temporal.
- **Kill zone**: área de mortandad de vegetación por CO2 difuso (tipo Mammoth Mountain).
