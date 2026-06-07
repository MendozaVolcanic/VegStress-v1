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
  → **DOI confirmado `10.1016/j.rse.2024.114408`** (vía OpenAlex; Elsevier, PAYWALL, sin OA verde)
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

> NOTA TÉCNICA (sesión jun 2026): curl NO baja estos por anti-bot (bepress
> devuelve HTML 3KB, MDPI/Akamai HTML 2KB). En NAVEGADOR REAL sí cargan
> (probado: Bogue abre en visor Chrome, 14 pp). El único bloqueo es el diálogo
> nativo "Guardar como" de Windows. Solución 1-vez: en `chrome://settings/downloads`
> apagar "Preguntar dónde guardar cada archivo" → las descargas caen directo a
> Descargas y se pueden automatizar. El tool de navegación de Claude NO puede
> abrir páginas `chrome://` (antepone https://), así que ese toggle lo hace el usuario.

URLs verificadas listas para bajar (1 clic c/u con toggle apagado):
1. **Bogue 2023** (green OA, carga OK en visor): `https://digitalcommons.chapman.edu/cgi/viewcontent.cgi?article=1633&context=sees_articles`
2. **Etna RSE 2024** — preprint SSRN: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4762417` (clic "Download This Paper")
3. **MDPI SIF-NDVI 2024**: `https://www.mdpi.com/2072-4292/16/10/1735/pdf`
4. **MDPI Coppola 2019**: `https://www.mdpi.com/2072-4292/11/13/1528/pdf`
5. **Magney 2019 PNAS** (PMC6575166): abrir `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6575166/`
6. **iScience 2024 review**: DOI `10.1016/j.isci.2024.110990` (Cell Press, CC-BY)
7. Seminales paywall (Farrar 1995, Houlié 2006, BFAST/CCDC/LandTrendr) → VPN SERNAGEOMIN
