# Literatura: Deteccion de Estres en Vegetacion como Precursor Volcanico

## Papers Criticos

### 1. Guinn et al. (2024) — Sentinel-2 NDVI + CO2 volcanico en Etna
- Compara Sentinel-2 con otras plataformas para correlacion NDVI-CO2 volcanico
- DOI: buscar en Remote Sensing / MDPI

### 2. Biass et al. (2022) — GEE + ML en Cordon Caulle, CHILE
- Usa Google Earth Engine + Machine Learning en volcan chileno
- Analisis de vulnerabilidad de vegetacion a tefra
- Directamente aplicable a nuestro sistema

### 3. Houlie et al. (2006) — NDVI detecta precursores 2 ANOS antes
- Paper fundacional: NDVI puede detectar cambios pre-eruptivos con anos de anticipacion
- DOI: buscar en Journal of Volcanology

### 4. Bogue et al. (2023) — 38 anos de NDVI en Yellowstone
- Demuestra tanto fertilizacion por CO2 como estres posterior
- Serie temporal de 38 anos como referencia metodologica

### 5. Weiser et al. (2022) — Sentinel-2 NDVI para dano por SO2 en La Palma
- Aplicacion directa de Sentinel-2 para detectar dano volcanico en vegetacion

### 6. NASA AVUELO Program (2025)
- Programa NASA liderado por Joshua Fisher
- Validando deteccion de estres vegetal volcanico en Rincon de la Vieja, Costa Rica
- Financiamiento autorizado hasta FY2033

## Hallazgo Clave
NO existe ningun sistema operacional de monitoreo volcanico basado en vegetacion en el mundo.
Este sistema seria el PRIMERO globalmente.

## Metodologia Propuesta
- Deteccion dual: greening (fertilizacion CO2) + browning (estres SO2/termico)
- Indices: NDVI, EVI, SAVI (para zonas aridas del norte)
- Fuente: Sentinel-2 (ya descargamos las imagenes en Copernicus-v1)
- Categorizacion por tipo de vegetacion para los 43 volcanes

## Gaps Identificados
- No hay estudios en especies chilenas (Nothofagus, Araucaria)
- No se ha aplicado SIF (Solar Induced Fluorescence) a volcanes
- No hay uso de SAVI para zonas volcanicas aridas
- Solo 3 de 16 papers usan Sentinel-2

## Papers NO encontrados (buscar manualmente)
- Fisher et al. (2025) — paper formal del programa AVUELO
- Estudios de NDVI en volcanes chilenos especificos (Villarrica, Calbuco)
