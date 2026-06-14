# Ficha: PEND-04

**Archivo PDF**: ⏳ NO descargado (gold-OA pero bloqueado por Cloudflare en Wiley/AGU)
**Título**: Solar Induced Fluorescence as an Application Ready Early Warning Indicator of Flash Drought
**Autores**: Nicholas Parazoo, Brian Fuchs · **Afiliación 1er autor**: [VERIFICAR-AFILIACION — no leído; Parazoo es típicamente NASA JPL / Caltech, confirmar en el PDF]
**Año**: 2025 · **Revista**: Geophysical Research Letters (AGU) 52 · **DOI**: 10.1029/2025GL119408
**OA**: **sí — gold OA, CC BY-NC-ND 4.0** (indexado en DOAJ; confirmado vía Crossref license + OpenAlex oa_status=gold) · **Leído**: ❌ **[PENDIENTE DE LECTURA]**

## Estado de obtención (2026-06-13)
- **DOI confirmado vía Crossref**: 10.1029/2025GL119408. Tipo: journal-article. Venue: Geophysical
  Research Letters, vol 52. Fecha publicación: 2025-12-02.
- **Es genuinamente OPEN ACCESS** (gold, CC BY-NC-ND 4.0 — Crossref `license`; OpenAlex
  `oa_status=gold`; presente en DOAJ artículo a8996c97666c4052b8012d51a6abc7e1).
- **NO se pudo descargar el PDF**: TODOS los endpoints de Wiley/AGU
  (`onlinelibrary.wiley.com/doi/pdfdirect/...`, `agupubs.onlinelibrary.wiley.com/doi/pdf/...`)
  devuelven una página de desafío **Cloudflare ("Just a moment...", HTTP 403/200 con HTML)**
  que `curl` no puede resolver (requiere ejecución de JS de navegador). Unpaywall reporta
  `is_oa=True` con `url_for_pdf` de Wiley, pero esa URL queda tras el muro anti-bot.
- **DOAJ** solo enlaza de vuelta al DOI (mismo destino Cloudflare). No hay mirror sin protección.
- **NO hay preprint** en arXiv / ESSOAr detectado (OpenAlex solo lista Wiley + el registro DOAJ;
  Semantic Scholar `openAccessPdf` vacío).

## Vía sugerida para conseguirlo
- **La más simple**: abrir el DOI en un navegador real (es OA, descarga gratis una vez pasado el
  challenge Cloudflare). URL directa del PDF: `https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/2025GL119408`
  o el botón "PDF" en `https://doi.org/10.1029/2025GL119408`.
- Alternativa: MCP `playwright`/Chrome (navegador headful) para pasar Cloudflare y guardar el PDF.
- No requiere VPN SERNAGEOMIN (es OA), solo un navegador que resuelva el JS de Cloudflare.

## Relevancia para VegStress (esperada — SIN leer)
Uno de los **dos papers SIF-antes-que-NDVI 2025** que fundamentan el pivote de NDVI a SIF/red-edge.
Por el título, propone **SIF como indicador de ALERTA TEMPRANA listo-para-aplicación de "flash
drought"** (sequía relámpago) → directamente alineado con la hipótesis central de VegStress de que
la SIF precede a la señal NDVI. **NO transcribir hallazgos hasta leer el PDF** (no inventar
números de lead-time).

## Flags
- **`[PENDIENTE DE LECTURA]`** — metadatos confirmados vía API; contenido NO leído.
- `[VERIFICAR-AFILIACION]` — afiliación del 1er autor (Parazoo) no confirmada en footer.
- `[ACCIÓN]` — descargar vía navegador (es OA gold) y completar Metodología/Hallazgos/Citas.
- `[OA-CONFIRMADO]` — gold OA CC BY-NC-ND; el único obstáculo es Cloudflare, no un paywall real.
