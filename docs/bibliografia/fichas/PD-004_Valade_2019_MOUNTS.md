# Ficha: PD-004

**Archivo PDF**: `pdfs/Valade_2019_MOUNTS_monitoring_system.pdf` (31 pp)
**Título**: Towards Global Volcano Monitoring Using Multisensor Sentinel Missions and Artificial Intelligence: The MOUNTS Monitoring System
**Autores**: Sébastien Valade, Andreas Ley, Francesco Massimetti, Olivier D'Hondt, Marco Laiolo, Diego Coppola, David Loibl, Olaf Hellwich, Thomas R. Walter
**Afiliación 1er autor**: Dep. Computer Vision & Remote Sensing, Technische Universität Berlin, 10587 Berlín, Alemania (también GFZ Potsdam) — verificado en p.1
**Año**: 2019 · **Revista**: Remote Sensing (MDPI) · **DOI**: 10.3390/rs11131528
**OA**: sí (MDPI open-access, CC-BY)
**Leído**: ✅ (vía markitdown `md/Valade_2019_MOUNTS_monitoring_system.md`, 2026-06-07)

## Metodología
Presenta **MOUNTS** (Monitoring Unrest from Space), el primer sistema operativo de monitoreo
volcánico que integra en una sola plataforma **multisensor Sentinel + IA**. Fusiona tres
sensores satelitales más sismicidad terrestre, con arquitectura modular en Python (toolbox
SNAP de ESA). Monitorea **17 volcanes** (subducción, hotspots oceánicos, rifts continentales).
Resultados en web abierta `www.mounts-project.com` (plantilla heredada de MIROVA).

## Sensores y bandas que fusiona (núcleo para VegStress v2)
- **Sentinel-1 SAR (banda C)** → deformación de superficie (DInSAR, fringes; 1 fringe = 2.8 cm
  en línea de vista) + cambios de reflectividad (cambio incoherente). Píxel de salida 14×14 m,
  revisita 6–12 días (sección 3.3.1).
- **Sentinel-2 SWIR (MSI)** → anomalías térmicas. Usa bandas **B12-B11-B8A** (TOA, 2190/1610/865 nm),
  algoritmo contextual tipo HOTMAP; resolución 20 m, revisita ~5 días. Cuenta "píxeles calientes",
  correlaciona con VRP de MIROVA (sección 3.3.2).
- **Sentinel-5P TROPOMI (UV)** → SO2. VCD en Unidad Dobson, factor de conversión 2241.15 desde
  mol·m⁻², máscara DU>1 + filtro morfológico (erosión+dilatación 5×5 px). Caja de 500×500 km,
  resolución 7×3.5 km, revisita 1 día (sección 3.3.3).
- **Catálogos sísmicos GEOFON + USGS** (dato terrestre, no satelital).

## Hallazgos clave (para el pipeline)
- **IA = CNN sobre interferogramas.** Una **red convolucional totalmente convolucional tipo
  auto-encoder con bloques residuales (ResNet)** detecta deformación fuerte (intrusión de diques)
  en interferogramas wrapped. Entrenada **solo con interferogramas sintéticos** (ruido procedural
  + reglas empíricas). CNN pública en GitHub `Andreas-Ley/SAR-InterfPhaseFilter` (sección 3.4).
- **AOI estándar = máscara de 10×10 km** centrada en la cumbre; adaptable (ej. Kilauea Rift Zone
  40×60 km en erupción de flanco) (p.7-8, sección 3.1).
- **Latencia NRT de diseminación: <1–6 h** tras disponibilidad del producto en el Data Hub de ESA.
  Disponibilidad tras sensado: <24 h S1 SLC, 2–12 h S2 L1C, <3 h S5P NRTI SO2 (p.7).
- **NO incluye vegetación.** Los procesos monitoreados (Figura 1) son deformación, anomalía
  térmica de alta temperatura, SO2 y reflectividad SAR — **ningún índice de vegetación (NDVI) ni
  estrés vegetal**. La vegetación aparece solo como *fuente de ruido* (decorrelación InSAR por
  scatterers cambiantes; sección 3.3.1 DInSAR).

## Citas útiles (con línea/sección del markitdown)
- "MOUNTS is the first system to integrate all these components on a unique platform, with
  open-access, and global coverage capability" (L701)
- "the standard AOI for a specific volcano is defined as a 10×10 km mask centered around the
  volcano summit" (L726)
- "vegetation, water, sand-covered areas will appear highly incoherent as the scatterers change
  continuously" (L851) — la vegetación es tratada como ruido, no como señal.

## Relevancia para VegStress
**Es la referencia #1 de sistema operativo multisensor y el mapa de la oportunidad de VegStress.**
MOUNTS demuestra que la fusión SAR+térmico+SO2+sismicidad ya está resuelta operativamente, pero
**deja explícitamente fuera la vegetación**: la trata como decorrelación a filtrar. VegStress
ocupa exactamente ese hueco — añadir un canal NDVI/estrés vegetal como 5º sensor a una
arquitectura del estilo MOUNTS. Su patrón de diseño (Python modular, AOI 10×10 km, CNN entrenada
con datos sintéticos, web tipo MIROVA) es el blueprint de arquitectura para VegStress v2.

## Dónde aplica (mapeo a código/doc)
- `BIBLIOGRAPHY_SYNTHESIS.md §5` — referencia ancla del paradigma multisensor; documentar el GAP
  de vegetación como justificación del proyecto.
- `aoi_config.json` — el AOI de 10×10 km de MOUNTS es el estándar a contrastar con `radio_m`.
- `change_detector.py` — adoptar la idea de "score por sensor + serie temporal" como salida.
- Roadmap v2 (fusión multisensor) — MOUNTS es la arquitectura de referencia a replicar/extender
  con el canal vegetal.

## Flags
Afiliación 1er autor verificada (TU Berlín + GFZ, p.1). Sin números inventados. Nota: el conteo
de "17 volcanes" es del cuerpo (p.2); la Tabla 1 cita "~20" para MOUNTS — usar 17 (lista nominal).
