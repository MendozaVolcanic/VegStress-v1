# Ficha: PD-007

**Archivo PDF**: `pdfs/Eitel_2010_rededge_drought.pdf`
**Título**: High-throughput shoot imaging to study drought responses
**Autores**: Bettina Berger, Boris Parent, Mark Tester · **Afiliación 1er autor**: Australian Centre for Plant Functional Genomics & School of Agriculture, Food and Wine, University of Adelaide (Glen Osmond, SA, Australia) — verificado en p.3519
**Año**: 2010 · **Revista**: Journal of Experimental Botany 61(13):3519–3528 · **DOI**: 10.1093/jxb/erq201
**OA**: green-OA (academic.oup.com) · **Leído**: ✅ (vía markitdown `md/Eitel_2010_rededge_drought.md`, 2026-06-07)

## ⚠️ Discrepancia crítica de fuente (LEER PRIMERO)
El archivo `md/Eitel_2010_rededge_drought.md` **NO es un paper de Eitel sobre red-edge**.
El PDF descargado bajo ese nombre es en realidad **Berger, Parent & Tester (2010)**, un
**review** de *imaging de alto rendimiento para fenotipado de sequía* en cámaras de
crecimiento/invernadero (JXB 61(13), doi:10.1093/jxb/erq201). **El DOI que dio el prompt
(10.1093/jxb/erq201) corresponde a este review, NO a un paper de Eitel.**

Este review **no contiene** el hallazgo central que VegStress esperaba (lead-time
cuantificado de red-edge/NDRE/CIred-edge sobre NDVI). El único Eitel que aparece es una
**cita secundaria**: Eitel, Gessler, Smith & Robberecht (2006), *"Suitability of existing
and novel spectral indices to remotely detect water stress in Populus spp."*, Forest Ecology
and Management 229:170–182 (p.3522, líneas ~810 y ref. p.3525). **Ese** sí es el paper de
red-edge/estrés hídrico que el cluster quería — pero **no está descargado**.

## Metodología (del review realmente descargado)
Review de técnicas **no-destructivas de imaging** para diseccionar la respuesta a sequía en
rasgos componentes (para fenotipado genético): infrarrojo térmico (IRT, conductancia
estomática), NIR (contenido de agua foliar), RGB/visible (senescencia, biomasa) y
fluorescencia de clorofila. No es teledetección satelital; es plataforma de fenotipado.

## Hallazgos clave (para el pipeline)
- **El crecimiento foliar es el PROCESO MÁS TEMPRANO afectado por déficit hídrico**, *antes*
  que caiga la conductancia estomática o la fotosíntesis (p.3523, líneas 928–931, citando
  Boyer 1970; Saab & Sharp 1989). → soporta la idea de buscar señal temprana en proxies de
  crecimiento/estructura, no en verdor agregado.
- **NDVI mide un nivel de estrés GENERAL, no específico, y satura** con cobertura alta
  (p.3523, líneas 975–978). → debilidad conocida de NDVI que VegStress busca complementar.
- **Fluorescencia de clorofila NO sirve para detección temprana de estrés hídrico**: la
  fotosíntesis sólo cambia notablemente bajo estrés severo (p.3524, líneas 1147–1154). →
  matiz importante: la "SIF temprana" del PD-018 aplica a déficit de agua que afecta GPP, no
  a daño fotosintético severo.
- Bandas NIR de agua útiles (970 nm, 1200 nm; Water Index R900/R970); índices NIR sólo
  correlacionan bien con contenido relativo de agua cuando se incluyen muestras severamente
  estresadas (p.3522, líneas 806–811, citando Eitel et al. 2006).
- **Red-edge**: el review sólo define el "red edge" como el salto de reflectancia visible→NIR
  (~700–750 nm, p.3522 líneas 763–767). **NO cuantifica lead-time de NDRE/CIred-edge vs NDVI.**

## Citas útiles (con página/línea)
- "leaf growth, as its decrease usually occurs before any reduction of stomatal conductance
  or photosynthesis" (p.3523, L928–931)
- "these spectral indices measure a general stress level of the plant canopy rather than a
  stress-specific trait" (p.3523, L975–978)
- "fluorescence imaging on its own does not seem suitable for the early detection of water
  stress" (p.3524, L1153–1154)

## Relevancia para VegStress
**Parcial / indirecta.** Confirma dos principios del proyecto: (1) NDVI satura y mide estrés
inespecífico → justifica buscar índices alternativos; (2) la señal temprana está en
crecimiento/estructura, no en fotosíntesis (que sólo cae bajo estrés severo). **Pero NO
aporta el lead-time red-edge↔NDVI que se necesitaba para validar la hipótesis central.** Para
eso hay que **descargar el paper correcto**: Eitel et al. 2006 (Forest Ecol. Manag. 229:170–
182) y/o un paper de red-edge satelital reciente (p.ej. NDRE Sentinel-2). Acción pendiente.

## Dónde aplica (mapeo a código/doc)
- `BIBLIOGRAPHY_SYNTHESIS.md §4` (hipótesis señal-temprana) — usar SÓLO como soporte de "NDVI
  satura / señal temprana en crecimiento", no como evidencia de lead-time red-edge.
- `seasonal_vs_volcanic.md` — el punto "fluorescencia no detecta estrés leve" matiza el uso de SIF.
- `change_detector.py` — no aporta umbral directo.

## Flags
- **`[VERIFICAR: identidad del paper]`** — el archivo descargado es Berger/Parent/Tester 2010
  (review JXB), NO Eitel red-edge. Renombrar el `.md`/`.pdf` o re-descargar el verdadero Eitel.
- **`[FALTA-DATO]`** — no hay lead-time cuantificado red-edge vs NDVI en esta fuente.
- **`[ACCIÓN]`** — descargar Eitel, Gessler, Smith & Robberecht 2006 (Forest Ecol. Manag. 229:170–182).
- Afiliación 1er autor (Berger, Univ. Adelaide) verificada en p.3519.
