"""
vegetation_trends.py — Tendencia plurianual MISMO-MES de TODA la vegetación, con el
clima regional descontado. La versión comprehensiva del análisis que hicimos para Q8.

Idea (la síntesis de la semana):
  - Comparar siempre el mismo mes (febrero) anula la fenología estacional.
  - El clima inter-anual (verano lluvioso vs seco) mueve a TODA la cuenca junta -> se
    descuenta restando, año a año, la mediana de la cuenca (tendencia regional).
  - Lo que queda por componente es su tendencia PROPIA. Un componente con pendiente
    residual sostenida y CONSISTENTE (alto r²) es el único candidato creíble a señal
    volcánica localizada (CO2 difuso, Guinn 2024); una anomalía de un solo año es ruido.

Para cada componente de vegetación (NDVI∈[0.41,0.95] en >=min_frac de las fechas,
área>=min_area_ha) calcula su serie de NDVI de febrero 2021-2026, le resta la mediana
de la cuenca año a año (residuo), y ajusta una recta al residuo: pendiente (NDVI/año) y
r² (consistencia). Ranking por pendiente residual.

Uso:
    python vegetation_trends.py --volcan "Laguna del Maule"
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

NDVI_VEG_MIN, NDVI_VEG_MAX = 0.41, 0.95
NDVI_MIN_VALIDO = 0.40


def list_dates(volcan):
    vdir = DATOS / volcan.replace(" ", "_")
    return sorted(p.stem.replace("ndvi_raw_", "") for p in vdir.glob("ndvi_raw_*.npy"))


def feb_dates(volcan):
    """Fechas de febrero (mismo mes), una por año, ordenadas."""
    out = {}
    for d in list_dates(volcan):
        dt = datetime.strptime(d, '%Y-%m-%d')
        if dt.month == 2:
            out[dt.year] = d
    return [out[y] for y in sorted(out)]


def main():
    from scipy.ndimage import label, center_of_mass
    from skimage.morphology import skeletonize

    ap = argparse.ArgumentParser()
    ap.add_argument('--volcan', default='Laguna del Maule')
    ap.add_argument('--min_frac', type=float, default=0.7)
    ap.add_argument('--min_area_ha', type=float, default=0.3)
    ap.add_argument('--top', type=int, default=12)
    args = ap.parse_args()

    vdir = DATOS / args.volcan.replace(' ', '_')
    febs = feb_dates(args.volcan)
    print(f"\n{'='*64}\n Tendencia plurianual de vegetación — {args.volcan}\n{'='*64}")
    print(f"  Febreros disponibles ({len(febs)}): {febs}")
    if len(febs) < 4:
        print("  Se necesitan >=4 febreros para una tendencia fiable."); return

    arrs = {f: np.load(vdir / f"ndvi_raw_{f}.npy") for f in febs}
    all_dates = list_dates(args.volcan)
    stack = np.stack([np.load(vdir / f"ndvi_raw_{f}.npy") for f in all_dates])
    meta = json.load(open(vdir / f"ndvi_meta_{febs[-1]}.json"))
    bbox, shape = meta['bbox'], tuple(meta['shape'])
    px_m = (bbox[2]-bbox[0]) * 111000 * abs(np.cos(np.radians((bbox[1]+bbox[3])/2))) / shape[1]
    min_area_px = max(5, int(args.min_area_ha * 1e4 / px_m**2))

    with np.errstate(invalid='ignore'):
        veg_each = (stack >= NDVI_VEG_MIN) & (stack <= NDVI_VEG_MAX)
    veg = (veg_each.sum(axis=0) / len(all_dates)) >= args.min_frac
    skel = skeletonize(veg)
    lbl, nl = label(veg)
    años = np.array([int(f[:4]) for f in febs], dtype=float)

    comps = []
    for l in range(1, nl + 1):
        comp = (lbl == l)
        area = int(comp.sum())
        if area < min_area_px:
            continue
        serie = []
        for f in febs:
            a = arrs[f]
            with np.errstate(invalid='ignore'):
                m = comp & (a >= NDVI_MIN_VALIDO) & ~np.isnan(a)
            serie.append(float(np.mean(a[m])) if int(m.sum()) >= 10 else np.nan)
        serie = np.array(serie)
        if np.isnan(serie).sum() > 1:   # exigir casi toda la serie
            continue
        sl = int((skel & comp).sum())
        shape_t = 'quebrada' if (sl >= 3 and area/sl <= 8) else 'parche'
        cy, cx = center_of_mass(comp)
        lon = bbox[0] + cx/shape[1]*(bbox[2]-bbox[0])
        lat = bbox[3] - cy/shape[0]*(bbox[3]-bbox[1])
        comps.append({'serie': serie, 'area_ha': round(area*px_m**2/1e4, 2),
                      'shape': shape_t, 'lat': round(lat, 5), 'lon': round(lon, 5)})

    if len(comps) < 5:
        print("  Muy pocos componentes con serie completa."); return

    # ── tendencia de la cuenca (mediana año a año) = fondo climático ──
    M = np.vstack([c['serie'] for c in comps])           # (Ncomp, Naños)
    basin = np.nanmedian(M, axis=0)
    basin_slope = np.polyfit(años, basin, 1)[0]
    print(f"  {len(comps)} componentes con serie completa de febrero.")
    print(f"  Tendencia de la cuenca (fondo climático): {basin_slope:+.4f} NDVI/año  "
          f"| NDVI mediano feb: {[round(float(v),3) for v in basin]}")

    def fit(x, y):
        m = ~np.isnan(y)
        if m.sum() < 4: return np.nan, np.nan
        s, b = np.polyfit(x[m], y[m], 1)
        pred = s*x[m]+b; ss_res = np.sum((y[m]-pred)**2); ss_tot = np.sum((y[m]-np.mean(y[m]))**2)
        return s, (1 - ss_res/ss_tot if ss_tot > 1e-12 else 0.0)

    for c in comps:
        resid = c['serie'] - basin                       # quita el fondo climático
        s, r2 = fit(años, resid)
        c['resid_slope'] = round(float(s), 4)
        c['resid_r2'] = round(float(r2), 2)
        c['raw_slope'] = round(float(fit(años, c['serie'])[0]), 4)

    comps.sort(key=lambda c: c['resid_slope'], reverse=True)

    def show(title, items, tag):
        print(f"\n  ── {title} ──")
        print(f"  {'#':>3s} {'forma':9s} {'área_ha':>7s} {'pend_resid':>10s} {'r²':>5s} "
              f"{'pend_cruda':>10s}  centro(lat,lon)")
        for i, c in enumerate(items, 1):
            print(f"  {tag}{i:<2d} {c['shape']:9s} {c['area_ha']:>7.2f} {c['resid_slope']:>+10.4f} "
                  f"{c['resid_r2']:>5.2f} {c['raw_slope']:>+10.4f}  {c['lat']:.4f}, {c['lon']:.4f}")

    # candidatos robustos = pendiente residual fuerte Y consistente (r² alto)
    show("TOP greening sostenido (enverdece más que la cuenca, multi-año)", comps[:args.top], "G")
    show("TOP browning sostenido (pierde vigor más que la cuenca, multi-año)", comps[::-1][:args.top], "B")
    robustos = [c for c in comps if abs(c['resid_slope']) >= 0.01 and c['resid_r2'] >= 0.6]
    print(f"\n  Candidatos ROBUSTOS (|pend_resid|>=0.010 y r²>=0.6): {len(robustos)} de {len(comps)}")
    for c in sorted(robustos, key=lambda c: -abs(c['resid_slope'])):
        sgn = 'GREENING' if c['resid_slope'] > 0 else 'BROWNING'
        print(f"    {sgn} {c['shape']:9s} {c['area_ha']:>6.2f}ha  pend={c['resid_slope']:+.4f} "
              f"r²={c['resid_r2']:.2f}  {c['lat']:.4f}, {c['lon']:.4f}")

    # ── mapa ──
    lon_w, lat_s, lon_e, lat_n = bbox
    ndvi_mean = np.nanmean(stack, axis=0)
    fig, ax = plt.subplots(figsize=(13, 12), facecolor='#0f1117')
    ax.imshow(ndvi_mean, cmap='Greys_r', vmin=-0.1, vmax=0.6,
              extent=[lon_w, lon_e, lat_s, lat_n], origin='upper', aspect='auto', alpha=0.7)
    sl_arr = np.array([c['resid_slope'] for c in comps])
    vmax = max(0.01, float(np.percentile(np.abs(sl_arr), 95)))
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    cmap = mcolors.LinearSegmentedColormap.from_list('r', ['#7B0000','#e05c20','#f0f0f0','#7cc35a','#10500f'])
    # opacidad/tamaño ~ consistencia (r²): los consistentes resaltan
    sc = ax.scatter([c['lon'] for c in comps], [c['lat'] for c in comps], c=sl_arr,
                    cmap=cmap, norm=norm, s=[20 + 120*c['resid_r2'] for c in comps],
                    alpha=[0.25 + 0.7*c['resid_r2'] for c in comps],
                    edgecolors='#00e5ff', linewidths=0.3, zorder=5)
    cbar = plt.colorbar(sc, ax=ax, fraction=0.04, pad=0.01)
    cbar.set_label('Pendiente residual NDVI/año (clima de cuenca descontado)\n'
                   'tamaño/opacidad ~ consistencia (r²)', color='#8892a4')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8892a4'); cbar.ax.yaxis.set_tick_params(color='#8892a4')
    ax.set_title(f'{args.volcan} — Tendencia plurianual de vegetación (febreros {int(años[0])}-{int(años[-1])})\n'
                 f'{len(comps)} componentes; fondo climático de cuenca descontado', color='#e2e8f0',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Longitud', color='#8892a4'); ax.set_ylabel('Latitud', color='#8892a4'); ax.tick_params(colors='#8892a4')
    for sp in ax.spines.values(): sp.set_edgecolor('#2a2d3a')
    out = DOCS / "maps" / f"{args.volcan.replace(' ','_')}_vegetation_trends.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=140, facecolor='#0f1117', bbox_inches='tight'); plt.close()
    print(f"\n  Mapa: {out}")

    for c in comps: c['serie'] = [round(float(v), 4) for v in c['serie']]
    out_json = vdir / "vegetation_trends.json"
    json.dump({'volcan': args.volcan, 'febreros': febs, 'basin_slope': round(float(basin_slope),4),
               'n_componentes': len(comps), 'componentes': comps},
              open(out_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"  JSON: {out_json}")


if __name__ == '__main__':
    main()
