"""
Change Detector — VegStress-v1
Detecta cambios NDVI entre fechas, analiza zonas de interes (AOIs),
genera mapas de diferencia y alertas automaticas.

Uso:
    python change_detector.py --volcan "Laguna del Maule"
    python change_detector.py --volcan "Laguna del Maule" --fecha_a 2026-01-11 --fecha_b 2026-04-11
    python change_detector.py --todos
"""

import os
import sys
import json
import csv
import math
import shutil
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from io import BytesIO

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Circle
from matplotlib.gridspec import GridSpec

ROOT = Path(__file__).parent
DATOS = ROOT / "datos"
DOCS  = ROOT / "docs"

# ── Paleta divergente ΔNDVI (azul=greening, rojo=browning) ──────────────────
DELTA_CMAP = mcolors.LinearSegmentedColormap.from_list('delta_ndvi', [
    (0.00, '#1a4480'),  # greening fuerte
    (0.20, '#4a9edd'),
    (0.35, '#a8d4f0'),
    (0.42, '#ddeeff'),
    (0.50, '#f0f0f0'),  # sin cambio
    (0.58, '#fde8c0'),
    (0.65, '#f5a742'),
    (0.80, '#e05c20'),
    (1.00, '#7B0000'),  # browning fuerte
], N=256)


# ═══════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════

def load_config():
    path = DATOS / "aoi_config.json"
    if not path.exists():
        return {"volcanes": {}, "umbrales_globales": {}}
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def list_available_dates(volcan_name):
    """Lista fechas con array .npy disponible, ordenadas."""
    vdir = DATOS / volcan_name.replace(" ", "_")
    npys = sorted(vdir.glob("ndvi_raw_*.npy"))
    return [p.stem.replace("ndvi_raw_", "") for p in npys]


def load_array(volcan_name, fecha):
    vdir = DATOS / volcan_name.replace(" ", "_")
    npy  = vdir / f"ndvi_raw_{fecha}.npy"
    meta_path = vdir / f"ndvi_meta_{fecha}.json"
    if not npy.exists():
        return None, None
    arr = np.load(npy)
    meta = {}
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
    return arr, meta


def align_arrays(arr_a, meta_a, arr_b, meta_b):
    """Asegura que ambos arrays tengan el mismo shape. Usa el mas pequeno."""
    if arr_a.shape == arr_b.shape:
        return arr_a, arr_b
    from scipy.ndimage import zoom
    Ha, Wa = arr_a.shape
    Hb, Wb = arr_b.shape
    # Usar la resolucion mas baja para no inventar datos
    H, W = min(Ha, Hb), min(Wa, Wb)
    if arr_a.shape != (H, W):
        arr_a = zoom(arr_a, (H / Ha, W / Wa), order=1)
    if arr_b.shape != (H, W):
        arr_b = zoom(arr_b, (H / Hb, W / Wb), order=1)
    return arr_a, arr_b


# ═══════════════════════════════════════════════════════════════
# CALCULO DE ΔNDVI
# ═══════════════════════════════════════════════════════════════

def compute_delta(arr_a, arr_b, umbrales):
    """
    Calcula ΔNDVI = arr_b - arr_a.
    NaN donde alguno de los dos es NaN.
    """
    delta = arr_b - arr_a
    # Propagar NaN
    nan_mask = np.isnan(arr_a) | np.isnan(arr_b)
    delta[nan_mask] = np.nan

    valid = ~nan_mask
    vals = delta[valid]

    if len(vals) < 100:
        return {'delta': delta, 'valid_pct': 0, 'error': 'Sin datos suficientes'}

    watch_abs    = umbrales.get('delta_ndvi_watch',    0.10)
    warning_abs  = umbrales.get('delta_ndvi_warning',  0.15)
    critical_abs = umbrales.get('delta_ndvi_critical', 0.25)

    return {
        'delta': delta,
        'valid_pct':    float(valid.sum() / valid.size * 100),
        'delta_mean':   float(np.nanmean(delta)),
        'delta_std':    float(np.nanstd(delta)),
        'greening_pct': float((delta[valid] < -watch_abs).sum() / valid.sum() * 100),
        'browning_pct': float((delta[valid] >  watch_abs).sum() / valid.sum() * 100),
    }


# ═══════════════════════════════════════════════════════════════
# ANALISIS POR AOI
# ═══════════════════════════════════════════════════════════════

def aoi_mask(aoi, bbox, shape):
    """Crea mascara circular para un AOI dado bbox y shape del array."""
    H, W = shape
    lon_w, lat_s, lon_e, lat_n = bbox
    lat, lon, radio_m = aoi['lat'], aoi['lon'], aoi['radio_m']

    # Coordenadas pixel del centro del AOI
    cx = (lon - lon_w) / (lon_e - lon_w) * W
    cy = (lat_n - lat) / (lat_n - lat_s) * H

    # Radio en pixeles (aproximado a partir del buffer_km)
    km_per_px_x = (lon_e - lon_w) * 111.0 * abs(math.cos(math.radians(lat))) / W
    km_per_px_y = (lat_n - lat_s) * 111.0 / H
    r_px_x = (radio_m / 1000.0) / km_per_px_x
    r_px_y = (radio_m / 1000.0) / km_per_px_y

    Y, X = np.ogrid[:H, :W]
    mask = ((X - cx) / r_px_x) ** 2 + ((Y - cy) / r_px_y) ** 2 <= 1.0
    return mask, (cx, cy)


def analyze_aoi(aoi, delta, arr_a, arr_b, bbox, umbrales):
    """Estadisticas de cambio dentro de un AOI."""
    mask, center_px = aoi_mask(aoi, bbox, delta.shape)
    aoi_delta = delta[mask]
    aoi_a     = arr_a[mask]
    aoi_b     = arr_b[mask]

    valid = ~np.isnan(aoi_delta)
    valid_pct = float(valid.sum() / mask.sum() * 100) if mask.sum() > 0 else 0

    if valid.sum() < 20:
        return {
            'id': aoi['id'], 'nombre': aoi['nombre'],
            'valid_pct': valid_pct, 'status': 'SIN_DATOS',
            'center_px': center_px,
        }

    vals = aoi_delta[valid]
    delta_mean = float(np.mean(vals))
    delta_std  = float(np.std(vals))
    ndvi_a     = float(np.nanmean(aoi_a))
    ndvi_b     = float(np.nanmean(aoi_b))

    watch_abs    = aoi.get('umbral_delta_abs', umbrales.get('delta_ndvi_watch',   0.10))
    warning_abs  = aoi.get('umbral_delta_abs', umbrales.get('delta_ndvi_warning', 0.15))
    critical_abs = umbrales.get('delta_ndvi_critical', 0.25)

    abs_delta = abs(delta_mean)
    if abs_delta >= critical_abs:
        nivel = 'CRITICAL'
    elif abs_delta >= warning_abs * 1.3:
        nivel = 'WARNING'
    elif abs_delta >= watch_abs:
        nivel = 'WATCH'
    else:
        nivel = 'OK'

    tipo = 'NINGUNO'
    if delta_mean < -watch_abs:
        tipo = 'GREENING'
    elif delta_mean > watch_abs:
        tipo = 'BROWNING'

    return {
        'id': aoi['id'],
        'nombre': aoi['nombre'],
        'valid_pct': round(valid_pct, 1),
        'ndvi_a': round(ndvi_a, 4),
        'ndvi_b': round(ndvi_b, 4),
        'delta_mean': round(delta_mean, 4),
        'delta_std':  round(delta_std,  4),
        'tipo': tipo,
        'nivel': nivel,
        'descripcion': aoi.get('descripcion', ''),
        'tipo_esperado': aoi.get('tipo_esperado', 'NINGUNO'),
        'center_px': center_px,
        'radio_m': aoi['radio_m'],
    }


# ═══════════════════════════════════════════════════════════════
# HISTORIAL DE CAMBIOS
# ═══════════════════════════════════════════════════════════════

def update_history(volcan_name, fecha_a, fecha_b, aoi_results):
    vdir = DATOS / volcan_name.replace(" ", "_")
    hist_path = vdir / "change_history.csv"
    fieldnames = ['fecha_a', 'fecha_b', 'aoi_id', 'delta_mean', 'delta_std', 'valid_pct', 'tipo', 'nivel']

    rows = []
    if hist_path.exists():
        with open(hist_path, newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

    # Eliminar entrada existente para este par de fechas si existe
    rows = [r for r in rows if not (r['fecha_a'] == fecha_a and r['fecha_b'] == fecha_b)]

    for r in aoi_results:
        if r.get('status') == 'SIN_DATOS':
            continue
        rows.append({
            'fecha_a': fecha_a, 'fecha_b': fecha_b,
            'aoi_id': r['id'],
            'delta_mean': r.get('delta_mean', ''),
            'delta_std':  r.get('delta_std',  ''),
            'valid_pct':  r.get('valid_pct',  ''),
            'tipo':  r.get('tipo',  ''),
            'nivel': r.get('nivel', ''),
        })

    with open(hist_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def load_history_for_aoi(volcan_name, aoi_id):
    hist_path = DATOS / volcan_name.replace(" ", "_") / "change_history.csv"
    if not hist_path.exists():
        return []
    with open(hist_path, newline='', encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['aoi_id'] == aoi_id]
    return rows


def sigma_from_history(hist_rows, delta_mean):
    """Calcula cuantos sigmas esta el delta actual respecto al historial."""
    if len(hist_rows) < 5:
        return None
    vals = [float(r['delta_mean']) for r in hist_rows if r['delta_mean']]
    h_mean = np.mean(vals)
    h_std  = np.std(vals)
    if h_std < 0.001:
        return None
    return (delta_mean - h_mean) / h_std


# ═══════════════════════════════════════════════════════════════
# MAPA DE CAMBIOS (ΔNDVI)
# ═══════════════════════════════════════════════════════════════

def generate_delta_map(volcan_name, fecha_a, fecha_b, delta_result, aoi_results, bbox, meta_b):
    delta = delta_result['delta']
    H, W  = delta.shape
    lon_w, lat_s, lon_e, lat_n = bbox

    norm = mcolors.TwoSlopeNorm(vmin=-0.4, vcenter=0.0, vmax=0.4)
    fig = plt.figure(figsize=(16, 10), facecolor='#0f1117')
    gs  = GridSpec(1, 2, figure=fig, width_ratios=[2.2, 1], wspace=0.04)
    ax_map  = fig.add_subplot(gs[0])
    ax_info = fig.add_subplot(gs[1])

    # ── Mapa ΔNDVI ──
    im = ax_map.imshow(
        delta, cmap=DELTA_CMAP, norm=norm,
        extent=[lon_w, lon_e, lat_s, lat_n],
        origin='upper', aspect='auto', interpolation='nearest'
    )

    # Marcar AOIs
    for r in aoi_results:
        if r.get('status') == 'SIN_DATOS':
            continue
        cx_px, cy_px = r['center_px']
        lon_c = lon_w + cx_px / W * (lon_e - lon_w)
        lat_c = lat_n - cy_px / H * (lat_n - lat_s)
        radio_deg = r['radio_m'] / 111000.0

        color_borde = {'OK': '#22c55e', 'WATCH': '#eab308',
                       'WARNING': '#f97316', 'CRITICAL': '#ef4444'}.get(r['nivel'], 'white')
        circ = plt.Circle((lon_c, lat_c), radio_deg,
                           fill=False, edgecolor=color_borde,
                           linewidth=2.0, linestyle='--', zorder=5)
        ax_map.add_patch(circ)
        ax_map.text(lon_c, lat_c + radio_deg * 1.15, r['nombre'],
                    ha='center', va='bottom', fontsize=7.5,
                    color=color_borde, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5, linewidth=0))
        if r.get('delta_mean') is not None:
            ax_map.text(lon_c, lat_c, f"{r['delta_mean']:+.3f}",
                        ha='center', va='center', fontsize=8,
                        color='white', fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.6, linewidth=0))

    cbar = plt.colorbar(im, ax=ax_map, fraction=0.025, pad=0.01)
    cbar.set_label('ΔNDVI (positivo = browning)', color='#8892a4', fontsize=9)
    cbar.ax.yaxis.set_tick_params(color='#8892a4')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8892a4')

    ax_map.set_facecolor('#1a1d26')
    ax_map.set_title(
        f'{volcan_name} — Cambio NDVI\n{fecha_a}  →  {fecha_b}  |  ΔNDVI = B - A',
        color='#e2e8f0', fontsize=13, fontweight='bold', pad=12)
    ax_map.set_xlabel('Longitud', color='#8892a4')
    ax_map.set_ylabel('Latitud',  color='#8892a4')
    ax_map.tick_params(colors='#8892a4')
    for sp in ax_map.spines.values():
        sp.set_edgecolor('#2a2d3a')

    # ── Panel info ──
    ax_info.set_facecolor('#0f1117')
    ax_info.set_xlim(0, 1)
    ax_info.set_ylim(0, 1)
    ax_info.axis('off')

    def txt(x, y, s, **kw):
        ax_info.text(x, y, s, transform=ax_info.transAxes, **kw)

    y = 0.97
    txt(0, y, 'Cambio global', color='#e2e8f0', fontsize=11, fontweight='bold')
    y -= 0.04
    dm = delta_result.get('delta_mean', float('nan'))
    txt(0, y, f"ΔNDVI medio:   {dm:+.4f}", color='#8892a4', fontsize=10)
    y -= 0.03
    txt(0, y, f"ΔNDVI std:      {delta_result.get('delta_std', 0):.4f}", color='#8892a4', fontsize=10)
    y -= 0.03
    txt(0, y, f"Pixels validos: {delta_result.get('valid_pct', 0):.1f}%", color='#8892a4', fontsize=10)
    y -= 0.03
    gc = delta_result.get('greening_pct', 0)
    bc = delta_result.get('browning_pct', 0)
    txt(0, y, f"Greening:  {gc:.1f}%   Browning: {bc:.1f}%", color='#8892a4', fontsize=10)

    # Escala
    y -= 0.06
    txt(0, y, 'Escala ΔNDVI', color='#e2e8f0', fontsize=11, fontweight='bold')
    y -= 0.01
    items = [
        ('#1a4480', '< -0.15  GREENING significativo'),
        ('#4a9edd', '-0.15 a -0.05  GREENING leve'),
        ('#f0f0f0', '-0.05 a +0.05  Sin cambio'),
        ('#f5a742', '+0.05 a +0.15  BROWNING leve'),
        ('#e05c20', '+0.15 a +0.25  BROWNING significativo'),
        ('#7B0000', '> +0.25   BROWNING severo'),
    ]
    from matplotlib.patches import Rectangle as Rect
    for col, label in items:
        y -= 0.04
        ax_info.add_patch(Rect((0, y - 0.005), 0.06, 0.03,
                               facecolor=col, transform=ax_info.transAxes, clip_on=False))
        txt(0.09, y, label, color='#8892a4', fontsize=8.5)

    # Tabla AOIs
    y -= 0.07
    txt(0, y, 'Zonas de interes (AOIs)', color='#e2e8f0', fontsize=11, fontweight='bold')
    y -= 0.04
    txt(0.00, y, 'Zona',    color='#8892a4', fontsize=8, fontweight='bold')
    txt(0.42, y, 'ΔNDVI',  color='#8892a4', fontsize=8, fontweight='bold')
    txt(0.60, y, 'Tipo',    color='#8892a4', fontsize=8, fontweight='bold')
    txt(0.78, y, 'Nivel',   color='#8892a4', fontsize=8, fontweight='bold')

    nivel_col = {'OK': '#22c55e', 'WATCH': '#eab308', 'WARNING': '#f97316', 'CRITICAL': '#ef4444'}
    tipo_col  = {'GREENING': '#3b82f6', 'BROWNING': '#ef4444', 'NINGUNO': '#8892a4'}

    for r in aoi_results:
        if y < 0.04:
            break
        y -= 0.045
        if r.get('status') == 'SIN_DATOS':
            txt(0.00, y, r['nombre'][:22], color='#555', fontsize=8)
            txt(0.42, y, 'N/D',           color='#555', fontsize=8)
            txt(0.60, y, 'N/D',           color='#555', fontsize=8)
            txt(0.78, y, 'N/D',           color='#555', fontsize=8)
        else:
            nc = nivel_col.get(r['nivel'], '#e2e8f0')
            tc = tipo_col.get(r['tipo'],   '#8892a4')
            txt(0.00, y, r['nombre'][:22],               color='#e2e8f0', fontsize=8)
            txt(0.42, y, f"{r['delta_mean']:+.3f}",       color=nc,        fontsize=8, fontweight='bold')
            txt(0.60, y, r['tipo'],                        color=tc,        fontsize=8)
            txt(0.78, y, r['nivel'],                       color=nc,        fontsize=8, fontweight='bold')

    plt.tight_layout(pad=1.5)

    vdir = DATOS / volcan_name.replace(" ", "_")
    vdir.mkdir(parents=True, exist_ok=True)
    out_path = vdir / f"ndvi_delta_{fecha_a}_vs_{fecha_b}.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='#0f1117')
    plt.close()

    docs_maps = DOCS / "maps"
    docs_maps.mkdir(parents=True, exist_ok=True)
    shutil.copy(out_path, docs_maps / f"{volcan_name.replace(' ', '_')}_delta_latest.png")
    print(f"  Mapa ΔNDVI guardado: {out_path}")
    return out_path


# ═══════════════════════════════════════════════════════════════
# GENERACION DE ALERTAS
# ═══════════════════════════════════════════════════════════════

def generate_alerts(volcan_name, fecha_a, fecha_b, delta_result, aoi_results, volcan_config):
    alertas = []
    umbrales = load_config().get('umbrales_globales', {})

    for r in aoi_results:
        if r.get('status') == 'SIN_DATOS' or r.get('nivel') == 'OK':
            continue
        hist = load_history_for_aoi(volcan_name, r['id'])
        sigma = sigma_from_history(hist[:-1], r['delta_mean'])  # excluir el actual

        alertas.append({
            'volcan': volcan_name,
            'fecha_a': fecha_a,
            'fecha_b': fecha_b,
            'aoi_id': r['id'],
            'aoi_nombre': r['nombre'],
            'delta_ndvi': r['delta_mean'],
            'tipo': r['tipo'],
            'nivel': r['nivel'],
            'valid_pct': r['valid_pct'],
            'sigma': round(sigma, 2) if sigma is not None else None,
            'ndvi_a': r['ndvi_a'],
            'ndvi_b': r['ndvi_b'],
            'descripcion': r['descripcion'],
        })

    if not alertas:
        return None

    # Nivel maximo
    orden = ['WATCH', 'WARNING', 'CRITICAL']
    nivel_max = max(alertas, key=lambda x: orden.index(x['nivel']) if x['nivel'] in orden else -1)['nivel']

    # Markdown
    now = datetime.now().strftime('%Y-%m-%d')
    alertas_dir = DOCS / "alertas"
    alertas_dir.mkdir(parents=True, exist_ok=True)

    md_file = alertas_dir / f"{now}_{volcan_name.replace(' ', '_')}.md"
    nivel_emoji = {'WATCH': 'WATCH', 'WARNING': 'ADVERTENCIA', 'CRITICAL': 'CRITICO'}
    lines = [
        f"# ALERTA VEGSTRESS — {volcan_name}",
        f"",
        f"**Nivel:** {nivel_max} ({nivel_emoji.get(nivel_max, nivel_max)})",
        f"**Fecha analisis:** {now}",
        f"**Periodo comparado:** {fecha_a} → {fecha_b}",
        f"",
        f"## Resumen de anomalias",
        f"",
        f"| Zona | ΔNDVI | Tipo | Nivel | σ historial |",
        f"|------|-------|------|-------|------------|",
    ]
    for a in alertas:
        sig_str = f"{a['sigma']:+.1f}σ" if a['sigma'] is not None else "N/D"
        lines.append(f"| {a['aoi_nombre']} | {a['delta_ndvi']:+.3f} | {a['tipo']} | {a['nivel']} | {sig_str} |")

    lines += ["", "## Detalle por zona", ""]
    for a in alertas:
        lines += [
            f"### {a['aoi_nombre']}",
            f"- **NDVI anterior ({fecha_a}):** {a['ndvi_a']:.4f}",
            f"- **NDVI actual ({fecha_b}):** {a['ndvi_b']:.4f}",
            f"- **Cambio (ΔNDVI):** {a['delta_ndvi']:+.4f}",
            f"- **Pixels validos:** {a['valid_pct']:.1f}%",
            f"- **Contexto:** {a['descripcion']}",
            f"",
            "**Interpretacion:**  ",
        ]
        if a['tipo'] == 'BROWNING':
            lines.append("Reduccion de biomasa vegetal. Posibles causas: deposicion de SO2, "
                         "calentamiento geotermal de suelo, acidificacion, o sequia local.")
        elif a['tipo'] == 'GREENING':
            lines.append("Aumento de biomasa vegetal. Posibles causas: fertilizacion por CO2/SO2 "
                         "en bajas concentraciones, mayor precipitacion, o recuperacion post-evento.")
        lines.append("")

    lines += [
        "---",
        f"*Generado automaticamente por VegStress-v1 el {now}.*",
        f"*Datos: Sentinel-2 L2A via Copernicus CDSE. Umbral deteccion: +/-{umbrales.get('delta_ndvi_watch', 0.10)} NDVI.*",
    ]

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Alerta guardada: {md_file}")

    return {
        'volcan': volcan_name,
        'nivel': nivel_max,
        'fecha_a': fecha_a,
        'fecha_b': fecha_b,
        'alertas': alertas,
        'md_path': str(md_file.relative_to(ROOT)),
    }


def update_alerts_summary(new_alert):
    """Actualiza docs/alerts_summary.json con la ultima alerta."""
    summary_path = DOCS / "alerts_summary.json"
    summary = {'last_updated': datetime.now().strftime('%Y-%m-%d'), 'active_alerts': []}
    if summary_path.exists():
        with open(summary_path, encoding='utf-8') as f:
            summary = json.load(f)

    # Reemplazar alerta del mismo volcan si existe
    summary['active_alerts'] = [
        a for a in summary['active_alerts'] if a['volcan'] != new_alert['volcan']
    ]
    if new_alert['nivel'] != 'OK':
        for a in new_alert['alertas']:
            summary['active_alerts'].append({
                'volcan':    new_alert['volcan'],
                'nivel':     a['nivel'],
                'aoi':       a['aoi_nombre'],
                'delta_ndvi': a['delta_ndvi'],
                'tipo':      a['tipo'],
                'fecha_a':   new_alert['fecha_a'],
                'fecha_b':   new_alert['fecha_b'],
                'md_path':   new_alert['md_path'],
            })

    summary['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    DOCS.mkdir(exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  Resumen alertas actualizado: {summary_path}")


# ═══════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def run_detection(volcan_name, fecha_a=None, fecha_b=None):
    print(f"\n{'='*60}")
    print(f" Change Detector — {volcan_name}")
    print(f"{'='*60}")

    config = load_config()
    umbrales = config.get('umbrales_globales', {})
    volcan_config = config.get('volcanes', {}).get(volcan_name, {})
    aois_def = [a for a in volcan_config.get('aois', []) if a.get('activo', True)]

    # Seleccionar fechas
    available = list_available_dates(volcan_name)
    if len(available) < 2:
        print(f"  Solo {len(available)} array(s) disponible(s). Se necesitan al menos 2.")
        print(f"  Ejecuta: python spatial_mapper.py --volcan \"{volcan_name}\"")
        return

    if not fecha_b:
        fecha_b = available[-1]
    if not fecha_a:
        # Elegir fecha anterior, preferir misma estacion (~90 dias antes)
        target = datetime.strptime(fecha_b, '%Y-%m-%d') - timedelta(days=90)
        diffs = [(abs((datetime.strptime(f, '%Y-%m-%d') - target).days), f)
                 for f in available if f < fecha_b]
        if not diffs:
            fecha_a = available[-2]
        else:
            fecha_a = min(diffs)[1]

    print(f"  Comparando: {fecha_a}  →  {fecha_b}")

    # Cargar arrays
    arr_a, meta_a = load_array(volcan_name, fecha_a)
    arr_b, meta_b = load_array(volcan_name, fecha_b)

    if arr_a is None or arr_b is None:
        print("  No se encontraron arrays crudos .npy para esas fechas.")
        print("  Ejecuta spatial_mapper.py primero para generar los arrays.")
        return

    print(f"  Arrays: {arr_a.shape} y {arr_b.shape}")
    arr_a, arr_b = align_arrays(arr_a, meta_a, arr_b, meta_b)
    print(f"  Alineados a: {arr_a.shape}")

    bbox = meta_b.get('bbox', meta_a.get('bbox'))
    if not bbox:
        print("  Sin metadatos bbox. Verifica que spatial_mapper.py se ejecuto correctamente.")
        return

    # Calcular ΔNDVI
    delta_result = compute_delta(arr_a, arr_b, umbrales)
    dm = delta_result.get('delta_mean', float('nan'))
    print(f"  ΔNDVI medio: {dm:+.4f}  |  valido: {delta_result.get('valid_pct', 0):.1f}%")

    # Analizar AOIs
    aoi_results = []
    if aois_def:
        print(f"\n  Analizando {len(aois_def)} zonas de interes...")
        for aoi in aois_def:
            r = analyze_aoi(aoi, delta_result['delta'], arr_a, arr_b, bbox, umbrales)
            aoi_results.append(r)
            status = r.get('nivel', r.get('status', '?'))
            d = r.get('delta_mean')
            dstr = f"{d:+.4f}" if d is not None else "N/D"
            print(f"    [{status:8s}] {r['nombre'][:30]:30s}  ΔNDVI={dstr}  valid={r['valid_pct']:.0f}%")
    else:
        print("  Sin AOIs configuradas para este volcan en aoi_config.json")

    # Guardar historial
    update_history(volcan_name, fecha_a, fecha_b, aoi_results)

    # Generar mapa ΔNDVI
    print("\n  Generando mapa de cambios...")
    generate_delta_map(volcan_name, fecha_a, fecha_b, delta_result, aoi_results, bbox, meta_b)

    # Generar alertas
    alert = generate_alerts(volcan_name, fecha_a, fecha_b, delta_result, aoi_results, volcan_config)
    if alert:
        print(f"\n  *** {alert['nivel']}: {len(alert['alertas'])} zona(s) con anomalias ***")
        update_alerts_summary(alert)
    else:
        print("\n  Sin anomalias detectadas en AOIs.")
        # Limpiar alerta previa de este volcan si existia
        summary_path = DOCS / "alerts_summary.json"
        if summary_path.exists():
            with open(summary_path) as f:
                s = json.load(f)
            s['active_alerts'] = [a for a in s['active_alerts'] if a['volcan'] != volcan_name]
            with open(summary_path, 'w') as f:
                json.dump(s, f, indent=2, ensure_ascii=False)

    print(f"\n  Completado: {volcan_name} ({fecha_a} → {fecha_b})")
    return delta_result, aoi_results


def main():
    parser = argparse.ArgumentParser(description='VegStress-v1 — Deteccion de cambios NDVI')
    parser.add_argument('--volcan',  default='Laguna del Maule', help='Nombre del volcan')
    parser.add_argument('--fecha_a', default=None, help='Fecha base YYYY-MM-DD')
    parser.add_argument('--fecha_b', default=None, help='Fecha actual YYYY-MM-DD')
    parser.add_argument('--todos',   action='store_true', help='Analizar todos los volcanes con datos')
    args = parser.parse_args()

    if args.todos:
        config = load_config()
        for vname in config.get('volcanes', {}):
            dates = list_available_dates(vname)
            if len(dates) >= 2:
                run_detection(vname)
            else:
                print(f"\n  {vname}: sin suficientes arrays .npy (tiene {len(dates)})")
    else:
        run_detection(args.volcan, args.fecha_a, args.fecha_b)


if __name__ == '__main__':
    main()
