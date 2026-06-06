# Perplexity Pro (Chrome) — hallazgos complementarios, junio 2026

**Modo**: Investigación profunda (Deep Research). El primer intento falló
("algo salió mal"); el reintento corrió en modo Búsqueda y generó fuentes.
La prosa final no llegó a renderizar antes del cierre, pero la pestaña **Enlaces**
ya tenía las fuentes — que es lo valioso para bibliografía.

## Validación de la lección AP20 (Perplexity complementa, no reemplaza)
Las APIs gratis (arXiv/Crossref/OpenAlex/S2) ya habían cubierto ~90%. Perplexity
aportó 2 cosas que las APIs gratis NO encontraron:

### 🔑 Hallazgo NUEVO 1 — Paper de Etna (el que el subagente no pudo ubicar)
- **"Monitoring volcanic CO2 flux by the remote sensing of vegetation on Mt. Etna, Italy"**
- ScienceDirect (Remote Sensing of Environment): `S0034425724004346`
  → DOI probable `10.1016/j.rse.2024.114346` (Elsevier, PAYWALL)
- **Preprint SSRN GRATIS**: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4762417`
  → descarga MANUAL vía navegador (SSRN no entrega PDF por curl directo)
- **Por qué importa**: es el caso operacional MÁS cercano a VegStress —
  mide flujo de CO2 volcánico vía teledetección de vegetación en un volcán activo.
  Probablemente el "Guinn 2024 Etna" que figuraba sin DOI en papers_completo.md.

### 🔑 Hallazgo NUEVO 2 — Ruta OA verde para Bogue 2023
- La versión Wiley (`10.1029/2023GC010938`) bloquea curl, pero hay copia
  **green-OA en Chapman**: `digitalcommons.chapman.edu/sees_articles/635/`
  PDF: `https://digitalcommons.chapman.edu/cgi/viewcontent.cgi?article=1633&context=sees_articles`
  (curl devuelve 0 bytes por anti-bot bepress → descargar vía navegador)

## Otras fuentes que listó Enlaces (dominios vistos)
- digitalcommons.chapman.edu (Bogue green OA)
- bohrium.com (mirror del paper Bogue)
- sciencedirect.com (Etna RSE)
- papers.ssrn.com (Etna preprint 4762417)
- semanticscholar.org (varios)

> Quedó la sesión Perplexity abierta en Chrome (tab "Estoy construyendo un
> sistema operacional VegStress..."). Al reabrir, ir a esa sesión en Historial
> para leer la prosa final + pestaña Enlaces completa (había ~93KB de fuentes,
> no alcancé a extraerlas todas por scroll).

## TODO próxima sesión (descargas manuales vía navegador)
1. Etna RSE — bajar preprint SSRN 4762417 (alta prioridad, caso análogo directo)
2. Bogue 2023 — bajar de Chapman (green OA)
3. Magney 2019 PNAS (PMC6575166), Magney 2018 GRL, iScience 2024 review,
   MDPI rs16101735 + rs11131528 — todos vía EO/navegador
4. Seminales paywall (Farrar 1995, Houlié 2006, BFAST/CCDC/LandTrendr) → VPN SERNAGEOMIN
