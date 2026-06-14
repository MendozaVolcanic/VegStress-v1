"""
gas_pixel_trends.py — Tendencia de NDVI PÍXEL A PÍXEL dentro del área de desgasificación,
para detectar SPOTS CHICOS afectados en las quebradas (no el promedio del polígono).

Por qué (corrección de campo, Nicolás 2026-06-13): la afectación NO cubre todo el polígono;
son zonas pequeñas en las quebradas. Promediar el área entera diluye la señal localizada
(Guinn 2024: el CO2 difuso se concentra en ≤30 m ≈ 3 px Sentinel-2). Por eso acá NO se
promedia: se ajusta una recta a la serie de NDVI de febrero 2021-2026 EN CADA PÍXEL, y se
buscan grupos chicos de píxeles con DECLIVE sostenido (browning / zona de muerte por CO2
alto, sensu Cawse-Nicholson NDVI 0.27→0.10) — y también enverdecimiento localizado.

Mismo-mes (febrero) para anular fenología. Se exige que el píxel haya sido vegetación al
inicio (no buscamos roca), y consistencia temporal (r²) para descartar ruido.

Uso:
    python gas_pixel_trends.py
    python gas_pixel_trends.py --slope_min 0.015 --r2_min 0.5 --min_cluster 2
"""
import sys
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.path import Path as MplPath

ROOT  = Path(__file__).parent
DATOS = ROOT / "datos"
VDIR  = DATOS / "Laguna_del_Maule"
DOCS  = ROOT / "docs" / "maps"
NDVI_VEG = 0.40


def feb_dates():
    out = {}
    for p in VDIR.glob("ndvi_raw_*.npy"):
        d = p.stem.replace("ndvi_raw_", "")
        dt = datetime.strptime(d, '%Y-%m-%d')
        if dt.month == 2:
            out[dt.year] = d
    return [out[y] for y in sorted(out)]


def per_pixel_trend(stack, años):
    """Ajuste lineal por píxel sobre el eje tiempo. Devuelve slope, r2, n_valid (H,W)."""
    T, H, W = stack.shape
    x = años.astype(float)
    valid = np.isfinite(stack)
    n = valid.sum(axis=0)
    # medias ignorando NaN
    xm = np.where(valid, x[:, None, None], np.nan)
    xbar = np.nanmean(xm, axis=0)
    ybar = np.nanmean(stack, axis=0)
    dx = xm - xbar
    dy = stack - ybar
    sxy = np.nansum(dx * dy, axis=0)
    sxx = np.nansum(dx * dx, axis=0)
    with np.errstate(invalid='ignore', divide='ignore'):
        slope = sxy / sxx
        pred = slope[None] * (xm - xbar) + ybar
        ss_res = np.nansum((stack - pred) ** 2, axis=0)
        ss_tot = np.nansum(dy ** 2, axis=0)
        r2 = 1 - ss_res / ss_tot
    return slope, r2, n


def main():
    from scipy.ndimage import label

    ap = argparse.ArgumentParser()
    ap.add_argument('--slope_min', type=float, default=0.015,
                    help='|pendiente| mínima NDVI/año para marcar un píxel')
    ap.add_argument('--r2_min', type=float, default=0.5, help='r² mínimo (consistencia)')
    ap.add_argument('--min_cluster', type=int, default=2, help='píxeles contiguos mínimos por spot')
    ap.add_argument('--pad', type=float, default=0.008)
    args = ap.parse_args()

    area = json.load(open(DATOS / "area_desgasificacion.json", encoding="utf-8"))
    poly_ll = area["poligono_latlon"]
    poly = MplPath([(lo, la) for la, lo in poly_ll])

    febs = feb_dates()
    print(f"\n{'='*64}\n NDVI píxel a píxel — área de gas LdM\n{'='*64}")
    print(f"  Febreros ({len(febs)}): {febs}")
    if len(febs) < 4:
        print("  Se necesitan >=4 febreros."); return

    meta = json.load(open(VDIR / f"ndvi_meta_{febs[-1]}.json"))
    bbox, shape = meta['bbox'], tuple(meta['shape'])
    lon_w, lat_s, lon_e, lat_n = bbox
    H, W = shape
    px_m = (lon_e-lon_w)*111000*abs(np.cos(np.radians((lat_s+lat_n)/2)))/W

    # sub-ventana alrededor del polígono (eficiencia + zoom)
    plons = [lo for la, lo in poly_ll]; plats = [la for la, lo in poly_ll]
    x0 = max(0, int((min(plons)-args.pad - lon_w)/(lon_e-lon_w)*W))
    x1 = min(W, int((max(plons)+args.pad - lon_w)/(lon_e-lon_w)*W))
    y0 = max(0, int((lat_n - (max(plats)+args.pad))/(lat_n-lat_s)*H))
    y1 = min(H, int((lat_n - (min(plats)-args.pad))/(lat_n-lat_s)*H))

    stack = np.stack([np.load(VDIR / f"ndvi_raw_{f}.npy")[y0:y1, x0:x1] for f in febs])
    años = np.array([int(f[:4]) for f in febs])
    hh, ww = stack.shape[1:]

    # máscara polígono en la ventana
    ys, xs = np.mgrid[y0:y1, x0:x1]
    lons = lon_w + (xs+0.5)/W*(lon_e-lon_w); lats = lat_n - (ys+0.5)/H*(lat_n-lat_s)
    in_poly = poly.contains_points(np.column_stack([lons.ravel(), lats.ravel()])).reshape(hh, ww)

    # vegetación al INICIO (no buscamos roca): NDVI>=0.4 en alguno de los 2 primeros febreros
    with np.errstate(invalid='ignore'):
        veg_early = np.nanmax(stack[:2], axis=0) >= NDVI_VEG
    slope, r2, nvalid = per_pixel_trend(stack, años)
    analizable = in_poly & veg_early & (nvalid >= 4)
    print(f"  Píxeles vegetados (inicio) analizables dentro del polígono: {int(analizable.sum())} "
          f"({analizable.sum()*px_m**2/1e4:.2f} ha)")

    def spots(sign):
        if sign < 0:
            sel = analizable & (slope <= -args.slope_min) & (r2 >= args.r2_min)
        else:
            sel = analizable & (slope >= args.slope_min) & (r2 >= args.r2_min)
        lbl, nl = label(sel)
        out = []
        for l in range(1, nl+1):
            comp = lbl == l
            npx = int(comp.sum())
            if npx < args.min_cluster:
                continue
            cy, cx = np.argwhere(comp).mean(axis=0)
            lat = lat_n - (y0+cy+0.5)/H*(lat_n-lat_s); lon = lon_w + (x0+cx+0.5)/W*(lon_e-lon_w)
            serie = [round(float(np.nanmean(stack[t][comp])), 3) for t in range(len(febs))]
            out.append({'n_px': npx, 'area_ha': round(npx*px_m**2/1e4, 3),
                        'slope': round(float(np.nanmean(slope[comp])), 4),
                        'r2': round(float(np.nanmean(r2[comp])), 2),
                        'lat': round(lat, 5), 'lon': round(lon, 5), 'serie_feb': serie})
        out.sort(key=lambda s: s['slope'])
        return out

    decline = spots(-1)
    greening = spots(+1)
    print(f"\n  SPOTS con DECLIVE sostenido (slope<=-{args.slope_min}/año, r²>={args.r2_min}, "
          f">={args.min_cluster}px): {len(decline)}")
    print(f"  {'área_ha':>7s} {'npx':>4s} {'slope':>8s} {'r²':>5s}  serie_feb {febs[0][:4]}..{febs[-1][:4]}  (lat,lon)")
    for s in decline:
        print(f"  {s['area_ha']:>7.3f} {s['n_px']:>4d} {s['slope']:>+8.4f} {s['r2']:>5.2f}  "
              f"{s['serie_feb']}  ({s['lat']:.4f},{s['lon']:.4f})")
    print(f"\n  SPOTS con ENVERDECIMIENTO sostenido: {len(greening)}")
    for s in greening:
        print(f"  {s['area_ha']:>7.3f} {s['n_px']:>4d} {s['slope']:>+8.4f} {s['r2']:>5.2f}  "
              f"{s['serie_feb']}  ({s['lat']:.4f},{s['lon']:.4f})")

    # ── mapa zoom: pendiente por píxel ──
    ndvi_mean = np.nanmean(stack, axis=0)
    fig, ax = plt.subplots(figsize=(12, 11), facecolor='#0f1117')
    ext = [lon_w + x0/W*(lon_e-lon_w), lon_w + x1/W*(lon_e-lon_w),
           lat_n - y1/H*(lat_n-lat_s), lat_n - y0/H*(lat_n-lat_s)]
    ax.imshow(ndvi_mean, cmap='Greys_r', vmin=-0.1, vmax=0.6, extent=ext, origin='upper', aspect='auto')
    sl_map = np.where(analizable, slope, np.nan)
    vmax = 0.05
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    cmap = mcolors.LinearSegmentedColormap.from_list('s', ['#7B0000','#e05c20','#f0f0f0','#7cc35a','#10500f'])
    im = ax.imshow(sl_map, cmap=cmap, norm=norm, extent=ext, origin='upper', aspect='auto')
    ax.plot(plons+[plons[0]], plats+[plats[0]], '-', color='#ff3b3b', lw=2.2, zorder=6,
            label='Área desgasificación (campo)')
    for s in decline:
        ax.add_patch(plt.Circle((s['lon'], s['lat']), 0.0006, fill=False, edgecolor='#ff3b3b',
                                lw=1.6, zorder=7))
    for s in greening:
        ax.add_patch(plt.Circle((s['lon'], s['lat']), 0.0006, fill=False, edgecolor='#00e5ff',
                                lw=1.6, zorder=7))
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.01)
    cbar.set_label('Pendiente NDVI/año por píxel (rojo=declive, verde=enverdece)', color='#8892a4')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8892a4'); cbar.ax.yaxis.set_tick_params(color='#8892a4')
    ax.set_title(f'Área de desgasificación LdM — tendencia NDVI por píxel (febreros {años[0]}-{años[-1]})\n'
                 f'spots con declive (rojo) / enverdecimiento (cian) sostenido', color='#e2e8f0',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Longitud', color='#8892a4'); ax.set_ylabel('Latitud', color='#8892a4'); ax.tick_params(colors='#8892a4')
    ax.legend(facecolor='#1a1d26', labelcolor='#e2e8f0', edgecolor='#2a2d3a', fontsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor('#2a2d3a')
    out = DOCS / "Laguna_del_Maule_gas_pixel_trends.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=160, facecolor='#0f1117', bbox_inches='tight'); plt.close()
    print(f"\n  Mapa: {out}")

    json.dump({'febreros': febs, 'slope_min': args.slope_min, 'r2_min': args.r2_min,
               'min_cluster': args.min_cluster, 'spots_declive': decline, 'spots_greening': greening},
              open(VDIR / "gas_pixel_trends.json", 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"  JSON: {VDIR / 'gas_pixel_trends.json'}")


if __name__ == '__main__':
    main()
