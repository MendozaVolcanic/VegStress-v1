# Ficha: PD-011

**Archivo PDF**: `pdfs/USGS_1996_Mammoth_CO2_TreeKill.pdf`
**Título**: Invisible CO2 Gas Killing Trees at Mammoth Mountain, California
**Autores**: Michael L. Sorey, Christopher D. Farrar, William C. Evans, David P. Hill, Roy A. Bailey, James W. Hendley II, Peter H. Stauffer
**Afiliación 1er autor**: U.S. Geological Survey (USGS), Menlo Park, CA (verificado en footer — Mail Stop 977, 345 Middlefield Road, Menlo Park, líneas 249-250)
**Año**: 1996 · **Tipo**: USGS Fact Sheet-172-96 (hoja informativa de divulgación, NO journal) · **DOI**: n/d (fact sheet sin DOI)
**OA**: sí — documento público USGS
**Leído**: ✅ (vía markitdown `md/USGS_1996_Mammoth_CO2_TreeKill.md`, 2026-06-07)

> Fuente secundaria estilo V2- (fact sheet de divulgación). Útil para el dato clásico de "tree-kill"
> de Mammoth Mountain; los números primarios refinados están en los papers que la citan (ver Cawse-Nicholson
> PD-006 y la review iScience PD-003).

## Metodología
Hoja informativa USGS que resume el episodio de desgasificación de CO2 magmático en Mammoth Mountain tras
el enjambre sísmico de 1989. No es un estudio: describe mediciones de campo (gas de suelo con instrumentos
de colección manual sobre el suelo) y la tasa de emisión total estimada.

## Hallazgos clave (para el pipeline)
- **Concentración de CO2 en el suelo en zonas de tree-kill: 20 a 95 %** del contenido gaseoso del suelo
  (= 200 000 a 950 000 ppm), frente a **≤ 1 %** en suelo normal (línea 104, 130-131, 195-196). Este es el
  contraste fondo↔anomalía: ~1 % normal vs hasta 95 % en zona de muerte.
- **Mecanismo de muerte:** el CO2 alto en el suelo mata los árboles por **asfixia radicular** (priva a las
  raíces de O2) y por **interferencia con la absorción de nutrientes** — NO por la parte aérea/foliar
  (líneas 97-103, 191-194). La fotosíntesis foliar no se afecta directamente; el daño es subterráneo.
- **Área afectada: más de 100 acres (~40 ha)** de árboles muertos/moribundos al 1995 (líneas 51-53, 93).
  (La review iScience PD-003 cita ~50 ha al verano 1995, ref. consistente en orden de magnitud.)
- **Año de inicio:** árboles comienzan a morir en **1990**, un año después del enjambre sísmico de **1989**
  (mayo–noviembre 1989) que abrió fracturas para el ascenso del CO2 (líneas 53-55, 76-82).
- **Tasa de emisión total: ~1 300 toneladas/día** de CO2 (estimación preliminar; comparable a cráteres de
  Mt. St. Helens y Kilauea en actividad eruptiva baja) (líneas 164-167).
- **Umbral letal para personas:** respirar aire con **> 30 % CO2** (300 000 ppm) causa inconsciencia y
  muerte muy rápidamente; el CO2 (más denso que el aire) se acumula en depresiones, snowbanks y recintos
  mal ventilados (líneas 121-128, 135-151).
- **Edad de los árboles más viejos en la zona de tree-kill ≈ 250 años** → se interpreta que el episodio
  actual es la primera liberación a gran escala en al menos ese lapso (líneas 176-179).

## Citas útiles (con línea)
- "In the areas of tree kill, C02 makes up about 20 to 95% of the gas content of the soil; soil gas normally contains 1% or less C02" (L104, L130-131)
- "The high C02 concentrations in the soil ... are killing trees by denying their roots O2 and by interfering with nutrient uptake" (L100-103)
- "areas of dead and dying trees at Mammoth Mountain total more than 100 acres" (L92-93)
- "A preliminary estimate of the current rate of C02 gas emission at Mammoth Mountain is 1,300 tons per day" (L164-166)

## Relevancia para VegStress
**Es el caso-tipo histórico del fenómeno que VegStress quiere detectar por satélite:** CO2 difuso magmático
→ muerte de vegetación (browning) tras unrest sísmico. Aporta el contraste físico fondo↔anomalía
(1 % → 20-95 % de CO2 en suelo) que justifica por qué la firma de browning es detectable, y aclara el
**mecanismo** (asfixia radicular, no daño foliar directo) — relevante para entender por qué hay un retardo
temporal entre el unrest y la señal visible en NDVI. Sirve de ground-truth conceptual para el modelo
bifásico (greening a flujo bajo → browning/muerte a flujo alto).

## Dónde aplica (mapeo a código/doc)
- `seasonal_vs_volcanic.md` — caso de referencia para el retardo temporal unrest sísmico (1989) → señal de
  vegetación (1990): la señal volcánica puede demorar ~1 año, distinto de la estacional.
- `change_detector.py` — refuerza que el browning es señal válida cuando hay anomalía de CO2 de suelo extrema.
- `aoi_config.json` — Mammoth Mountain como AOI de validación histórica (~40-50 ha de tree-kill).
- `BIBLIOGRAPHY_SYNTHESIS.md §1, §3` (como fuente de divulgación/contexto, no como dato primario fino).

## Flags
Afiliación verificada (USGS Menlo Park, footer). **Fuente de divulgación (fact sheet), no peer-reviewed:**
las cifras (área, 1 300 t/d) son estimaciones preliminares de 1996 — para números primarios usar los papers
que miden directamente el flujo (Werner et al. 2014 vía PD-006; review PD-003 cita 31 000 g·m⁻²·d⁻¹ y
900 000 ppm para Mammoth). `[VERIFICAR-AFILIACION]` no aplica (footer claro).
