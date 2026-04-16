# VegStress-v1

**Sistema de monitoreo de estrés vegetacional como precursor volcánico — Chile**

Dashboard en vivo: [mendozavolcanic.github.io/VegStress-v1](https://mendozavolcanic.github.io/VegStress-v1)

---

## ¿Qué hace?

Detecta cambios anómalos en la vegetación perivolcánica de Chile usando el índice NDVI (Normalized Difference Vegetation Index) calculado desde imágenes Sentinel-2 (10 m, cada 5 días).

Los cambios de vegetación pueden ser indicadores tempranos de actividad volcánica:

| Señal | Tipo | Causa probable |
|-------|------|----------------|
| Aumento NDVI > +2σ | **GREENING** | Fertilización por CO₂/SO₂ en bajas concentraciones, degasificación difusa |
| Disminución NDVI < −2σ | **BROWNING** | Estrés por SO₂, acidificación de suelo, calentamiento geotérmico, daño directo |

## Volcanes monitoreados (10)

| Zona | Volcanes |
|------|----------|
| Norte (árido) | Lascar |
| Centro | Laguna del Maule, Nevados de Chillán |
| Sur (boscoso) | Villarrica, Copahue, Llaima, Calbuco, Osorno, Puyehue-Cordón Caulle, Chaitén |

## Arquitectura

```
VegStress-v1/
├── ndvi_analyzer.py        — Descarga y analiza NDVI via Sentinel Hub (CDSE)
├── dashboard_generator.py  — Genera docs/index.html con mapa + graficos
├── docs/index.html         — Dashboard GitHub Pages (generado automático)
├── datos/                  — CSVs de series temporales por volcán
│   └── Villarrica/
│       └── ndvi_timeseries.csv
└── .github/workflows/
    └── vegstress.yml       — Workflow diario automatizado
```

## Uso local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar credenciales Copernicus CDSE
cp .env.example .env
# Editar .env con SH_CLIENT_ID y SH_CLIENT_SECRET
# (cuenta gratuita en dataspace.copernicus.eu)

# 3. Analizar un volcán
python ndvi_analyzer.py --volcan Villarrica --meses 12

# 4. Generar dashboard
python dashboard_generator.py
```

## Detección de anomalías

Se usa un umbral estadístico de **±2 desviaciones estándar** respecto al promedio histórico del período analizado. Con al menos 3 imágenes válidas se calcula la línea base; con 12 meses se obtiene representatividad estacional.

## Fuente de datos

- **Sentinel-2 L2A** via [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu) (gratuito)
- Bandas: B04 (Red, 665 nm) y B08 (NIR, 842 nm) a 10 m de resolución
- Filtro de nubes/nieve via Scene Classification Layer (SCL)
- Frecuencia: cada 5 días por volcán

## Contexto científico

No existen estudios sistemáticos previos sobre estrés vegetacional como precursor volcánico en especies chilenas (Nothofagus, matorral altiplánico, estepa patagónica). Este sistema es un primer paso para establecer líneas base y detectar señales anómalas de forma automatizada.

---

Desarrollado en SERNAGEOMIN · Datos: ESA Copernicus · Imágenes: Sentinel-2
