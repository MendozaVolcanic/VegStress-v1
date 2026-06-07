# Reglas para tratar la bibliografía — VegStress-v1

> Documento canónico de cómo trabajamos la bibliografía en este proyecto.
> Destilado de dos proyectos hermanos maduros: **VRP Chile** (síntesis central de
> números) y **Educación y riesgos** (fichas + anti-alucinación). Si dudás de cómo
> hacer algo bibliográfico acá, este es el documento a leer.

---

## 0. Filosofía en una línea

**Bajar 15 papers leídos vale más que 50 sin leer.** Cada número que entra al código
tiene que poder rastrearse a un DOI con página. Nunca inventamos un dato que el paper no da.

---

## 1. Estructura de carpetas (dónde va cada cosa)

```
docs/bibliografia/
├── REGLAS_BIBLIOGRAFIA.md      ← este documento
├── index.md                    ← portada + enlaces
├── BIBLIOGRAPHY_SYNTHESIS.md   ← FUENTE DE VERDAD: solo números accionables
├── GAPS.md                     ← evidencia que falta (alta/media/baja)
├── papers_completo.md          ← 54 papers indexados por tema (descubrimiento)
├── proyectos_similares.md      ← 55 sistemas/plataformas comparables
├── seasonal_vs_volcanic.md     ← el problema científico #1
├── descargas_2026-06.md        ← log de descargas
├── preguntas_busqueda.md       ← Fase-0 de cada búsqueda
├── fichas/                     ← una ficha .md por paper USADO
│   ├── _PLANTILLA.md
│   ├── INDICE_FICHAS.md        ← tabla maestra de IDs
│   └── PD-XXX_Autor_Año.md
└── pdfs/                       ← los PDF (gitignored, locales)
```

**Regla de oro de ubicación**: el PDF en `pdfs/`, los números en `BIBLIOGRAPHY_SYNTHESIS.md`,
la prosa/contexto en su ficha. Nunca duplicar el mismo número en tres lados sin que la
síntesis sea la autoridad.

---

## 2. Nombres de archivo (vinculante)

- **Patrón**: `Autor_Año_TemaCorto.pdf` — sin espacios, sin acentos, sin eñes.
- Año en 4 dígitos. Ej: `Guinn_2024_Etna_CO2flux_vegetation.pdf`.
- Si el archivo cae con nombre de editorial (`remotesensing-11-01528.pdf`,
  `UUID.tmp`), **renombrarlo** al patrón antes de dejarlo en `pdfs/`.

---

## 3. El flujo completo (de buscar a usar)

### Fase 0 — Definir la pregunta
Una línea con output esperado, en `preguntas_busqueda.md`. Si no podés escribirla así,
no estás listo para buscar.

### Fase 1 — Buscar (local primero, después online)
1. Agotar local: `papers_completo.md` → `BIBLIOGRAPHY_SYNTHESIS.md` → `pdfs/`.
2. Online: **APIs gratis primero** (arXiv, Crossref, OpenAlex, Semantic Scholar).
   Perplexity solo como complemento (descubre lo que las APIs no indexan).

### Fase 2 — Descargar y verificar
1. OA directo: `curl`. Editorial con anti-bot (MDPI/Cell/PNAS/Wiley/bepress): **navegador
   real** con "Preguntar dónde guardar" apagado → navegar a la URL del PDF → cae en
   Descargas → mover a `pdfs/` con nombre correcto.
2. **Verificar SIEMPRE** post-descarga:
   ```bash
   head -c5 archivo.pdf   # debe ser %PDF-  (si <!DOC = HTML disfrazado)
   stat -c%s archivo.pdf  # >50KB para paper journal
   ```
3. Cloudflare/intersticial: esperar pasivo (pasa solo). **Nunca resolver CAPTCHA.**
4. Paywall sin OA verde → anotar en `GAPS.md`, conseguir por VPN SERNAGEOMIN.

### Fase 3 — Procesar (fichar)
1. Convertir con **markitdown** ANTES de leer: `markitdown archivo.pdf > archivo.md`
   (ahorra 50-80% tokens).
2. Crear ficha `fichas/PD-XXX_Autor_Año.md` desde `_PLANTILLA.md`.
3. **Verificar afiliación del 1er autor en el footer de la p.1** antes de citarlo como
   autoridad. Si no la confirmaste → tag `[VERIFICAR-AFILIACION]`.
4. Llenar "Hallazgos clave" SOLO con números que el paper da. Lo que no leíste →
   `[PENDIENTE DE LECTURA]`. Nunca inventar.
5. Llenar "Dónde aplica" (qué archivo/función del código usa este paper).
6. Registrar en `INDICE_FICHAS.md`.

### Fase 4 — Migrar al pipeline
1. Los umbrales/fórmulas extraídos → `BIBLIOGRAPHY_SYNTHESIS.md` con DOI + página.
2. Si el número entra al código → docstring en `change_detector.py` (etc.) con el DOI,
   y tag `[IMPLEMENTADO: fecha + commit]`.
3. Si revela un hueco → `GAPS.md`.

---

## 4. Sistema de IDs de fichas

| Prefijo | Significado |
|---|---|
| `PD-XXX` | Paper Descargado (PDF en `pdfs/`) |
| `V2-XXX` | Fuente secundaria: reporte, dataset, fact-sheet (no paper journal) |
| `PEND-XX` | Identificado pero sin PDF (paywall / pendiente) |

Una ficha se crea cuando el paper **se va a usar** (informa una decisión). Los de
solo-contexto NO necesitan ficha: basta su entrada en `papers_completo.md`.

---

## 5. Tags anti-alucinación (vinculantes)

| Tag | Cuándo |
|---|---|
| `[PENDIENTE DE LECTURA]` | Paper citado/fichado pero aún no leído a fondo |
| `[VERIFICAR-AFILIACION]` | Afiliación del autor no confirmada en footer |
| `[VERIFICAR: sin cita]` | Número en uso (código) sin respaldo de paper |
| `[VERIFICAR: dato]` | Afirmación sin evidencia en el catálogo |

**Regla dura**: ningún valor físico/umbral se inventa. Si el paper no lo da, se dice
"no queda claro en el texto" — no se completa con un número plausible.

---

## 6. Canonicidad de autores

No todos los papers del mismo tema son la misma escuela. Antes de citar a alguien como
**autoridad metodológica**, abrir el PDF y leer la afiliación. Tabla viva en
`BIBLIOGRAPHY_SYNTHESIS.md §7`. Ejemplo: para CO2-vegetación, la autoridad es
Farrar/Bogue/Guinn/Lewicki, NO papers de CO2 agrícola genérico (otro mecanismo físico).

---

## 7. Git

- **PDFs**: gitignored (`pdfs/*.pdf`). Locales, re-descargables por DOI.
- **Versionado**: todos los `.md` (síntesis, fichas, índices, gaps).
- **Nunca** commitear `.env` ni nada con tokens.

---

## 8. Checklist al cerrar una sesión de bibliografía

- [ ] Pregunta de Fase-0 tiene respuesta o gap explícito.
- [ ] PDFs nuevos verificados (magic bytes) + nombre `Autor_Año_Tema`.
- [ ] Fichas nuevas registradas en `INDICE_FICHAS.md`.
- [ ] Números nuevos migrados a `BIBLIOGRAPHY_SYNTHESIS.md` con DOI+página.
- [ ] Huecos nuevos anotados en `GAPS.md`.
- [ ] Si un paper entró al código → docstring con DOI + tag `[IMPLEMENTADO]`.
- [ ] Commit + push de los `.md` (PDFs quedan locales).
