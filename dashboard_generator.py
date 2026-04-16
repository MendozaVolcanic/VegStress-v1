"""
Dashboard Generator — VegStress-v1
Genera docs/index.html con mapa de Chile, series temporales,
mapas NDVI espaciales y deteccion de cambios.
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
DOCS_DIR  = Path(__file__).parent / "docs"

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

MAP_LAT_N, MAP_LAT_S = -18.0, -46.0
MAP_LON_W, MAP_LON_E = -74.0, -66.0
ANOMALY_THRESHOLD = 2.0


def load_csv(name):
    p = DATOS_DIR / name.replace(" ", "_") / "ndvi_timeseries.csv"
    if not p.exists():
        return []
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def compute_stats(rows):
    ok = [r for r in rows if r.get('status') == 'OK' and r.get('ndvi_mean')]
    if len(ok) < 3:
        return None
    vals  = [float(r['ndvi_mean']) for r in ok]
    mean  = sum(vals) / len(vals)
    std   = (sum((v - mean)**2 for v in vals) / len(vals))**0.5
    recent = [float(r['ndvi_mean']) for r in ok[-3:]]
    trend  = sum(recent)/len(recent) - mean if recent else 0
    anomalies = []
    for r in ok:
        v = float(r['ndvi_mean'])
        z = (v - mean) / (std + 1e-6)
        if abs(z) > ANOMALY_THRESHOLD:
            anomalies.append({"fecha": r['fecha'], "ndvi": round(v,4),
                               "z": round(z,2), "tipo": "BROWNING" if z<0 else "GREENING"})
    return {"mean": round(mean,4), "std": round(std,4), "trend": round(trend,4),
            "n_valid": len(ok), "n_total": len(rows),
            "last_ndvi": round(float(ok[-1]['ndvi_mean']),4) if ok else None,
            "last_fecha": ok[-1]['fecha'] if ok else None,
            "anomalies": anomalies}


def build_chart_data(rows):
    ok = [r for r in rows if r.get('status') == 'OK' and r.get('ndvi_mean')]
    return {"labels": [r['fecha'] for r in ok],
            "ndvi":   [round(float(r['ndvi_mean']),4) for r in ok]}


def load_alerts():
    p = DOCS_DIR / "alerts_summary.json"
    if not p.exists():
        return {"active_alerts": []}
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def load_aoi_config():
    p = DATOS_DIR / "aoi_config.json"
    if not p.exists():
        return {}
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def check_maps(name):
    slug = name.replace(" ", "_")
    spatial = (DOCS_DIR / "maps" / f"{slug}_spatial_latest.png").exists()
    delta   = (DOCS_DIR / "maps" / f"{slug}_delta_latest.png").exists()
    return {"spatial": spatial, "delta": delta,
            "spatial_url": f"maps/{slug}_spatial_latest.png" if spatial else None,
            "delta_url":   f"maps/{slug}_delta_latest.png"   if delta   else None}


def load_change_history(name):
    p = DATOS_DIR / name.replace(" ", "_") / "change_history.csv"
    if not p.exists():
        return []
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def generate_dashboard():
    DOCS_DIR.mkdir(exist_ok=True)

    alerts_data = load_alerts()
    aoi_config  = load_aoi_config()
    active_alerts = alerts_data.get("active_alerts", [])

    volcanes_data = {}
    for nombre in VOLCANES_INFO:
        rows  = load_csv(nombre)
        info  = VOLCANES_INFO[nombre]
        stats = compute_stats(rows) if rows else None
        chart = build_chart_data(rows) if rows else {"labels": [], "ndvi": []}
        maps  = check_maps(nombre)
        aois  = aoi_config.get("volcanes", {}).get(nombre, {}).get("aois", [])
        hist  = load_change_history(nombre)
        # alertas de AOIs para este volcan
        valertas = [a for a in active_alerts if a['volcan'] == nombre]

        volcanes_data[nombre] = {
            "zona": info["zona"], "lat": info["lat"], "lon": info["lon"],
            "has_data": bool(rows),
            "stats": stats, "chart": chart,
            "maps": maps, "aois": aois,
            "change_history": hist[-20:],   # ultimas 20 entradas
            "alerts": valertas,
        }

    data_json    = json.dumps(volcanes_data, ensure_ascii=False)
    alerts_json  = json.dumps(active_alerts, ensure_ascii=False)
    umbrales     = aoi_config.get("umbrales_globales", {})
    umbrales_json = json.dumps(umbrales, ensure_ascii=False)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    n_volcanes   = sum(1 for v in volcanes_data.values() if v["has_data"])
    n_alerts     = len(active_alerts)
    alert_color  = "red" if n_alerts > 0 else "green"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VegStress-v1 | Monitoreo NDVI Volcanico Chile</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    :root {{
      --bg:#0f1117;--card:#1a1d26;--border:#2a2d3a;
      --text:#e2e8f0;--muted:#8892a4;
      --green:#22c55e;--yellow:#eab308;--red:#ef4444;
      --orange:#f97316;--blue:#3b82f6;
    }}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;font-size:14px;height:100vh;display:flex;flex-direction:column}}
    header{{background:var(--card);border-bottom:1px solid var(--border);padding:11px 22px;display:flex;align-items:center;gap:14px;flex-shrink:0}}
    header h1{{font-size:1.15rem;font-weight:700;color:var(--green)}}
    header .subtitle{{color:var(--muted);font-size:.8rem}}
    header .updated{{margin-left:auto;color:var(--muted);font-size:.76rem}}
    .summary-bar{{display:flex;gap:10px;padding:9px 22px;background:var(--card);border-bottom:1px solid var(--border);flex-wrap:wrap;flex-shrink:0;align-items:center}}
    .stat-chip{{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:7px 14px;display:flex;align-items:center;gap:8px}}
    .stat-chip .value{{font-size:1.3rem;font-weight:700}}
    .stat-chip .label{{color:var(--muted);font-size:.7rem;line-height:1.3}}
    .green{{color:var(--green)}}.red{{color:var(--red)}}.yellow{{color:var(--yellow)}}.blue{{color:var(--blue)}}.orange{{color:var(--orange)}}
    /* Barra de alertas activas */
    .alert-bar{{display:none;padding:8px 22px;background:rgba(239,68,68,.12);border-bottom:1px solid rgba(239,68,68,.3);flex-shrink:0;gap:10px;flex-wrap:wrap;align-items:center}}
    .alert-bar.visible{{display:flex}}
    .alert-bar .alert-label{{font-weight:700;font-size:.82rem;color:var(--red)}}
    .alert-chip{{background:rgba(239,68,68,.15);border:1px solid rgba(239,68,68,.3);border-radius:6px;padding:3px 10px;font-size:.78rem;cursor:pointer}}
    .alert-chip:hover{{background:rgba(239,68,68,.25)}}
    .alert-chip.warning{{background:rgba(249,115,22,.15);border-color:rgba(249,115,22,.3);color:var(--orange)}}
    .alert-chip.watch{{background:rgba(234,179,8,.12);border-color:rgba(234,179,8,.3);color:var(--yellow)}}
    .alert-chip.critical{{color:var(--red)}}
    /* Layout */
    .main{{display:flex;flex:1;min-height:0}}
    .sidebar{{width:215px;min-width:180px;background:var(--card);border-right:1px solid var(--border);overflow-y:auto;flex-shrink:0}}
    .sidebar-section{{padding:9px 13px 3px;color:var(--muted);font-size:.67rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}}
    .volcano-item{{padding:8px 13px;cursor:pointer;border-left:3px solid transparent;display:flex;justify-content:space-between;align-items:center;gap:5px}}
    .volcano-item:hover{{background:rgba(255,255,255,.04)}}
    .volcano-item.active{{border-left-color:var(--green);background:rgba(34,197,94,.06)}}
    .vname{{font-size:.83rem;font-weight:500;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
    .badge{{font-size:.63rem;padding:2px 6px;border-radius:99px;white-space:nowrap;flex-shrink:0}}
    .badge-ok{{background:rgba(34,197,94,.15);color:var(--green)}}
    .badge-alert-b{{background:rgba(239,68,68,.2);color:var(--red)}}
    .badge-alert-g{{background:rgba(59,130,246,.2);color:var(--blue)}}
    .badge-warn{{background:rgba(249,115,22,.2);color:var(--orange)}}
    .badge-nodata{{background:rgba(136,146,164,.12);color:var(--muted)}}
    /* Mapa Chile */
    .map-panel{{flex:1;display:flex;flex-direction:column}}
    .map-panel.hidden{{display:none}}
    .map-title{{padding:12px 18px;font-size:.83rem;color:var(--muted);font-weight:600;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;flex-shrink:0}}
    .map-legend{{display:flex;gap:12px;font-size:.73rem}}
    .legend-dot{{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:3px;vertical-align:middle}}
    .map-container{{flex:1;overflow:hidden}}
    .map-svg{{width:100%;height:100%}}
    .volcano-dot{{cursor:pointer}}
    /* Panel detalle */
    .content{{flex:1;overflow-y:auto;padding:0;display:none;flex-direction:column}}
    .content.active{{display:flex}}
    /* Tabs */
    .tabs-bar{{display:flex;gap:2px;padding:12px 20px 0;background:var(--card);border-bottom:1px solid var(--border);flex-shrink:0}}
    .tab-btn{{padding:7px 16px;border:none;background:transparent;color:var(--muted);font-size:.83rem;cursor:pointer;border-bottom:2px solid transparent;font-family:inherit;transition:color .15s}}
    .tab-btn:hover{{color:var(--text)}}
    .tab-btn.active{{color:var(--green);border-bottom-color:var(--green)}}
    .tab-btn .tab-badge{{display:inline-block;background:rgba(239,68,68,.2);color:var(--red);font-size:.6rem;padding:1px 5px;border-radius:99px;margin-left:5px;vertical-align:middle}}
    .tab-pane{{display:none;flex:1;overflow-y:auto;padding:18px 20px}}
    .tab-pane.active{{display:block}}
    /* Detail content */
    .panel-top{{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px}}
    .panel-top h2{{font-size:1.2rem;font-weight:700}}
    .panel-top .meta{{color:var(--muted);font-size:.78rem;margin-top:3px}}
    .back-btn{{background:var(--card);border:1px solid var(--border);color:var(--text);padding:5px 12px;border-radius:6px;cursor:pointer;font-size:.8rem;flex-shrink:0}}
    .back-btn:hover{{background:var(--border)}}
    .cards-row{{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:14px}}
    .metric-card{{background:var(--card);border:1px solid var(--border);border-radius:9px;padding:11px 15px;min-width:115px}}
    .metric-card .mlabel{{color:var(--muted);font-size:.7rem;margin-bottom:2px}}
    .metric-card .mvalue{{font-size:1.35rem;font-weight:700}}
    .metric-card .msub{{font-size:.72rem;margin-top:1px}}
    .chart-card{{background:var(--card);border:1px solid var(--border);border-radius:9px;padding:14px;margin-bottom:14px}}
    .chart-card h3{{font-size:.83rem;color:var(--muted);margin-bottom:10px;font-weight:600}}
    .interp-box{{background:var(--card);border:1px solid var(--border);border-radius:9px;padding:12px 15px;margin-bottom:14px;font-size:.83rem;line-height:1.6}}
    .interp-box b{{color:var(--text)}}
    .anomaly-table,.aoi-table{{width:100%;border-collapse:collapse;font-size:.82rem}}
    .anomaly-table th,.aoi-table th{{text-align:left;padding:6px 9px;color:var(--muted);font-weight:600;border-bottom:1px solid var(--border)}}
    .anomaly-table td,.aoi-table td{{padding:6px 9px;border-bottom:1px solid rgba(255,255,255,.04)}}
    .tag-browning{{color:var(--red);font-weight:600}}
    .tag-greening{{color:var(--blue);font-weight:600}}
    canvas{{max-height:240px}}
    /* Mapas de imagen */
    .map-img-container{{background:var(--card);border:1px solid var(--border);border-radius:9px;overflow:hidden;margin-bottom:14px}}
    .map-img-container img{{width:100%;display:block}}
    .map-img-header{{padding:10px 14px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border)}}
    .map-img-header span{{font-size:.82rem;color:var(--muted);font-weight:600}}
    .map-img-header a{{font-size:.75rem;color:var(--blue);text-decoration:none}}
    .map-img-header a:hover{{text-decoration:underline}}
    .no-map{{padding:40px;text-align:center;color:var(--muted);font-size:.88rem;background:var(--card);border:1px solid var(--border);border-radius:9px;margin-bottom:14px}}
    /* Nivel alerta */
    .nivel-ok{{color:var(--green)}}.nivel-watch{{color:var(--yellow)}}.nivel-warning{{color:var(--orange)}}.nivel-critical{{color:var(--red)}}
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
  <div class="stat-chip"><div class="value green">{n_volcanes}</div><div class="label">Volcanes<br>con datos</div></div>
  <div class="stat-chip"><div class="value {alert_color}">{n_alerts}</div><div class="label">Alertas<br>activas</div></div>
  <div class="stat-chip" style="gap:14px">
    <div style="font-size:.75rem;color:var(--muted)">
      <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#3b82f6;margin-right:4px;vertical-align:middle"></span>GREENING — posible CO2/lluvia<br>
      <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#ef4444;margin-right:4px;vertical-align:middle"></span>BROWNING — posible SO2/calor
    </div>
  </div>
</div>
<div class="alert-bar" id="alertBar"></div>
<div class="main">
  <div class="sidebar" id="sidebar"></div>
  <div class="map-panel" id="mapPanel">
    <div class="map-title">
      Estado NDVI por volcan — Clic para detalle
      <div class="map-legend">
        <span><span class="legend-dot" style="background:#22c55e"></span>Normal</span>
        <span><span class="legend-dot" style="background:#3b82f6"></span>GREENING</span>
        <span><span class="legend-dot" style="background:#ef4444"></span>BROWNING</span>
        <span><span class="legend-dot" style="background:#f97316"></span>ALERTA AOI</span>
        <span><span class="legend-dot" style="background:#374151"></span>Sin datos</span>
      </div>
    </div>
    <div class="map-container"><svg id="mapSvg" class="map-svg" viewBox="0 0 400 700" preserveAspectRatio="xMidYMid meet"></svg></div>
  </div>
  <div class="content" id="detailContent"></div>
</div>

<script>
const DATA     = {data_json};
const ALERTS   = {alerts_json};
const UMBRALES = {umbrales_json};
const charts   = {{}};

// ── Colores ──────────────────────────────────────────────────
function ndviColor(v, d) {{
  const alerts = d && d.alerts ? d.alerts : [];
  if (alerts.some(a=>a.tipo==='BROWNING')) return '#ef4444';
  if (alerts.some(a=>a.tipo==='GREENING')) return '#3b82f6';
  if (v===null||v===undefined) return '#374151';
  if (v<0.0) return '#ef4444';
  if (v<0.15) return '#eab308';
  if (v<0.3)  return '#84cc16';
  return '#22c55e';
}}
function nivelColor(n) {{
  return {{OK:'var(--green)',WATCH:'var(--yellow)',WARNING:'var(--orange)',CRITICAL:'var(--red)'}}[n]||'var(--muted)';
}}
function tipoColor(t) {{
  return {{GREENING:'var(--blue)',BROWNING:'var(--red)',NINGUNO:'var(--muted)'}}[t]||'var(--muted)';
}}
function trendLabel(t) {{
  if (!t&&t!==0) return '';
  if (Math.abs(t)<0.01) return '= estable';
  return t>0?'▲ subiendo':'▼ bajando';
}}
function trendCol(t) {{
  if (!t&&t!==0||Math.abs(t)<0.01) return 'var(--muted)';
  return t>0?'var(--red)':'var(--blue)';
}}

// ── Barra de alertas ─────────────────────────────────────────
function buildAlertBar() {{
  const bar = document.getElementById('alertBar');
  if (!ALERTS.length) return;
  bar.classList.add('visible');
  const lbl = document.createElement('span');
  lbl.className='alert-label';
  lbl.textContent = 'ALERTAS ACTIVAS:';
  bar.appendChild(lbl);
  ALERTS.forEach(a => {{
    const chip = document.createElement('span');
    chip.className = 'alert-chip ' + (a.nivel||'').toLowerCase();
    chip.textContent = a.volcan + ' — ' + a.aoi + ' ' + (a.delta_ndvi>=0?'+':'') + (a.delta_ndvi||0).toFixed(3) + ' (' + a.nivel + ')';
    chip.addEventListener('click', ()=>showDetail(a.volcan, 'cambios'));
    bar.appendChild(chip);
  }});
}}

// ── Sidebar ──────────────────────────────────────────────────
function buildSidebar() {{
  const sb = document.getElementById('sidebar');
  const zones = {{}};
  for (const [n,d] of Object.entries(DATA)) {{
    if (!zones[d.zona]) zones[d.zona]=[];
    zones[d.zona].push([n,d]);
  }}
  for (const [zona, list] of Object.entries(zones)) {{
    const sec=document.createElement('div'); sec.className='sidebar-section'; sec.textContent=zona; sb.appendChild(sec);
    for (const [name,d] of list) {{
      const alerts = d.alerts||[];
      const hasAnomB = (d.stats&&d.stats.anomalies||[]).some(a=>a.tipo==='BROWNING');
      const hasAnomG = (d.stats&&d.stats.anomalies||[]).some(a=>a.tipo==='GREENING');
      const maxAlertNivel = alerts.reduce((m,a)=>{{const o=['WATCH','WARNING','CRITICAL'];return o.indexOf(a.nivel)>o.indexOf(m)?a.nivel:m;}},'');
      const item=document.createElement('div'); item.className='volcano-item';
      item.id='item-'+name.replace(/ /g,'_');
      item.addEventListener('click',()=>showDetail(name));
      const ns=document.createElement('span'); ns.className='vname'; ns.textContent=name;
      const badge=document.createElement('span');
      if (maxAlertNivel==='CRITICAL') {{ badge.className='badge badge-alert-b'; badge.textContent='CRITICAL'; }}
      else if (maxAlertNivel==='WARNING') {{ badge.className='badge badge-warn'; badge.textContent='WARNING'; }}
      else if (maxAlertNivel==='WATCH')   {{ badge.className='badge badge-warn'; badge.textContent='WATCH'; }}
      else if (hasAnomB) {{ badge.className='badge badge-alert-b'; badge.textContent='BROWNING'; }}
      else if (hasAnomG) {{ badge.className='badge badge-alert-g'; badge.textContent='GREENING'; }}
      else if (d.has_data&&d.stats) {{ badge.className='badge badge-ok'; badge.textContent='OK'; }}
      else {{ badge.className='badge badge-nodata'; badge.textContent='Sin datos'; }}
      item.appendChild(ns); item.appendChild(badge); sb.appendChild(item);
    }}
  }}
}}

// ── Mapa SVG ─────────────────────────────────────────────────
function latY(lat,H){{return Math.round((lat-(-18))/((-46)-(-18))*H);}}
function lonX(lon,W){{return Math.round((lon-(-74))/((-66)-(-74))*W);}}

function buildMap() {{
  const svg=document.getElementById('mapSvg'); const W=400,H=700;
  const bg=document.createElementNS('http://www.w3.org/2000/svg','rect');
  bg.setAttribute('width',W); bg.setAttribute('height',H); bg.setAttribute('fill','#0f1117'); svg.appendChild(bg);
  for (let lat=-20;lat>=-45;lat-=5) {{
    const y=latY(lat,H);
    const gl=document.createElementNS('http://www.w3.org/2000/svg','line');
    gl.setAttribute('x1',30);gl.setAttribute('y1',y);gl.setAttribute('x2',W);gl.setAttribute('y2',y);
    gl.setAttribute('stroke','#1a1f2e');gl.setAttribute('stroke-width','1'); svg.appendChild(gl);
    const gt=document.createElementNS('http://www.w3.org/2000/svg','text');
    gt.setAttribute('x',5);gt.setAttribute('y',y+4);gt.setAttribute('fill','#2a3040');gt.setAttribute('font-size','10');
    gt.textContent=lat+'S'; svg.appendChild(gt);
  }}
  for (const [name,d] of Object.entries(DATA)) {{
    const s=d.stats; const x=lonX(d.lon,W); const y=latY(d.lat,H);
    const color=ndviColor(s?s.last_ndvi:null,d);
    const hasAlert=(d.alerts||[]).length>0;
    if (hasAlert) {{
      const halo=document.createElementNS('http://www.w3.org/2000/svg','circle');
      halo.setAttribute('cx',x);halo.setAttribute('cy',y);halo.setAttribute('r',18);
      halo.setAttribute('fill',color);halo.setAttribute('opacity','0.18'); svg.appendChild(halo);
    }}
    const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
    c.setAttribute('cx',x);c.setAttribute('cy',y);c.setAttribute('r',d.has_data&&s?9:6);
    c.setAttribute('fill',color);c.setAttribute('stroke','#0f1117');c.setAttribute('stroke-width','2');
    c.setAttribute('class','volcano-dot');
    const t=document.createElementNS('http://www.w3.org/2000/svg','title');
    t.textContent=name+(s?' — NDVI: '+(s.last_ndvi||'--'):' — Sin datos'); c.appendChild(t);
    c.addEventListener('click',()=>showDetail(name)); svg.appendChild(c);
    const lbl=document.createElementNS('http://www.w3.org/2000/svg','text');
    lbl.setAttribute('x',x+11);lbl.setAttribute('y',y+4);lbl.setAttribute('fill','#8892a4');lbl.setAttribute('font-size','10');
    lbl.textContent=name.length>14?name.slice(0,13)+'.':name; svg.appendChild(lbl);
  }}
}}

// ── Detalle volcan ────────────────────────────────────────────
function showDetail(name, defaultTab) {{
  document.querySelectorAll('.volcano-item').forEach(e=>e.classList.remove('active'));
  const el=document.getElementById('item-'+name.replace(/ /g,'_'));
  if (el) el.classList.add('active');
  document.getElementById('mapPanel').classList.add('hidden');
  const content=document.getElementById('detailContent');
  content.classList.add('active');
  content.innerHTML='';

  const d=DATA[name]; const s=d.stats;
  const alerts=d.alerts||[]; const aois=d.aois||[];
  const hasAlerts=alerts.length>0;
  const hasMaps=d.maps&&(d.maps.spatial||d.maps.delta);

  // ── Header + back ──
  const hdr=document.createElement('div'); hdr.style.cssText='padding:14px 20px 0;flex-shrink:0';
  const row=document.createElement('div'); row.className='panel-top';
  const left=document.createElement('div');
  const h2=document.createElement('h2'); h2.textContent=name;
  const meta=document.createElement('div'); meta.className='meta';
  meta.textContent='Zona '+d.zona+' \u00b7 '+d.lat.toFixed(2)+'\u00b0S, '+Math.abs(d.lon).toFixed(2)+'\u00b0O'+(s?' \u00b7 Ultima imagen: '+s.last_fecha:'');
  left.appendChild(h2); left.appendChild(meta);
  const backBtn=document.createElement('button'); backBtn.className='back-btn';
  backBtn.textContent='Volver al mapa'; backBtn.addEventListener('click',showMap);
  row.appendChild(left); row.appendChild(backBtn); hdr.appendChild(row);
  content.appendChild(hdr);

  // ── Tabs ──
  const tabsBar=document.createElement('div'); tabsBar.className='tabs-bar';
  const tabs=[['serie','Serie temporal'],['mapas','Mapas NDVI'],['cambios','Cambio '+String.fromCharCode(0x394)+'NDVI'+(hasAlerts?' \u26a0':'')],['aois','Zonas AOI'+(hasAlerts?' ('+alerts.length+')':'')]];
  tabs.forEach(([id,label])=>{{
    const btn=document.createElement('button'); btn.className='tab-btn'; btn.dataset.tab=id;
    btn.innerHTML=label+(id==='cambios'&&hasAlerts?'<span class="tab-badge">'+alerts.length+'</span>':'');
    btn.addEventListener('click',()=>activateTab(id));
    tabsBar.appendChild(btn);
  }});
  content.appendChild(tabsBar);

  // ── Panes ──
  const paneWrap=document.createElement('div'); paneWrap.style.cssText='flex:1;overflow:hidden;display:flex;flex-direction:column';

  // Pane 1: Serie temporal
  const p1=createPane('serie');
  if (!d.has_data||!s) {{
    const msg=document.createElement('div'); msg.style.cssText='color:var(--muted);text-align:center;padding:50px';
    msg.textContent='Sin datos. Ejecuta ndvi_analyzer.py para este volcan.'; p1.appendChild(msg);
  }} else {{
    // Interpretacion
    const ib=document.createElement('div'); ib.className='interp-box';
    const anomalies=s.anomalies||[];
    const nAnom=anomalies.length;
    const browning=anomalies.filter(a=>a.tipo==='BROWNING');
    const greening=anomalies.filter(a=>a.tipo==='GREENING');
    let interpText='';
    if (!nAnom) interpText='Sin anomalias en la serie temporal. NDVI dentro del rango normal ('+String.fromCharCode(0xB1)+'2'+String.fromCharCode(0x3C3)+').';
    else if (greening.length&&!browning.length) interpText='<b>GREENING</b> en '+greening.length+' fecha(s). Posible fertilizacion por CO2/SO2 o mayor precipitacion.';
    else if (browning.length&&!greening.length) interpText='<b>BROWNING</b> en '+browning.length+' fecha(s). Posible estres por SO2, calentamiento de suelo o acidificacion.';
    else interpText='Anomalias mixtas: '+greening.length+' GREENING + '+browning.length+' BROWNING. Requiere analisis detallado.';
    ib.innerHTML='<b>Interpretacion:</b> '+interpText; p1.appendChild(ib);
    // Metricas
    const cr=document.createElement('div'); cr.className='cards-row';
    [[s.last_ndvi!==null?s.last_ndvi.toFixed(3):'--','NDVI actual',ndviColor(s.last_ndvi,d),''],
     [s.mean.toFixed(3),'Promedio historico','var(--text)',''],
     [s.std.toFixed(3),'Desv. estandar','var(--text)',''],
     [s.trend!==undefined?(s.trend>0?'+':'')+s.trend.toFixed(3):'--','Tendencia reciente',trendCol(s.trend),trendLabel(s.trend)],
     [s.n_valid+'/'+s.n_total,'Imagenes validas','var(--blue)',''],
     [String(nAnom),'Anomalias serie',nAnom>0?'var(--red)':'var(--green)','']
    ].forEach(([v,l,c,sub])=>{{
      const mc=document.createElement('div'); mc.className='metric-card';
      const ml=document.createElement('div'); ml.className='mlabel'; ml.textContent=l;
      const mv=document.createElement('div'); mv.className='mvalue'; mv.style.color=c; mv.textContent=v;
      mc.appendChild(ml); mc.appendChild(mv);
      if (sub){{ const ms=document.createElement('div'); ms.className='msub'; ms.style.color=c; ms.textContent=sub; mc.appendChild(ms); }}
      cr.appendChild(mc);
    }}); p1.appendChild(cr);
    // Chart
    const cc=document.createElement('div'); cc.className='chart-card';
    const ch3=document.createElement('h3'); ch3.textContent='Serie temporal NDVI (pixeles validos, sin nubes/nieve)'; cc.appendChild(ch3);
    const canvas=document.createElement('canvas'); canvas.id='chart-'+name.replace(/ /g,'_'); cc.appendChild(canvas); p1.appendChild(cc);
    // Tabla anomalias serie
    const ac=document.createElement('div'); ac.className='chart-card';
    const ah3=document.createElement('h3'); ah3.textContent='Anomalias detectadas en serie temporal ('+String.fromCharCode(0xB1)+'2'+String.fromCharCode(0x3C3)+')'; ac.appendChild(ah3);
    buildAnomalyTable(anomalies, ac, 5); p1.appendChild(ac);
  }}
  paneWrap.appendChild(p1);

  // Pane 2: Mapas NDVI
  const p2=createPane('mapas');
  if (d.maps&&d.maps.spatial) {{
    const mc=document.createElement('div'); mc.className='map-img-container';
    const mh=document.createElement('div'); mh.className='map-img-header';
    const ms=document.createElement('span'); ms.textContent='Mapa NDVI espacial (ultima imagen disponible, ~10m/px)';
    const ml=document.createElement('a'); ml.href=d.maps.spatial_url; ml.target='_blank'; ml.textContent='Abrir';
    mh.appendChild(ms); mh.appendChild(ml); mc.appendChild(mh);
    const img=document.createElement('img'); img.src=d.maps.spatial_url; img.alt='Mapa NDVI '+name; mc.appendChild(img);
    p2.appendChild(mc);
  }} else {{
    const nm=document.createElement('div'); nm.className='no-map';
    nm.textContent='Mapa espacial no disponible. Ejecuta: python spatial_mapper.py --volcan "'+name+'"'; p2.appendChild(nm);
  }}
  paneWrap.appendChild(p2);

  // Pane 3: Cambio ΔNDVI
  const p3=createPane('cambios');
  if (hasAlerts) {{
    const ab=document.createElement('div'); ab.className='interp-box'; ab.style.borderColor='rgba(239,68,68,.4)';
    let atxt='<b style="color:var(--red)">ALERTAS ACTIVAS en zonas de interes:</b><br>';
    alerts.forEach(a=>{{
      atxt+='&bull; <b>'+a.aoi+'</b>: '+(a.delta_ndvi>=0?'+':'')+a.delta_ndvi.toFixed(3)+' NDVI ('+(a.tipo)+') — nivel '+a.nivel+'<br>';
    }}); ab.innerHTML=atxt; p3.appendChild(ab);
  }}
  if (d.maps&&d.maps.delta) {{
    const mc=document.createElement('div'); mc.className='map-img-container';
    const mh=document.createElement('div'); mh.className='map-img-header';
    const ms=document.createElement('span'); ms.textContent='Mapa de cambio '+String.fromCharCode(0x394)+'NDVI (azul=greening, rojo=browning)';
    const ml=document.createElement('a'); ml.href=d.maps.delta_url; ml.target='_blank'; ml.textContent='Abrir';
    mh.appendChild(ms); mh.appendChild(ml); mc.appendChild(mh);
    const img=document.createElement('img'); img.src=d.maps.delta_url; img.alt='Delta NDVI '+name; mc.appendChild(img);
    p3.appendChild(mc);
  }} else {{
    const nm=document.createElement('div'); nm.className='no-map';
    nm.textContent='Mapa de cambio no disponible. Ejecuta: python change_detector.py --volcan "'+name+'"'; p3.appendChild(nm);
  }}
  // Historial de comparaciones
  if (d.change_history&&d.change_history.length) {{
    const hc=document.createElement('div'); hc.className='chart-card';
    const hh=document.createElement('h3'); hh.textContent='Historial de cambios por AOI'; hc.appendChild(hh);
    const ht=document.createElement('table'); ht.className='aoi-table';
    const thead=document.createElement('thead'); const hrow=document.createElement('tr');
    ['Fecha A','Fecha B','Zona','ΔNDVI','Tipo','Nivel'].forEach(h=>{{ const th=document.createElement('th'); th.textContent=h; hrow.appendChild(th); }});
    thead.appendChild(hrow); ht.appendChild(thead);
    const tbody=document.createElement('tbody');
    [...d.change_history].reverse().forEach(r=>{{
      const row=document.createElement('tr');
      const nc=nivelColor(r.nivel); const tc=tipoColor(r.tipo);
      const dm=parseFloat(r.delta_mean);
      [r.fecha_a,r.fecha_b,r.aoi_id,
       isNaN(dm)?'N/D':(dm>=0?'+':'')+dm.toFixed(3),
       r.tipo||'--',r.nivel||'--'].forEach((v,i)=>{{
        const td=document.createElement('td'); td.textContent=v;
        if (i===3) td.style.color=nc;
        if (i===4) td.style.color=tc;
        if (i===5){{ td.style.color=nc; td.style.fontWeight='600'; }}
        row.appendChild(td);
      }}); tbody.appendChild(row);
    }}); ht.appendChild(tbody); hc.appendChild(ht); p3.appendChild(hc);
  }}
  paneWrap.appendChild(p3);

  // Pane 4: AOIs
  const p4=createPane('aois');
  if (!aois.length) {{
    const nm=document.createElement('div'); nm.className='no-map';
    nm.textContent='Sin zonas de interes configuradas. Edita datos/aoi_config.json para agregar AOIs.'; p4.appendChild(nm);
  }} else {{
    const intro=document.createElement('div'); intro.className='interp-box';
    intro.innerHTML='<b>Zonas de interes (AOIs)</b> configuradas para este volcan. '
      +'Las alertas se generan cuando el '+String.fromCharCode(0x394)+'NDVI supera los umbrales definidos en <code>datos/aoi_config.json</code>.';
    p4.appendChild(intro);
    const at=document.createElement('table'); at.className='aoi-table';
    const thead=document.createElement('thead'); const hrow=document.createElement('tr');
    ['Zona','Lat','Lon','Radio','Tipo esperado','Descripcion'].forEach(h=>{{ const th=document.createElement('th'); th.textContent=h; hrow.appendChild(th); }});
    thead.appendChild(hrow); at.appendChild(thead);
    const tbody=document.createElement('tbody');
    aois.forEach(aoi=>{{
      if (!aoi.activo) return;
      const row=document.createElement('tr');
      const alert=alerts.find(a=>a.aoi===aoi.nombre);
      const nc=alert?nivelColor(alert.nivel):'var(--muted)';
      [[aoi.nombre,'','bold'],[aoi.lat.toFixed(4)],[aoi.lon.toFixed(4)],[aoi.radio_m+'m'],
       [aoi.tipo_esperado||'--','','',(aoi.tipo_esperado==='GREENING'?'var(--blue)':aoi.tipo_esperado==='BROWNING'?'var(--red)':'var(--muted)')],
       [aoi.descripcion||'']
      ].forEach(([v,cls,fw,col])=>{{
        const td=document.createElement('td'); td.textContent=v||'';
        if (fw) td.style.fontWeight=fw;
        if (col) td.style.color=col;
        row.appendChild(td);
      }});
      if (alert) row.style.background='rgba(239,68,68,.05)';
      tbody.appendChild(row);
    }}); at.appendChild(tbody); p4.appendChild(at);
  }}
  paneWrap.appendChild(p4);
  content.appendChild(paneWrap);

  // Activar tab por defecto
  activateTab(defaultTab||(hasAlerts?'cambios':'serie'));

  // Renderizar chart si es visible
  if (!defaultTab||defaultTab==='serie') {{
    if (d.has_data&&d.stats) renderChart(name,d,s);
  }}
}}

function createPane(id) {{
  const p=document.createElement('div'); p.className='tab-pane'; p.id='pane-'+id; return p;
}}

function activateTab(id) {{
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab===id));
  document.querySelectorAll('.tab-pane').forEach(p=>p.classList.toggle('active',p.id==='pane-'+id));
  // Renderizar chart cuando se active su tab
  const activeContent=document.getElementById('detailContent');
  if (id==='serie'&&activeContent.classList.contains('active')) {{
    const canvas=activeContent.querySelector('canvas[id^="chart-"]');
    if (canvas) {{
      const name=canvas.id.replace('chart-','').replace(/_/g,' ');
      if (!charts[name]) {{
        const d=DATA[name]||DATA[Object.keys(DATA).find(k=>k.replace(/ /g,'_')===canvas.id.replace('chart-',''))];
        if (d&&d.stats) renderChart(canvas.id.replace('chart-','').replace(/_/g,' '),d,d.stats);
      }}
    }}
  }}
}}

function buildAnomalyTable(anomalies, container, maxRows) {{
  const t=document.createElement('table'); t.className='anomaly-table';
  const thead=document.createElement('thead'); const hrow=document.createElement('tr');
  ['Fecha','NDVI','Z-score','Tipo','Interpretacion'].forEach(h=>{{ const th=document.createElement('th'); th.textContent=h; hrow.appendChild(th); }});
  thead.appendChild(hrow); t.appendChild(thead);
  const tbody=document.createElement('tbody');
  if (!anomalies.length) {{
    const row=document.createElement('tr'); const td=document.createElement('td');
    td.colSpan=5; td.style.cssText='color:var(--muted);padding:10px';
    td.textContent='Sin anomalias detectadas.'; row.appendChild(td); tbody.appendChild(row);
  }} else {{
    anomalies.slice(0,maxRows||999).forEach(a=>{{
      const row=document.createElement('tr');
      const interp=a.tipo==='BROWNING'?'Posible estres SO2 / calentamiento':'Posible greening CO2 / precipitacion';
      [a.fecha,a.ndvi.toFixed(3),(a.z>0?'+':'')+a.z.toFixed(1),a.tipo,interp].forEach((v,i)=>{{
        const td=document.createElement('td'); td.textContent=v;
        if (i===3) td.className='tag-'+a.tipo.toLowerCase(); row.appendChild(td);
      }}); tbody.appendChild(row);
    }});
  }}
  t.appendChild(tbody); container.appendChild(t);
}}

function showMap() {{
  document.querySelectorAll('.volcano-item').forEach(e=>e.classList.remove('active'));
  document.getElementById('mapPanel').classList.remove('hidden');
  document.getElementById('detailContent').classList.remove('active');
}}

function renderChart(name,d,s) {{
  if (!d.chart||!d.chart.labels.length) return;
  const ctx=document.getElementById('chart-'+name.replace(/ /g,'_'));
  if (!ctx) return;
  const mean=s?s.mean:null; const std=s?s.std:0;
  if (charts[name]) charts[name].destroy();
  const pointColors=d.chart.ndvi.map((v,i)=>{{
    const lbl=d.chart.labels[i];
    const anom=s&&s.anomalies.find(a=>a.fecha===lbl);
    return anom?(anom.tipo==='BROWNING'?'#ef4444':'#3b82f6'):'#6366f1';
  }});
  const pointSizes=d.chart.ndvi.map((v,i)=>{{
    const lbl=d.chart.labels[i];
    return s&&s.anomalies.find(a=>a.fecha===lbl)?8:3.5;
  }});
  charts[name]=new Chart(ctx,{{
    type:'line',
    data:{{
      labels:d.chart.labels,
      datasets:[
        {{label:'NDVI medio',data:d.chart.ndvi,borderColor:'#6366f1',backgroundColor:'rgba(99,102,241,0.07)',
          pointBackgroundColor:pointColors,pointRadius:pointSizes,pointHoverRadius:6,tension:0.3,fill:true}},
        ...(mean!==null?[
          {{label:'Promedio ('+mean.toFixed(3)+')',data:d.chart.labels.map(()=>mean),borderColor:'rgba(34,197,94,0.5)',borderDash:[6,3],pointRadius:0,fill:false}},
          {{label:'+2\u03C3 ('+(mean+2*std).toFixed(3)+')',data:d.chart.labels.map(()=>mean+2*std),borderColor:'rgba(239,68,68,0.4)',borderDash:[3,3],pointRadius:0,fill:false}},
          {{label:'-2\u03C3 ('+(mean-2*std).toFixed(3)+')',data:d.chart.labels.map(()=>mean-2*std),borderColor:'rgba(239,68,68,0.4)',borderDash:[3,3],pointRadius:0,fill:false}},
        ]:[]),
      ],
    }},
    options:{{
      responsive:true,
      plugins:{{
        legend:{{labels:{{color:'#8892a4',boxWidth:12,font:{{size:10}}}}}},
        tooltip:{{backgroundColor:'#1a1d26',borderColor:'#2a2d3a',borderWidth:1,
          callbacks:{{afterLabel:ctx=>{{const a=s&&s.anomalies.find(a=>a.fecha===ctx.label);return a?'\u26A0 '+a.tipo+' (z='+a.z+')':'';}}}}
        }},
      }},
      scales:{{
        x:{{ticks:{{color:'#8892a4',maxTicksLimit:8}},grid:{{color:'rgba(255,255,255,0.04)'}}}},
        y:{{ticks:{{color:'#8892a4'}},grid:{{color:'rgba(255,255,255,0.04)'}},min:-0.3,max:0.9}},
      }},
    }},
  }});
}}

buildSidebar();
buildMap();
buildAlertBar();

// Abrir directamente el volcan con alerta si hay alguno
if (ALERTS.length) {{
  const first=ALERTS[0]; if(first) setTimeout(()=>showDetail(first.volcan,'cambios'),200);
}}
</script>
</body>
</html>"""

    out = DOCS_DIR / "index.html"
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Dashboard generado: {out}")
    print(f"  Volcanes con datos: {n_volcanes}")
    print(f"  Alertas activas:    {n_alerts}")
    if active_alerts:
        for a in active_alerts:
            print(f"    [{a['nivel']}] {a['volcan']} — {a['aoi']}: {a['delta_ndvi']:+.3f} ({a['tipo']})")


if __name__ == '__main__':
    generate_dashboard()
