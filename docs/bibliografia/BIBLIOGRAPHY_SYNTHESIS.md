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

> 🔑 **HALLAZGO QUE RESUELVE LA "CONTRADICCIÓN" greening vs browning:**
> el efecto del CO2 sobre la vegetación es **NO MONOTÓNICO — depende del FLUJO**:
> - **CO2 bajo/moderado → GREENING** (fertilización; Guinn 2024, desgasificación difusa de Etna).
> - **CO2 alto → BROWNING/kill zone** (asfixia radicular; Cawse-Nicholson 2018, USGS Mammoth).
>
> ⇒ VegStress debe detectar **ambos signos** y usar el flujo/contexto (térmico, SO2) para
> distinguir fertilización de asfixia. El signo solo NO basta: hay que ver la magnitud y la zona.

### Viveiros & Silva 2024 — Hazardous volcanic CO2 diffuse degassing: systematic review ⭐ LEÍDO
- **PDF**: `iScience_2024_VolcanicCO2_Degassing_Review.pdf` (Cell OA) · DOI `10.1016/j.isci.2024.110990` · ficha `PD-003`
- **Umbrales de CO2 en suelo → vegetación** (atribuir a estudios primarios al citar):
  - Línea base **biogénica (no volcánica): ≤ 50 000 ppm y ≤ 50 g·m⁻²·d⁻¹**.
  - **180 000–200 000 ppm** → plantas dispersas; **350 000–400 000 ppm** → casi ausente; **>500 000 ppm** → suelo desnudo.
  - Flujos extremos: Mammoth ~**31 000 g·m⁻²·d⁻¹** (900 000 ppm); Cumbre Vieja máx **449 500 g·m⁻²·d⁻¹**.
  - Letal humanos: **>100 000 ppm (10 %)**; muerte súbita **>200 000 ppm**.
  - Confusor meteo cuantificado: presión barométrica varía el flujo de suelo **hasta 3 órdenes de magnitud**.

### Cawse-Nicholson et al. 2018 — Airborne RS de ecosistema bajo CO2 elevado ⭐ LEÍDO
- **PDF**: `CawseNicholson_2018_AirborneRS_CO2.pdf` · DOI `10.5194/bg-15-7403-2018` · ficha `PD-006`
- **NDVI cae con CO2 alto**: **0.27 @ 200 g·m⁻²·d⁻¹ → 0.10 @ 800 g·m⁻²·d⁻¹** (régimen de asfixia, browning).
- Soil CO2 flux predice NDVI, N foliar, ET, biomasa. Con CO2↑: ↓ET, ↑N foliar, ↓NDVI, ↓biomasa.
- Sensores: AVIRIS 13 m, MASTER 50 m (NO Sentinel-2 → magnitudes absolutas no transferibles directo).

### USGS 1996 — Mammoth Mountain CO2 tree-kill (fact sheet) LEÍDO
- **PDF**: `USGS_1996_Mammoth_CO2_TreeKill.pdf` · `10.3133/fs17296_1996` · ficha `PD-011` (V2-style)
- CO2 en suelo tree-kill: **20–95 % (200 000–950 000 ppm)** vs **≤1 %** normal. Mecanismo: **asfixia
  radicular + bloqueo de nutrientes** (no daño foliar directo) → explica el RETARDO de la señal NDVI.
- Área >100 acres (~40 ha); inicio **1990 tras enjambre sísmico 1989** (retardo ~1 año); ~1 300 t/día.

---

## 4. Índices que detectan ANTES que NDVI (lead-time)

### SIF vs NDVI 2024 — comparación ⭐ LEÍDO — VALIDA LA HIPÓTESIS CENTRAL
- **PDF**: `SIF_NDVI_2024_comparison.pdf` · DOI `10.3390/rs16101735` · ficha `PD-018`
- **LEAD-TIME SIF → NDVI ≈ 1 mes**: en la sequía 2009-2010 la anomalía SIF cayó en **enero 2010**,
  NDVI/kNDVI recién en **febrero 2010**.
- SIF–GPP **lag 0, R²=0.92**; NDVI/kNDVI alcanzan máximo a **lag 1 mes** (R²~0.80).
- **Caveat**: ventaja NO universal (en sitio seco DHS, SIF peor que NDVI). **GOSIF = 0.05° (~5 km)
  → demasiado grueso para AOIs volcánicas.** SIF satelital fino aún no disponible para nuestro caso.

### Eitel — Red-edge antes que NDVI ⚠️ PDF EQUIVOCADO (re-descargar)
- **PDF descargado NO es Eitel red-edge**: el DOI `10.1093/jxb/erq201` resuelve a un review de
  fenotipado (Berger, Parent & Tester 2010), no al paper red-edge. → **NO hay evidencia
  cuantificada de lead-time red-edge todavía** (ver GAPS.md).
- Paper correcto a conseguir: **Eitel, Gessler, Smith & Robberecht 2006**, *Forest Ecol. Manag.*
  229:170-182.

### Köhler/Magney et al. 2018 — SIF global con TROPOMI
- **PDF**: ⏳ pendiente (lector Wiley no soltó limpio) · DOI `10.1029/2018GL079031`

> **Estado de la hipótesis central** (SIF/red-edge preceden a NDVI):
> **SIF VALIDADO (~1 mes de lead-time)** pero sin sensor fino operativo. **Red-edge AÚN SIN
> VALIDAR** por error de descarga. Papers TGRS 2025 (`10.1109/TGRS.2025.3561216`) y
> GRL 2025 (`10.1029/2025GL119408`) lo afirman directamente — **conseguir vía IEEE/AGU**.

---

## 5. Mejoras de pipeline (LEÍDOS — números citados)

### MOUNTS — Valade 2019 ⭐ (sistema ref. #1, candidato colaboración) · ficha PD-004
- Fusiona 4 fuentes: **S1 SAR banda C (deformación, 14×14 m) + S2 SWIR (térmico B12-B11-B8A, 20 m)
  + S5P TROPOMI (SO2) + sismicidad GEOFON/USGS**. IA: **CNN auto-encoder tipo ResNet**. AOI estándar
  **10×10 km**; latencia NRT <1-6 h.
- **GAP CLAVE: MOUNTS NO incluye vegetación** (la trata como ruido de decorrelación InSAR).
  → Esta es la justificación-ancla de VegStress: el **5º canal vegetal** sobre una arquitectura MOUNTS.

### MIROVA — Coppola 2020 (térmico, lo usa SERNAGEOMIN) · ficha PD-009
- **VRP = 18.9 · A_pixel · Σ(L_MIR,alert − L_MIR,bk)**; MODIS MIR 3.959 µm + TIR 12.02 µm, píxel 1 km.
- Piso de detección **alto: solo T>500 K**, rango 1 MW–50 GW, error ±30% → **invisible a
  desgasificación difusa fría que SÍ afecta vegetación** ⇒ complementariedad.
- **Solo 6-8 % de erupciones VEI≥3 tienen precursor térmico detectable** → justifica sumar canal vegetal.

### TROPOMI SO2 — Theys 2019 (co-validador atmosférico) · ficha PD-010
- Resolución **7×3.5 km**, límite de emisión 4× mejor que OMI, **revisita 1 día**, NRT <3 h.
- **Cross-validación**: anomalía NDVI + SO2 coincidente en tiempo/lugar → confirma origen volcánico.
  **Caveat Chile**: la huella 7×3.5 km valida la *fuente regional*, no el píxel AOI; <100 t/día cae bajo el límite.

### Prithvi FM — Jakubik 2023 (roadmap v2 DL) · ficha PD-008
- Preentrenado en **>1 TB HLS, 30 m, 6 bandas** (rojo/NIR/SWIR → compatibles con NDVI). **100M params**.
- **~90 % menos etiquetas** para converger (IoU>80%); fine-tuning **>2× más rápido**. Tareas demostradas:
  inundación/incendio/cultivo (volcánico = extrapolación). 30 m adecuado para AOIs.

### CAMELS-CL — Alvarez-Garreton 2018 (control climático) · ficha PD-012
- 516 cuencas, **17.8°S–55.0°S**, diario **1979-2016**. Variables para `regress_out_climate()`:
  `precip_cr2met`, `pet`, `swe`, `aridity_i`, **`p_seasonality_i`** (confusor estacional),
  `low_prec_freq/dur_i`, `frac_snow_i`. Unidad = cuenca → asignar cada AOI a su cuenca.
  **[VERIFICAR]** vigencia CR2MET post-2016 (¿v2.x?).

### HLS — Claverie 2018 ❌ paywall (probar HAL) · DOI 10.1016/j.rse.2018.09.002 — duplica densidad temporal

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
| **NDVI esperado bosque sano** | **0.41–0.62** (Araucaria-Nothofagus) | Ojeda 2011 (10.4067/s0717-92002011000200002) | ✅ citado |
| **Umbral ceniza detectable** | **~3 cm** (mín. para perturbar NDVI) | De Schutter 2015 (10.1186/s13617-015-0032-z) | ✅ citado |
| **Recuperación post-ceniza** | <1 año si <3 cm; años si >8-10 cm | De Schutter 2015 | ✅ citado |
| **Daño tefra (browning)** | DS1-5 por espesor mm (Jenkins 2015) | Biass 2022 (10.5194/nhess-22-2829-2022) | ✅ citado |
| **CO2→greening (fertiliz.)** | flujo bajo/moderato | Guinn 2024 | ✅ citado |
| **CO2→browning (asfixia)** | NDVI 0.27→0.10 @ 200→800 g·m⁻²·d⁻¹ | Cawse-Nicholson 2018 (10.5194/bg-15-7403-2018) | ✅ citado |
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
