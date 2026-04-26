# Discriminacion Estacional vs Volcanico

> **El problema:** una baja de NDVI puede ser otono normal, sequia, nieve temprana, herbivoria,
> incendio, o degasificacion volcanica. Si confundimos las dos primeras con la ultima, generamos
> falsas alarmas y el sistema pierde credibilidad. Si fallamos al reves, perdemos precursores reales.

Este documento define la estrategia formal del proyecto VegStress-v1 para separar la senal volcanica
de la variabilidad natural.

---

## 1. Naturaleza de las senales

| Caracteristica           | Estacional / climatico              | Volcanico (CO2, SO2, termico)         |
|--------------------------|-------------------------------------|---------------------------------------|
| **Escala espacial**      | Regional (10-100 km)                | Local (50 m – 2 km)                   |
| **Forma temporal**       | Periodica anual                     | Monotona o escalonada                 |
| **Reversibilidad**       | Total cada ciclo                    | Lenta o irreversible                  |
| **Distribucion espacial**| Continua, suave                     | Parchada, ligada a fracturas/quebradas|
| **Correlacion con clima**| Alta (T, precipitacion, dia/anio)   | Nula o debil                          |
| **Efecto sobre control** | Misma senal que area de interes     | Control NO afectado                   |
| **Indices afectados**    | Todos por igual                     | NDRE/red-edge antes que NDVI          |

Esta tabla es la base de las 7 estrategias que siguen.

---

## 2. Siete estrategias acumulables

Cada estrategia reduce falsos positivos. Se acumulan: la alerta final solo se dispara si la senal
sobrevive a las 7. Pensar como **filtros en cascada**.

### Estrategia 1 — Comparacion inter-anual mismo DOY

**Que:** comparar NDVI(2026-04-15) vs NDVI(2025-04-15), no vs NDVI(2026-01-15).

**Por que:** elimina por construccion la fenologia anual. Si abril del ano pasado tenia NDVI 0.45
y abril de este ano tiene 0.30, esa diferencia ya no es "porque es otono".

**Implementacion:**
- `change_detector.py` debe aceptar `fecha_a` y `fecha_b` separadas por ~365 dias (+/- 30).
- Tolerancia DOY: <= 15 dias de diferencia entre fechas comparadas.
- Si no hay imagen clara dentro de la ventana DOY+/-15, ampliar a +/-30 con flag de menor confianza.

**Limitacion:** anos anomalos (sequia historica 2019-2020 en Chile central) sesgan la referencia.
Por eso necesitamos la Estrategia 3 (baseline multi-anual).

---

### Estrategia 2 — Normalizacion por AOI de control

**Que:** restar al delta del AOI volcanico el delta del AOI control (zona similar, sin influencia volcanica).

```
delta_anomalo = delta_AOI_volcanico - delta_AOI_control
```

**Por que:** sequia, ola de calor, nieve temprana afectan a ambos por igual. La diferencia aisla
lo que SOLO ocurre en la zona volcanica.

**Criterio de seleccion del control:**
- Misma cota (+/- 100 m)
- Misma exposicion (N/S)
- Misma vegetacion dominante (Nothofagus, estepa, matorral)
- Distancia >= 5 km del centro volcanico
- No afectado por dispersion conocida de gases (revisar vientos predominantes)

**Implementacion:** `aoi_config.json` ya tiene campo `tipo_esperado: "CONTROL"`. Hay que:
1. Marcar al menos 2 controles por volcan (norte y sur, exposiciones distintas).
2. En `change_detector.analyze_aoi()` calcular `delta_normalizado = delta - delta_control_promedio`.
3. Disparar alerta sobre `delta_normalizado`, no sobre `delta` crudo.

---

### Estrategia 3 — Baseline fenologico historico

**Que:** para cada AOI, construir la curva NDVI(DOY) de 2018-2025 (8 anos = 288+ imagenes claras
por AOI). Calcular percentiles 10/50/90 por DOY.

**Por que:** "DOY 105 deberia tener NDVI entre 0.42 y 0.58 con mediana 0.50". Si hoy 105 marca 0.31,
es **estadisticamente anomalo** independiente de cualquier comparacion punto-a-punto.

**Implementacion:**
- Nuevo script `phenology_baseline.py`: descarga serie 2018-presente, agrupa por DOY (ventana movil
  +/- 7 dias), guarda `datos/{volcan}/baseline_{aoi_id}.csv` con columnas `doy, p10, p50, p90, n_samples`.
- En `change_detector.py`: alerta si `NDVI_actual < p10(DOY_actual)` durante la Estrategia 4
  (persistencia).
- Z-score: `z = (NDVI_actual - p50) / sigma_doy`. |z| > 2 = anomalo, |z| > 3 = critico.

**Bonus:** este baseline tambien detecta **greening anomalo** (fertilizacion por CO2): NDVI > p90.

---

### Estrategia 4 — Persistencia temporal

**Que:** alerta solo si la anomalia se sostiene en N >= 3 fechas claras consecutivas.

**Por que:** una nube no detectada, sombra de cumulo, o mascara SCL imperfecta pueden bajar NDVI
una imagen aislada. Estres real persiste. Sequia se recupera con lluvia; CO2 sostenido no.

**Implementacion:**
- Mantener buffer rodante de las N=3 ultimas observaciones validas por AOI.
- Estado discreto: `NORMAL → SOSPECHA (1/3) → CONFIRMACION (2/3) → ALERTA (3/3)`.
- Solo emitir notificacion ruidosa al pasar a ALERTA.

---

### Estrategia 5 — Coherencia espacial

**Que:** medir si la baja es localizada (parches) o regional (uniforme).

**Por que:** ruptura por degasificacion afecta hectareas; sequia afecta el cuadrante completo.
Senal volcanica = alta varianza local + baja media regional.

**Metrica propuesta:**
```
indice_localidad = std(delta_dentro_AOI) / std(delta_buffer_5km_externo)
```

- `indice_localidad > 1.5` → senal localizada (sospechoso volcanico)
- `indice_localidad ≈ 1.0` → senal regional (probable estacional/climatico)

**Implementacion:** `change_detector.py` calcula esto por AOI usando los rasters delta ya disponibles.

---

### Estrategia 6 — Multi-indice cruzado

**Que:** calcular NDVI + NDRE + NDWI + NBR. La firma espectral del estres difiere segun la causa.

**Tabla de firmas:**

| Causa            | NDVI  | NDRE  | NDWI  | NBR   | Patron                               |
|------------------|-------|-------|-------|-------|--------------------------------------|
| Sequia           | bajo  | bajo  | **muy bajo** | medio | NDWI cae primero                     |
| Otono normal     | bajo  | bajo  | bajo  | bajo  | Todos caen juntos, gradual           |
| Nieve            | nulo  | nulo  | nulo  | bajo  | Cobertura total, deteccion via SCL   |
| Quemado          | bajo  | bajo  | bajo  | **muy bajo** | NBR cae mucho mas que NDVI    |
| **CO2 cronico**  | bajo  | **bajo (precoz)** | normal | normal | NDRE cae 2-3 meses ANTES que NDVI |
| **SO2 agudo**    | bajo  | bajo  | bajo  | bajo  | Caida rapida y profunda en dias-semanas |
| Termico (suelo)  | bajo  | bajo  | bajo  | medio | Patron muy localizado, halo radial   |

**Por que NDRE es clave:** la banda red-edge B05 (705 nm) responde al contenido de clorofila, que
cae ANTES que la biomasa visible (lo que mide NDVI con B04). Diferentes papers reportan 30-90 dias
de adelanto en deteccion de estres con NDRE vs NDVI.

**Implementacion:**
- Modificar evalscript en `spatial_mapper.py` y `ndvi_analyzer.py` para devolver un cubo
  `[NDVI, NDRE, NDWI, NBR, valid, cloud, snow]` en lugar de solo `[NDVI, valid, cloud, snow]`.
- Bands necesarias: B03, B04, B05, B08, B11, B12, SCL.
- Discriminador final: clasificador simple de reglas sobre el vector de 4 indices.

---

### Estrategia 7 — Cruce con datos externos

**Que:** validar contra datasets independientes para descartar causas naturales.

**Datos a consumir:**
- **CR2 / DGA Chile:** estacion meteorologica mas cercana (T, P) — descartar sequia.
- **MODIS Active Fire / VIIRS:** descartar incendios.
- **CDI Sequia (CR2):** indice de sequia regional.
- **ERA5 reanalysis:** anomalia climatica del mes.
- **MIROVA:** anomalia termica del cono — coherencia con actividad volcanica.
- **OVDAS sismicidad:** correlacion con tasa sismica.

**Implementacion:** modulo nuevo `validators/` con un cliente por fuente. Antes de emitir alerta
final, marcar flags:
- `sequia_regional: true/false`
- `incendio_proximo: true/false`
- `anomalia_termica_concurrente: true/false`

**Regla de oro:** si hay sequia regional + senal coherente en el control → no es volcanico.
Si hay anomalia termica MIROVA + caida en NDRE en quebradas + control sin senal → ALERTA real.

---

## 3. Algoritmo final integrado

```
def evaluar_alerta(aoi, fecha):
    # 1. Inter-anual mismo DOY
    delta_iy = ndvi(aoi, fecha) - ndvi(aoi, fecha - 365d)

    # 2. Normalizar por control
    delta_iy_control = ndvi(control, fecha) - ndvi(control, fecha - 365d)
    delta_anomalo = delta_iy - delta_iy_control

    # 3. Z-score fenologico
    z = (ndvi(aoi, fecha) - p50_DOY) / sigma_DOY

    # 4. Persistencia
    n_consecutivas = contar_anomalias_recientes(aoi)

    # 5. Localidad espacial
    loc = std_intra(aoi) / std_buffer(aoi)

    # 6. Multi-indice
    firma = clasificar_firma(NDVI, NDRE, NDWI, NBR)

    # 7. Cruce externo
    flags = consultar_validadores(aoi, fecha)

    # Decision
    if (abs(delta_anomalo) > 0.10
        and abs(z) > 2.0
        and n_consecutivas >= 3
        and loc > 1.5
        and firma in ["CO2_cronico", "SO2_agudo", "Termico"]
        and not flags.sequia_regional
        and not flags.incendio_proximo):
        return ALERTA(severidad=funcion(z, delta_anomalo, firma))
    else:
        return MONITOREAR
```

---

## 4. Roadmap de implementacion

| Fase | Estrategia                | Dificultad | Datos extra requeridos                  |
|------|---------------------------|------------|-----------------------------------------|
| 1    | Inter-anual               | Baja       | Ninguno (re-correr con fechas adecuadas)|
| 2    | Control AOI               | Baja       | Ya existe en `aoi_config.json`          |
| 3    | Baseline fenologico       | Media      | Backfill 2018-presente (~5 GB Sentinel) |
| 4    | Persistencia              | Baja       | Acumular >= 3 fechas                    |
| 5    | Coherencia espacial       | Baja       | Ya disponible en rasters                |
| 6    | Multi-indice              | Media      | Modificar evalscript                    |
| 7    | Cruce externo             | Alta       | Integrar 4-5 APIs externas              |

Empezar por 1+2 (cero datos nuevos), luego 6 (alta ganancia cientifica), luego 3 (alto costo
computacional pero permite z-scores rigurosos), finalmente 7.

---

## 5. Referencias claves para esta seccion

Pendiente integrar con `papers_completo.md` cuando termine la busqueda bibliografica. Buscar
especificamente:

- **BFAST / BFAST Monitor** — Verbesselt et al. — descomposicion de senales de tendencia, estacional, ruido en series MODIS/Landsat.
- **Harmonic regression NDVI** — Zhu & Woodcock (2014, RSE) — modelo armonico que separa fenologia de cambio anomalo.
- **Phenocam network** — referencia de baseline fenologico empirico.
- **Eklundh & Jonsson — TIMESAT** — software estandar de fenologia satelital.
- **Bogue 2023 Yellowstone** (ya en lista) — caso de uso operacional de baseline fenologico.

---

## 6. Notas para validacion en terreno

Para validar el sistema sin esperar una erupcion, usar zonas con desgasificacion **conocida y estable**:
- **Sector sur Laguna del Maule** — CO2 confirmado por usuario (Nicolas, SERNAGEOMIN).
- **Crateres laterales Villarrica** — actividad continua.
- **Copahue** — emisiones SO2 historicas.
- **Caulle pos-2011** — cicatriz tefra para cuantificar recuperacion.

Si el sistema emite alertas en estas zonas y NO en el control, la metodologia es valida.
Si tambien emite en control → falso positivo estructural, revisar.
