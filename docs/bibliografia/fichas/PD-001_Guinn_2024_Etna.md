# Ficha: PD-001

**Archivo PDF**: `pdfs/Guinn_2024_Etna_CO2flux_vegetation.pdf` (29 pp, SSRN preprint)
**Título**: Monitoring Volcanic CO2 Flux by the Remote Sensing of Vegetation on Mt. Etna, Italy
**Autores**: Nicole K. Guinn, Craig L. Glennie, Marco Liuzzo, Giovanni Giuffrida, Sergio Gurrieri
**Afiliación 1er autor**: National Center for Airborne Laser Mapping (NCALM), University of Houston, Texas (verificado en p.1 del preprint)
**Año**: 2024 · **Revista**: Remote Sensing of Environment · **DOI**: 10.1016/j.rse.2024.114408
**OA**: preprint libre en SSRN (abstract_id 4762417); versión final RSE = paywall
**Leído**: `[PENDIENTE DE LECTURA]`

## Metodología
`[PENDIENTE DE LECTURA]` — confirmar al leer: sensor (¿Sentinel-2? ¿airborne?), índice
de vegetación usado, método de correlación con flujo de CO2, ventana temporal.

## Hallazgos clave (para el pipeline)
- `[PENDIENTE DE LECTURA]` — extraer: umbral de índice asociado a flujo CO2 elevado;
  resolución espacial; lead-time respecto a otras señales; r² de la correlación
  vegetación↔CO2. Estos números migran a `BIBLIOGRAPHY_SYNTHESIS.md §6`.

## Citas útiles (con página)
- `[PENDIENTE DE LECTURA]`

## Relevancia para VegStress
Es el **caso operacional publicado más cercano** a lo que VegStress intenta: detectar
flujo de CO2 volcánico mediante la respuesta de la vegetación en un volcán activo
(Etna). Define el estado del arte que debemos igualar/citar. Equipo NCALM (LiDAR/RS) +
INGV (gases) — posible referencia de validación cruzada para Laguna del Maule.

## Dónde aplica (mapeo a código/doc)
- `change_detector.py` — umbrales (cuando se lea el método)
- `seasonal_vs_volcanic.md` — cómo separan señal CO2 de variabilidad natural
- `BIBLIOGRAPHY_SYNTHESIS.md §1` y `§6`

## Flags
Ninguno pendiente de afiliación (footer verificado). Análisis `[PENDIENTE DE LECTURA]`.
