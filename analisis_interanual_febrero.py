"""
analisis_interanual_febrero.py
==============================

Pregunta científica
-------------------
Con una serie de 6 febreros consecutivos (2021-2026, misma estación, ~mismo día del
año), ¿el NDVI de la quebrada Q8 — la única clima-robusta y la más austral — muestra
una TENDENCIA PLURIANUAL SOSTENIDA (esperable si hay un aporte volcánico de CO2 que
crece o se mantiene) o solo fluctúa año a año siguiendo la lluvia (confusor climático)?

Por qué febrero y por qué inter-anual
-------------------------------------
Comparar siempre el mismo mes anula la fenología estacional (la senescencia otoñal que
inundaba el detector de falsos positivos). Lo que queda entre febreros es la variabilidad
inter-anual: clima (lluvia/temp de cada verano) + cualquier señal volcánica sostenida.
Si separamos el clima (precipitación antecedente, De Schutter 2015 / Guinn 2024), un
residuo con tendencia monótona en Q8 sería el candidato a precursor.

Salida: tabla por año (NDVI + precip antecedente) por AOI, pendiente de tendencia,
correlación NDVI~precip, y una figura docs/maps/Q8_interanual_febrero.png.
Solo análisis: no toca change_detector.py, vegstress_signal.py ni la config.
"""
import sys
import json
import numpy as np
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from aoi_geometry import aoi_to_mask
from climate_control import build_climate_series

ROOT  = Path(__file__).parent
DATOS = ROOT / "datos" / "Laguna_del_Maule"
DOCS  = ROOT / "docs" / "maps"

# Serie de febreros (misma estación). Clave = año.
FECHAS_FEB = {
    2021: "2021-02-19", 2022: "2022-02-19", 2023: "2023-02-19",
    2024: "2024-02-19", 2025: "2025-02-18", 2026: "2026-02-16",
}
NDVI_MIN = 0.4   # Guinn 2024 L882
AOIS_FOCO = ["quebrada_Q8", "quebrada_Q9"]          # candidatas sector sur
AOIS_CTRL = ["quebrada_Q3", "quebrada_Q6"]          # controles lejanos (NE / N)


def load_aois():
    cfg = json.load(open(ROOT / "datos" / "aoi_config.json", encoding="utf-8"))
    return {a["id"]: a for a in cfg["volcanes"]["Laguna del Maule"]["aois"]}


def serie_ndvi_aoi(aoi):
    """NDVI medio (solo vegetación NDVI>=0.4) de un AOI en cada febrero. None si <20 px veg."""
    años, ndvis = [], []
    for año, fecha in sorted(FECHAS_FEB.items()):
        npy = DATOS / f"ndvi_raw_{fecha}.npy"
        meta = json.load(open(DATOS / f"ndvi_meta_{fecha}.json"))
        arr = np.load(npy)
        mask, _ = aoi_to_mask(aoi, meta["bbox"], tuple(meta["shape"]))
        vals = arr[mask]
        vals = vals[(~np.isnan(vals)) & (vals >= NDVI_MIN)]
        años.append(año)
        ndvis.append(float(np.mean(vals)) if len(vals) >= 20 else np.nan)
    return np.array(años), np.array(ndvis)


def trend(x, y):
    """Pendiente, r² de y~x ignorando NaN."""
    m = ~np.isnan(y)
    if m.sum() < 3:
        return np.nan, np.nan
    sx, sy = x[m].astype(float), y[m]
    slope, intercept = np.polyfit(sx, sy, 1)
    pred = slope * sx + intercept
    ss_res = np.sum((sy - pred) ** 2)
    ss_tot = np.sum((sy - np.mean(sy)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0
    return slope, r2


def main():
    aois = load_aois()
    ids = AOIS_FOCO + AOIS_CTRL
    fechas_list = [FECHAS_FEB[a] for a in sorted(FECHAS_FEB)]

    # precip antecedente por AOI (centroide) en cada febrero
    print("Pidiendo precipitación antecedente (Open-Meteo)...")
    precip = {}
    for aid in ids:
        aoi = aois[aid]
        wps = aoi["waypoints"]
        lat = float(np.mean([w[0] for w in wps])); lon = float(np.mean([w[1] for w in wps]))
        clim = build_climate_series(lat, lon, fechas_list)
        precip[aid] = np.array([clim[f]["precip_antecedente"] for f in fechas_list], dtype=float)

    series = {}
    print(f"\n{'AOI':14s} " + " ".join(f"{a}" for a in sorted(FECHAS_FEB)))
    for aid in ids:
        años, ndvi = serie_ndvi_aoi(aois[aid])
        series[aid] = (años, ndvi)
        print(f"{aid:14s} " + " ".join(f"{v:5.3f}" if not np.isnan(v) else "  -  " for v in ndvi))

    print(f"\n{'AOI':14s} {'pend_NDVI/año':>13s} {'r²(año)':>8s} {'r²(NDVI~precip)':>16s}  interpretación")
    for aid in ids:
        años, ndvi = series[aid]
        sl, r2y = trend(años, ndvi)
        _, r2p = trend(precip[aid], ndvi)
        tag = "FOCO" if aid in AOIS_FOCO else "ctrl"
        print(f"{aid:14s} {sl:>+13.4f} {r2y:>8.2f} {r2p:>16.2f}  [{tag}]")

    # precip media de la cuenca (promedio de los AOIs) por año
    precip_mean = np.nanmean(np.vstack([precip[a] for a in ids]), axis=0)

    # ── figura ──
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8), facecolor='#0f1117',
                                   gridspec_kw={'height_ratios': [2, 1]})
    años_x = sorted(FECHAS_FEB)
    colores = {'quebrada_Q8': '#00e5ff', 'quebrada_Q9': '#ff7ad6',
               'quebrada_Q3': '#8892a4', 'quebrada_Q6': '#b0b0b0'}
    for aid in ids:
        años, ndvi = series[aid]
        estilo = '-o' if aid in AOIS_FOCO else '--s'
        lw = 2.6 if aid in AOIS_FOCO else 1.4
        ax1.plot(años, ndvi, estilo, color=colores[aid], linewidth=lw,
                 markersize=6, label=f"{aid.replace('quebrada_','')}"
                 + (" (sur)" if aid in AOIS_FOCO else " (ctrl)"))
    ax1.set_title('NDVI de febrero por año — Q8/Q9 (sur) vs controles\nLaguna del Maule, '
                  'misma estación 2021-2026', color='#e2e8f0', fontweight='bold', fontsize=12)
    ax1.set_ylabel('NDVI medio (veg NDVI≥0.4)', color='#8892a4')
    ax1.legend(facecolor='#1a1d26', edgecolor='#2a2d3a', labelcolor='#e2e8f0', fontsize=9)
    for ax in (ax1, ax2):
        ax.set_facecolor('#1a1d26'); ax.tick_params(colors='#8892a4')
        for sp in ax.spines.values(): sp.set_edgecolor('#2a2d3a')
        ax.grid(alpha=0.15)
    ax2.bar([str(a) for a in años_x], precip_mean, color='#4a9edd', alpha=0.8)
    ax2.set_title('Precipitación antecedente media (48 d previos a cada febrero)',
                  color='#e2e8f0', fontsize=10)
    ax2.set_ylabel('mm', color='#8892a4')
    plt.tight_layout()
    DOCS.mkdir(parents=True, exist_ok=True)
    out = DOCS / "Q8_interanual_febrero.png"
    plt.savefig(out, dpi=140, facecolor='#0f1117', bbox_inches='tight')
    plt.close()
    print(f"\nFigura: {out}")
    print(f"\nPrecip antecedente media por año (mm): "
          + ", ".join(f"{a}={p:.0f}" for a, p in zip(años_x, precip_mean)))


if __name__ == "__main__":
    main()
