# GAPS — evidencia que falta (VegStress-v1)

> Lista viva de información que el proyecto NECESITA pero NO tiene aún (modelo Educación
> y riesgos). Evita que el código/paper avance sobre cimientos inestables. Actualizar
> al descubrir un hueco. Cada gap: qué falta + cómo se resuelve.

## 🔴 Prioridad ALTA (bloquean decisiones de diseño)

- **🐛 BUG DE SIGNO GREENING/BROWNING — RESUELTO 2026-06-07.** El path ΔNDVI
  (`vegstress_signal.classify_change`/`pct_matching_sign` + `change_detector.compute_delta`/
  colormap) tenía el convenio **invertido**: marcaba ΔNDVI<0 (NDVI que BAJA) como GREENING.
  Verificado contra datos crudos: Q9 NDVI ene=0.81 → abr=0.56 (senescencia) se reportaba
  "GREENING CRITICAL". El path z-score (`ndvi_analyzer.py:406`, `dashboard_generator.py:61`,
  `z<0 → BROWNING`) ya era correcto → los dos subsistemas se contradecían. **Fix**: ΔNDVI>0
  = GREENING (ganancia de vigor), <0 = BROWNING. Tests de regresión añadidos. Impacto: el bug
  invertía el mecanismo de CADA alerta (CO2/fertilización vs tefra/ácido), el corazón de Guinn.

- **🚨 LAS AOIs DE LAGUNA DEL MAULE NO TIENEN VEGETACIÓN (descubierto 2026-06-07).**
  Al aplicar el filtro NDVI≥0.4 de Guinn 2024, las 4 AOIs dan **veg = 0-3%**: están sobre
  roca/nieve de caldera a ~2200 m, no sobre vegetación. → La alerta WARNING previa de Borde
  Norte (+0.157 browning) era **FALSO POSITIVO**: cambio estacional de nieve/roca verano→otoño.
  **Acción**: reubicar las AOIs a terreno con vegetación real (cotas más bajas, donde haya
  Nothofagus/matorral), usando el mapa NDVI espacial para elegir. **Target citado**: bosque
  Araucaria-Nothofagus sano tiene **NDVI ≈ 0.41-0.62** (Ojeda 2011, PD-016) → buscar AOIs en ese
  rango. O evaluar si Laguna del Maule es viable para monitoreo vegetal (puede estar sobre
  treeline). Requiere conocimiento de campo de Nicolás + inspección del mapa espacial.
  - **ACTUALIZACIÓN 2026-06-07 (aoi_finder.py):** solo **1.1% de la escena** es vegetación
    estable. Los 5 parches grandes (NDVI 0.62-0.67, 8-18 ha) están en los **bordes/valles
    bajos**, LEJOS del centro de caldera. Las zonas de desgasificación (Sector Sur, etc.)
    están sobre roca pelada → **no monitoreables por vegetación directamente**. PERO hay
    **vegetación riparia en hilos a lo largo de las quebradas** = justo donde Guinn dice que
    el gas se concentra (30 m de la falla). **Decisión de diseño pendiente con Nicolás**:
    (a) monitorear vegetación riparia de quebradas próximas a la caldera, o (b) usar los
    parches de borde como control y aceptar que LdM no es ideal para señal vegetal directa.
    Candidatas en `datos/Laguna_del_Maule/aoi_candidatas.json` + mapa
    `docs/maps/Laguna_del_Maule_aoi_candidatas.png`.
  - **✅ DECISIÓN DE CAMPO (Nicolás, 2026-06-07): las emisiones de CO2 se concentran en las
    QUEBRADAS.** ⇒ Próxima sesión: crear AOIs sobre la **vegetación riparia de las quebradas**
    (no parches de borde). Coincide con Guinn 2024 (gas en 30 m de la estructura). TAREA:
    (1) identificar las quebradas con desgasificación conocida (coords de Nicolás o trazas de
    drenaje del DEM); (2) definir AOIs lineales/estrechas siguiendo la quebrada, no círculos
    grandes; (3) extraer la vegetación riparia (hilos verdes NDVI≥0.4 visibles en el mapa
    `_aoi_candidatas.png` a lo largo de los drenajes); (4) re-correr change_detector sobre
    esas AOIs. El detector ya filtra NDVI<0.4 y reporta pct_coincide_esperado para señal localizada.
  - **✅ IMPLEMENTADO 2026-06-07.** `riparian_finder.py` extrae los hilos verdes lineales
    (NDVI 0.41-0.95 estable, ancho≤80 m, largo≥150 m) y traza su centerline como waypoints.
    15 quebradas candidatas (Q1-Q15) volcadas a `aoi_config.json` como AOIs **tipo línea**
    (motor nuevo `aoi_geometry.py`: polilínea + buffer 30 m = Guinn). Las 4 AOIs circulares
    viejas se desactivaron (eran roca/nieve). Ahora las 15 quebradas SÍ tienen vegetación.
    **HALLAZGO:** comparación misma-estación verano 2025 vs 2026 → **Q8 (+0.118) y Q9 (+0.110)
    = GREENING WATCH rel=ALTA**, y son los 2 hilos más cercanos al sector de desgasificación
    sur. El control otoño-vs-otoño los muestra estables → el greening no es artefacto. Es el
    precursor de fertilización por CO2 (Guinn).
  - **🔬 ANÁLISIS 2026-06-07 (3 agentes paralelos) — el greening es MAYORMENTE CLIMÁTICO:**
    1. **Clima (Open-Meteo, precip antecedente 48d De Schutter):** el verano 2025-26 fue
       marcadamente más lluvioso (precip antec. ~28-48 mm vs ~1-8 mm en 2024-25). El greening
       es generalizado en la cuenca (12/15 quebradas suben NDVI), no exclusivo del sur. **Q8 es
       la ÚNICA quebrada donde el clima explica <10% de la varianza (r²=0.047, NO removido) →
       señal robusta al modelo lineal.** Las otras 14 tienen r²>0.13 (clima-dominadas). **Q9
       (r²=0.176) sí se explica por más lluvia → confusor, no robusto.**
    2. **Localización espacial (analisis_localizacion_q8q9.py):** el greening de Q8/Q9 está
       repartido DIFUSO a lo largo de toda la quebrada (61%/55% de píxeles enverdecen,
       fragmentado en 11-18 parches chicos), NO un hotspot compacto <30 m como predice Guinn
       para gas localizado. Hay gradiente sur→norte en intensidad (Q8/Q9 ~+0.11 → Q6 +0.088 →
       Q3 +0.053), débilmente compatible con aporte volcánico difuso sobre el fondo climático.
    3. **Wiring clima→detector:** implementado y testeado (control climático en analyze_timeseries,
       nota de confusor en alertas, flag --sin-clima). Verificado end-to-end.
    **VEREDICTO:** la señal de greening NO es un precursor confirmado; domina el clima. **Q8 es
    el único candidato residual** (clima-robusto, más al sur) pero su patrón difuso debilita la
    interpretación CO2. **PENDIENTE:** (a) confirmar con Nicolás que Q8/Q9 corresponden
    geográficamente a quebradas de desgasificación conocida (el 1er waypoint de Q9 está al
    OESTE, lon -70.582, no al sur); (b) datos de flujo CO2 de campo en el centroide de Q8;
    (c) más fechas inter-anuales de verano (BLOQUEADO: credenciales CDSE vacías en .env).
  - **🧊 RESULTADO DEFINITIVO 2026-06-13 (serie de 6 febreros, misma estación) — NO HAY
    PRECURSOR DE GREENING EN Q8.** Con credenciales CDSE se bajaron los febreros 2021-2024 +
    2026-02-16 (+ el 2025-02-18 ya existente) = serie inter-anual mismo-mes 2021-2026
    (analisis_interanual_febrero.py, figura docs/maps/Q8_interanual_febrero.png). NDVI de Q8 por
    año: 0.627, 0.608, 0.619, 0.632, 0.574, 0.577 → **pendiente -0.010/año (plano/leve declive),
    r²(año)=0.53, r²(NDVI~precip)=0.06.** Q8 NO enverdece; si acaso declina levemente y está
    DESACOPLADA de las oscilaciones climáticas regionales que sí mueven juntas a Q9 y los controles
    Q3/Q6. **El "greening +0.118" reportado antes era un ARTEFACTO FENOLÓGICO**: comparaba
    2025-02-18 (mediados de feb, NDVI 0.574) contra 2026-01-11 (mediados de ene, NDVI 0.663), y el
    NDVI cae naturalmente de enero a febrero al avanzar el verano. Comparando feb-vs-feb (0.574 →
    0.577) Q8 está plano. **Conclusión: sin evidencia de fertilización por CO2 en la vegetación
    riparia de LdM con los datos actuales.** Refuerza por qué la comparación DEBE ser mismo-mes
    (lección ya cableada al default del detector). Q9 muestra una tendencia +0.017/año pero ruidosa
    (r²=0.32) e indistinguible del control Q3 (+0.014/año) → ruido climático, no señal.

- **✅ RESUELTO (conflicto greening/browning):** tras fichar PD-003/PD-006/PD-011, el efecto del
  CO2 resultó **NO monotónico — depende del flujo**: bajo/moderado → GREENING (fertilización,
  Guinn); alto → BROWNING/kill zone (asfixia, Cawse-Nicholson NDVI 0.27→0.10 @ 200→800 g·m⁻²·d⁻¹;
  Mammoth 200 000-950 000 ppm). El detector ya distingue ambos signos (implementado). Pendiente:
  usar magnitud + contexto térmico/SO2 para separar fertilización de asfixia.
- **Eitel red-edge: PDF EQUIVOCADO + DOI corregido (2026-06-13).** `Eitel_2010_rededge_drought.pdf`
  es en realidad Berger/Parent/Tester 2010 (DOI 10.1093/jxb/erq201 = review de fenotipado).
  → **El lead-time de red-edge vs NDVI sigue SIN evidencia cuantificada.** El paper correcto es
  **Eitel, Gessler, Smith & Robberecht 2006** — DOI REAL confirmado vía Crossref:
  **`10.1016/j.foreco.2006.03.027`**, *Forest Ecol. Manag.* 229:170-182, julio 2006. **OJO**: el
  título es *"...water stress in **Populus spp.**"* (NO "Pinus" como decía el pedido). **NO es OA**
  (Unpaywall is_oa=False, OpenAlex closed, sin repositorio) → **paywall Elsevier, conseguir vía VPN
  SERNAGEOMIN o biblioteca**. Ficha: `fichas/PEND-05_Eitel_2006_rededge_waterstress.md` [PENDIENTE
  DE LECTURA].
- **Umbrales ΔNDVI sin cita.** WATCH/WARNING/CRITICAL (0.10/0.15/0.25) siguen sin respaldo.
  Guinn no usa umbrales absolutos (usa 2ª derivada). → Decidir: ¿migramos a 2ª derivada o
  mantenemos umbral pero citado? Pendiente leer más casos (iScience PD-003, papers SIF 2025).
- **✅ PARCIALMENTE RESUELTO — control climático implementado (2026-06-07).** `climate_control.py`
  remueve el confusor por regresión lineal NDVI~clima cuando r²>0.1 (Guinn) usando precipitación
  antecedente de 48 días (De Schutter PD-014) vía Open-Meteo (gratis). Probado en Sector Sur:
  el clima explicaba **34% de la varianza NDVI** → removido. **Pendiente**: (a) upgrade a CR2MET
  (autoritativo Chile, PD-012) — interfaz lista en `fetch_climate_cr2met()`; (b) cablear el NDVI
  corregido al detector de alertas.
  - **✅ (c) RESUELTO 2026-06-07 — comparación inter-anual misma-estación.** El default de
    `change_detector` ahora elige la misma estación del año anterior (~365 d, ±45 d) en vez de
    ~90 d antes. Esto anula la senescencia estacional (que generaba falsos CRITICAL: el cambio
    verano→otoño es fenología, no volcán). Para LdM el default pasó a otoño-25 vs otoño-26.
- **Seminales de change-detection en paywall** (BFAST Verbesselt 2010/2012, CCDC Zhu 2014,
  LandTrendr Kennedy 2010). → Resolver: VPN SERNAGEOMIN o biblioteca.

## 🎯 ANCLAJE DE CAMPO — área de desgasificación real (2026-06-13)

- **Nicolás aportó el polígono del área de desgasificación PRINCIPAL** (area.kmz →
  `datos/area_desgasificacion.json`): centro **−36.089, −70.549**, ~2.12 km², orilla
  centro-oeste del lago. Esto da por fin el anclaje de campo que faltaba.
  - **Rechaza los candidatos data-driven previos:** los clústeres "robustos" que había
    marcado (SO −36.127/−70.58 y NE −36.00/−70.40) **NO caen en el área de gas** → eran
    ruido estadístico, no señal. (Valor de la verdad de campo.)
  - **Dentro del área de gas la vegetación es ESCASA:** solo **4.25 ha vegetadas (2% del
    polígono)**, en 8 componentes chicos (0.19-1.02 ha) sobre un drenaje del borde SO.
  - **NINGÚN componente muestra tendencia sostenida:** todos r²≤0.20 (febreros 2021-2026);
    sus series siguen casi exactas la mediana climática de la cuenca (0.67,0.54,0.57,0.67,
    0.62,0.59) → solo clima, sin residuo volcánico. **No hay firma espectral NDVI de la
    desgasificación detectable con Sentinel-2 a esta resolución/sensibilidad.**
  - **Lectura:** o (a) NDVI no es suficientemente sensible al CO2 difuso aquí (→ probar SIF
    /red-edge, que preceden y son más sensibles), o (b) la vegetación es rala por el ambiente
    de altura/gas y lo que queda no responde de forma detectable. Es un **resultado negativo
    sólido y publicable** (el gap de literatura: respuesta espectral de Nothofagus/Araucaria
    a desgasificación difusa, no documentada).
  - **AOIs de monitoreo ahora ancladas al gas:** 8 AOIs `gas_quebrada_*`/`gas_parche_*`
    (área_desgasificacion.py) reemplazan a las Q1-Q15 especulativas (desactivadas). Mapa zoom:
    `docs/maps/Laguna_del_Maule_area_gas.png`. Datos: `datos/Laguna_del_Maule/aois_area_gas.json`.
  - **PENDIENTE de campo:** ¿hay OTRAS quebradas de desgasificación además de esta área
    principal? ¿conviene bajar SIF (TROPOMI/OCO-3) para esta zona?
  - **🔴 RED-EDGE (NDRE) TAMBIÉN NEGATIVO 2026-06-13.** `rededge_gas.py` bajó B05 (705 nm) y
    computó NDRE=(B08−B05)/(B08+B05) a 10 m sobre el área de gas, 6 febreros 2021-2026. NDRE de
    la vegetación del área sigue EN LOCKSTEP al NDVI y al fondo climático del tile (baja 2022,
    sube 2024, baja 2026). Pendiente residual NDRE +0.0042/año (r²=0.06) ≈ NDVI +0.0033 (r²=0.02):
    ninguna tendencia robusta. **El red-edge, más sensible al estrés temprano (Eitel 2006), tampoco
    capta firma de desgasificación.** ⇒ No es saturación de NDVI: simplemente NO hay señal vegetal
    detectable con S2 (NDVI ni red-edge) en esta zona. Próxima palanca real = SIF fino (no NDVI/NDRE)
    o validación de flujo CO2 de campo. Figura: `docs/maps/Laguna_del_Maule_rededge_gas.png`.

## 🟢 Cobertura comprehensiva de vegetación (2026-06-13)

- **Escaneo de red ancha + tendencia plurianual de TODA la vegetación** (no solo 15 hilos).
  `vegetation_scan.py` (par inter-anual mismo-mes, clima descontado espacialmente vía mediana
  de cuenca) y `vegetation_trends.py` (tendencia de 6 febreros 2021-2026 por componente, clima
  de cuenca restado año a año). Criterio veg: NDVI 0.41-0.95 en ≥70% de fechas (incluye
  caducifolias; ~1.38% de la escena, 250 componentes ≥0.3 ha).
  - **Tendencia de cuenca (clima): plana (-0.0017 NDVI/año)** → no hay deriva regional grande.
  - **18 de 250 componentes "robustos"** (|pend. residual|≥0.010 NDVI/año Y r²≥0.6): 10 greening,
    8 browning. Clústeres: **greening sostenido en el SO (~-36.127, -70.58/-70.59; el más fuerte
    +0.025/año r²=0.87, y un parche de 8.85 ha +0.014 r²=0.61)** — coincide con la zona de Q9 — y
    un clúster mixto en el NE (~-36.00, -70.40). **CAVEAT estadístico:** con 6 puntos y 250
    componentes, r²≥0.6 ocurre por azar en parte (18/250=7%); son CANDIDATOS a inspección de
    campo, ponderados por dónde Nicolás sabe que hay desgasificación, no detecciones confirmadas.
  - **Acción de campo pendiente:** contrastar el clúster SO (-36.127, -70.58) y el NE
    (-36.00, -70.40) con desgasificación conocida. Mapas: `docs/maps/Laguna_del_Maule_vegetation_scan.png`
    y `_vegetation_trends.png`; datos en `datos/Laguna_del_Maule/vegetation_{scan,trends}.json`.

## 🟡 Prioridad MEDIA (mejoran rigor)

- **⚠️ La 2ª derivada (Guinn) aliasa estacionalidad con muestreo multi-estación (visto
  2026-06-13).** Al ampliar la serie LdM a 10 fechas de distintas estaciones (febreros +
  otoño + dic + ene), `analyze_timeseries` reportó 20 "eventos de aceleración" que son
  FENOLOGÍA, no recarga de magma. La 2ª derivada de Guinn 2024 asume muestreo regular /
  misma fenofase. → **Acción**: restringir la serie de 2ª derivada a una sola estación
  (p.ej. solo febreros) o deseasonalizar antes de derivar. Hasta entonces, los "spikes"
  del dashboard con datos multi-estación NO son interpretables como volcánicos.

- **Farrar 1995 (Mammoth, seminal CO2-vegetación)** — paywall Nature. → VPN.
- **Houlié 2006 (NDVI-dikes seminal)** — paywall Elsevier. → VPN / preprint.
- **Magney 2019 PNAS + Magney 2018 GRL (SIF)** — visores JS no soltaron PDF limpio.
  → Reintentar vía navegador o europepmc.
- **Papers SIF-antes-que-NDVI 2025** (validan hipótesis central) — estado 2026-06-13:
  - ✅ **TGRS `10.1109/TGRS.2025.3561216`** = Gao et al. 2025, *"Normalized Solar-Induced Fluorescence
    Responds Earlier Than Vegetation Indices to the 2019 North China Plain Drought"*, IEEE TGRS
    63:1-13. **DESCARGADO** (green-OA accepted manuscript desde Lirias/KU Leuven, 8.99 MB) y
    LEÍDO → ficha `PD-019`. Hallazgo: SIFn desciende antes que VIs/NDVI; cae 8.2/7.0/12.5/8.2 %
    en las 2 primeras semanas de sequía.
  - ⏳ **GRL `10.1029/2025GL119408`** = Parazoo & Fuchs 2025, *"Solar Induced Fluorescence as an
    Application Ready Early Warning Indicator of Flash Drought"*, Geophys. Res. Lett. 52. Es
    **gold-OA (CC BY-NC-ND)** pero el PDF está tras **Cloudflare** en Wiley/AGU (curl no pasa el
    challenge) → bajar vía **navegador real** (no requiere VPN). Ficha `PEND-04` [PENDIENTE DE LECTURA].
- **Lead-time real de red-edge/SIF vs NDVI** sin cuantificar para nuestro bioma. → fichar
  Eitel 2010 (PD-007) + conseguir papers SIF 2025.

## 🟢 Prioridad BAJA (nice-to-have)

- **HLS v2.0 2025** — supersede Claverie 2018. Para pipeline v2.
- **Respuesta espectral específica de Nothofagus/Araucaria a desgasificación difusa** —
  no existe literatura (gap de publicación identificado). → oportunidad de paper propio.
- **Coordenadas exactas de quebradas de desgasificación** en Laguna del Maule — depende de
  conocimiento de campo de Nicolás (SERNAGEOMIN), no de bibliografía.

---
*Resuelto un gap → moverlo a "Cerrados" abajo con fecha y cómo se cerró.*

## ✅ Cerrados
- (ninguno aún)
