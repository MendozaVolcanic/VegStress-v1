# VegStress-v1 — Plan de Proyecto

## Objetivo
Sistema automatizado de deteccion de estres en vegetacion como precursor de actividad volcanica, usando imagenes Sentinel-2 que ya descargamos en Copernicus-v1.

## Arquitectura
```
Copernicus-v1 (imagenes Sentinel-2 existentes)
    |
    v
VegStress-v1/
├── config_volcanes.py        — 43 volcanes + clasificacion vegetacion
├── ndvi_calculator.py        — Calculo NDVI/EVI/SAVI desde bandas S2
├── baseline_builder.py       — Construye linea base estacional por volcan
├── anomaly_detector.py       — Detecta anomalias vs baseline
├── alert_generator.py        — Genera alertas markdown
├── visualizador.py           — Graficos temporales NDVI
├── docs/index.html           — Dashboard GitHub Pages
└── .github/workflows/
    └── vegstress.yml         — Workflow diario post-Copernicus
```

## Fases

### Fase 1: MVP (1-2 semanas)
1. Calcular NDVI desde bandas B04 (Red) y B08 (NIR) de Sentinel-2
2. Crear baseline estacional (promedio movil 90 dias) por volcan
3. Detectar anomalias (>2σ desviacion de baseline)
4. Dashboard basico con series temporales NDVI

### Fase 2: Multi-indice (semana 3)
5. Agregar EVI (Enhanced Vegetation Index) — mejor para vegetacion densa del sur
6. Agregar SAVI (Soil-Adjusted) — mejor para volcanes aridos del norte
7. Clasificar volcanes por tipo de cobertura vegetal

### Fase 3: Alertas inteligentes (semana 4)
8. Detectar tanto greening (CO2) como browning (SO2/calor)
9. Cross-reference con datos VRP termicos de Mirova-v1
10. Integrar con sistema de alertas Copernicus-v1

## Evalscript NDVI para Sentinel Hub
```javascript
//VERSION=3
function setup() {
  return {
    input: [{bands: ["B04", "B08", "SCL"]}],
    output: {bands: 1, sampleType: "FLOAT32"}
  };
}
function evaluatePixel(sample) {
  // Scene Classification Layer: 4=vegetation, 5=bare soil
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
```

## Bandas Sentinel-2 necesarias
| Banda | Longitud de onda | Resolucion | Uso |
|-------|-----------------|------------|-----|
| B04 | 665 nm (Red) | 10m | NDVI, EVI |
| B08 | 842 nm (NIR) | 10m | NDVI |
| B8A | 865 nm (NIR narrow) | 20m | EVI refinado |
| B11 | 1610 nm (SWIR) | 20m | Deteccion humedad |
| SCL | Scene Classification | 20m | Filtro nubes |

## Clasificacion de Volcanes por Vegetacion
| Zona | Volcanes | Vegetacion | Indice principal |
|------|----------|-----------|-----------------|
| Norte (arida) | Taapaca, Parinacota, Guallatiri, Isluga, Irruputuncu, Ollagüe, San Pedro, Lascar | Matorral altiplanico / desierto | SAVI |
| Centro | Tupungatito, San Jose, Tinguiririca, Planchon-Peteroa, Descabezado, Laguna del Maule, Nevado de Longavi, N. Chillan | Matorral esclerofilo | NDVI + EVI |
| Sur (boscosa) | Copahue → Chaiten | Bosque valdiviano / Nothofagus | EVI |
| Austral | Hudson → Yate | Bosque patagonico | EVI |

## Dashboard
- Repo GitHub independiente con GitHub Pages
- Graficos de series temporales NDVI por volcan
- Mapa de anomalias actual
- Tabla de alertas activas
- Cross-reference con alertas termicas Copernicus-v1

## Dependencias
- numpy, rasterio (lectura GeoTIFF)
- matplotlib (graficos)
- scipy (deteccion anomalias)
- Imagenes Sentinel-2 de Copernicus-v1 (ya existentes)
