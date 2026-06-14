# Baseline Sentinel-2 — Laguna del Maule (VegStress-v1)

> Registro reproducible de la investigación de detección de estrés vegetal por
> desgasificación difusa de CO₂ en Laguna del Maule con Sentinel-2 (2021–2026).
> **Resultado principal: ausencia de firma espectral detectable** (resultado negativo
> robusto, multi-escala). Este documento permite re-correr todo y sirve de línea base
> para monitoreo futuro. *No contiene coordenadas de campo ni información operativa
> sensible (esas quedan en archivos locales gitignored).*

## 1. Objetivo

Probar si la vegetación responde de forma detectable (greening por fertilización de CO₂
a flujo bajo, o browning/zona de muerte a flujo alto) sobre las zonas de desgasificación
difusa de CO₂ del Complejo Volcánico Laguna del Maule, usando series de Sentinel-2.

Base científica fichada (ver `docs/bibliografia/`): Guinn 2024 (CO₂ difuso → greening,
señal a ≤30 m de la estructura, detección por 2ª derivada, control climático si r²>0.1);
Cawse-Nicholson 2018 (flujo alto → kill zone, NDVI 0.27→0.10); Biass 2022 (tefra → browning);
Wang 2024 + Gao 2025 (SIF precede al NDVI ~1 mes).

## 2. Datos

- **Sensor:** Sentinel-2 L2A vía Copernicus Data Space Ecosystem (Sentinel Hub Process API).
- **Escena:** ~18×18 km centrada en la caldera, 10 m/px (1800×1800), NDVI = (B08−B04)/(B08+B04).
- **Serie inter-anual mismo-mes (clave):** 6 febreros 2021–2026 (anula la fenología estacional).
- **Serie multi-estación:** + abril, diciembre, enero para contexto (úsese con cuidado: la 2ª
  derivada aliasa estacionalidad si se mezclan estaciones — ver GAPS).
- Bandas red-edge (B05) descargadas para el área de gas (NDRE).
- Arrays crudos `.npy` y PDFs: **gitignored** (no se versionan; se re-descargan).

## 3. Herramientas (pipeline)

| Script | Rol |
|---|---|
| `spatial_mapper.py` | Descarga NDVI espacial 10 m de una fecha (CDSE). |
| `find_clear_dates.py` | Escanea fechas despejadas (baja-res) antes de descargar full-res. |
| `aoi_geometry.py` | Geometría pura de AOIs: círculo y **polilínea+buffer** (quebradas). 11 tests. |
| `change_detector.py` | ΔNDVI entre fechas por AOI, alertas, 2ª derivada; **default mismo-mes año anterior**; control climático integrado. |
| `vegstress_signal.py` | Lógica de señal (signo = mecanismo). **Convenio: ΔNDVI>0 = greening, <0 = browning.** |
| `climate_control.py` | Remueve confusor climático (precip antecedente 48 d, Open-Meteo) por regresión si r²>0.1. |
| `aoi_finder.py` / `riparian_finder.py` | Hallan vegetación: parches grandes / hilos riparios lineales. |
| `vegetation_scan.py` | Escaneo de red ancha: TODA la vegetación, clima descontado espacialmente (mediana de cuenca). |
| `vegetation_trends.py` | Tendencia plurianual mismo-mes por componente, clima de cuenca restado, r² = consistencia. |
| `gas_pixel_trends.py` | Tendencia NDVI **píxel a píxel** dentro de una zona (spots chicos, sin promediar). |
| `rededge_gas.py` | NDRE (B05) sobre el área de gas, NDRE vs NDVI. |
| `drone_vegindex.py` | **(fase campo)** índices de vegetación a cm-escala sobre ortomosaicos de dron. |

Tests: `python -m pytest tests/ -q` (38/38).

## 4. Resultados (negativos, multi-escala)

Se buscó señal en **todas las escalas**, con controles climáticos, y anclado al área de
desgasificación confirmada en campo:

1. **Promedio de zona:** sin anomalía.
2. **Por componente de vegetación** (escaneo de red ancha, 250 componentes): el clima de
   cuenca es ~plano (−0.0017 NDVI/año); los componentes "robustos" caen FUERA del área de gas.
3. **Píxel a píxel** dentro del área de gas: aparecen 3 spots de declive, pero el control los
   rechaza — la tasa de declive es **2.5 % dentro vs 11.6 % fuera** (el declive es sequía
   regional; el área de gas declina *menos* que el promedio).
4. **Venteos exactos** (georreferenciados): ambos siguen el clima regional; declive por debajo
   del fondo; cero greening.
5. **Red-edge (NDRE):** misma conclusión — NDRE en lockstep con NDVI y el clima. No es
   saturación de NDVI: no hay señal óptica de vegetación.

**Conclusión:** Sentinel-2 (NDVI y red-edge, 10 m) **no detecta** la desgasificación difusa
de Laguna del Maule. Límite físico: resolución (venteos <30 m sobre vegetación rala) y
sensibilidad. Es coherente con la literatura (NDVI satura y responde tarde; la señal
fisiológica temprana está en SIF, sin sensor satelital fino disponible para esta escala).

### Lecciones metodológicas (cableadas al código)
- **Comparar SIEMPRE el mismo mes** (un "greening" inicial resultó ser artefacto fenológico
  de comparar enero vs febrero). Default del detector corregido a misma-estación año anterior.
- **Bug de signo corregido:** ΔNDVI<0 se etiquetaba como GREENING (invertía el mecanismo de
  cada alerta). Ahora ΔNDVI>0 = greening, con tests de regresión.
- **Descontar el clima** espacial (mediana de cuenca) y temporalmente (regresión) — el clima
  domina y debe removerse antes de atribuir nada al volcán.
- **No promediar áreas grandes** sobre señales localizadas (Guinn: gas ≤30 m) — ir a píxel.

## 5. Reproducir

```bash
# (requiere credenciales CDSE en .env: SH_CLIENT_ID / SH_CLIENT_SECRET)
python find_clear_dates.py --volcan "Laguna del Maule" --desde 2021-01-01 --hasta 2026-03-01 --paso 10
python spatial_mapper.py  --volcan "Laguna del Maule" --fecha <fecha_despejada>   # repetir por fecha
python change_detector.py --volcan "Laguna del Maule"        # detección + alertas + dashboard
python vegetation_trends.py --volcan "Laguna del Maule"      # tendencia plurianual mismo-mes
python gas_pixel_trends.py                                   # píxel a píxel en zona de interés
python -m pytest tests/ -q                                   # 38/38
```

## 6. Próximas palancas (no más Sentinel-2)

1. **Dron (cm-escala)** — ortomosaicos de la campaña OVDAS → `drone_vegindex.py` resuelve los
   spots de venteo que Sentinel-2 no puede. **Vía más prometedora.**
2. **Flujo de CO₂ de campo** — correlacionar/calibrar la respuesta vegetal directamente.
3. **PlanetScope 3 m** — intermedio entre Sentinel-2 y dron, si hay descargas disponibles.
4. **Monitoreo continuo** — esta línea base de 6 años permite detectar cambios *futuros* si la
   desgasificación se intensifica.

---
*VegStress-v1 · Baseline al 2026-06 · resultado negativo robusto + infraestructura lista para
fase de integración con campo.*
