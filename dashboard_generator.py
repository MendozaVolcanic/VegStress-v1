"""
Dashboard Generator — VegStress-v1
Genera docs/index.html desde los CSV de datos NDVI.
Uso: python dashboard_generator.py
"""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DATOS_DIR = Path(__file__).parent / "datos"
DOCS_DIR = Path(__file__).parent / "docs"

VOLCANES_INFO = {
    "Villarrica":              {"zona": "Sur",    "lat": -39.42, "lon": -71.94},
    "Copahue":                 {"zona": "Sur",    "lat": -37.86, "lon": -71.17},
    "Llaima":                  {"zona": "Sur",    "lat": -38.71, "lon": -71.73},
    "Calbuco":                 {"zona": "Sur",    "lat": -41.33, "lon": -72.61},
    "Osorno":                  {"zona": "Sur",    "lat": -41.14, "lon": -72.50},
    "Puyehue - Cordon Caulle": {"zona": "Sur",    "lat": -40.56, "lon": -72.12},
    "Chaiten":                 {"zona": "Sur",    "lat": -42.84, "lon": -72.65},
    "Nevados de Chillan":      {"zona": "Centro", "lat": -37.41, "lon": -71.35},
    "Laguna del Maule":        {"zona": "Centro", "lat": -36.07, "lon": -70.50},
    "Lascar":                  {"zona": "Norte",  "lat": -23.37, "lon": -67.74},
}

ANOMALY_THRESHOLD = 2.0

# Latitud de la extension visual del mapa (norte a sur de Chile volcanico)
MAP_LAT_N = -18.0
MAP_LAT_S = -46.0
MAP_LON_W = -74.0
MAP_LON_E = -66.0


def load_csv(volcan_name):
    csv_path = DATOS_DIR / volcan_name.replace(" ", "_") / "ndvi_timeseries.csv"
    if not csv_path.exists():
        return []
    with open(csv_path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def compute_stats(rows):
    ok = [r for r in rows if r.get('status') == 'OK' and r.get('ndvi_mean')]
    if len(ok) < 3:
        return None
    vals = [float(r['ndvi_mean']) for r in ok]
    mean = sum(vals) / len(vals)
    std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5

    # Tendencia: comparar ultima semana vs promedio
    recent = [float(r['ndvi_mean']) for r in ok[-3:]]
    trend = sum(recent) / len(recent) - mean if recent else 0

    anomalies = []
    for r in ok:
        v = float(r['ndvi_mean'])
        z = (v - mean) / (std + 1e-6)
        if abs(z) > ANOMALY_THRESHOLD:
            anomalies.append({
                "fecha": r['fecha'],
                "ndvi": round(v, 4),
                "z": round(z, 2),
                "tipo": "BROWNING" if z < 0 else "GREENING"
            })
    return {
        "mean": round(mean, 4),
        "std": round(std, 4),
        "trend": round(trend, 4),
        "n_valid": len(ok),
        "n_total": len(rows),
        "last_ndvi": round(float(ok[-1]['ndvi_mean']), 4) if ok else None,
        "last_fecha": ok[-1]['fecha'] if ok else None,
        "anomalies": anomalies,
    }


def build_chart_data(rows):
    ok = [r for r in rows if r.get('status') == 'OK' and r.get('ndvi_mean')]
    return {
        "labels": [r['fecha'] for r in ok],
        "ndvi": [round(float(r['ndvi_mean']), 4) for r in ok],
    }


def lat_to_pct(lat):
    return round((lat - MAP_LAT_N) / (MAP_LAT_S - MAP_LAT_N) * 100, 2)


def lon_to_pct(lon):
    return round((lon - MAP_LON_W) / (MAP_LON_E - MAP_LON_W) * 100, 2)


def generate_dashboard():
    DOCS_DIR.mkdir(exist_ok=True)

    volcanes_data = {}
    all_anomalies = []

    for nombre in VOLCANES_INFO:
        rows = load_csv(nombre)
        info = VOLCANES_INFO[nombre]
        stats = compute_stats(rows) if rows else None
        chart = build_chart_data(rows) if rows else {"labels": [], "ndvi": []}
        volcanes_data[nombre] = {
            "zona": info["zona"],
            "lat": info["lat"],
            "lon": info["lon"],
            "map_y": lat_to_pct(info["lat"]),
            "map_x": lon_to_pct(info["lon"]),
            "has_data": bool(rows),
            "stats": stats,
            "chart": chart,
        }
        if stats and stats["anomalies"]:
            for a in stats["anomalies"]:
                all_anomalies.append({**a, "volcan": nombre, "zona": info["zona"]})

    all_anomalies.sort(key=lambda x: x["fecha"], reverse=True)

    data_json = json.dumps(volcanes_data, ensure_ascii=False)
    anomalies_json = json.dumps(all_anomalies, ensure_ascii=False)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    n_volcanes = sum(1 for v in volcanes_data.values() if v["has_data"])
    n_anomalies = len(all_anomalies)
    alert_color = "red" if n_anomalies > 0 else "green"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VegStress-v1 | Monitoreo NDVI Volcanico Chile</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    :root {{
      --bg:#0f1117; --card:#1a1d26; --border:#2a2d3a;
      --text:#e2e8f0; --muted:#8892a4;
      --green:#22c55e; --yellow:#eab308; --red:#ef4444;
      --orange:#f97316; --blue:#3b82f6; --purple:#a855f7;
    }}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;font-size:14px;height:100vh;display:flex;flex-direction:column}}
    header{{background:var(--card);border-bottom:1px solid var(--border);padding:12px 24px;display:flex;align-items:center;gap:16px;flex-shrink:0}}
    header h1{{font-size:1.2rem;font-weight:700;color:var(--green)}}
    header .subtitle{{color:var(--muted);font-size:.82rem}}
    header .updated{{margin-left:auto;color:var(--muted);font-size:.78rem}}
    .summary-bar{{display:flex;gap:10px;padding:10px 24px;background:var(--card);border-bottom:1px solid var(--border);flex-wrap:wrap;flex-shrink:0}}
    .stat-chip{{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:8px 16px;text-align:center;display:flex;align-items:center;gap:10px}}
    .stat-chip .value{{font-size:1.4rem;font-weight:700}}
    .stat-chip .label{{color:var(--muted);font-size:.72rem}}
    .green{{color:var(--green)}} .red{{color:var(--red)}} .yellow{{color:var(--yellow)}} .blue{{color:var(--blue)}}
    .main{{display:flex;flex:1;min-height:0}}

    /* SIDEBAR */
    .sidebar{{width:220px;min-width:180px;background:var(--card);border-right:1px solid var(--border);overflow-y:auto;flex-shrink:0}}
    .sidebar-section{{padding:10px 14px 4px;color:var(--muted);font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}}
    .volcano-item{{padding:9px 14px;cursor:pointer;border-left:3px solid transparent;display:flex;justify-content:space-between;align-items:center;gap:6px}}
    .volcano-item:hover{{background:rgba(255,255,255,.04)}}
    .volcano-item.active{{border-left-color:var(--green);background:rgba(34,197,94,.06)}}
    .volcano-item .vname{{font-size:.84rem;font-weight:500;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .badge{{font-size:.65rem;padding:2px 6px;border-radius:99px;white-space:nowrap;flex-shrink:0}}
    .badge-ok{{background:rgba(34,197,94,.15);color:var(--green)}}
    .badge-alert-b{{background:rgba(239,68,68,.2);color:var(--red)}}
    .badge-alert-g{{background:rgba(249,115,22,.2);color:var(--orange)}}
    .badge-nodata{{background:rgba(136,146,164,.12);color:var(--muted)}}

    /* CONTENT */
    .content{{flex:1;overflow-y:auto;padding:20px;display:none}}
    .content.active{{display:block}}

    /* MAP */
    .map-panel{{flex:1;display:flex;flex-direction:column;background:var(--bg)}}
    .map-panel.hidden{{display:none}}
    .map-title{{padding:14px 20px;font-size:.85rem;color:var(--muted);font-weight:600;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px}}
    .map-legend{{display:flex;gap:14px;font-size:.75rem}}
    .legend-dot{{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:4px;vertical-align:middle}}
    .map-container{{flex:1;position:relative;overflow:hidden}}
    .map-svg{{width:100%;height:100%}}
    .volcano-dot{{cursor:pointer;transition:r .15s}}
    .volcano-dot:hover{{opacity:.85}}
    .dot-label{{font-size:11px;fill:#e2e8f0;pointer-events:none}}

    /* DETAIL PANEL */
    .panel-header{{margin-bottom:16px;display:flex;align-items:flex-start;justify-content:space-between}}
    .panel-header h2{{font-size:1.3rem;font-weight:700}}
    .panel-header .meta{{color:var(--muted);font-size:.8rem;margin-top:4px}}
    .back-btn{{background:var(--card);border:1px solid var(--border);color:var(--text);padding:6px 14px;border-radius:6px;cursor:pointer;font-size:.82rem}}
    .back-btn:hover{{background:var(--border)}}
    .cards-row{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}}
    .metric-card{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:12px 16px;min-width:120px}}
    .metric-card .label{{color:var(--muted);font-size:.72rem;margin-bottom:3px}}
    .metric-card .value{{font-size:1.4rem;font-weight:700}}
    .metric-card .trend{{font-size:.75rem;margin-top:2px}}
    .chart-card{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;margin-bottom:16px}}
    .chart-card h3{{font-size:.85rem;color:var(--muted);margin-bottom:12px;font-weight:600}}
    .anomaly-table{{width:100%;border-collapse:collapse;font-size:.83rem}}
    .anomaly-table th{{text-align:left;padding:7px 10px;color:var(--muted);font-weight:600;border-bottom:1px solid var(--border)}}
    .anomaly-table td{{padding:7px 10px;border-bottom:1px solid rgba(255,255,255,.04)}}
    .tag-browning{{color:var(--red);font-weight:600}}
    .tag-greening{{color:var(--orange);font-weight:600}}
    .interp-box{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px;margin-bottom:16px;font-size:.84rem;line-height:1.6}}
    .interp-box .interp-title{{font-weight:700;margin-bottom:6px;font-size:.9rem}}
    canvas{{max-height:260px}}
  </style>
</head>
<body>
<header>
  <div>
    <h1>VegStress-v1</h1>
    <div class="subtitle">Monitoreo NDVI Sentinel-2 — Precursores Vegetacionales Volcanicos Chile</div>
  </div>
  <div class="updated">Actualizado: {generated_at}</div>
</header>
<div class="summary-bar">
  <div class="stat-chip"><div class="value green">{n_volcanes}</div><div class="label">Volcanes con datos</div></div>
  <div class="stat-chip"><div class="value {alert_color}">{n_anomalies}</div><div class="label">Anomalias (+/-2s)</div></div>
  <div class="stat-chip"><div style="display:flex;gap:8px;align-items:center">
    <span style="font-size:1.1rem">&#x1F7E2;</span><div class="label">GREENING<br><span style="color:var(--muted);font-size:.7rem">aumento CO2/lluvia</span></div>
    <span style="font-size:1.1rem;margin-left:8px">&#x1F534;</span><div class="label">BROWNING<br><span style="color:var(--muted);font-size:.7rem">estres SO2/calor</span></div>
  </div></div>
</div>
<div class="main">
  <div class="sidebar" id="sidebar"></div>

  <!-- Mapa principal -->
  <div class="map-panel" id="mapPanel">
    <div class="map-title">
      Mapa de estado NDVI — Haz clic en un volcan para ver la serie temporal
      <div class="map-legend">
        <span><span class="legend-dot" style="background:#22c55e"></span>Normal</span>
        <span><span class="legend-dot" style="background:#f97316"></span>GREENING</span>
        <span><span class="legend-dot" style="background:#ef4444"></span>BROWNING</span>
        <span><span class="legend-dot" style="background:#4b5563"></span>Sin datos</span>
      </div>
    </div>
    <div class="map-container" id="mapContainer">
      <svg id="mapSvg" class="map-svg" viewBox="0 0 400 700" preserveAspectRatio="xMidYMid meet"></svg>
    </div>
  </div>

  <!-- Panel detalle volcan -->
  <div class="content" id="detailContent"></div>
</div>

<script>
const DATA = {data_json};
const charts = {{}};

function ndviColor(v, anomalies) {{
  if (v === null || v === undefined) return '#4b5563';
  if (anomalies && anomalies.length > 0) {{
    const last = anomalies[anomalies.length - 1];
    if (last.tipo === 'BROWNING') return '#ef4444';
    if (last.tipo === 'GREENING') return '#f97316';
  }}
  if (v < 0.0) return '#ef4444';
  if (v < 0.15) return '#eab308';
  if (v < 0.3) return '#84cc16';
  return '#22c55e';
}}

function trendText(t) {{
  if (!t && t !== 0) return '';
  if (Math.abs(t) < 0.01) return '= estable';
  return t > 0 ? '+ subiendo' : '- bajando';
}}
function trendColor(t) {{
  if (!t && t !== 0) return 'var(--muted)';
  if (Math.abs(t) < 0.01) return 'var(--muted)';
  return t > 0 ? 'var(--green)' : 'var(--red)';
}}

// ---- SIDEBAR ----
function buildSidebar() {{
  const sidebar = document.getElementById('sidebar');
  const zones = {{}};
  for (const [name, d] of Object.entries(DATA)) {{
    if (!zones[d.zona]) zones[d.zona] = [];
    zones[d.zona].push([name, d]);
  }}
  for (const [zona, volcanes] of Object.entries(zones)) {{
    const sec = document.createElement('div');
    sec.className = 'sidebar-section';
    sec.textContent = zona;
    sidebar.appendChild(sec);
    for (const [name, d] of volcanes) {{
      const s = d.stats;
      const anomalies = s ? s.anomalies : [];
      const hasAnomB = anomalies.some(a => a.tipo === 'BROWNING');
      const hasAnomG = anomalies.some(a => a.tipo === 'GREENING');
      const item = document.createElement('div');
      item.className = 'volcano-item';
      item.id = 'item-' + name.replace(/ /g,'_');
      item.addEventListener('click', () => showDetail(name));
      const nameEl = document.createElement('span');
      nameEl.className = 'vname';
      nameEl.textContent = name;
      const badge = document.createElement('span');
      if (hasAnomB) {{ badge.className = 'badge badge-alert-b'; badge.textContent = 'BROWNING'; }}
      else if (hasAnomG) {{ badge.className = 'badge badge-alert-g'; badge.textContent = 'GREENING'; }}
      else if (d.has_data && s) {{ badge.className = 'badge badge-ok'; badge.textContent = 'OK'; }}
      else {{ badge.className = 'badge badge-nodata'; badge.textContent = 'Sin datos'; }}
      item.appendChild(nameEl);
      item.appendChild(badge);
      sidebar.appendChild(item);
    }}
  }}
}}

// ---- MAPA SVG ----
function buildMap() {{
  const svg = document.getElementById('mapSvg');
  const W = 400, H = 700;

  // Fondo
  const bg = document.createElementNS('http://www.w3.org/2000/svg','rect');
  bg.setAttribute('width', W); bg.setAttribute('height', H);
  bg.setAttribute('fill', '#0f1117');
  svg.appendChild(bg);

  // Linea de cordillera (referencia visual)
  const line = document.createElementNS('http://www.w3.org/2000/svg','line');
  line.setAttribute('x1', 200); line.setAttribute('y1', 0);
  line.setAttribute('x2', 200); line.setAttribute('y2', H);
  line.setAttribute('stroke', '#1e2535'); line.setAttribute('stroke-width', '1');
  svg.appendChild(line);

  // Latitudes de referencia
  for (let lat = -20; lat >= -45; lat -= 5) {{
    const y = latY(lat, H);
    const g = document.createElementNS('http://www.w3.org/2000/svg','text');
    g.setAttribute('x', 8); g.setAttribute('y', y + 4);
    g.setAttribute('fill', '#2a3040'); g.setAttribute('font-size', '10');
    g.textContent = lat + '\u00b0S';
    svg.appendChild(g);
    const gl = document.createElementNS('http://www.w3.org/2000/svg','line');
    gl.setAttribute('x1', 30); gl.setAttribute('y1', y);
    gl.setAttribute('x2', W); gl.setAttribute('y2', y);
    gl.setAttribute('stroke', '#1a1f2e'); gl.setAttribute('stroke-width', '1');
    svg.appendChild(gl);
  }}

  // Puntos de volcanes
  for (const [name, d] of Object.entries(DATA)) {{
    const s = d.stats;
    const anomalies = s ? s.anomalies : [];
    const color = ndviColor(s ? s.last_ndvi : null, anomalies);
    const x = lonX(d.lon, W);
    const y = latY(d.lat, H);

    // Halo si hay anomalia
    if (anomalies.length > 0) {{
      const halo = document.createElementNS('http://www.w3.org/2000/svg','circle');
      halo.setAttribute('cx', x); halo.setAttribute('cy', y); halo.setAttribute('r', 16);
      halo.setAttribute('fill', color); halo.setAttribute('opacity', '0.15');
      svg.appendChild(halo);
    }}

    const circle = document.createElementNS('http://www.w3.org/2000/svg','circle');
    circle.setAttribute('cx', x); circle.setAttribute('cy', y);
    circle.setAttribute('r', d.has_data && s ? 9 : 6);
    circle.setAttribute('fill', color);
    circle.setAttribute('stroke', '#0f1117'); circle.setAttribute('stroke-width', '2');
    circle.setAttribute('class', 'volcano-dot');
    circle.addEventListener('click', () => showDetail(name));

    const title = document.createElementNS('http://www.w3.org/2000/svg','title');
    title.textContent = name + (s ? ' — NDVI: ' + (s.last_ndvi || '--') : ' — Sin datos');
    circle.appendChild(title);
    svg.appendChild(circle);

    // Etiqueta
    const label = document.createElementNS('http://www.w3.org/2000/svg','text');
    label.setAttribute('x', x + 12); label.setAttribute('y', y + 4);
    label.setAttribute('fill', '#8892a4'); label.setAttribute('font-size', '10');
    label.setAttribute('class', 'dot-label');
    label.textContent = name.length > 14 ? name.slice(0,13) + '.' : name;
    svg.appendChild(label);
  }}
}}

function latY(lat, H) {{
  const LAT_N = -18, LAT_S = -46;
  return Math.round((lat - LAT_N) / (LAT_S - LAT_N) * H);
}}
function lonX(lon, W) {{
  const LON_W = -74, LON_E = -66;
  return Math.round((lon - LON_W) / (LON_E - LON_W) * W);
}}

// ---- DETALLE ----
function showDetail(name) {{
  document.querySelectorAll('.volcano-item').forEach(el => el.classList.remove('active'));
  const itemEl = document.getElementById('item-' + name.replace(/ /g, '_'));
  if (itemEl) itemEl.classList.add('active');

  document.getElementById('mapPanel').classList.add('hidden');
  const content = document.getElementById('detailContent');
  content.classList.add('active');
  content.innerHTML = '';

  const d = DATA[name];
  const s = d.stats;
  const anomalies = s ? s.anomalies : [];
  const lastNdvi = s ? s.last_ndvi : null;
  const lastFecha = s ? s.last_fecha : 'Sin datos';

  // Back button
  const backBtn = document.createElement('button');
  backBtn.className = 'back-btn';
  backBtn.textContent = 'Volver al mapa';
  backBtn.addEventListener('click', showMap);

  // Header
  const headerDiv = document.createElement('div');
  headerDiv.className = 'panel-header';
  const leftDiv = document.createElement('div');
  const h2 = document.createElement('h2');
  h2.textContent = name;
  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.textContent = 'Zona ' + d.zona + ' \u00b7 ' + d.lat.toFixed(2) + '\u00b0S, ' + Math.abs(d.lon).toFixed(2) + '\u00b0O \u00b7 Ultima imagen valida: ' + lastFecha;
  leftDiv.appendChild(h2);
  leftDiv.appendChild(meta);
  headerDiv.appendChild(leftDiv);
  headerDiv.appendChild(backBtn);
  content.appendChild(headerDiv);

  if (!d.has_data || !s) {{
    const msg = document.createElement('div');
    msg.style.cssText = 'color:var(--muted);text-align:center;padding:60px;font-size:.95rem';
    msg.textContent = 'Sin datos disponibles. Ejecuta ndvi_analyzer.py para este volcan.';
    content.appendChild(msg);
    return;
  }}

  // Interpretacion automatica
  const interpDiv = document.createElement('div');
  interpDiv.className = 'interp-box';
  const interpTitle = document.createElement('div');
  interpTitle.className = 'interp-title';
  interpTitle.textContent = 'Interpretacion';
  const interpText = document.createElement('div');
  let interp = '';
  const nAnom = anomalies.length;
  const browning = anomalies.filter(a => a.tipo === 'BROWNING');
  const greening = anomalies.filter(a => a.tipo === 'GREENING');
  if (nAnom === 0) {{
    interp = 'Sin anomalias detectadas. NDVI dentro del rango normal (+/-2 desviaciones del promedio historico).';
  }} else if (greening.length > 0 && browning.length === 0) {{
    interp = 'GREENING detectado en ' + greening.length + ' fecha(s): aumento de biomasa vegetal sobre el promedio historico. '
      + 'Posibles causas: efecto fertilizacion por CO2/SO2 en bajas concentraciones, mayor precipitacion, o recuperacion post-evento.';
  }} else if (browning.length > 0 && greening.length === 0) {{
    interp = 'BROWNING detectado en ' + browning.length + ' fecha(s): reduccion de biomasa vegetal bajo el promedio historico. '
      + 'Posibles causas: estres por SO2, calentamiento de suelo, acidificacion, o sequia local.';
  }} else {{
    interp = 'Anomalias mixtas: ' + greening.length + ' evento(s) GREENING y ' + browning.length + ' evento(s) BROWNING. '
      + 'Requiere analisis temporal detallado.';
  }}
  interpText.textContent = interp;
  interpDiv.appendChild(interpTitle);
  interpDiv.appendChild(interpText);
  content.appendChild(interpDiv);

  // Metricas
  const cardsRow = document.createElement('div');
  cardsRow.className = 'cards-row';
  const metrics = [
    ['NDVI actual', lastNdvi !== null ? lastNdvi.toFixed(3) : '--', ndviColor(lastNdvi, anomalies), ''],
    ['Promedio historico', s.mean.toFixed(3), 'var(--text)', ''],
    ['Desv. estandar', s.std.toFixed(3), 'var(--text)', ''],
    ['Tendencia reciente', s.trend !== undefined ? (s.trend > 0 ? '+' : '') + s.trend.toFixed(3) : '--', trendColor(s.trend), trendText(s.trend)],
    ['Imagenes validas', s.n_valid + '/' + s.n_total, 'var(--blue)', ''],
    ['Anomalias', String(nAnom), nAnom > 0 ? 'var(--red)' : 'var(--green)', ''],
  ];
  for (const [label, value, color, sub] of metrics) {{
    const card = document.createElement('div');
    card.className = 'metric-card';
    const lbl = document.createElement('div');
    lbl.className = 'label';
    lbl.textContent = label;
    const val = document.createElement('div');
    val.className = 'value';
    val.style.color = color;
    val.textContent = value;
    card.appendChild(lbl);
    card.appendChild(val);
    if (sub) {{
      const s2 = document.createElement('div');
      s2.className = 'trend';
      s2.style.color = color;
      s2.textContent = sub;
      card.appendChild(s2);
    }}
    cardsRow.appendChild(card);
  }}
  content.appendChild(cardsRow);

  // Grafico
  const chartCard = document.createElement('div');
  chartCard.className = 'chart-card';
  const chartTitle = document.createElement('h3');
  chartTitle.textContent = 'Serie temporal NDVI (pixeles validos, filtrado nubes/nieve)';
  chartCard.appendChild(chartTitle);
  const canvas = document.createElement('canvas');
  canvas.id = 'chart-' + name.replace(/ /g, '_');
  chartCard.appendChild(canvas);
  content.appendChild(chartCard);

  // Tabla anomalias
  const anomalyCard = document.createElement('div');
  anomalyCard.className = 'chart-card';
  const anomalyTitle = document.createElement('h3');
  anomalyTitle.textContent = 'Anomalias detectadas (umbral +/-2 desviaciones estandar)';
  anomalyCard.appendChild(anomalyTitle);
  const table = document.createElement('table');
  table.className = 'anomaly-table';
  const thead = document.createElement('thead');
  const hrow = document.createElement('tr');
  for (const h of ['Fecha','NDVI','Z-score','Tipo','Interpretacion']) {{
    const th = document.createElement('th'); th.textContent = h; hrow.appendChild(th);
  }}
  thead.appendChild(hrow);
  table.appendChild(thead);
  const tbody = document.createElement('tbody');
  if (anomalies.length === 0) {{
    const row = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 5; td.style.color = 'var(--muted)'; td.style.padding = '12px';
    td.textContent = 'Sin anomalias detectadas en el periodo analizado.';
    row.appendChild(td); tbody.appendChild(row);
  }} else {{
    for (const a of anomalies) {{
      const row = document.createElement('tr');
      const interp2 = a.tipo === 'BROWNING'
        ? 'Posible estres: SO2, calor de suelo, acidificacion'
        : 'Posible greening: CO2, lluvia, recuperacion';
      const cells = [a.fecha, a.ndvi.toFixed(3), (a.z > 0?'+':'') + a.z.toFixed(1), a.tipo, interp2];
      for (let i = 0; i < cells.length; i++) {{
        const td = document.createElement('td');
        td.textContent = cells[i];
        if (i === 3) td.className = 'tag-' + a.tipo.toLowerCase();
        row.appendChild(td);
      }}
      tbody.appendChild(row);
    }}
  }}
  table.appendChild(tbody);
  anomalyCard.appendChild(table);
  content.appendChild(anomalyCard);

  renderChart(name, d, s);
}}

function showMap() {{
  document.querySelectorAll('.volcano-item').forEach(el => el.classList.remove('active'));
  document.getElementById('mapPanel').classList.remove('hidden');
  document.getElementById('detailContent').classList.remove('active');
}}

function renderChart(name, d, s) {{
  if (!d.chart || d.chart.labels.length === 0) return;
  const ctx = document.getElementById('chart-' + name.replace(/ /g, '_'));
  if (!ctx) return;
  const mean = s ? s.mean : null;
  const std = s ? s.std : 0;
  if (charts[name]) charts[name].destroy();

  // Marcar anomalias en el grafico
  const pointColors = d.chart.ndvi.map((v, i) => {{
    const label = d.chart.labels[i];
    const anom = s && s.anomalies.find(a => a.fecha === label);
    if (anom) return anom.tipo === 'BROWNING' ? '#ef4444' : '#f97316';
    return '#3b82f6';
  }});
  const pointSizes = d.chart.ndvi.map((v, i) => {{
    const label = d.chart.labels[i];
    const anom = s && s.anomalies.find(a => a.fecha === label);
    return anom ? 8 : 4;
  }});

  charts[name] = new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: d.chart.labels,
      datasets: [
        {{
          label: 'NDVI medio',
          data: d.chart.ndvi,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59,130,246,0.07)',
          pointBackgroundColor: pointColors,
          pointRadius: pointSizes,
          pointHoverRadius: 7,
          tension: 0.3,
          fill: true,
        }},
        ...(mean !== null ? [
          {{ label: 'Promedio (' + mean.toFixed(3) + ')', data: d.chart.labels.map(()=>mean), borderColor:'rgba(34,197,94,0.5)', borderDash:[6,3], pointRadius:0, fill:false }},
          {{ label: '+2s (' + (mean+2*std).toFixed(3) + ')', data: d.chart.labels.map(()=>mean+2*std), borderColor:'rgba(239,68,68,0.4)', borderDash:[3,3], pointRadius:0, fill:false }},
          {{ label: '-2s (' + (mean-2*std).toFixed(3) + ')', data: d.chart.labels.map(()=>mean-2*std), borderColor:'rgba(239,68,68,0.4)', borderDash:[3,3], pointRadius:0, fill:false }},
        ] : []),
      ],
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ labels: {{ color:'#8892a4', boxWidth:12, font:{{size:10}} }} }},
        tooltip: {{ backgroundColor:'#1a1d26', borderColor:'#2a2d3a', borderWidth:1,
          callbacks: {{
            afterLabel: function(ctx) {{
              const label = ctx.label;
              const anom = s && s.anomalies.find(a => a.fecha === label);
              return anom ? '\u26a0 ' + anom.tipo + ' (z=' + anom.z + ')' : '';
            }}
          }}
        }},
      }},
      scales: {{
        x: {{ ticks:{{color:'#8892a4',maxTicksLimit:8}}, grid:{{color:'rgba(255,255,255,0.04)'}} }},
        y: {{ ticks:{{color:'#8892a4'}}, grid:{{color:'rgba(255,255,255,0.04)'}}, min:-0.3, max:0.9 }},
      }},
    }},
  }});
}}

buildSidebar();
buildMap();
</script>
</body>
</html>"""

    out_path = DOCS_DIR / "index.html"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Dashboard generado: {out_path}")
    print(f"  Volcanes con datos: {n_volcanes}")
    print(f"  Anomalias: {n_anomalies}")


if __name__ == '__main__':
    generate_dashboard()
