"""
drone_vegindex.py — Índices de vegetación a cm-escala sobre ORTOMOSAICOS DE DRON.

Por qué (fase de integración con campo, 2026-06): Sentinel-2 (10 m) no resuelve los spots
de venteo de <30 m sobre vegetación rala (resultado negativo multi-escala, ver
docs/BASELINE_LdM.md). El dron de la campaña OVDAS (objetivos fotogramétricos) entrega
ortomosaicos de cm/px que SÍ pueden resolver la afectación localizada de la vegetación
alrededor de los venteos. Este pipeline está listo para ingerir esos ortomosaicos.

Soporta:
  - Dron MULTIESPECTRAL (con NIR / red-edge): NDVI, NDRE (los índices fisiológicos reales).
  - Dron RGB (típico de fotogrametría/DEM, sin NIR): índices de verdor de banda visible
    VARI, GLI, ExG — correlacionan con vigor/clorofila cuando no hay NIR (menos potentes
    que NDVI, pero útiles a cm-escala).

El orden de bandas varía por sensor → se especifica con --bands (ej. "R,G,B,RE,NIR").
Los puntos de venteo NO van hardcodeados (info de campo sensible): se leen de un archivo
local --puntos (JSON [{nombre,lat,lon}], gitignored) o se pasan por --lat/--lon.

Uso:
    # multiespectral (MicaSense/DJI P4MS, orden B,G,R,RE,NIR):
    python drone_vegindex.py ortho.tif --bands B,G,R,RE,NIR --index ndvi --puntos datos/_vent_points.json
    # RGB:
    python drone_vegindex.py ortho_rgb.tif --bands R,G,B --index vari --lat -36.111 --lon -70.573
"""
import sys
import json
import argparse
import numpy as np
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Definición de índices: qué bandas necesita cada uno (falla claro si faltan).
INDEX_DEFS = {
    "ndvi": {"needs": ["NIR", "R"], "desc": "(NIR-R)/(NIR+R) — vigor (necesita NIR)"},
    "ndre": {"needs": ["NIR", "RE"], "desc": "(NIR-RE)/(NIR+RE) — estrés temprano (necesita red-edge)"},
    "gndvi": {"needs": ["NIR", "G"], "desc": "(NIR-G)/(NIR+G) — clorofila (necesita NIR)"},
    "vari": {"needs": ["R", "G", "B"], "desc": "(G-R)/(G+R-B) — verdor RGB (sin NIR)"},
    "gli":  {"needs": ["R", "G", "B"], "desc": "(2G-R-B)/(2G+R+B) — Green Leaf Index (RGB)"},
    "exg":  {"needs": ["R", "G", "B"], "desc": "2g-r-b normalizado — Excess Green (RGB)"},
}


def load_ortho(path):
    """Lee un ortomosaico GeoTIFF. Devuelve (arr[bands,H,W] float32, transform, crs)."""
    import rasterio
    with rasterio.open(path) as ds:
        arr = ds.read().astype(np.float32)
        # tratar nodata como NaN
        if ds.nodata is not None:
            arr[arr == ds.nodata] = np.nan
        return arr, ds.transform, ds.crs


def _b(arr, bandmap, name):
    if name not in bandmap:
        raise ValueError(f"Banda '{name}' no disponible en --bands {list(bandmap)}")
    return arr[bandmap[name]]


def compute_index(arr, bandmap, index_name):
    """Computa un índice de vegetación. bandmap: {'R':idx,'G':..,'NIR':..,'RE':..}."""
    index_name = index_name.lower()
    if index_name not in INDEX_DEFS:
        raise ValueError(f"Índice '{index_name}' desconocido. Opciones: {list(INDEX_DEFS)}")
    for need in INDEX_DEFS[index_name]["needs"]:
        if need not in bandmap:
            raise ValueError(f"El índice {index_name} necesita la banda {need}, "
                             f"no está en --bands {list(bandmap)}")
    eps = 1e-6
    with np.errstate(invalid='ignore', divide='ignore'):
        if index_name == "ndvi":
            nir, r = _b(arr, bandmap, "NIR"), _b(arr, bandmap, "R")
            return (nir - r) / (nir + r + eps)
        if index_name == "ndre":
            nir, re = _b(arr, bandmap, "NIR"), _b(arr, bandmap, "RE")
            return (nir - re) / (nir + re + eps)
        if index_name == "gndvi":
            nir, g = _b(arr, bandmap, "NIR"), _b(arr, bandmap, "G")
            return (nir - g) / (nir + g + eps)
        r, g, b = _b(arr, bandmap, "R"), _b(arr, bandmap, "G"), _b(arr, bandmap, "B")
        if index_name == "vari":
            return (g - r) / (g + r - b + eps)
        if index_name == "gli":
            return (2*g - r - b) / (2*g + r + b + eps)
        if index_name == "exg":
            s = r + g + b + eps
            rn, gn, bn = r/s, g/s, b/s
            return 2*gn - rn - bn


def latlon_to_rowcol(lat, lon, transform, crs):
    """Convierte lat/lon (EPSG:4326) a (row, col) del raster, reproyectando al CRS del raster."""
    from rasterio.warp import transform as warp_transform
    from rasterio.crs import CRS
    xs, ys = warp_transform(CRS.from_epsg(4326), crs, [lon], [lat])
    x, y = xs[0], ys[0]
    # invertir el affine: col,row desde x,y
    col, row = ~transform * (x, y)
    return row, col


def analyze_window(index, row, col, radius_px=50, veg_thr=0.3):
    """Estadística del índice en una ventana cuadrada alrededor de (row,col)."""
    H, W = index.shape
    r0, r1 = max(0, int(row - radius_px)), min(H, int(row + radius_px) + 1)
    c0, c1 = max(0, int(col - radius_px)), min(W, int(col + radius_px) + 1)
    win = index[r0:r1, c0:c1]
    vals = win[np.isfinite(win)]
    if len(vals) == 0:
        return {"n_total": 0, "error": "ventana fuera del raster o sin datos"}
    veg = vals[vals >= veg_thr]
    return {
        "n_total": int(len(vals)),
        "n_veg": int(len(veg)),
        "pct_veg": round(float(len(veg) / len(vals) * 100), 1),
        "mean": round(float(np.mean(vals)), 4),
        "mean_veg": round(float(np.mean(veg)), 4) if len(veg) else None,
        "p10": round(float(np.percentile(vals, 10)), 4),
        "p90": round(float(np.percentile(vals, 90)), 4),
        "window_px": [r0, r1, c0, c1],
    }


def make_map(index, points_rc, index_name, out_path, radius_px=50):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    cmap = mcolors.LinearSegmentedColormap.from_list('veg', [
        '#7a3b1a', '#b58a3a', '#e8d98a', '#9fd17a', '#3a9d23', '#0d4f1e'])
    fig, ax = plt.subplots(figsize=(11, 10), facecolor='#0f1117')
    vmin = float(np.nanpercentile(index, 2)); vmax = float(np.nanpercentile(index, 98))
    im = ax.imshow(index, cmap=cmap, vmin=vmin, vmax=vmax)
    for nombre, (row, col) in points_rc.items():
        ax.add_patch(plt.Circle((col, row), radius_px, fill=False, edgecolor='#00e5ff', lw=2))
        ax.plot(col, row, '+', color='#ff3b3b', ms=12, mew=2)
        ax.text(col, row - radius_px - 8, nombre, color='#00e5ff', fontsize=9,
                ha='center', fontweight='bold')
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.01)
    cbar.set_label(index_name.upper(), color='#8892a4')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8892a4'); cbar.ax.yaxis.set_tick_params(color='#8892a4')
    ax.set_title(f'Dron — {index_name.upper()} sobre venteos', color='#e2e8f0', fontweight='bold')
    ax.tick_params(colors='#8892a4')
    for sp in ax.spines.values(): sp.set_edgecolor('#2a2d3a')
    plt.savefig(out_path, dpi=130, facecolor='#0f1117', bbox_inches='tight'); plt.close()


def main():
    ap = argparse.ArgumentParser(description='Índices de vegetación sobre ortomosaicos de dron')
    ap.add_argument('ortho', help='GeoTIFF del ortomosaico de dron (georreferenciado)')
    ap.add_argument('--bands', required=True,
                    help='Orden de bandas, p.ej. "R,G,B" o "B,G,R,RE,NIR" (nombres: R,G,B,RE,NIR)')
    ap.add_argument('--index', default='auto', help='ndvi|ndre|gndvi|vari|gli|exg|auto')
    ap.add_argument('--puntos', default=None, help='JSON local [{nombre,lat,lon}] de venteos (gitignored)')
    ap.add_argument('--lat', type=float, default=None)
    ap.add_argument('--lon', type=float, default=None)
    ap.add_argument('--radio_m', type=float, default=10, help='radio de la ventana de análisis (m)')
    ap.add_argument('--veg_thr', type=float, default=0.3, help='umbral del índice para "vegetación"')
    ap.add_argument('--out', default=None, help='prefijo de salida (default: junto al ortho)')
    args = ap.parse_args()

    bandmap = {n.strip().upper(): i for i, n in enumerate(args.bands.split(','))}
    arr, transform, crs = load_ortho(args.ortho)
    nbands = arr.shape[0]
    print(f"\nOrtomosaico: {args.ortho}")
    print(f"  bandas={nbands}  CRS={crs}  tamaño={arr.shape[1]}x{arr.shape[2]} px")
    res_m = abs(transform.a)
    print(f"  resolución ≈ {res_m*100:.1f} cm/px")

    index_name = args.index.lower()
    if index_name == 'auto':
        index_name = 'ndvi' if 'NIR' in bandmap and 'R' in bandmap else 'vari'
        print(f"  índice auto-elegido: {index_name} ({INDEX_DEFS[index_name]['desc']})")
    index = compute_index(arr, bandmap, index_name)

    # puntos de venteo
    pts = []
    if args.puntos and Path(args.puntos).exists():
        pts = json.load(open(args.puntos, encoding='utf-8'))
    elif args.lat is not None and args.lon is not None:
        pts = [{"nombre": "punto", "lat": args.lat, "lon": args.lon}]
    else:
        print("  [aviso] sin puntos de venteo (--puntos o --lat/--lon). Solo genero el índice.")

    radius_px = max(1, int(args.radio_m / res_m))
    points_rc, stats = {}, {}
    for p in pts:
        row, col = latlon_to_rowcol(p['lat'], p['lon'], transform, crs)
        if not (0 <= row < index.shape[0] and 0 <= col < index.shape[1]):
            print(f"  [aviso] '{p['nombre']}' ({p['lat']},{p['lon']}) cae FUERA del ortomosaico.")
            continue
        points_rc[p['nombre']] = (row, col)
        st = analyze_window(index, row, col, radius_px, args.veg_thr)
        stats[p['nombre']] = st
        print(f"\n  Venteo '{p['nombre']}' ({p['lat']},{p['lon']}) | ventana ±{args.radio_m} m ({radius_px}px):")
        print(f"    {index_name.upper()} medio={st.get('mean')}  veg={st.get('pct_veg')}%  "
              f"medio_veg={st.get('mean_veg')}  p10={st.get('p10')} p90={st.get('p90')}")

    out_prefix = args.out or str(Path(args.ortho).with_suffix(''))
    if points_rc:
        make_map(index, points_rc, index_name, out_prefix + f"_{index_name}.png", radius_px)
        print(f"\n  Mapa: {out_prefix}_{index_name}.png")
    json.dump({"ortho": args.ortho, "index": index_name, "res_cm_px": round(res_m*100, 1),
               "stats": stats}, open(out_prefix + f"_{index_name}_stats.json", 'w', encoding='utf-8'),
              indent=2, ensure_ascii=False)
    print(f"  Stats: {out_prefix}_{index_name}_stats.json")


if __name__ == '__main__':
    main()
