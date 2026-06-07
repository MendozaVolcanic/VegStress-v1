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
- **Método de discriminación estacional vs volcánico no implementado.** Las estrategias en
  `seasonal_vs_volcanic.md` están escritas pero no en código. Guinn aporta una concreta:
  **remover por regresión lineal** la influencia de clima (lluvia/temp/humedad) cuando r²>0.1.
  → Implementar.
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
