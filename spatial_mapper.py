"""
Spatial NDVI Mapper — VegStress-v1
Descarga imagen NDVI espacial a maxima resolucion (10m/px Sentinel-2)
y genera mapa de colores con grilla de sectores.

Uso:
    python spatial_mapper.py                          # Laguna del Maule, ultima imagen
    python spatial_mapper.py --volcan Villarrica --fecha 2026-03-12
    python spatial_mapper.py --volcan "Laguna del Maule" --meses 3  # busca mejor imagen en 3 meses
"""

import os
import sys
import math
import time
import argparse
import requests
import numpy as np
from pathlib import Path
from io import BytesIO
from datetime import datetime, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass

import tifffile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_API_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

VOLCANES = {
    "Laguna del Maule": {"lat": -36.07100, "lon": -70.49828, "buffer_km": 9.0,  "zona": "Centro"},
    "Villarrica":        {"lat": -39.42052, "lon": -71.93939, "buffer_km": 6.0,  "zona": "Sur"},
    "Copahue":           {"lat": -37.85715, "lon": -71.16836, "buffer_km": 6.0,  "zona": "Sur"},
    "Llaima":            {"lat": -38.71238, "lon": -71.73447, "buffer_km": 6.0,  "zona": "Sur"},
    "Nevados de Chillan": {"lat": -37.41096, "lon": -71.35231, "buffer_km": 6.0, "zona": "Centro"},
    "Lascar":            {"lat": -23.36726, "lon": -67.73611, "buffer_km": 6.0,  "zona": "Norte"},
    "Calbuco":           {"lat": -41.32863, "lon": -72.61131, "buffer_km": 6.0,  "zona": "Sur"},
    "Osorno":            {"lat": -41.13500, "lon": -72.49700, "buffer_km": 6.0,  "zona": "Sur"},
}

# Paleta NDVI: rojo (sin vegetacion/estres) -> amarillo -> verde (vegetacion densa)
NDVI_COLORS = [
    (-0.5, '#1a1a2e'),   # agua / sombra
    (-0.1, '#8B0000'),   # sin vegetacion
    (0.0,  '#c0392b'),   # suelo desnudo
    (0.1,  '#e67e22'),   # vegetacion muy escasa
    (0.2,  '#f1c40f'),   # vegetacion escasa
    (0.3,  '#a8d08d'),   # vegetacion moderada
    (0.4,  '#27ae60'),   # vegetacion buena
    (0.6,  '#1e8449'),   # vegetacion densa
    (0.9,  '#0d4f2e'),   # vegetacion muy densa
]


def get_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': os.getenv('SH_CLIENT_ID'),
        'client_secret': os.getenv('SH_CLIENT_SECRET'),
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()['access_token']


def create_bbox(lat, lon, buffer_km):
    delta_lat = buffer_km / 111.0
    delta_lon = buffer_km / (111.0 * abs(math.cos(math.radians(lat))))
    return [lon - delta_lon, lat - delta_lat, lon + delta_lon, lat + delta_lat]


def find_best_date(token, lat, lon, buffer_km, meses=3):
    """Busca la fecha mas reciente con menos nubes."""
    print(f"  Buscando mejor imagen en los ultimos {meses} meses...")
    bbox = create_bbox(lat, lon, buffer_km)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    evalscript = """
//VERSION=3
function setup() { return { input:[{bands:["B04","B08","SCL"]}], output:{bands:3,sampleType:"FLOAT32"} } }
function evaluatePixel(s) {
  let ndvi = (s.B08-s.B04)/(s.B08+s.B04+0.0001);
  let valid = (s.SCL>=4 && s.SCL<=6) ? 1.0 : 0.0;
  let cloud = (s.SCL>=8 && s.SCL<=10) ? 1.0 : 0.0;
  return [ndvi, valid, cloud];
}
"""
    end = datetime.now()
    start = end - timedelta(days=meses * 30)
    candidates = []
    current = end
    while current >= start:
        fecha = current.strftime('%Y-%m-%d')
        payload = {
            "input": {
                "bounds": {"bbox": bbox, "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}},
                "data": [{"type": "sentinel-2-l2a", "dataFilter": {
                    "timeRange": {"from": f"{fecha}T00:00:00Z", "to": f"{fecha}T23:59:59Z"},
                    "maxCloudCoverage": 80
                }}]
            },
            "output": {"width": 128, "height": 128,
                       "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
            "evalscript": evalscript
        }
        resp = requests.post(PROCESS_API_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            arr = tifffile.imread(BytesIO(resp.content))
            if arr.ndim == 3 and arr.shape[2] >= 3:
                valid_pct = float(arr[:, :, 1].mean() * 100)
                cloud_pct = float(arr[:, :, 2].mean() * 100)
                if valid_pct > 5:
                    candidates.append((fecha, valid_pct, cloud_pct))
                    print(f"    {fecha}: valido={valid_pct:.0f}% nubes={cloud_pct:.0f}%")
        current -= timedelta(days=5)
        time.sleep(0.3)

    if not candidates:
        return None
    # Mejor = mas pixeles validos
    best = max(candidates, key=lambda x: x[1])
    print(f"  Mejor fecha: {best[0]} (valido={best[1]:.0f}%)")
    return best[0]


def download_ndvi_spatial(token, lat, lon, buffer_km, fecha, res_px=1800):
    """Descarga NDVI espacial a alta resolucion. Retorna array (H,W,3) float32."""
    bbox = create_bbox(lat, lon, buffer_km)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    # Calcular resolucion real disponible (~10m/px de Sentinel-2)
    # buffer_km * 2 = ancho en km. A 10m/px = km*100 pixeles
    px_ideal = int(buffer_km * 2 * 100)  # 10m resolution
    px = min(px_ideal, res_px, 2500)     # API max 2500
    print(f"  Descargando {px}x{px} px ({buffer_km*2:.0f}km x {buffer_km*2:.0f}km, ~{buffer_km*2000/px:.0f}m/px)...")

    evalscript = """
//VERSION=3
function setup() {
  return { input:[{bands:["B04","B08","SCL"]}], output:{bands:4,sampleType:"FLOAT32"} }
}
function evaluatePixel(s) {
  let ndvi = (s.B08-s.B04)/(s.B08+s.B04+0.0001);
  let valid = (s.SCL>=4 && s.SCL<=6) ? 1.0 : 0.0;
  let cloud = (s.SCL>=8 && s.SCL<=10) ? 1.0 : 0.0;
  let snow  = (s.SCL==11) ? 1.0 : 0.0;
  return [ndvi, valid, cloud, snow];
}
"""
    payload = {
        "input": {
            "bounds": {"bbox": bbox, "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}},
            "data": [{"type": "sentinel-2-l2a", "dataFilter": {
                "timeRange": {"from": f"{fecha}T00:00:00Z", "to": f"{fecha}T23:59:59Z"},
                "maxCloudCoverage": 100
            }}]
        },
        "output": {"width": px, "height": px,
                   "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
        "evalscript": evalscript
    }

    resp = requests.post(PROCESS_API_URL, headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        print(f"  Error API: {resp.status_code} — {resp.text[:200]}")
        return None, px, bbox

    arr = tifffile.imread(BytesIO(resp.content))
    print(f"  Array descargado: {arr.shape}, dtype={arr.dtype}")
    return arr, px, bbox


def ndvi_colormap():
    """Crea colormap personalizado para NDVI."""
    positions = [(v + 0.5) / 1.4 for v, _ in NDVI_COLORS]  # normalizar a [0,1]
    colors_list = [c for _, c in NDVI_COLORS]
    cmap = mcolors.LinearSegmentedColormap.from_list(
        'ndvi', list(zip(positions, colors_list)), N=256
    )
    return cmap


def generate_spatial_map(volcan_name, fecha, arr, bbox, grid_n=4, output_dir=None):
    """Genera imagen del mapa espacial NDVI con grilla."""
    if arr is None:
        print("  Sin datos para generar mapa.")
        return None

    if arr.ndim == 3 and arr.shape[2] >= 4:
        ndvi   = arr[:, :, 0].astype(np.float32)
        valid  = arr[:, :, 1] > 0.5
        cloud  = arr[:, :, 2] > 0.5
        snow   = arr[:, :, 3] > 0.5
    else:
        print(f"  Forma inesperada: {arr.shape}")
        return None

    H, W = ndvi.shape
    total_px = H * W
    valid_pct = valid.sum() / total_px * 100
    cloud_pct = cloud.sum() / total_px * 100
    snow_pct  = snow.sum()  / total_px * 100
    print(f"  Cobertura: valido={valid_pct:.1f}% nubes={cloud_pct:.1f}% nieve={snow_pct:.1f}%")

    # Imagen NDVI: enmascarar nubes/nieve
    ndvi_display = np.where(valid, ndvi, np.nan)
    ndvi_display = np.where(cloud, np.nan, ndvi_display)
    ndvi_display = np.where(snow,  np.nan, ndvi_display)

    # Stats globales
    valid_vals = ndvi[valid & ~cloud & ~snow]
    ndvi_mean = float(np.mean(valid_vals)) if len(valid_vals) > 0 else float('nan')
    ndvi_std  = float(np.std(valid_vals))  if len(valid_vals) > 0 else float('nan')

    # Stats por sector (grilla N x N)
    grid_stats = []
    cell_h = H // grid_n
    cell_w = W // grid_n
    lon_w, lat_s, lon_e, lat_n = bbox

    for row in range(grid_n):
        for col in range(grid_n):
            r0, r1 = row * cell_h, (row + 1) * cell_h
            c0, c1 = col * cell_w, (col + 1) * cell_w
            cell_ndvi  = ndvi[r0:r1, c0:c1]
            cell_valid = valid[r0:r1, c0:c1]
            cell_cloud = cloud[r0:r1, c0:c1]
            cell_snow  = snow[r0:r1, c0:c1]
            mask = cell_valid & ~cell_cloud & ~cell_snow
            vals = cell_ndvi[mask]
            # Coordenadas del centro del sector
            clat = lat_n - (row + 0.5) * (lat_n - lat_s) / grid_n
            clon = lon_w + (col + 0.5) * (lon_e - lon_w) / grid_n
            grid_stats.append({
                'row': row, 'col': col,
                'lat': clat, 'lon': clon,
                'ndvi_mean': float(np.mean(vals)) if len(vals) > 10 else None,
                'ndvi_std':  float(np.std(vals))  if len(vals) > 10 else None,
                'valid_pct': float(mask.sum() / mask.size * 100),
            })

    # ---- FIGURA ----
    cmap = ndvi_colormap()
    norm = mcolors.Normalize(vmin=-0.3, vmax=0.7)

    fig = plt.figure(figsize=(16, 10), facecolor='#0f1117')
    gs  = GridSpec(1, 2, figure=fig, width_ratios=[2.2, 1], wspace=0.04)

    ax_map  = fig.add_subplot(gs[0])
    ax_info = fig.add_subplot(gs[1])

    # -- Mapa principal --
    im = ax_map.imshow(
        ndvi_display, cmap=cmap, norm=norm,
        extent=[lon_w, lon_e, lat_s, lat_n],
        origin='upper', aspect='auto',
        interpolation='nearest'
    )

    # Grilla de sectores
    for row in range(grid_n + 1):
        lat = lat_n - row * (lat_n - lat_s) / grid_n
        ax_map.axhline(lat, color='white', linewidth=0.6, alpha=0.4)
    for col in range(grid_n + 1):
        lon = lon_w + col * (lon_e - lon_w) / grid_n
        ax_map.axvline(lon, color='white', linewidth=0.6, alpha=0.4)

    # Etiquetas NDVI por sector
    for s in grid_stats:
        if s['ndvi_mean'] is not None:
            v = s['ndvi_mean']
            color_text = 'white' if v < 0.25 else '#0d1117'
            ax_map.text(s['lon'], s['lat'], f"{v:+.2f}",
                        ha='center', va='center', fontsize=9,
                        color=color_text, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.4, linewidth=0))
        else:
            ax_map.text(s['lon'], s['lat'], 'N/D',
                        ha='center', va='center', fontsize=8, color='#555', style='italic')

    # Cruz en el centro (volcán)
    clon_v = (lon_w + lon_e) / 2
    clat_v = (lat_s + lat_n) / 2
    ax_map.plot(clon_v, clat_v, 'w^', markersize=10, markeredgecolor='#ff6b35',
                markeredgewidth=1.5, zorder=10)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax_map, fraction=0.025, pad=0.01)
    cbar.set_label('NDVI', color='#8892a4', fontsize=10)
    cbar.ax.yaxis.set_tick_params(color='#8892a4')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8892a4')

    ax_map.set_facecolor('#1a1d26')
    ax_map.set_title(f'{volcan_name} — Mapa NDVI Espacial\n{fecha}  |  Sentinel-2 L2A  |  ~10m/px',
                     color='#e2e8f0', fontsize=13, fontweight='bold', pad=12)
    ax_map.set_xlabel('Longitud', color='#8892a4')
    ax_map.set_ylabel('Latitud', color='#8892a4')
    ax_map.tick_params(colors='#8892a4')
    for spine in ax_map.spines.values():
        spine.set_edgecolor('#2a2d3a')

    # -- Panel de info --
    ax_info.set_facecolor('#0f1117')
    ax_info.set_xlim(0, 1)
    ax_info.set_ylim(0, 1)
    ax_info.axis('off')

    # Estadisticas globales
    y = 0.97
    def txt(ax, x, y, s, **kw):
        ax.text(x, y, s, transform=ax.transAxes, **kw)

    txt(ax_info, 0, y, 'Estadisticas globales', color='#e2e8f0', fontsize=11, fontweight='bold')
    y -= 0.04
    txt(ax_info, 0, y, f"NDVI medio:  {ndvi_mean:+.4f}", color='#8892a4', fontsize=10)
    y -= 0.03
    txt(ax_info, 0, y, f"Desv. std:    {ndvi_std:.4f}",  color='#8892a4', fontsize=10)
    y -= 0.03
    txt(ax_info, 0, y, f"Pixels validos: {valid_pct:.1f}%", color='#8892a4', fontsize=10)
    y -= 0.03
    txt(ax_info, 0, y, f"Nubes:        {cloud_pct:.1f}%",  color='#8892a4', fontsize=10)
    y -= 0.03
    txt(ax_info, 0, y, f"Nieve:        {snow_pct:.1f}%",   color='#8892a4', fontsize=10)

    # Interpretacion NDVI
    y -= 0.06
    txt(ax_info, 0, y, 'Escala NDVI', color='#e2e8f0', fontsize=11, fontweight='bold')
    y -= 0.01
    scale_items = [
        ('>0.4',        '#1e8449', 'Vegetacion densa'),
        ('0.3–0.4',     '#27ae60', 'Vegetacion buena'),
        ('0.2–0.3',     '#a8d08d', 'Vegetacion moderada'),
        ('0.1–0.2',     '#f1c40f', 'Vegetacion escasa'),
        ('0.0–0.1',     '#e67e22', 'Suelo / muy poca veg.'),
        ('<0.0',        '#c0392b', 'Sin vegetacion / estres'),
        ('nubes/nieve', '#555',    'Sin datos'),
    ]
    for rng, col, label in scale_items:
        y -= 0.04
        ax_info.add_patch(Rectangle((0, y - 0.005), 0.06, 0.03,
                                    facecolor=col, transform=ax_info.transAxes, clip_on=False))
        txt(ax_info, 0.09, y, f"{rng}: {label}", color='#8892a4', fontsize=9)

    # Tabla grilla sectores
    y -= 0.07
    txt(ax_info, 0, y, f'Sectores ({grid_n}x{grid_n})', color='#e2e8f0', fontsize=11, fontweight='bold')
    y -= 0.04
    # Encabezados
    txt(ax_info, 0.0,  y, 'Sector', color='#8892a4', fontsize=8, fontweight='bold')
    txt(ax_info, 0.38, y, 'NDVI',   color='#8892a4', fontsize=8, fontweight='bold')
    txt(ax_info, 0.6,  y, 'Valid%', color='#8892a4', fontsize=8, fontweight='bold')
    txt(ax_info, 0.8,  y, 'Estado', color='#8892a4', fontsize=8, fontweight='bold')

    row_dirs = ['N', 'CN', 'CS', 'S', 'SS']  # filas = norte a sur
    col_dirs = ['O', 'CO', 'CE', 'E', 'EE']  # cols = oeste a este

    for s in grid_stats:
        if y < 0.04:
            break
        y -= 0.035
        rname = row_dirs[s['row']] if s['row'] < len(row_dirs) else str(s['row'])
        cname = col_dirs[s['col']] if s['col'] < len(col_dirs) else str(s['col'])
        sector_name = f"{rname}-{cname}"
        if s['ndvi_mean'] is not None:
            v = s['ndvi_mean']
            if v > 0.3:
                estado, ecol = 'normal', '#22c55e'
            elif v > 0.1:
                estado, ecol = 'bajo', '#eab308'
            elif v > -0.05:
                estado, ecol = 'escaso', '#f97316'
            else:
                estado, ecol = 'estres', '#ef4444'
            txt(ax_info, 0.0,  y, sector_name,         color='#e2e8f0', fontsize=8)
            txt(ax_info, 0.38, y, f"{v:+.3f}",         color=ecol,      fontsize=8, fontweight='bold')
            txt(ax_info, 0.6,  y, f"{s['valid_pct']:.0f}%", color='#8892a4', fontsize=8)
            txt(ax_info, 0.8,  y, estado,              color=ecol,      fontsize=8)
        else:
            txt(ax_info, 0.0,  y, sector_name,  color='#555', fontsize=8)
            txt(ax_info, 0.38, y, 'N/D',        color='#555', fontsize=8)
            txt(ax_info, 0.6,  y, f"{s['valid_pct']:.0f}%", color='#555', fontsize=8)
            txt(ax_info, 0.8,  y, 'n/d',        color='#555', fontsize=8)

    plt.tight_layout(pad=1.5)

    if output_dir is None:
        output_dir = Path(__file__).parent / "datos" / volcan_name.replace(" ", "_")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    out_path = output_dir / f"ndvi_spatial_{fecha}.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='#0f1117')
    plt.close()
    print(f"  Mapa guardado: {out_path}")

    # Guardar array crudo .npy para deteccion de cambios
    npy_path = output_dir / f"ndvi_raw_{fecha}.npy"
    np.save(npy_path, ndvi_display.astype(np.float32))  # NaN donde no hay datos

    # Guardar mascara de validez
    valid_mask_clean = valid & ~cloud & ~snow
    np.save(output_dir / f"ndvi_valid_{fecha}.npy", valid_mask_clean)

    # Guardar metadatos de georreferenciacion
    import json as _json
    meta = {
        'fecha': fecha, 'bbox': list(bbox),
        'shape': [H, W], 'buffer_km': (bbox[2] - bbox[0]) / 2 * 111.0,
        'volcan': volcan_name,
        'ndvi_mean': round(ndvi_mean, 4) if not np.isnan(ndvi_mean) else None,
        'ndvi_std':  round(ndvi_std,  4) if not np.isnan(ndvi_std)  else None,
        'valid_pct': round(valid_pct, 1), 'cloud_pct': round(cloud_pct, 1),
    }
    with open(output_dir / f"ndvi_meta_{fecha}.json", 'w') as f:
        _json.dump(meta, f, indent=2)
    print(f"  Array crudo guardado: {npy_path}")

    # Copiar a docs/
    docs_maps = Path(__file__).parent / "docs" / "maps"
    docs_maps.mkdir(parents=True, exist_ok=True)
    import shutil
    dest = docs_maps / f"{volcan_name.replace(' ', '_')}_spatial_latest.png"
    shutil.copy(out_path, dest)
    print(f"  Copia en docs: {dest}")

    return out_path, grid_stats, {
        'fecha': fecha, 'ndvi_mean': ndvi_mean, 'ndvi_std': ndvi_std,
        'valid_pct': valid_pct, 'cloud_pct': cloud_pct, 'snow_pct': snow_pct,
        'grid_n': grid_n, 'grid_stats': grid_stats
    }


def main():
    parser = argparse.ArgumentParser(description='VegStress-v1 — Mapa NDVI Espacial')
    parser.add_argument('--volcan', default='Laguna del Maule')
    parser.add_argument('--fecha',  default=None,  help='YYYY-MM-DD (si no, busca la mejor reciente)')
    parser.add_argument('--meses',  type=int, default=3, help='Meses hacia atras para buscar imagen')
    parser.add_argument('--grid',   type=int, default=4, help='Tamano de grilla NxN (default 4)')
    args = parser.parse_args()

    if args.volcan not in VOLCANES:
        print(f"Volcan no encontrado. Disponibles: {list(VOLCANES.keys())}")
        return

    config = VOLCANES[args.volcan]
    lat, lon = config['lat'], config['lon']
    buffer_km = config['buffer_km']

    print(f"\n{'='*60}")
    print(f" VegStress-v1 — Mapa NDVI Espacial: {args.volcan}")
    print(f" Buffer: {buffer_km} km | Grilla: {args.grid}x{args.grid}")
    print(f"{'='*60}\n")

    token = get_token()
    print("  Auth OK")

    fecha = args.fecha
    if not fecha:
        fecha = find_best_date(token, lat, lon, buffer_km, meses=args.meses)
        if not fecha:
            print("  No se encontro imagen valida en el periodo.")
            return

    arr, px, bbox = download_ndvi_spatial(token, lat, lon, buffer_km, fecha)
    result = generate_spatial_map(args.volcan, fecha, arr, bbox, grid_n=args.grid)

    if result:
        out_path, grid_stats, stats = result
        print(f"\n  NDVI medio global: {stats['ndvi_mean']:+.4f}")
        print(f"  Pixels validos:    {stats['valid_pct']:.1f}%")
        print(f"\n  Mapa disponible en: {out_path}")


if __name__ == '__main__':
    main()
