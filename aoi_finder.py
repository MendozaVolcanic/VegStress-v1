"""
aoi_finder.py — Encuentra dónde HAY vegetación real en la escena de un volcán y
propone coordenadas de AOI sobre vegetación estable.

Motivación (descubierto 2026-06-07): las AOIs iniciales de Laguna del Maule caían
sobre roca/nieve de caldera (NDVI<0.4, no vegetación). Este script localiza los
parches de vegetación sana y propone AOIs centradas ahí, para que el monitoreo de
estrés sea interpretable.

Criterios citados:
  - Vegetación fiable: NDVI >= 0.4 (Guinn 2024, PD-001, L882).
  - Bosque Araucaria-Nothofagus sano: NDVI 0.41-0.62 (Ojeda 2011, PD-016).
Usa solo píxeles con vegetación en AMBAS fechas (estable, no estacional efímero).

Uso:
    python aoi_finder.py --volcan "Laguna del Maule"
    python aoi_finder.py --volcan "Laguna del Maule" --n 5 --radio 500
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


def px_to_lonlat(cx, cy, bbox, shape):
    lon_w, lat_s, lon_e, lat_n = bbox
    H, W = shape
    lon = lon_w + (cx / W) * (lon_e - lon_w)
    lat = lat_n - (cy / H) * (lat_n - lat_s)
    return lon, lat


def find_aois(volcan, n_aois=5, radio_m=500, min_veg_px=400):
    vdir = DATOS / volcan.replace(" ", "_")
    dates = list_dates(volcan)
    if not dates:
        print(f"  Sin arrays para {volcan}")
        return []

    # Cargar todas las fechas, exigir vegetación ESTABLE (en todas las fechas disponibles)
    arrs, meta = [], None
    for f in dates:
        a = np.load(vdir / f"ndvi_raw_{f}.npy")
        arrs.append(a)
        mp = vdir / f"ndvi_meta_{f}.json"
        if mp.exists() and meta is None:
            meta = json.load(open(mp))
    bbox = meta['bbox']
    shape = tuple(meta['shape'])

    stack = np.stack(arrs)  # (T, H, W)
    with np.errstate(invalid='ignore'):
        veg_each = (stack >= NDVI_VEG_MIN) & (stack <= NDVI_VEG_MAX)
    veg_stable = veg_each.all(axis=0)  # vegetación en TODAS las fechas
    ndvi_mean = np.nanmean(stack, axis=0)

    n_veg = int(veg_stable.sum())
    print(f"  {volcan}: {n_veg} px de vegetación estable (NDVI {NDVI_VEG_MIN}-{NDVI_VEG_MAX} "
          f"en {len(dates)} fechas) = {n_veg / veg_stable.size * 100:.2f}% de la escena")
    if n_veg < min_veg_px:
        print(f"  ⚠️ Muy poca vegetación estable (<{min_veg_px} px). Este volcán puede no ser "
              f"apto para monitoreo vegetal, o ampliar el buffer de la escena.")

    # Etiquetar regiones conexas de vegetación
    from scipy.ndimage import label, center_of_mass
    lbl, nlbl = label(veg_stable)
    if nlbl == 0:
        print("  No se hallaron parches de vegetación.")
        return []

    sizes = np.bincount(lbl.ravel())
    sizes[0] = 0  # fondo
    # Ordenar regiones por tamaño, tomar las n mayores con >= min_veg_px
    order = np.argsort(sizes)[::-1]
    candidates = []
    for ridx in order:
        if sizes[ridx] < min_veg_px:
            break
        if len(candidates) >= n_aois:
            break
        cy, cx = center_of_mass(veg_stable, lbl, ridx)
        lon, lat = px_to_lonlat(cx, cy, bbox, shape)
        # NDVI medio del parche
        patch = (lbl == ridx)
        ndvi_patch = float(np.nanmean(ndvi_mean[patch]))
        candidates.append({
            'cx': float(cx), 'cy': float(cy), 'lon': round(lon, 5), 'lat': round(lat, 5),
            'px': int(sizes[ridx]), 'ndvi_medio': round(ndvi_patch, 3),
            'area_ha': round(sizes[ridx] * 0.01, 1),  # 10m px → 100 m²/px = 0.01 ha
        })

    return candidates, ndvi_mean, veg_stable, bbox, shape


def generate_map(volcan, ndvi_mean, candidates, radio_m, bbox, shape):
    lon_w, lat_s, lon_e, lat_n = bbox
    fig, ax = plt.subplots(figsize=(12, 11), facecolor='#0f1117')
    cmap = mcolors.LinearSegmentedColormap.from_list('veg', [
        '#2b2b2b', '#5a4a3a', '#8a7a3a', '#b7d77a', '#3a9d23', '#10500f'])
    im = ax.imshow(ndvi_mean, cmap=cmap, vmin=-0.1, vmax=0.8,
                   extent=[lon_w, lon_e, lat_s, lat_n], origin='upper', aspect='auto')
    for i, c in enumerate(candidates, 1):
        lon, lat = c['lon'], c['lat']
        rd = radio_m / 111000.0
        ax.add_patch(plt.Circle((lon, lat), rd, fill=False, edgecolor='#00e5ff',
                                 linewidth=2.2, zorder=5))
        ax.text(lon, lat + rd * 1.2, f"AOI-{i}\nNDVI {c['ndvi_medio']}", ha='center',
                va='bottom', color='#00e5ff', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.6, linewidth=0))
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.01)
    cbar.set_label('NDVI medio (todas las fechas)', color='#8892a4')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#8892a4')
    cbar.ax.yaxis.set_tick_params(color='#8892a4')
    ax.set_title(f'{volcan} — Vegetación estable y AOIs propuestas\n'
                 f'(parches con NDVI {NDVI_VEG_MIN}-{NDVI_VEG_MAX} en todas las fechas)',
                 color='#e2e8f0', fontsize=13, fontweight='bold')
    ax.set_xlabel('Longitud', color='#8892a4'); ax.set_ylabel('Latitud', color='#8892a4')
    ax.tick_params(colors='#8892a4')
    for sp in ax.spines.values():
        sp.set_edgecolor('#2a2d3a')
    out = DOCS / "maps" / f"{volcan.replace(' ', '_')}_aoi_candidatas.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='#0f1117')
    plt.close()
    print(f"  Mapa guardado: {out}")
    return out


def main():
    ap = argparse.ArgumentParser(description='Buscador de AOIs sobre vegetación real')
    ap.add_argument('--volcan', default='Laguna del Maule')
    ap.add_argument('--n', type=int, default=5, help='Máx AOIs a proponer')
    ap.add_argument('--radio', type=int, default=500, help='Radio AOI propuesta (m)')
    ap.add_argument('--min_px', type=int, default=400, help='Mín px de vegetación por parche')
    args = ap.parse_args()

    print(f"\n{'='*60}\n Buscador de AOIs — {args.volcan}\n{'='*60}")
    res = find_aois(args.volcan, args.n, args.radio, args.min_px)
    if not res or not res[0]:
        print("  Sin candidatas.")
        return
    candidates, ndvi_mean, veg_stable, bbox, shape = res

    print(f"\n  {len(candidates)} AOI(s) candidata(s) sobre vegetación estable:")
    print(f"  {'#':2s} {'lat':>10s} {'lon':>10s} {'NDVI':>6s} {'area_ha':>8s} {'px':>7s}")
    for i, c in enumerate(candidates, 1):
        print(f"  {i:2d} {c['lat']:>10.5f} {c['lon']:>10.5f} {c['ndvi_medio']:>6.3f} "
              f"{c['area_ha']:>8.1f} {c['px']:>7d}")

    generate_map(args.volcan, ndvi_mean, candidates, args.radio, bbox, shape)

    # Guardar propuesta JSON para revisión/integración manual
    out_json = DATOS / args.volcan.replace(' ', '_') / "aoi_candidatas.json"
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump({'volcan': args.volcan, 'radio_m': args.radio,
                   'criterio': f'NDVI {NDVI_VEG_MIN}-{NDVI_VEG_MAX} estable (Ojeda 2011, Guinn 2024)',
                   'candidatas': candidates}, f, indent=2, ensure_ascii=False)
    print(f"\n  Propuesta guardada: {out_json}")
    print(f"  → Revisar el mapa y, si convencen, agregar a aoi_config.json con tu criterio de campo.")


if __name__ == '__main__':
    main()
