# Ficha: PD-008

**Archivo PDF**: `pdfs/Jakubik_2023_Prithvi_geospatial_FM.pdf`
**Título**: Foundation Models for Generalist Geospatial Artificial Intelligence
**Autores**: Johannes Jakubik, Sujit Roy, C. E. Phillips, Paolo Fraccaro, … Kommy Weldemariam, Rahul Ramachandran (equipo IBM Research + NASA Marshall + UAH + Clark Univ.) · **Afiliación 1er autor**: IBM Research — verificado en p.1
**Año**: 2023 · **Revista/Repo**: arXiv preprint (v2, 8-Nov-2023) · **DOI/ID**: arXiv:2310.18660
**OA**: sí (arXiv; modelo y pesos open-source en Hugging Face, ibm-nasa-geospatial) · **Leído**: ✅ (vía markitdown `md/Jakubik_2023_Prithvi_geospatial_FM.md`, 2026-06-07)

## Metodología
Presenta **Prithvi-100M**, un foundation model geoespacial **transformer (ViT) tipo Masked
Autoencoder (MAE)** preentrenado por auto-supervisión sobre imágenes satelitales
multiespectrales. Modificaciones clave al MAE/ViT: **embeddings posicionales 3D y patch
embedding 3D** (espacio + tiempo) para datos multitemporales. Preentrenamiento en watsonx con
hasta 64 GPUs A100, 1000 epochs.

## Hallazgos clave (para el pipeline)
- **Datos de preentrenamiento**: **>1 TB** de imágenes **HLS (Harmonized Landsat Sentinel-2)**,
  archivo de 3.61 PB desde 2015, resolución **30 m** cada ~2–3 días (p.4–5). Se usan **6 bandas**
  Sentinel: **B02, B03, B04, B8A, B11, B12** (azul, verde, rojo, NIR-estrecho, SWIR1, SWIR2)
  (p.5, líneas 314–319). Input 224×224, patch 1×16×16, tubelet temporal = 1.
- **Tamaño del modelo**: versión publicada **100 millones de parámetros** (Prithvi-100M),
  backbones ViT-base / ViT-large (p.1 abstract; p.8 líneas 436–437).
- **4 tareas downstream fine-tuneadas** (p.10–18): (1) imputación multitemporal de huecos por
  nubes; (2) **mapeo de inundaciones** (Sen1Floods11); (3) **segmentación de cicatrices de
  incendios** (MTBS); (4) **segmentación multitemporal de cultivos** (CDL).
- **Ventaja del preentrenamiento (eficiencia + datos escasos)**:
  - Inundaciones: el modelo preentrenado alcanza la performance de referencia en **25 epochs**
    vs **55** sin preentrenar → acelera **>2×** (p.16, líneas 794–798); IoU clase agua = 81.26
    (50 epochs) → 82.99 (500 epochs) (Tabla 2).
  - **Eficiencia de etiquetas**: reduciendo imágenes etiquetadas **~90%** el modelo aún
    converge a IoU >80% (inundaciones, p.16 líneas 805–811); en incendios baja de 540→135
    imágenes con performance comparable.
  - Incendios: IoU cicatriz = **73.62**, supera U-Net en **+2.61 pp** y ViT-base en **+4.58 pp**
    (Tabla 3, p.17).
  - Imputación de nubes: supera CGAN hasta **5 pp (5.7%) en SSIM**; con sólo 400 muestras
    supera al CGAN entrenado con 6231 (p.1 abstract; p.14 líneas 748–751).

## Citas útiles (con página)
- "Prithvi, a transformer-based geospatial foundational model pre-trained on more than 1TB of
  multispectral satellite imagery from the Harmonized Landsat-Sentinel 2 (HLS) dataset"
  (abstract, p.1)
- "the pretrained model surpasses a ViT-base model ... after 25 epochs of fine-tuning, while
  the same architecture with randomly initialized weights requires 55 epochs" (p.16, L794–798)
- "we reduce the number of labeled images ... by close to 90%, the models still converge to an
  IoU of over 80%" (p.16, L805–811)

## Relevancia para VegStress
**Habilitador del roadmap v2 (ML).** Prithvi ya está preentrenado **exactamente sobre las
bandas que VegStress usaría** (HLS 30 m, incluye rojo, NIR-estrecho y SWIR — base de NDVI y de
índices de agua), y demuestra que con **fine-tuning sobre pocas etiquetas** (~90% menos) se
logra segmentación robusta. Aunque sus tareas demostradas son inundación/incendio/cultivo y
**NO anomalía de vegetación volcánica**, el paradigma encaja: fine-tunear el encoder de Prithvi
con las series HLS de las AOIs chilenas para detección de anomalías (browning/greening)
reduciría la dependencia de umbrales manuales de ΔNDVI. La **resolución de 30 m** es coherente
con AOIs volcánicas (mejor que GOSIF/SIF de 5 km del PD-018). Riesgo: requiere etiquetas de
eventos de estrés volcánico (escasas) — pero justamente la eficiencia de datos de Prithvi
mitiga eso.

## Dónde aplica (mapeo a código/doc)
- `BIBLIOGRAPHY_SYNTHESIS.md §5` (roadmap ML v2) — candidato concreto de backbone.
- Roadmap v2 — fine-tuning de Prithvi-100M sobre HLS de AOIs; tarea = segmentación/anomalía
  de vegetación. Bandas HLS = compatibles con el pipeline NDVI actual.
- `change_detector.py` (futuro) — alternativa ML al detector de umbral/2ª-derivada.

## Flags
- Afiliación 1er autor (Jakubik, IBM Research) verificada en p.1.
- `[NOTA]` Preprint arXiv (no peer-reviewed en esta versión); números de la v2 (8-Nov-2023).
- `[NOTA]` Ninguna tarea demostrada es anomalía de vegetación volcánica → aplicación a
  VegStress es extrapolación de diseño, no resultado del paper.
- `[VERIFICAR]` La banda NIR-estrecho del preentrenamiento aparece como B8A en §3.1 (p.5) pero
  como B05 en §4.2 (p.9, "B02,B03,B04,B05,B06,B07"); el paper mezcla convención Sentinel y
  Landsat. Confirmar mapeo exacto de bandas antes de fine-tunear.
