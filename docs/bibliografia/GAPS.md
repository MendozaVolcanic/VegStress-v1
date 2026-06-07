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

- **✅ RESUELTO (conflicto greening/browning):** tras fichar PD-003/PD-006/PD-011, el efecto del
  CO2 resultó **NO monotónico — depende del flujo**: bajo/moderado → GREENING (fertilización,
  Guinn); alto → BROWNING/kill zone (asfixia, Cawse-Nicholson NDVI 0.27→0.10 @ 200→800 g·m⁻²·d⁻¹;
  Mammoth 200 000-950 000 ppm). El detector ya distingue ambos signos (implementado). Pendiente:
  usar magnitud + contexto térmico/SO2 para separar fertilización de asfixia.
- **Eitel red-edge: PDF EQUIVOCADO.** `Eitel_2010_rededge_drought.pdf` es en realidad
  Berger/Parent/Tester 2010 (DOI 10.1093/jxb/erq201 = review de fenotipado). → **El lead-time de
  red-edge vs NDVI sigue SIN evidencia cuantificada.** Descargar el correcto:
  **Eitel, Gessler, Smith & Robberecht 2006**, Forest Ecol. Manag. 229:170-182.
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

## 🟡 Prioridad MEDIA (mejoran rigor)

- **Farrar 1995 (Mammoth, seminal CO2-vegetación)** — paywall Nature. → VPN.
- **Houlié 2006 (NDVI-dikes seminal)** — paywall Elsevier. → VPN / preprint.
- **Magney 2019 PNAS + Magney 2018 GRL (SIF)** — visores JS no soltaron PDF limpio.
  → Reintentar vía navegador o europepmc.
- **Papers SIF-antes-que-NDVI 2025** (TGRS `10.1109/TGRS.2025.3561216`,
  GRL `10.1029/2025GL119408`) — validan hipótesis central. Paywall. → IEEE/AGU.
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
