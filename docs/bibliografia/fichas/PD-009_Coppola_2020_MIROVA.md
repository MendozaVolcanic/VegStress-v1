# Ficha: PD-009

**Archivo PDF**: `pdfs/Coppola_2020_MIROVA_thermal_volcano.pdf`
**Título**: Thermal Remote Sensing for Global Volcano Monitoring: Experiences From the MIROVA System
**Autores**: Diego Coppola, Marco Laiolo, Corrado Cigolini, Francesco Massimetti, D. Delle Donne, M. Ripepe, … L. E. Lara (SERNAGEOMIN), C. Bucarey Parra (SERNAGEOMIN), … (29 coautores, varios observatorios)
**Afiliación 1er autor**: Dipartimento di Scienze della Terra, Università di Torino, Turín, Italia — verificado en p.1
**Año**: 2020 · **Revista**: Frontiers in Earth Science · **DOI**: 10.3389/feart.2019.00362
**OA**: sí (Frontiers open-access, CC-BY)
**Leído**: ✅ (vía markitdown `md/Coppola_2020_MIROVA_thermal_volcano.md`, 2026-06-07)

## Metodología
Describe la arquitectura y uso operativo de **MIROVA** (Middle InfraRed Observation of Volcanic
Activity), sistema automático de detección de puntos calientes basado en **MODIS** (Terra+Aqua).
Detecta, localiza y cuantifica anomalías térmicas en NRT en **216 volcanes**, usado por **17
observatorios** (incluido SERNAGEOMIN para Villarrica/Llaima). Combina principios espectrales y
contextuales. Notable: dos coautores son del SERNAGEOMIN (Lara, Bucarey Parra) y trata Llaima/
Villarrica (Chile) como casos.

## Hallazgos clave (para el pipeline)
- **Método VRP (Volcanic Radiative Power) — fórmula MIR (Wooster et al. 2003):**
  `VRP = 18.9 · Apixel · Σ(L_MIR,alert − L_MIR,bk)`, donde 18.9 es la constante de
  proporcionalidad, Apixel = 1 km² (píxel MODIS remuestreado) (p.3).
- **Bandas MODIS usadas:** MIR a **3.959 µm** (canal dual low/high gain) y TIR a **12.02 µm**.
  De ahí calcula NTI (Normalized Thermal Index) y ETI (Enhanced Thermal Index) (p.3).
- **Umbral de temperatura:** solo detecta superficies con **T > 500 K** (solo lo más caliente
  emite suficiente MIR). Error del VRP = **±30%** (p.3).
- **Rango dinámico de detección: ~1 MW a ~50 GW.** El límite inferior (1 MW) corresponde a
  un caso caliente (vent de ~7 m² a 1000°C) o frío (campo fumarólico de ~143 m² a 300°C) (p.3).
- **Resolución y latencia:** píxel 1 km, ~4 imágenes/día (ecuador), grilla 50×50 km, datos L1b
  desde LANCE con latencia <3 h, productos online 1–4 h tras adquisición (p.3-4).
- **Precisión espacial ±1 km;** distingue anomalías proximales (<5 km de cumbre, stems azules)
  de distales (>5 km, stems negros), útil para descartar incendios forestales (p.4).
- **Precursores térmicos = raros.** Solo **6–8% de los volcanes** desarrollan estrés térmico
  detectable antes de una erupción VEI≥3 (4–5 de 65 targets) (p.11). Implica que el térmico
  por sí solo NO basta como early-warning → motiva la fusión multisensor.

## Citas útiles (con página)
- "the lower detection limit (1 MW) would correspond to … a vent of ~7 m² and a temperature
  of 1000°C, or … a fumarole field having an area of ~143 m² and a temperature of 300°C" (p.3)
- "only 6–8% of the volcanoes seem to develop thermal unrest before a VEI 3 eruption detectable
  by MIROVA" (p.11)
- "the appearance of thermal anomalies before an eruption is often considered as an important
  precursor and a clear symptom of volcanic unrest" (p.11)

## Relevancia para VegStress
**Es la fuente operativa del canal térmico con el que VegStress debe cruzar la señal vegetal.**
MIROVA es el sistema que SERNAGEOMIN ya usa, así que VegStress debe producir salidas compatibles.
Dos lecturas: (1) el térmico tiene un **piso de detección alto (T>500 K, 1 MW)** — invisible a
desgasificación difusa fría que sí altera la vegetación; la señal vegetal cubre ese hueco de
baja energía. (2) Que solo 6–8% de erupciones tengan precursor térmico **justifica añadir un
sensor independiente (vegetación)** para subir la tasa de detección por fusión. La señal NDVI y
el VRP son **complementarios, no redundantes**: VRP = magma caliente en superficie; NDVI/estrés =
desgasificación difusa subletal aguas abajo.

## Dónde aplica (mapeo a código/doc)
- `BIBLIOGRAPHY_SYNTHESIS.md §5` — MIROVA/VRP como canal térmico de la fusión multisensor.
- `change_detector.py` — diseñar la salida para co-registrar eventos NDVI con picos de VRP
  (cross-validation térmico↔vegetal).
- Roadmap v2 — VRP es uno de los ejes de fusión; el umbral T>500 K define la frontera de
  complementariedad con la señal vegetal (energía baja, difusa).

## Flags
Afiliación 1er autor verificada (Univ. Torino, p.1). Coautores SERNAGEOMIN (Lara, Bucarey Parra)
confirmados en lista de afiliaciones p.1. Sin números inventados (todos de p.3-4 y p.11).
