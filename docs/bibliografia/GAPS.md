# GAPS — evidencia que falta (VegStress-v1)

> Lista viva de información que el proyecto NECESITA pero NO tiene aún (modelo Educación
> y riesgos). Evita que el código/paper avance sobre cimientos inestables. Actualizar
> al descubrir un hueco. Cada gap: qué falta + cómo se resuelve.

## 🔴 Prioridad ALTA (bloquean decisiones de diseño)

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
  corregido al detector de alertas; (c) implementar la comparación inter-anual misma-estación
  (ya hay datos: Feb-2025 vs Ene-2026).
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
