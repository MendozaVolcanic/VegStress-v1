"""
area_desgasificacion.py — Análisis y AOIs ancladas al ÁREA DE DESGASIFICACIÓN PRINCIPAL
de Laguna del Maule (polígono de campo provisto por Nicolás, datos/area_desgasificacion.json,
derivado de area.kmz, 2026-06-13).

Por qué: hasta ahora las quebradas Q1-Q15 eran candidatas data-driven sin anclaje de campo;
el análisis plurianual no halló señal robusta en ellas. Con el polígono real de desgasificación
podemos (a) extraer la vegetación riparia QUE ESTÁ DENTRO del área de gas, (b) medir su
tendencia de NDVI de febrero 2021-2026 con el clima de cuenca descontado, y (c) generar AOIs
tipo quebrada/parche ancladas a la zona, que son los targets de monitoreo prioritarios.

Genera: mapa en zoom (docs/maps/Laguna_del_Maule_area_gas.png), entradas de AOI
(datos/Laguna_del_Maule/aois_area_gas.json) y un reporte de tendencias por componente.

Uso:
    python area_desgasificacion.py --volcan "Laguna del Maule"
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

from riparian_finder import order_polyline, px_size_m, px_to_lonlat

ROOT  = Path(__file__).parent
DATOS = ROOT / "datos"
DOCS  = ROOT / "docs"
NDVI_VEG_MIN, NDVI_VEG_MAX, NDVI_MIN_VALIDO = 0.41, 0.95, 0.40


def main():
    from scipy.ndimage import label, center_of_mass
    from skimage.morphology import skeletonize

    ap = argparse.ArgumentParser()
    ap.add_argument('--volcan', default='Laguna del Maule')
    ap.add_argument('--min_frac', type=float, default=0.7)
    ap.add_argument('--min_area_ha', type=float, default=0.2)
    ap.add_argument('--buffer_m', type=int, default=30)
    args = ap.parse_args()

    vdir = DATOS / args.volcan.replace(' ', '_')
    area = json.load(open(DATOS / "area_desgasificacion.json", encoding="utf-8"))
    poly_latlon = area["poligono_latlon"]
    poly = MplPath([(lo, la) for la, lo in poly_latlon])  # (lon,lat)

    dates = sorted(p.stem.replace("ndvi_raw_", "") for p in vdir.glob("ndvi_raw_*.npy"))
    stack = np.stack([np.load(vdir / f"ndvi_raw_{f}.npy") for f in dates])
    meta = json.load(open(vdir / f"ndvi_meta_{dates[-1]}.json"))
    bbox, shape = meta['bbox'], tuple(meta['shape'])
    H, W = shape
    mx, my = px_size_m(bbox, shape); px_m = (mx + my) / 2

    # máscara del polígono en píxeles
    lon_w, lat_s, lon_e, lat_n = bbox
    ys, xs = np.mgrid[0:H, 0:W]
    lons = lon_w + (xs + 0.5) / W * (lon_e - lon_w)
    lats = lat_n - (ys + 0.5) / H * (lat_n - lat_s)
    in_poly = poly.contains_points(np.column_stack([lons.ravel(), lats.ravel()])).reshape(H, W)

    with np.errstate(invalid='ignore'):
        veg_each = (stack >= NDVI_VEG_MIN) & (stack <= NDVI_VEG_MAX)
    veg = ((veg_each.sum(axis=0) / len(dates)) >= args.min_frac) & in_poly
    ndvi_mean = np.nanmean(stack, axis=0)

    print(f"\n{'='*64}\n Área de desgasificación — {args.volcan}\n{'='*64}")
    area_km2 = in_poly.sum() * px_m**2 / 1e6
    print(f"  Polígono: {area_km2:.2f} km² | vegetación dentro (≥{args.min_frac*100:.0f}% fechas): "
          f"{int(veg.sum())} px = {veg.sum()*px_m**2/1e4:.2f} ha "
          f"({veg.sum()/max(in_poly.sum(),1)*100:.1f}% del área)")

    # febreros para tendencia
    febs = [d for d in dates if datetime.strptime(d, '%Y-%m-%d').month == 2]
    feb_arr = {f: np.load(vdir / f"ndvi_raw_{f}.npy") for f in febs}
    años = np.array([int(f[:4]) for f in febs], dtype=float)
    # fondo climático de cuenca (mediana de toda la veg de la escena por febrero)
    with np.errstate(invalid='ignore'):
        veg_scene = (veg_each.sum(axis=0) / len(dates)) >= args.min_frac
    basin = []
    for f in febs:
        a = feb_arr[f]
        with np.errstate(invalid='ignore'):
            m = veg_scene & (a >= NDVI_MIN_VALIDO) & ~np.isnan(a)
        basin.append(float(np.median(a[m])))
    basin = np.array(basin)

    skel = skeletonize(veg)
    lbl, nl = label(veg)
    min_area_px = max(4, int(args.min_area_ha * 1e4 / px_m**2))

    def fit(x, y):
        m = ~np.isnan(y)
        if m.sum() < 4: return np.nan, np.nan
        s, b = np.polyfit(x[m], y[m], 1)
        pred = s*x[m]+b; sr = np.sum((y[m]-pred)**2); st = np.sum((y[m]-np.mean(y[m]))**2)
        return float(s), float(1 - sr/st if st > 1e-12 else 0.0)

    aois, comps = [], []
    k = 0
    for l in range(1, nl + 1):
        comp = (lbl == l)
        area_px = int(comp.sum())
        if area_px < min_area_px:
            continue
        k += 1
        sl = int((skel & comp).sum())
        is_thread = sl >= 3 and area_px / sl <= 8
        cyc, cxc = center_of_mass(comp)
        clon, clat = px_to_lonlat(cxc, cyc, bbox, shape)
        # serie de febrero + tendencia residual
        serie = []
        for f in febs:
            a = feb_arr[f]
            with np.errstate(invalid='ignore'):
                m = comp & (a >= NDVI_MIN_VALIDO) & ~np.isnan(a)
            serie.append(float(np.mean(a[m])) if int(m.sum()) >= 5 else np.nan)
        serie = np.array(serie)
        rs, rr2 = fit(años, serie - basin)
        comps.append({'serie': [round(float(v),3) for v in serie], 'resid_slope': round(rs,4),
                      'resid_r2': round(rr2,2), 'area_ha': round(area_px*px_m**2/1e4,2),
                      'lat': round(clat,5), 'lon': round(clon,5),
                      'shape': 'quebrada' if is_thread else 'parche'})

        if is_thread:
            ys2, xs2 = np.where(skel & comp)
            wp = order_polyline(ys2, xs2, max(2, int(round(120/px_m))))
            wpll = [list(px_to_lonlat(x, y, bbox, shape)) for x, y in wp]
            aois.append({'id': f"gas_quebrada_{k}", 'nombre': f"Gas — quebrada {k}",
                         'waypoints': [[round(la,5), round(lo,5)] for lo, la in wpll],
                         'buffer_m': args.buffer_m,
                         'descripcion': f"Veg riparia DENTRO del area de desgasificacion principal "
                                        f"(campo). area {area_px*px_m**2/1e4:.2f} ha.",
                         'tipo_esperado': 'NINGUNO',
                         '_nota_tipo': 'Area de gas principal: flujo posiblemente alto -> Guinn predice '
                                       'BROWNING (asfixia) si es alto, GREENING si bajo. Dejar NINGUNO y '
                                       'leer el signo observado.',
                         'umbral_delta_abs': 0.10, 'activo': True})
        else:
            r_m = max(60, (area_px*px_m**2/np.pi)**0.5)
            aois.append({'id': f"gas_parche_{k}", 'nombre': f"Gas — parche {k}",
                         'lat': round(clat,5), 'lon': round(clon,5), 'radio_m': int(r_m),
                         'descripcion': f"Veg DENTRO del area de desgasificacion principal (campo). "
                                        f"area {area_px*px_m**2/1e4:.2f} ha.",
                         'tipo_esperado': 'NINGUNO', 'umbral_delta_abs': 0.10, 'activo': True})

    print(f"  Componentes de vegetación ≥{args.min_area_ha} ha dentro del área: {len(comps)}")
    print(f"  Fondo climático cuenca (NDVI feb mediano): {[round(float(v),3) for v in basin]}")
    print(f"\n  {'forma':9s} {'área_ha':>7s} {'pend_resid':>10s} {'r²':>5s}  serie_feb {febs[0][:4]}..{febs[-1][:4]}  (lat,lon)")
    for c in sorted(comps, key=lambda c: c['resid_slope']):
        print(f"  {c['shape']:9s} {c['area_ha']:>7.2f} {c['resid_slope']:>+10.4f} {c['resid_r2']:>5.2f}  "
              f"{c['serie']}  ({c['lat']:.4f},{c['lon']:.4f})")

    # ── mapa en zoom ──
    pad = 0.01
    plons = [lo for la, lo in poly_latlon]; plats = [la for la, lo in poly_latlon]
    x0, x1 = min(plons)-pad, max(plons)+pad
    y0, y1 = min(plats)-pad, max(plats)+pad
    fig, ax = plt.subplots(figsize=(11, 10), facecolor='#0f1117')
    cmap = mcolors.LinearSegmentedColormap.from_list('veg', [
        '#2b2b2b', '#5a4a3a', '#8a7a3a', '#b7d77a', '#3a9d23', '#10500f'])
    ax.imshow(ndvi_mean, cmap=cmap, vmin=-0.1, vmax=0.7,
              extent=[lon_w, lon_e, lat_s, lat_n], origin='upper', aspect='auto')
    ax.plot(plons + [plons[0]], plats + [plats[0]], '-', color='#ff3b3b', lw=2.5,
            zorder=6, label='Área desgasificación (campo)')
    for a in aois:
        if a.get('waypoints'):
            ax.plot([w[1] for w in a['waypoints']], [w[0] for w in a['waypoints']],
                    '-', color='#00e5ff', lw=2.4, zorder=7)
        else:
            ax.add_patch(plt.Circle((a['lon'], a['lat']), a['radio_m']/111000.0,
                                    fill=False, edgecolor='#00e5ff', lw=2, zorder=7))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    ax.set_title(f'{args.volcan} — Área de desgasificación principal (campo)\n'
                 f'vegetación riparia dentro = AOIs de monitoreo (cian)', color='#e2e8f0',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Longitud', color='#8892a4'); ax.set_ylabel('Latitud', color='#8892a4')
    ax.tick_params(colors='#8892a4'); ax.legend(facecolor='#1a1d26', labelcolor='#e2e8f0', edgecolor='#2a2d3a')
    for sp in ax.spines.values(): sp.set_edgecolor('#2a2d3a')
    out = DOCS / "maps" / f"{args.volcan.replace(' ','_')}_area_gas.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=150, facecolor='#0f1117', bbox_inches='tight'); plt.close()
    print(f"\n  Mapa: {out}")

    out_json = vdir / "aois_area_gas.json"
    json.dump({'volcan': args.volcan, 'fuente': 'area.kmz (campo, Nicolas 2026-06-13)',
               'n_aois': len(aois), 'aois': aois, 'tendencias': comps},
              open(out_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"  AOIs propuestas: {out_json}  ({len(aois)} AOIs)")


if __name__ == '__main__':
    main()
