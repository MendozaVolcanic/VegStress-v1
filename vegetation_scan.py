"""
vegetation_scan.py — Escaneo de RED ANCHA sobre TODA la vegetación de la escena.

Por qué (decisión 2026-06-13, Nicolás): en vez de monitorear solo 15 hilos elegidos a
mano, revisar TODAS las quebradas y parches con vegetación, para no perder ninguna señal.

Cómo separa la señal volcánica del clima (la lección de esta semana):
  El confusor climático (un verano más/menos lluvioso) afecta a TODA la cuenca por igual
  (lo vimos: el "greening" de Q8/Q9 era clima regional + artefacto fenológico). Por eso
  este escaneo descuenta el clima ESPACIALMENTE: calcula el ΔNDVI de cada componente de
  vegetación y le resta el ΔNDVI MEDIANO de toda la cuenca. El RESIDUO aísla las zonas que
  cambian MÁS que el fondo climático — esas son las candidatas a señal localizada
  (CO2 difuso a ≤30 m, Guinn 2024), no el enverdecimiento general por lluvia.

Criterio de vegetación: NDVI∈[0.41,0.95] en >=`min_frac` de las fechas (default 70%).
Más inclusivo que "estable en todas las fechas" (que excluye caducifolias que bajan en
otoño) y más robusto que "en alguna fecha" (que mete ruido efímero).

Comparación por defecto: el par inter-anual MISMO-MES más reciente disponible (p.ej.
2025-02-18 -> 2026-02-16). Comparar el mismo mes anula la fenología estacional.

Uso:
    python vegetation_scan.py --volcan "Laguna del Maule"
    python vegetation_scan.py --volcan "Laguna del Maule" --fecha_a 2025-02-18 --fecha_b 2026-02-16
    python vegetation_scan.py --volcan "Laguna del Maule" --min_frac 0.7 --min_area_ha 0.3
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

ROOT  = Path(__file__).parent
DATOS = ROOT / "datos"
DOCS  = ROOT / "docs"

NDVI_VEG_MIN = 0.41   # Ojeda 2011 (PD-016)
NDVI_VEG_MAX = 0.95
NDVI_MIN_VALIDO = 0.40  # Guinn 2024 L882 (para stats de cambio)


def list_dates(volcan):
    vdir = DATOS / volcan.replace(" ", "_")
    return sorted(p.stem.replace("ndvi_raw_", "") for p in vdir.glob("ndvi_raw_*.npy"))


def load_meta(volcan, fecha):
    vdir = DATOS / volcan.replace(" ", "_")
    return json.load(open(vdir / f"ndvi_meta_{fecha}.json"))


def load_arr(volcan, fecha):
    vdir = DATOS / volcan.replace(" ", "_")
    return np.load(vdir / f"ndvi_raw_{fecha}.npy")


def pick_same_month_pair(dates):
    """Elige el par inter-anual MISMO-MES más reciente (mismo mes, años distintos)."""
    by = [(datetime.strptime(d, '%Y-%m-%d'), d) for d in dates]
    # buscar el par con mismo mes y mayor año-b, maximizando recencia
    best = None
    for i in range(len(by)):
        for j in range(i + 1, len(by)):
            da, db = by[i], by[j]
            if da[0].month == db[0].month and da[0].year != db[0].year:
                # b = más reciente
                a, b = (da, db) if da[0] < db[0] else (db, da)
                score = b[0].year * 100 + b[0].month
                if best is None or score > best[0]:
                    best = (score, a[1], b[1])
    if best:
        return best[1], best[2]
    return (dates[0], dates[-1]) if len(dates) >= 2 else (None, None)


def build_veg_mask(volcan, dates, min_frac):
    arrs = [load_arr(volcan, f) for f in dates]
    stack = np.stack(arrs)
    with np.errstate(invalid='ignore'):
        veg_each = (stack >= NDVI_VEG_MIN) & (stack <= NDVI_VEG_MAX)
    frac = veg_each.sum(axis=0) / len(dates)
    veg = frac >= min_frac
    ndvi_mean = np.nanmean(stack, axis=0)
    return veg, ndvi_mean


def classify_shape(comp, skel):
    area = int(comp.sum())
    sl = int((skel & comp).sum())
    if sl < 3:
        return 'parche', area, 0.0
    width_px = area / sl
    return ('quebrada' if width_px <= 8 else 'parche'), area, width_px


def px_to_lonlat(cx, cy, bbox, shape):
    lon_w, lat_s, lon_e, lat_n = bbox
    H, W = shape
    return (lon_w + cx / W * (lon_e - lon_w), lat_n - cy / H * (lat_n - lat_s))


def scan(volcan, fecha_a, fecha_b, min_frac, min_area_ha):
    from scipy.ndimage import label, center_of_mass
    from skimage.morphology import skeletonize

    dates = list_dates(volcan)
    if len(dates) < 2:
        print("  Se necesitan >=2 fechas."); return None
    if not (fecha_a and fecha_b):
        fecha_a, fecha_b = pick_same_month_pair(dates)
    print(f"  Comparación inter-anual mismo-mes: {fecha_a} -> {fecha_b}")

    meta = load_meta(volcan, fecha_b)
    bbox, shape = meta['bbox'], tuple(meta['shape'])
    px_m = (bbox[2] - bbox[0]) * 111000 * abs(np.cos(np.radians((bbox[1]+bbox[3])/2))) / shape[1]
    min_area_px = max(5, int(min_area_ha * 1e4 / px_m**2))

    veg, ndvi_mean = build_veg_mask(volcan, dates, min_frac)
    arr_a, arr_b = load_arr(volcan, fecha_a), load_arr(volcan, fecha_b)
    with np.errstate(invalid='ignore'):
        delta = arr_b - arr_a

    skel = skeletonize(veg)
    lbl, nl = label(veg)
    print(f"  Vegetación (NDVI {NDVI_VEG_MIN}-{NDVI_VEG_MAX} en >={min_frac*100:.0f}% de "
          f"{len(dates)} fechas): {int(veg.sum())} px ({veg.sum()/veg.size*100:.2f}%), "
          f"{nl} componentes; min área {min_area_ha} ha = {min_area_px} px.")

    comps = []
    for l in range(1, nl + 1):
        comp = (lbl == l)
        area = int(comp.sum())
        if area < min_area_px:
            continue
        shape_t, _, width_px = classify_shape(comp, skel)
        # cambio solo sobre pixels con veg fiable en AMBAS fechas (Guinn L882)
        with np.errstate(invalid='ignore'):
            veg_both = comp & (arr_a >= NDVI_MIN_VALIDO) & (arr_b >= NDVI_MIN_VALIDO) & ~np.isnan(delta)
        n_both = int(veg_both.sum())
        if n_both < 10:
            continue
        d_mean = float(np.mean(delta[veg_both]))
        cy, cx = center_of_mass(comp)
        lon, lat = px_to_lonlat(cx, cy, bbox, shape)
        comps.append({
            'shape': shape_t, 'area_ha': round(area * px_m**2 / 1e4, 2),
            'width_m': round(width_px * px_m, 0),
            'lat': round(lat, 5), 'lon': round(lon, 5),
            'ndvi_a': round(float(np.mean(arr_a[veg_both])), 3),
            'ndvi_b': round(float(np.mean(arr_b[veg_both])), 3),
            'delta': round(d_mean, 4), 'n_px': n_both,
        })

    if not comps:
        print("  Sin componentes de vegetación suficientes."); return None

    # ── descuento climático espacial: residuo vs mediana de la cuenca ──
    deltas = np.array([c['delta'] for c in comps])
    basin_med = float(np.median(deltas))
    basin_mad = float(np.median(np.abs(deltas - basin_med))) or 1e-6
    for c in comps:
        c['residual'] = round(c['delta'] - basin_med, 4)
        # z robusto (residuo en unidades de MAD escalado): qué tan atípico vs la cuenca
        c['z_robusto'] = round((c['delta'] - basin_med) / (1.4826 * basin_mad), 2)

    comps.sort(key=lambda c: c['residual'], reverse=True)
    print(f"\n  ΔNDVI mediano de la cuenca (fondo climático): {basin_med:+.4f}  "
          f"(MAD {basin_mad:.4f})")
    print(f"  {len(comps)} componentes vegetados analizados. "
          f"Convenio: Δ>0 greening, residual>0 = enverdece MÁS que el fondo climático.")

    return {'fecha_a': fecha_a, 'fecha_b': fecha_b, 'bbox': bbox, 'shape': shape,
            'basin_median_delta': round(basin_med, 4), 'comps': comps,
            'ndvi_mean': ndvi_mean, 'delta': delta, 'veg': veg}


def report_and_map(volcan, res, top=12):
    comps = res['comps']
    print(f"\n  ── TOP {top} anomalías de GREENING (enverdecen más que el fondo) ──")
    print(f"  {'#':>3s} {'forma':9s} {'área_ha':>7s} {'ΔNDVI':>7s} {'resid':>7s} {'zrob':>5s}  centro(lat,lon)")
    for i, c in enumerate(comps[:top], 1):
        print(f"  G{i:<2d} {c['shape']:9s} {c['area_ha']:>7.2f} {c['delta']:>+7.3f} "
              f"{c['residual']:>+7.3f} {c['z_robusto']:>5.1f}  {c['lat']:.4f}, {c['lon']:.4f}")
    print(f"\n  ── TOP {top} anomalías de BROWNING (pierden más vigor que el fondo) ──")
    print(f"  {'#':>3s} {'forma':9s} {'área_ha':>7s} {'ΔNDVI':>7s} {'resid':>7s} {'zrob':>5s}  centro(lat,lon)")
    for i, c in enumerate(comps[::-1][:top], 1):
        print(f"  B{i:<2d} {c['shape']:9s} {c['area_ha']:>7.2f} {c['delta']:>+7.3f} "
              f"{c['residual']:>+7.3f} {c['z_robusto']:>5.1f}  {c['lat']:.4f}, {c['lon']:.4f}")

    # mapa: residuo por componente sobre la escena NDVI
    lon_w, lat_s, lon_e, lat_n = res['bbox']
    fig, ax = plt.subplots(figsize=(13, 12), facecolor='#0f1117')
    ax.imshow(res['ndvi_mean'], cmap='Greys_r', vmin=-0.1, vmax=0.6,
              extent=[lon_w, lon_e, lat_s, lat_n], origin='upper', aspect='auto', alpha=0.7)
    resid = np.array([c['residual'] for c in comps])
    vmax = max(0.05, float(np.percentile(np.abs(resid), 95)))
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    cmap = mcolors.LinearSegmentedColormap.from_list('r', [
        '#7B0000', '#e05c20', '#f0f0f0', '#7cc35a', '#10500f'])
    sc = ax.scatter([c['lon'] for c in comps], [c['lat'] for c in comps],
                    c=resid, cmap=cmap, norm=norm,
                    s=[max(12, c['area_ha']*12) for c in comps],
                    edgecolors='#00e5ff', linewidths=0.4, zorder=5)
    for i, c in enumerate(comps[:6], 1):
        ax.text(c['lon'], c['lat'], f"G{i}", color='#00e5ff', fontsize=8, fontweight='bold')
    for i, c in enumerate(comps[::-1][:6], 1):
        ax.text(c['lon'], c['lat'], f"B{i}", color='#ff5555', fontsize=8, fontweight='bold')
    cbar = plt.colorbar(sc, ax=ax, fraction=0.04, pad=0.01)
    cbar.set_label('Residuo ΔNDVI vs fondo climático de la cuenca\n(verde=enverdece más, '
                   'rojo=pierde más vigor)', color='#8892a4')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8892a4')
    cbar.ax.yaxis.set_tick_params(color='#8892a4')
    ax.set_title(f'{volcan} — Escaneo de TODA la vegetación ({res["fecha_a"]} → {res["fecha_b"]})\n'
                 f'{len(comps)} componentes; clima descontado espacialmente (mediana de cuenca '
                 f'{res["basin_median_delta"]:+.3f})', color='#e2e8f0', fontsize=12, fontweight='bold')
    ax.set_xlabel('Longitud', color='#8892a4'); ax.set_ylabel('Latitud', color='#8892a4')
    ax.tick_params(colors='#8892a4')
    for sp in ax.spines.values(): sp.set_edgecolor('#2a2d3a')
    out = DOCS / "maps" / f"{volcan.replace(' ','_')}_vegetation_scan.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=140, facecolor='#0f1117', bbox_inches='tight')
    plt.close()
    print(f"\n  Mapa: {out}")
    return out


def main():
    ap = argparse.ArgumentParser(description='Escaneo de red ancha sobre toda la vegetación')
    ap.add_argument('--volcan', default='Laguna del Maule')
    ap.add_argument('--fecha_a', default=None)
    ap.add_argument('--fecha_b', default=None)
    ap.add_argument('--min_frac', type=float, default=0.7,
                    help='Fracción mínima de fechas con veg para contar un pixel')
    ap.add_argument('--min_area_ha', type=float, default=0.3)
    ap.add_argument('--top', type=int, default=12)
    args = ap.parse_args()

    print(f"\n{'='*64}\n Escaneo de vegetación — {args.volcan}\n{'='*64}")
    res = scan(args.volcan, args.fecha_a, args.fecha_b, args.min_frac, args.min_area_ha)
    if not res:
        return
    report_and_map(args.volcan, res, top=args.top)

    # guardar JSON (sin arrays)
    out_json = DATOS / args.volcan.replace(' ', '_') / "vegetation_scan.json"
    payload = {k: res[k] for k in ('fecha_a', 'fecha_b', 'basin_median_delta')}
    payload['n_componentes'] = len(res['comps'])
    payload['componentes'] = res['comps']
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"  JSON: {out_json}")


if __name__ == '__main__':
    main()
