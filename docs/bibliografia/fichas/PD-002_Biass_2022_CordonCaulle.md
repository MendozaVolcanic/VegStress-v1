# Ficha: PD-002

**Archivo PDF**: `pdfs/Biass_2022_CordonCaulle_Vegetation_Tephra_ML.pdf`
**Título**: Insights into the vulnerability of vegetation to tephra fallouts from interpretable
machine learning and big Earth observation data
**Autores**: S. Biass et al. · **Afiliación 1er autor**: (verificar — geociencias, GEE/ML)
**Año**: 2022 · **Revista**: NHESS (Copernicus) · **DOI**: 10.5194/nhess-22-2829-2022
**OA**: ✅ CC-BY · **Leído**: ✅ parcial (markitdown `md/`, 2026-06-07)

## Metodología
Modelo de vulnerabilidad de vegetación a **caída de tefra**, caso **Cordón Caulle 2011**
(Chile — mismo bioma templado del HS que nuestros volcanes). Usa **EVI** (no NDVI) de
Landsat/MODIS/Sentinel vía GEE, un **Cumulative Disturbance Index (CDI)**, **Random Forest**
+ **SHAP** para feature importance. Modela carga de tefra con densidades 1000/2000 kg·m⁻³.

## Hallazgos clave (para el pipeline)
- **Mecanismo = daño/browning por tefra**, opuesto al greening por CO2 de Guinn 2024.
  El **signo del cambio identifica el mecanismo**.
- Estados de daño **DS1–DS5 por espesor de depósito (mm)**, basados en Jenkins et al. 2015
  (Tabla 1): p.ej. pastoral: 1mm=disrupción, 25mm=menor, 60mm=mayor, 250mm=pérdida total.
- **minV (máxima perturbación) se alcanza 3–6 meses post-erupción** (L684) → ventana temporal
  relevante para detección de impacto.
- Métrica de recuperación: forma de la curva CDI (tiempo a mínimo y a recuperación).

## Citas útiles
- "minV was reached between 3–6 months after [the eruption]" (L684)
- Damage states DS1-5 as function of dry deposit thickness (Tabla 1, Jenkins 2015)

## Relevancia para VegStress
1. **Confirma los DOS mecanismos** que VegStress debe distinguir: CO2 difuso→greening
   (Guinn) vs tefra/ceniza→browning (Biass). El signo de ΔNDVI/2ª-derivada discrimina.
2. Caso **chileno, bioma templado HS** — el más transferible a Laguna del Maule/Villarrica.
3. **EVI + CDI + RandomForest + SHAP** es un stack de referencia para v2 de VegStress
   (vs nuestro ΔNDVI simple).
4. Ventana 3–6 meses post-evento útil para calibrar frecuencia de muestreo.

## Dónde aplica (mapeo a código/doc)
- `seasonal_vs_volcanic.md` — distinción de mecanismos por signo.
- `change_detector.py` — considerar EVI además de NDVI; ventana temporal 3-6 meses.
- Roadmap v2 — Random Forest + SHAP como sucesor del detector por umbral.

## Flags
`[VERIFICAR-AFILIACION]` del 1er autor (no confirmé footer). Lectura parcial (métodos+resultados).
