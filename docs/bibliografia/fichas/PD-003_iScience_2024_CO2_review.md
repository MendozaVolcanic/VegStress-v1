# Ficha: PD-003

**Archivo PDF**: `pdfs/iScience_2024_VolcanicCO2_Degassing_Review.pdf`
**Título**: Hazardous volcanic CO2 diffuse degassing areas — A systematic review on environmental impacts, health, and mitigation strategies
**Autores**: Fátima Viveiros, Catarina Silva · **Afiliación 1er autor**: Instituto de Investigação em Vulcanologia e Avaliação de Riscos (IVAR), Universidade dos Açores, Ponta Delgada, Azores, Portugal (verificado en footer p.1, líneas 58-61)
**Año**: 2024 · **Revista**: iScience (Cell Press) · **DOI**: 10.1016/j.isci.2024.110990
**OA**: sí — open access CC BY 4.0
**Leído**: ✅ (vía markitdown `md/iScience_2024_VolcanicCO2_Degassing_Review.md`, 2026-06-07)

## Metodología
Revisión sistemática (PRISMA): 564 artículos identificados en 5 bases de datos, 106 a lectura
de texto completo, **58 incluidos** finalmente. Compila impactos del CO2 difuso volcánico sobre
infraestructura, suelos, vegetación, microbiota, fauna y salud humana en **22 sistemas volcánicos
de 12 países** (mayormente en quietud/quiescentes). Sintetiza umbrales de concentración/flujo,
casos de letalidad y estrategias de mitigación en 6 categorías.

## Hallazgos clave (para el pipeline)
- **Umbral letal de CO2 para humanos/animales: > 100 000 ppm (10 vol. %)** (abstract; línea 37, 1192).
  Por encima de **200 000 ppm** → pérdida súbita de consciencia y muerte por hipoxia aguda tras pocas
  respiraciones (línea 1193).
- **Vegetación — umbral de browning/ausencia (la métrica clave para VegStress):**
  - CO2 en suelo **180 000–200 000 ppm** → plantas solo en grupos pequeños y dispersos (línea 577-579, Latera).
  - **350 000–400 000 ppm** → vegetación extremadamente escasa o ausente (línea 587, Latera; Pantelleria ~350 000 ppm, línea 1243).
  - **> 500 000 ppm** → la vegetación no se desarrolla (suelo desnudo, rocas meteorizadas, suelos acidificados) — Nyiragongo/Nyamulagira (línea 1096, 1244).
- **Valores de fondo (biogénico / respiración del suelo, NO volcánico):** concentración hasta
  **~50 000 ppm** y flujo hasta **~50 g·m⁻²·d⁻¹** (línea 108-110). Esto delimita la línea base.
- **Flujos máximos de CO2 medidos:** **449 500 g·m⁻²·d⁻¹** en La Bombilla (Cumbre Vieja, línea 105-106);
  Mammoth Mountain hasta **31 000 g·m⁻²·d⁻¹** con concentración de **900 000 ppm** (línea 1236-1237).
  Concentración máxima de suelo **100 vol. % = 1 000 000 ppm** (Furnas, Latera, Laacher See, Massif Central; línea 103).
- **Umbrales de planificación territorial (hazard maps):** Barberi et al. — suelo > **10 000 ppm** requiere
  acciones estructurales; > **50 000 ppm** = "no building areas". Viveiros et al. — alto riesgo de asfixia
  > **50 000 ppm** (línea 1340-1342). Criterio de área peligrosa Lavinio-Tor Caldara: concentración
  > **400 000 ppm a 50 cm** y flujo > **65 g·m⁻²·d⁻¹**, con buffer circular de **radio 0.5 km** por sitio (línea 1329-1332).
- **Confusor meteorológico cuantificado:** ~**30 %** de la variabilidad del CO2 indoor se explica por
  presión barométrica, velocidad de viento y contenido de agua del suelo (línea 1399). El flujo de CO2
  del suelo puede variar **hasta 3 órdenes de magnitud** por cambios de presión barométrica (línea 1405).
- **Estacionalidad:** CO2 indoor más alto en invierno que en verano en Azores (acople presión
  barométrica + menor ventilación + saturación de poros por lluvia) (línea 1408-1413).
- **Vínculo con teledetección:** la review cita (ref. 79) que "las plantas pueden ser sensibles a cambios
  menores en la actividad volcánica" vía detección remota, y que el impacto es **más significativo si hay
  anomalía térmica del suelo coincidente** (ref. 80, Azores; línea 1247-1249, Figura 3).

## Citas útiles (con línea)
- "CO2 ... is lethal in concentrations above approximately 100,000 ppm (10 vol. %)" (L37)
- "vegetation is very scarce in Pantelleria when soil CO2 concentrations reach ~350 000 ppm ... vegetation does not develop where there is more than 500 000 ppm of CO2 in the soil" (L1243-1244)
- "concentrations and fluxes up to 50 000 ppm and 50 g m⁻² d⁻¹ [son] biogenic values related to soil respiration" (L108-110)
- "the impact on the vegetation is even more significant if there is a soil thermal anomaly" (L1248-1249)

## Relevancia para VegStress
**Es la fuente que ancla los umbrales físicos de la cadena CO2→vegetación.** A diferencia de Guinn
(PD-001), que documenta *greening* por fertilización a CO2 difuso bajo/moderado, esta review documenta
el otro extremo: a CO2 alto (>180 000 ppm suelo) la vegetación **muere** (browning/ausencia). Esto
define el modelo de respuesta bifásica: fertilización (greening) a flujos bajos → estrés/muerte
(browning) a flujos altos. Confirma que el browning **sí** es señal válida de CO2 cuando la
concentración del suelo es extrema, y que la coincidencia con anomalía térmica amplifica el impacto
(consistente con el enfoque multivariable de VegStress).

## Dónde aplica (mapeo a código/doc)
- `change_detector.py` — los umbrales de suelo (50 000 / 200 000 / 350 000 / 500 000 ppm) informan
  la interpretación del signo de alerta: greening vs browning según régimen de flujo.
- `seasonal_vs_volcanic.md` — cuantificación del confusor meteorológico (~30 % varianza; estacionalidad
  invierno/verano) como estrategia de control.
- `aoi_config.json` — buffer de **0.5 km** de hazard maps publicados (contrastar con el de 30 m de Guinn;
  ambos coexisten: 30 m = dispersión local del difuso, 0.5 km = zona peligrosa de planificación).
- `BIBLIOGRAPHY_SYNTHESIS.md §1, §3, §6` — umbrales letales y de vegetación.

## Flags
Afiliación verificada (footer p.1). Es **review/secundaria**: los umbrales citados provienen de los 58
estudios primarios — al migrarlos a SYNTHESIS, atribuir al estudio original cuando se necesite precisión
(p.ej. Latera 180k–200k = refs. 55,56; Pantelleria ~350k = D'Alessandro et al., ref. 57).
