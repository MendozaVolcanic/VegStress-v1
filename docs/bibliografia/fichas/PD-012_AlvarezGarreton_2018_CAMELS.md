# Ficha: PD-012 (DATASET — estilo V2)

**Archivo PDF**: `pdfs/AlvarezGarreton_2018_CAMELS-CL.pdf` (30 pp, OA)
**Título**: The CAMELS-CL dataset: catchment attributes and meteorology for large sample studies – Chile dataset
**Autores**: Camila Alvarez-Garreton, Pablo A. Mendoza, Juan Pablo Boisier, Nans Addor, Mauricio Galleguillos, Mauricio Zambrano-Bigiarini, Antonio Lara, Cristóbal Puelma, Gonzalo Cortés, René Garreaud, James McPhee, Alvaro Ayala
**Afiliación 1er autora**: Center for Climate and Resilience Research (CR2), Santiago + Univ. Austral de Chile, Valdivia (p.1)
**Año**: 2018 · **Revista**: Hydrology and Earth System Sciences (HESS) 22:5817–5846 · **DOI**: 10.5194/hess-22-5817-2018
**OA**: sí (CC-BY 4.0) · **Leído**: ✅ (vía markitdown `md/AlvarezGarreton_2018_CAMELS_CL.md`, 2026-06-07)

## Qué es (tipo de recurso)
**Dataset de cuencas + clima para Chile continental** (no es un método de teledetección). 516 cuencas, visualizable en http://camels.cr2.cl, descargable en PANGAEA (10.1594/PANGAEA.894885). Réplica chilena del CAMELS de EE.UU. (Addor et al. 2017).

## Cobertura espacial / temporal
- **Espacial**: 516 cuencas en Chile continental, latitud **17.8°S a 55.0°S** (4300 km N–S), elevación **0 a 6993 m s.n.m.** (p.1, p.3). Cubre las zonas volcánicas de La Araucanía / Los Lagos (Sur).
- **Temporal**: series **diarias**. Precipitación CR2MET **1979–2016**; TMPA 1998–2016 (Tabla 1). Caudal diario de estaciones DGA con ≥10 años de registro.
- **Resolución**: variables meteo agregadas por cuenca; CR2MET nativo a 0.05° (~5 km).

## Variables provistas (las útiles como control climático)
Series diarias por cuenca: **precipitación** (4 productos: CR2MET nacional, CHIRPS, MSWEP, TMPA), **temperatura** (máx/mín/media), **PET** (2 productos, incl. Hargreaves `pethar`), **SWE** (equivalente de agua en nieve), caudal. Además, **índices climáticos** (atributos por cuenca, computados 1-abr-1990 a 31-mar; def. p.~25):
- `p_mean_i` — precipitación media diaria (mm/día).
- `aridity_i` — **índice de aridez = PET_media / P_media** (humedad: <0.8; medio: 0.8–1.5; árido: >1.5) (p.33, Fig.9).
- `p_seasonality_i` — **estacionalidad de la precipitación** (ajuste sinusoidal; positivo = picos en verano, negativo = en invierno, ~0 = uniforme). **Clave para el confusor estacional.**
- `frac_snow_i` — fracción de precipitación que cae como nieve (días <0 °C).
- `high_prec_freq/dur/timing_i` — frecuencia/duración/estación de días muy lluviosos (≥5× media).
- `low_prec_freq/dur/timing_i` — frecuencia/duración/estación de días secos (<1 mm/día) → **indicador de sequía meteorológica**.
- `pet_mean` — PET media diaria (producto Hargreaves).

## Hallazgos / notas de calidad (para el pipeline)
- **Gran discrepancia entre productos de precipitación en zonas áridas** y subestimación sistemática en cuencas de cabecera de montaña húmedas (p.1). → En el sur volcánico, preferir **CR2MET** (producto nacional, base del balance hídrico DGA, p.~13).
- PET: buen desempeño en regiones húmedas (r>0.91), peor en hiperáridas (r<0.76); PET satelital sobreestima (p.1).
- El dataset incluye `interv_degree` (grado de intervención antrópica por cuenca) — útil para descartar cuencas con extracción/embalses al elegir AOIs de control.

## Citas útiles (con página)
- "This dataset includes 516 catchments; it covers particularly wide latitude (17.8 to 55.0°S) and elevation (0 to 6993 m a.s.l.) ranges" (abstract).
- "aridity, calculated as the ratio of mean daily PET (pet_mean) to mean daily precipitation" (def. atributos).
- "p_seasonality ... positive (negative) values indicate that precipitation peaks in summer (winter); values close to 0 indicate uniform precipitation" (def. atributos).

## Relevancia para VegStress (control climático del confusor estacional)
**Es la fuente chilena para "regredir fuera" el clima del NDVI** y separar señal volcánica de fenología/sequía. El NDVI de bosque andino sube/baja con la estación lluviosa y con sequías multianuales (megasequía); CAMELS-CL provee, para la cuenca donde cae cada AOI, **precipitación CR2MET diaria, PET, SWE y los índices `aridity`/`p_seasonality`/`low_prec_*`** que cuantifican el ciclo y las anomalías de sequía. Con ello, `regress_out_climate()` puede usar precipitación/PET antecedente como covariables (igual que la decorrelación polinómica de De Schutter PD-014 y la regresión r²>0.1 de Guinn PD-001), de modo que un browning solo se marca como volcánico si persiste **tras** remover el efecto del clima de la cuenca.

## Dónde aplica (mapeo a código/doc)
- `vegstress_signal.py::regress_out_climate()` — usar `precip_cr2met` (y `pet`) diaria de la cuenca de la AOI como covariable para remover el componente climático del NDVI.
- `seasonal_vs_volcanic.md §Estrategia-climática` — `p_seasonality_i` para modelar el ciclo estacional esperado; `low_prec_freq/dur_i` y `aridity_i` para detectar años de sequía que imitan estrés volcánico.
- `aoi_config.json` — mapear cada AOI a su `gauge_id`/cuenca CAMELS-CL; preferir cuencas con `interv_degree` bajo como referencia.
- `BIBLIOGRAPHY_SYNTHESIS.md §control-climático`.

## Flags
Afiliación verificada (p.1). Es un **dataset de cuencas hidrológicas**, no de píxeles: la unidad espacial es la cuenca, no la AOI puntual → habrá que asignar cada AOI a su cuenca contenedora (cuencas pequeñas de alta montaña pueden no coincidir con la AOI). CR2MET termina en 2016 en esta v1.3; verificar si existe versión actualizada (CR2MET v2.x) antes de operacionalizar. [VERIFICAR: vigencia/actualización del producto CR2MET para fechas >2016].
