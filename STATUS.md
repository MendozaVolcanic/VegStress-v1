# STATUS — VegStress-v1

## Estado actual (2026-06)
Fase satelital **cerrada con resultado negativo robusto**; proyecto entrando en
**integración con campo** (dron + flujo CO₂).

## Objetivo
Detectar estrés/respuesta de vegetación a desgasificación volcánica con Sentinel-2.
Caso piloto: Laguna del Maule (desgasificación difusa de CO₂).

## Resultado principal
**Sentinel-2 (NDVI y red-edge, 10 m) NO detecta la desgasificación difusa de Laguna del
Maule**, probado en todas las escalas (zona, componente, píxel, venteo exacto) con controles
climáticos y anclaje de campo. Límite = resolución (venteos <30 m sobre vegetación rala).
Detalle reproducible en [`docs/BASELINE_LdM.md`](docs/BASELINE_LdM.md).

## Hitos de esta etapa
- Motor de AOIs con geometría línea (quebradas) + círculo — `aoi_geometry.py` (11 tests).
- **Bug de signo GREENING/BROWNING corregido** (invertía el mecanismo de cada alerta).
- Control climático cableado al detector; default de comparación = misma estación año anterior.
- Escaneo de red ancha + tendencia plurianual + píxel-a-píxel + red-edge (NDRE).
- Serie inter-anual de 6 febreros 2021–2026 (CDSE).
- Pipeline de dron `drone_vegindex.py` listo para ortomosaicos de campo (6 tests).
- Suite: 38/38.

## Próximo paso
- Ingerir ortomosaicos de dron de la campaña (cm-escala) con `drone_vegindex.py`.
- Conseguir y cruzar las mediciones de flujo de CO₂ de campo.
- Mantener el baseline para detección de cambios futuros.

## Archivos clave
- `docs/BASELINE_LdM.md` — registro reproducible + resultado.
- `docs/bibliografia/GAPS.md` — evidencia pendiente y hallazgos.
- `PLAN.md` — arquitectura del proyecto.
