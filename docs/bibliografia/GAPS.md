# GAPS — evidencia que falta (VegStress-v1)

> Lista viva de información que el proyecto NECESITA pero NO tiene aún (modelo Educación
> y riesgos). Evita que el código/paper avance sobre cimientos inestables. Actualizar
> al descubrir un hueco. Cada gap: qué falta + cómo se resuelve.

## 🔴 Prioridad ALTA (bloquean decisiones de diseño)

- **Umbrales ΔNDVI sin cita.** WATCH/WARNING/CRITICAL (0.10/0.15/0.25) son criterio
  propio, sin respaldo bibliográfico. → Resolver: leer Guinn 2024 (PD-001) y Biass 2022
  (PD-002), extraer umbrales validados, reemplazar en `change_detector.py` + `aoi_config.json`.
- **Método de discriminación estacional vs volcánico no implementado.** Las estrategias en
  `seasonal_vs_volcanic.md` están escritas pero no en código. → Resolver: leer cómo lo
  hace Guinn 2024 / BFAST, implementar Estrategia 1+2.
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
