# Ficha: PD-016

**Archivo PDF**: `pdfs/Ojeda_2011_Araucaria_Conguillio_LandsatTM.pdf` (13 pp, OA)
**Título**: Discriminación de bosques de Araucaria araucana en el Parque Nacional Conguillío, centro-sur de Chile, mediante datos Landsat TM
**Autores**: Nelson Ojeda, Víctor Sandoval, Héctor Soto, José Luis Casanova, Miguel A. Herrera, Luis Morales, Alejandro Espinosa, José San Martín
**Afiliación 1er autor**: Universidad de La Frontera, Depto. de Ciencias Forestales, Temuco, Chile (p.1)
**Año**: 2011 · **Revista**: Bosque 32(2):113–125 · **DOI**: 10.4067/s0717-92002011000200002
**OA**: sí (SciELO Chile) · **Leído**: ✅ (vía markitdown `md/Zamorano_2011_Araucaria_discriminacion.md`, 2026-06-07)

> ⚠️ El archivo dice "Zamorano_2011"; el **1er autor real es Nelson Ojeda** (UFRO). Zamorano no figura entre los autores.

## Metodología
Clasificación supervisada (máxima probabilidad) de **Landsat-5 TM** (27×27 m, enero 2003) sobre el **P.N. Conguillío** (La Araucanía, Chile), zona de relieve abrupto. **Índice = NDVI** = (TM4−TM3)/(TM4+TM3). Usan NDVI + modelo digital de elevación (MDE, corrección topográfica no-lambertiana) como datos auxiliares para discriminar 7 tipos de bosque de Araucaria araucana según densidad de copa y especies acompañantes (Nothofagus dombeyi, N. pumilio, N. antarctica, Chusquea culeou, Festuca). Validación con 105 puntos de campo, estadístico kappa.

## Hallazgos clave (para el pipeline)
- **Bandas discriminantes**: máxima diferencia espectral entre **rojo (TM3) e infrarrojo cercano (TM4)**, manteniéndose menor en SWIR (TM5, TM7). El PCA dio a **TM3 (rojo) como banda más informativa** (autovalor dominante), seguida de TM1, TM2, TM4 (p.6, p.7). → El contraste rojo/NIR (base del NDVI) es lo que separa los bosques.
- **Firma espectral de Araucaria por densidad de copa**: el bosque más denso (B1, cobertura 80%) es el **más absortivo** (NDVI medio 0.6225); los más ralos (B5 55%, B7 50%) los más reflectivos y con NDVI más bajo (B5=0.4123, B7=0.4623) (Cuadro 2). Rango NDVI de los 7 tipos ≈ **0.41–0.62**.
- **NDVI correlaciona con estructura del rodal**: cobertura de copa R²=0.743 (r=0.861), **dap R²=0.792 (r=0.89, la mejor)**, altura total R²=0.463 (r=0.68, regular) (p.8). NDVI predice mejor cobertura y diámetro que altura.
- **Fiabilidad global de la clasificación: 83.8%** (kappa); fiabilidad por tipo similar excepto B7 (consumidor 71%). El MDE fue determinante en relieve abrupto (p.9).

## Citas útiles (con página)
- "NDVI = (TM4-TM3)/(TM4+TM3)" donde "TM4: banda del infrarrojo cercano. TM3: banda del rojo" (p.5) — definición operativa.
- "La mayor diferencia de reflectancia espectral se observó entre la banda del rojo (TM3) y la de infrarrojo cercano (TM4)" (p.7) — firma característica.
- "Para el dap se obtuvo un R²=79,2%, y la mejor correlación positiva, r=0,89" (p.8) — NDVI↔estructura.

## Relevancia para VegStress
**Es la calibración espectral chilena clave** para las especies objetivo (Araucaria araucana + Nothofagus spp.) en los volcanes de La Araucanía (Llaima, Lonquimay, Villarrica). Confirma que (1) **el NDVI rojo/NIR es el índice válido para esta vegetación nativa**, (2) un bosque sano de Araucaria-Nothofagus tiene **NDVI típico ~0.55–0.62**, lo que ancla un valor base esperado y permite contextualizar caídas de ΔNDVI, y (3) en relieve volcánico abrupto la **corrección topográfica (MDE) es necesaria** para no confundir sombra con estrés.

## Dónde aplica (mapeo a código/doc)
- `change_detector.py` / configuración de índice — confirma NDVI(rojo,NIR) y aporta NDVI base ~0.55–0.62 para bosque sano andino.
- `spatial_mapper.py` / `aoi_config.json` — necesidad de corrección topográfica por sombra en AOIs de relieve abrupto.
- `BIBLIOGRAPHY_SYNTHESIS.md §calibración-especies-Chile` — firma espectral de Araucaria/Nothofagus.

## Flags
Afiliación verificada (p.1). 1er autor = **Nelson Ojeda (UFRO)**, no "Zamorano" del nombre de archivo → corregir referencia. Datos Landsat-5 TM (sensor histórico); para VegStress operativo (Sentinel-2/Landsat-8/9) las bandas son análogas pero no idénticas. NDVI de 2003, sin evento volcánico → es línea base de bosque sano, no de estrés.
