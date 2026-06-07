"""
riparian_finder.py — Extrae los HILOS de vegetación riparia (lineales) de una escena
y propone AOIs tipo "quebrada" siguiendo su centerline.

Por qué (decisión de campo, Nicolás 2026-06-07): en Laguna del Maule el CO2 difuso se
concentra en las QUEBRADAS. La vegetación sana de la caldera no son parches grandes
(esos están en bordes/valles lejos del gas) sino HILOS RIPARIOS finos a lo largo de
los drenajes — justo donde Guinn et al. 2024 (PD-001) dice que el gas se concentra
(≤30 m de la estructura). aoi_finder.py busca parches grandes; este script busca lo
contrario: features lineales finas y alargadas.

Método (data-driven, sin DEM):
  1. Vegetación estable: NDVI∈[0.41, 0.95] en TODAS las fechas (Ojeda 2011 PD-016,
     Guinn 2024 PD-001 L882). Igual criterio que aoi_finder.py.
  2. Por cada componente conexa de vegetación, se mide su esqueleto (centerline).
     Un HILO tiene ancho≈área/longitud pequeño y longitud grande; un PARCHE tiene
     ancho grande. Se filtran los hilos (finos y largos).
  3. Se ordena el esqueleto en una polilínea (proyección PCA sobre el eje principal)
     y se submuestrea a waypoints lat/lon.
  4. Se genera un mapa numerado + JSON para que Nicolás confirme cuáles son quebradas
     de desgasificación conocida → se vuelcan a aoi_config.json como AOIs tipo línea.

Uso:
    python riparian_finder.py --volcan "Laguna del Maule"
    python riparian_finder.py --volcan "Laguna del Maule" --max_width_m 80 --min_len_m 150
"""
import sys
import json
import argparse
import numpy as np
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

ROOT  = Path(__file__).parent
DATOS = ROOT / "datos"
DOCS  = ROOT / "docs"

NDVI_VEG_MIN = 0.41   # Ojeda 2011 (PD-016) — piso de bosque sano
NDVI_VEG_MAX = 0.95   # tope físico


def list_dates(volcan):
    vdir = DATOS / volcan.replace(" ", "_")
    return sorted(p.stem.replace("ndvi_raw_", "") for p in vdir.glob("ndvi_raw_*.npy"))


def load_stack(volcan):
    vdir = DATOS / volcan.replace(" ", "_")
    dates = list_dates(volcan)
    arrs, meta = [], None
    for f in dates:
        arrs.append(np.load(vdir / f"ndvi_raw_{f}.npy"))
        mp = vdir / f"ndvi_meta_{f}.json"
        if mp.exists() and meta is None:
            meta = json.load(open(mp))
    return np.stack(arrs), meta, dates


def px_size_m(bbox, shape):
    """Tamaño de pixel en metros (x, y) usando 111 km/° y cos(lat)."""
    lon_w, lat_s, lon_e, lat_n = bbox
    H, W = shape
    lat_med = (lat_s + lat_n) / 2
    mx = (lon_e - lon_w) * 111000.0 * abs(np.cos(np.radians(lat_med))) / W
    my = (lat_n - lat_s) * 111000.0 / H
    return mx, my


def px_to_lonlat(cx, cy, bbox, shape):
    lon_w, lat_s, lon_e, lat_n = bbox
    H, W = shape
    lon = lon_w + (cx / W) * (lon_e - lon_w)
    lat = lat_n - (cy / H) * (lat_n - lat_s)
    return lon, lat


def order_polyline(ys, xs, step_px):
    """Ordena los píxeles del esqueleto en una polilínea por proyección PCA y los
    submuestrea cada `step_px`. Robusto para hilos aproximadamente lineales."""
    pts = np.column_stack([xs.astype(float), ys.astype(float)])  # (N,2) -> (x,y)
    c = pts.mean(axis=0)
    # eje principal (mayor varianza)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    axis = vt[0]
    proj = (pts - c) @ axis
    order = np.argsort(proj)
    pts_sorted = pts[order]
    step = max(1, int(step_px))
    wp = pts_sorted[::step]
    if len(wp) == 0:
        wp = pts_sorted[[0]]
    # asegurar incluir el último extremo
    if not np.array_equal(wp[-1], pts_sorted[-1]):
        wp = np.vstack([wp, pts_sorted[-1]])
    return wp  # array (M,2) de (x,y)


def polyline_length_m(wp_xy, mx, my):
    if len(wp_xy) < 2:
        return 0.0
    d = np.diff(wp_xy, axis=0)
    seg = np.sqrt((d[:, 0] * mx) ** 2 + (d[:, 1] * my) ** 2)
    return float(seg.sum())


def find_threads(volcan, max_width_m=80, min_len_m=150, min_area_px=20,
                 max_threads=15, waypoint_step_m=120):
    from scipy.ndimage import label
    from skimage.morphology import skeletonize

    stack, meta, dates = load_stack(volcan)
    if meta is None:
        print("  Sin metadatos.")
        return None
    bbox = meta['bbox']
    shape = tuple(meta['shape'])
    mx, my = px_size_m(bbox, shape)
    px_m = (mx + my) / 2

    with np.errstate(invalid='ignore'):
        veg_each = (stack >= NDVI_VEG_MIN) & (stack <= NDVI_VEG_MAX)
    veg_stable = veg_each.all(axis=0)
    ndvi_mean = np.nanmean(stack, axis=0)

    n_veg = int(veg_stable.sum())
    print(f"  {volcan}: {n_veg} px de vegetación estable ({n_veg/veg_stable.size*100:.2f}% "
          f"de la escena), pixel ≈ {px_m:.1f} m, {len(dates)} fechas.")

    # esqueleto global, luego intersección por componente
    skel = skeletonize(veg_stable)
    lbl, nlbl = label(veg_stable)
    if nlbl == 0:
        print("  Sin componentes de vegetación.")
        return None

    max_width_px = max_width_m / px_m
    min_len_px   = min_len_m / px_m
    step_px      = max(2, int(round(waypoint_step_m / px_m)))

    threads = []
    for l in range(1, nlbl + 1):
        comp = (lbl == l)
        area = int(comp.sum())
        if area < min_area_px:
            continue
        sk = skel & comp
        slen = int(sk.sum())
        if slen < 3:
            continue
        width_px = area / slen           # ancho medio ≈ área / longitud
        len_m = slen * px_m
        # FILTRO DE HILO: fino (ancho pequeño) y largo
        if width_px > max_width_px or len_m < min_len_m:
            continue

        ys, xs = np.where(sk)
        wp_xy = order_polyline(ys, xs, step_px)
        length_m = polyline_length_m(wp_xy, mx, my)
        if length_m < min_len_m:
            continue
        wp_lonlat = [list(px_to_lonlat(x, y, bbox, shape)) for x, y in wp_xy]
        # waypoints como [lat, lon] (orden que consume aoi_geometry/aoi_config)
        wp_latlon = [[round(lat, 5), round(lon, 5)] for lon, lat in wp_lonlat]
        ndvi_medio = float(np.nanmean(ndvi_mean[sk]))
        cx, cy = xs.mean(), ys.mean()
        clon, clat = px_to_lonlat(cx, cy, bbox, shape)
        threads.append({
            'waypoints': wp_latlon,
            'length_m': round(length_m, 0),
            'width_m': round(width_px * px_m, 1),
            'area_ha': round(area * (px_m ** 2) / 1e4, 2),
            'ndvi_medio': round(ndvi_medio, 3),
            'centro': [round(clat, 5), round(clon, 5)],
            '_cx': float(cx), '_cy': float(cy),
        })

    threads.sort(key=lambda t: t['length_m'], reverse=True)
    threads = threads[:max_threads]

    # distancia al centro de caldera (para juzgar proximidad al gas)
    cfg_path = DATOS / "aoi_config.json"
    cen_lat = cen_lon = None
    if cfg_path.exists():
        cfg = json.load(open(cfg_path, encoding='utf-8'))
        v = cfg.get('volcanes', {}).get(volcan, {})
        cen_lat, cen_lon = v.get('centro_lat'), v.get('centro_lon')
    if cen_lat is not None:
        for t in threads:
            dlat = (t['centro'][0] - cen_lat) * 111000.0
            dlon = (t['centro'][1] - cen_lon) * 111000.0 * abs(np.cos(np.radians(cen_lat)))
            t['dist_caldera_km'] = round(np.hypot(dlat, dlon) / 1000.0, 2)

    print(f"  {len(threads)} hilo(s) riparios (ancho≤{max_width_m} m, largo≥{min_len_m} m).")
    return threads, ndvi_mean, bbox, shape


def generate_map(volcan, ndvi_mean, threads, bbox, shape):
    lon_w, lat_s, lon_e, lat_n = bbox
    fig, ax = plt.subplots(figsize=(13, 12), facecolor='#0f1117')
    cmap = mcolors.LinearSegmentedColormap.from_list('veg', [
        '#2b2b2b', '#5a4a3a', '#8a7a3a', '#b7d77a', '#3a9d23', '#10500f'])
    im = ax.imshow(ndvi_mean, cmap=cmap, vmin=-0.1, vmax=0.8,
                   extent=[lon_w, lon_e, lat_s, lat_n], origin='upper', aspect='auto')
    for i, t in enumerate(threads, 1):
        wp_lon = [w[1] for w in t['waypoints']]
        wp_lat = [w[0] for w in t['waypoints']]
        ax.plot(wp_lon, wp_lat, color='#00e5ff', linewidth=2.6, zorder=5,
                solid_capstyle='round')
        ax.text(t['centro'][1], t['centro'][0], f"Q{i}", ha='center', va='center',
                color='#00e5ff', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.18', facecolor='black', alpha=0.7, linewidth=0))
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.01)
    cbar.set_label('NDVI medio (todas las fechas)', color='#8892a4')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8892a4')
    cbar.ax.yaxis.set_tick_params(color='#8892a4')
    ax.set_title(f'{volcan} — Hilos de vegetación riparia (candidatos a quebradas)\n'
                 f'centerline NDVI {NDVI_VEG_MIN}-{NDVI_VEG_MAX} estable, features lineales finas',
                 color='#e2e8f0', fontsize=13, fontweight='bold')
    ax.set_xlabel('Longitud', color='#8892a4'); ax.set_ylabel('Latitud', color='#8892a4')
    ax.tick_params(colors='#8892a4')
    for sp in ax.spines.values():
        sp.set_edgecolor('#2a2d3a')
    out = DOCS / "maps" / f"{volcan.replace(' ', '_')}_quebradas_candidatas.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=145, bbox_inches='tight', facecolor='#0f1117')
    plt.close()
    print(f"  Mapa guardado: {out}")
    return out


def main():
    ap = argparse.ArgumentParser(description='Extractor de hilos de vegetación riparia')
    ap.add_argument('--volcan', default='Laguna del Maule')
    ap.add_argument('--max_width_m', type=float, default=80,
                    help='Ancho máx del hilo (m) para considerarlo riparian')
    ap.add_argument('--min_len_m', type=float, default=150,
                    help='Largo mín del hilo (m)')
    ap.add_argument('--max_threads', type=int, default=15)
    ap.add_argument('--waypoint_step_m', type=float, default=120,
                    help='Separación entre waypoints de la polilínea (m)')
    args = ap.parse_args()

    print(f"\n{'='*64}\n Hilos riparios — {args.volcan}\n{'='*64}")
    res = find_threads(args.volcan, args.max_width_m, args.min_len_m,
                       max_threads=args.max_threads, waypoint_step_m=args.waypoint_step_m)
    if not res:
        print("  Sin hilos candidatos.")
        return
    threads, ndvi_mean, bbox, shape = res

    print(f"\n  {'#':>3s} {'largo_m':>8s} {'ancho_m':>8s} {'NDVI':>5s} {'dist_cald_km':>12s}  centro(lat,lon)")
    for i, t in enumerate(threads, 1):
        dc = t.get('dist_caldera_km', float('nan'))
        print(f"  Q{i:<2d} {t['length_m']:>8.0f} {t['width_m']:>8.1f} {t['ndvi_medio']:>5.2f} "
              f"{dc:>12.2f}  {t['centro'][0]:.4f}, {t['centro'][1]:.4f}")

    generate_map(args.volcan, ndvi_mean, threads, bbox, shape)

    # limpiar campos internos antes de guardar
    for t in threads:
        t.pop('_cx', None); t.pop('_cy', None)
    out_json = DATOS / args.volcan.replace(' ', '_') / "quebradas_candidatas.json"
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump({'volcan': args.volcan,
                   'criterio': f'centerline NDVI {NDVI_VEG_MIN}-{NDVI_VEG_MAX} estable, '
                               f'hilo fino (≤{args.max_width_m} m) y largo (≥{args.min_len_m} m)',
                   'buffer_m_sugerido': 30,
                   '_nota': 'Guinn 2024 PD-001: CO2 difuso a ≤30 m de la estructura.',
                   'quebradas': threads}, f, indent=2, ensure_ascii=False)
    print(f"\n  Propuesta guardada: {out_json}")
    print(f"  → Revisar el mapa _quebradas_candidatas.png y confirmar cuáles son "
          f"quebradas de desgasificación conocida.")


if __name__ == '__main__':
    main()
