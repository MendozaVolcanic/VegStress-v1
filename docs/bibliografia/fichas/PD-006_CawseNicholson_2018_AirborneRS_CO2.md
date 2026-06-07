# Ficha: PD-006

**Archivo PDF**: `pdfs/CawseNicholson_2018_AirborneRS_CO2.pdf`
**Título**: Ecosystem responses to elevated CO2 using airborne remote sensing at Mammoth Mountain, California
**Autores**: Kerry Cawse-Nicholson, Joshua B. Fisher, Caroline A. Famiglietti, Amy Braverman, Florian M. Schwandner, Jennifer L. Lewicki, Philip A. Townsend, David S. Schimel, et al. (18 autores)
**Afiliación 1er autor**: Jet Propulsion Laboratory (JPL), California Institute of Technology, Pasadena, CA, USA (verificado en footer p.1, líneas 10-19)
**Año**: 2018 · **Revista**: Biogeosciences (EGU/Copernicus) · **DOI**: 10.5194/bg-15-7403-2018
**OA**: sí — open access CC BY 4.0
**Leído**: ✅ (vía markitdown `md/CawseNicholson_2018_AirborneRS_CO2.md`, 2026-06-07)

## Metodología
Estudio exploratorio en Mammoth Mountain (volcán pasivamente desgasificante de CO2 "frío", sin H2S/SO2;
CO2 ≈ 99 % del gas). Cruza **flujo de CO2 del suelo medido in situ** (cámara de acumulación, West Systems +
LI-COR 820; 5 áreas, datos Werner et al. 2014, rango 0–2000 g·m⁻²·d⁻¹) contra una batería de variables
ecológicas teledetectadas con **datos aerotransportados**: AVIRIS-C (espectrómetro 400–2500 nm, 224 bandas,
**13 m**), MASTER (térmico, **50 m** → ET), lidar ASO (**30 m** → biomasa/altura de dosel). Modela cada
variable con **ensembles de regresión lineal múltiple** usando eCO2 como predictor y controlando confusores
topográficos (elevación, pendiente, aspecto, cobertura fraccional FC).

## Hallazgos clave (para el pipeline)
- **NDVI BAJA al aumentar el CO2 del suelo (browning):** NDVI medio **0.27 a 200 g·m⁻²·d⁻¹** → **0.10 a
  800 g·m⁻²·d⁻¹** de CO2 (abstract, líneas 49-52). Es decir, en el régimen de flujo ALTO el CO2 produce
  *browning*, no greening. (Nota: los autores marcan que esto es "inconsistente con la teoría" de
  fertilización pero consistente con mayor eficiencia de menos hojas.)
- **El soil CO2 flux es predictor estadísticamente significativo** de: NDVI (greenness del dosel),
  nitrógeno foliar del dosel, ET y biomasa (abstract, líneas 38-42).
- **Direcciones de respuesta (con CO2 creciente):** ↓ ET, ↑ nitrógeno foliar del dosel (ambos consistentes
  con teoría → doseles más eficientes en agua/nutrientes), ↓ NDVI, ↓ biomasa aérea, ↓ varianza de biomasa
  (homogeneización estructural) (abstract, líneas 44-62).
- **Índices espectrales evaluados (todos de AVIRIS):** NDVI, simple ratio, EVI, red-edge NDVI, modified
  red-edge simple ratio, modified red-edge NDVI, Vogelmann red-edge index 1 (líneas 307-274). Los índices
  **red-edge** son candidatos por su sensibilidad a clorofila/nitrógeno.
- **Rasgos foliares por espectroscopía de imágenes (SWIR):** nitrógeno, isótopo de N-15, LMA (leaf mass per
  area), celulosa, lignina ácido-digestible — derivados por PLS regression (líneas 300-301).
- **Confusor de cobertura es dominante:** eCO2 tuvo efecto **despreciable sobre vegetación rala/suelo
  desnudo** y efecto mayor sobre **píxeles densamente vegetados**; por eso umbralizan con **FC > 0.7**
  (cobertura fraccional, líneas 425, 520-523).
- **Buffer/exclusión:** se excluyeron explícitamente las zonas tree-kill (suelo no representativo) y se
  estudiaron los **gradientes alrededor** de ellas; se descartaron puntos con CO2 < **5 g·m⁻²·d⁻¹** (borde)
  (líneas 178-234).
- **Desacople estructura-función con CO2 alto:** ET y biomasa correlacionadas SIN CO2 elevado, pero
  **desacopladas** con CO2 elevado (abstract, líneas 28-29) → la firma de CO2 no es solo un índice, es un
  *cambio en las relaciones* entre variables.

## Citas útiles (con línea)
- "a mean NDVI of 0.27 at 200 g m⁻² d⁻¹ CO2 reduced to a mean NDVI of 0.10 at 800 g m⁻² d⁻¹ CO2" (L49-52)
- "soil CO2 flux was a significant predictor for ecological variables, including canopy greenness (NDVI), canopy nitrogen, ET, and biomass" (L38-42)
- "eCO2 had a negligible effect on vegetation indices ... over bare ground but showed higher impacts on fully vegetated pixels" (L520-523)
- "no significant H2S nor any SO2 present ... CO2 makes up ~99% of the gas by volume" (L193-195)

## Relevancia para VegStress
**Es la validación teledetectada de la respuesta de browning al CO2 alto**, complementaria a Guinn (PD-001,
greening por fertilización a flujo bajo). Aporta tres decisiones de diseño: (1) NDVI **sí** baja con CO2
alto → el browning es señal válida en ese régimen; (2) los índices **red-edge** y el **nitrógeno foliar**
pueden ser más sensibles/específicos que NDVI a la firma de CO2 (candidatos para añadir al detector);
(3) la firma robusta no es un umbral de un índice, sino el **cambio en el acople entre variables** (ET-biomasa)
y el filtro por cobertura (FC > 0.7) para no diluir la señal en píxeles ralos.

## Dónde aplica (mapeo a código/doc)
- `change_detector.py` — considerar añadir índices **red-edge** y proxy de **nitrógeno foliar**; aplicar
  filtro de cobertura tipo **FC > 0.7** análogo al NDVI < 0.4 de Guinn (descartar píxeles ralos).
- `seasonal_vs_volcanic.md` — su control de confusores topográficos (elevación/pendiente/aspecto como
  proxies de temperatura/humedad/luz) es una estrategia concreta de regresión.
- `aoi_config.json` — exclusión de zonas tree-kill (suelo no representativo) y estudio de **gradientes**
  alrededor; umbral de descarte de borde (CO2 < 5 g·m⁻²·d⁻¹).
- `BIBLIOGRAPHY_SYNTHESIS.md §1, §2, §6`.

## Flags
Afiliación verificada (JPL/Caltech, footer p.1). Sensores aerotransportados (AVIRIS 13 m, MASTER 50 m,
lidar 30 m) NO son los de VegStress (Sentinel-2 10 m): las direcciones de respuesta son transferibles,
pero las magnitudes absolutas de NDVI dependen del sensor/resolución. `[VERIFICAR: las relaciones
exactas (pendientes de regresión) están en figuras/tablas de las páginas no leídas (md líneas 539+) —
los números de esta ficha provienen del abstract, que es la fuente más confiable para las magnitudes
reportadas.]`
