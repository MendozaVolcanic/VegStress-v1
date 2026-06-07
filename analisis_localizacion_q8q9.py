"""
analisis_localizacion_q8q9.py
=============================

Pregunta científica
-------------------
El greening observado en las quebradas riparias Q8 (+0.118) y Q9 (+0.110) entre
el verano 2025 (2025-02-18) y el verano 2026 (2026-01-11), ¿es un HOTSPOT
LOCALIZADO o un patrón DIFUSO/UNIFORME a lo largo de toda la quebrada?

Por qué importa (fenómeno físico)
---------------------------------
Guinn et al. 2024 (Mt. Etna): el CO2 difuso volcánico se concentra a <=30 m de la
estructura de desgasificación. Por eso su huella en NDVI es LOCALIZADA: un parche
compacto de vigor anómalo sobre el conducto/falla, no un enverdecimiento parejo de
todo el drenaje. Si en cambio el greening está repartido de forma uniforme a lo
largo de la quebrada entera, el motor más probable es climático/fenológico
(precipitación, temperatura, fecha de fenofase), que afecta a toda la cuenca por
igual y también debería aparecer en quebradas de control alejadas del gas.

Convenio de signo (ya fijado en el repo)
----------------------------------------
delta_NDVI = NDVI(2026-01-11) - NDVI(2025-02-18)
  > 0  -> GREENING (gana vigor)
  < 0  -> BROWNING (pierde vigor)

Filtro de vegetación (Guinn L882): se exige NDVI >= 0.4 en AMBAS fechas para
evitar mezclar roca/suelo desnudo en la estadística de la banda riparia.

Salidas
-------
- Figura PNG: docs/maps/Q8_Q9_localizacion_greening.png  (recorte delta-NDVI de
  Q8 y Q9 con colormap divergente y los hotspots etiquetados).
- Reporte en consola: por cada quebrada (Q8, Q9 + controles Q6, Q1, Q3):
  delta medio, %pix greening>+0.10, nº y tamaño de componentes conexas de greening
  fuerte (delta>+0.15), y diagnóstico LOCALIZADO vs DIFUSO.

Este script es SOLO de análisis: no modifica change_detector.py, vegstress_signal.py
ni la configuración.
"""
from __future__ import annotations

import io
import json
import os
import sys

import numpy as np

# Consola Windows (cp1252) rompe con Δ/≥. Forzar UTF-8 en stdout/stderr.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from scipy.ndimage import label

from aoi_geometry import aoi_to_mask

# --------------------------------------------------------------------------- #
# Configuración (rutas relativas al root del proyecto)
# --------------------------------------------------------------------------- #
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "datos", "Laguna_del_Maule")
CFG = os.path.join(ROOT, "datos", "aoi_config.json")
OUT_PNG = os.path.join(ROOT, "docs", "maps", "Q8_Q9_localizacion_greening.png")

FECHA_A = "2025-02-18"   # verano 2025
FECHA_B = "2026-01-11"   # verano 2026

VEG_THR = 0.40           # umbral vegetación en AMBAS fechas (Guinn L882)
GREEN_THR = 0.10         # umbral "greening" para % de píxeles
HOTSPOT_THR = 0.15       # umbral "greening fuerte" para componentes conexas

QUEBRADAS_FOCO = ["quebrada_Q8", "quebrada_Q9"]
QUEBRADAS_CONTROL = ["quebrada_Q6", "quebrada_Q1", "quebrada_Q3"]

# Tamaño del pixel: la escena cubre ~22.3 km (bbox) en 1800 px ~= 12.4 m/px.
# Lo calculamos exacto desde el meta para no inventar números.


# --------------------------------------------------------------------------- #
# Carga de datos
# --------------------------------------------------------------------------- #
def cargar_meta(fecha: str) -> dict:
    with open(os.path.join(DATA, f"ndvi_meta_{fecha}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def cargar_ndvi(fecha: str) -> np.ndarray:
    return np.load(os.path.join(DATA, f"ndvi_raw_{fecha}.npy"))


def cargar_aois() -> dict:
    with open(CFG, encoding="utf-8") as fh:
        cfg = json.load(fh)
    aois = cfg["volcanes"]["Laguna del Maule"]["aois"]
    return {a["id"]: a for a in aois}


def metros_por_pixel(meta: dict) -> float:
    """m/px medio (promedio x/y). bbox = (lon_w, lat_s, lon_e, lat_n)."""
    lon_w, lat_s, lon_e, lat_n = meta["bbox"]
    H, W = meta["shape"]
    lat_med = (lat_s + lat_n) / 2.0
    m_x = (lon_e - lon_w) * 111_000.0 * abs(np.cos(np.radians(lat_med))) / W
    m_y = (lat_n - lat_s) * 111_000.0 / H
    return float((m_x + m_y) / 2.0)


# --------------------------------------------------------------------------- #
# Análisis de una quebrada
# --------------------------------------------------------------------------- #
def analizar_quebrada(aoi, bbox, shape, delta, veg_mask, m_px):
    """Devuelve métricas de localización del greening dentro de la quebrada."""
    qmask, info = aoi_to_mask(aoi, bbox, shape)
    # Solo píxeles de la quebrada que son vegetación en ambas fechas
    valid = qmask & veg_mask
    n_valid = int(valid.sum())
    res = {
        "n_mask_px": int(qmask.sum()),
        "n_valid_px": n_valid,
        "mask": qmask,
        "valid": valid,
        "info": info,
    }
    if n_valid == 0:
        res.update(delta_medio=np.nan, frac_green=np.nan, n_hotspot=0,
                   hotspot_px=0, hotspot_area_m2=0.0, diag="SIN VEGETACION")
        return res

    d = delta[valid]
    res["delta_medio"] = float(np.nanmean(d))
    res["frac_green"] = float(np.mean(d > GREEN_THR))

    # Componentes conexas de greening FUERTE (delta>HOTSPOT_THR) dentro de la veg
    strong = valid & (delta > HOTSPOT_THR)
    lbl, n = label(strong)  # conectividad 4 por defecto
    sizes = np.bincount(lbl.ravel())[1:] if n > 0 else np.array([], dtype=int)
    res["n_hotspot"] = int(n)
    res["hotspot_px"] = int(sizes.max()) if sizes.size else 0
    res["hotspot_area_m2"] = float(res["hotspot_px"] * (m_px ** 2))
    res["strong"] = strong
    res["lbl"] = lbl
    res["sizes"] = sizes

    # Fracción de los píxeles "greening fuerte" que caen en el mayor cluster:
    # alto -> concentrado (hotspot); bajo -> disperso (difuso).
    total_strong = int(strong.sum())
    res["frac_strong"] = float(total_strong / n_valid)
    res["concentracion"] = float(res["hotspot_px"] / total_strong) if total_strong else 0.0

    # Diagnóstico heurístico:
    #  LOCALIZADO si hay greening fuerte agrupado en un parche dominante
    #  (>=5 px contiguos y ese parche concentra >=40% del greening fuerte).
    #  DIFUSO si el greening es generalizado y/o el greening fuerte está disperso.
    if res["hotspot_px"] >= 5 and res["concentracion"] >= 0.40:
        res["diag"] = "LOCALIZADO (hotspot)"
    elif res["frac_green"] >= 0.50 and res["concentracion"] < 0.40:
        res["diag"] = "DIFUSO (uniforme)"
    elif total_strong == 0:
        res["diag"] = "SIN greening fuerte"
    else:
        res["diag"] = "INTERMEDIO"
    return res


def centroide_mayor_hotspot(res):
    """(row, col) del mayor cluster de greening fuerte, o None."""
    if res.get("hotspot_px", 0) == 0:
        return None
    sizes = res["sizes"]
    big = int(np.argmax(sizes)) + 1
    ys, xs = np.where(res["lbl"] == big)
    return float(ys.mean()), float(xs.mean())


# --------------------------------------------------------------------------- #
# Figura: recorte delta-NDVI sobre Q8 y Q9
# --------------------------------------------------------------------------- #
def recorte_bbox(mask, pad=12):
    ys, xs = np.where(mask)
    y0, y1 = ys.min() - pad, ys.max() + pad
    x0, x1 = xs.min() - pad, xs.max() + pad
    H, W = mask.shape
    return max(0, y0), min(H, y1), max(0, x0), min(W, x1)


def figura_q8q9(delta, resultados, m_px):
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    norm = TwoSlopeNorm(vmin=-0.30, vcenter=0.0, vmax=0.30)
    cmap = plt.get_cmap("BrBG")  # marrón=browning, verde=greening (divergente)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, qid in zip(axes, QUEBRADAS_FOCO):
        res = resultados[qid]
        mask = res["mask"]
        y0, y1, x0, x1 = recorte_bbox(mask)

        # delta enmascarado fuera de la quebrada (para destacar la banda)
        d = np.where(mask, delta, np.nan)[y0:y1, x0:x1]
        im = ax.imshow(d, cmap=cmap, norm=norm, interpolation="nearest")

        # contorno de la quebrada
        ax.contour(mask[y0:y1, x0:x1], levels=[0.5], colors="k",
                   linewidths=0.6, alpha=0.7)

        # marcar el mayor hotspot si existe
        c = centroide_mayor_hotspot(res)
        if c is not None:
            ax.plot(c[1] - x0, c[0] - y0, marker="o", ms=14, mfc="none",
                    mec="red", mew=2.0)
            ax.annotate(f"hotspot\n{res['hotspot_px']} px\n"
                        f"~{res['hotspot_area_m2']/1e4:.2f} ha",
                        xy=(c[1] - x0, c[0] - y0),
                        xytext=(6, 6), textcoords="offset points",
                        color="red", fontsize=8, weight="bold")

        ax.set_title(
            f"{qid.replace('quebrada_', '')}  "
            f"Δmedio={res['delta_medio']:+.3f}\n"
            f"%green>+0.10={res['frac_green']*100:.0f}%  | {res['diag']}",
            fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])

    cbar = fig.colorbar(im, ax=axes, fraction=0.035, pad=0.02)
    cbar.set_label("ΔNDVI = (2026-01-11) − (2025-02-18)\nverde=greening · marrón=browning")
    fig.suptitle(
        "Localización del greening en quebradas riparias Q8 y Q9 — Laguna del Maule\n"
        f"escala ≈ {m_px:.1f} m/px · vegetación: NDVI≥{VEG_THR} en ambas fechas (Guinn L882)",
        fontsize=12)
    fig.savefig(OUT_PNG, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return OUT_PNG


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    meta = cargar_meta(FECHA_B)
    bbox = tuple(meta["bbox"])
    shape = tuple(meta["shape"])
    m_px = metros_por_pixel(meta)

    a = cargar_ndvi(FECHA_A)
    b = cargar_ndvi(FECHA_B)
    assert a.shape == tuple(shape) == b.shape, (a.shape, shape, b.shape)

    delta = b - a
    veg_mask = (a >= VEG_THR) & (b >= VEG_THR)

    aois = cargar_aois()

    print("=" * 78)
    print(f"ΔNDVI = NDVI({FECHA_B}) - NDVI({FECHA_A})   |   escala {m_px:.2f} m/px")
    print(f"Vegetación: NDVI>={VEG_THR} en AMBAS fechas. "
          f"greening>={GREEN_THR}; hotspot>={HOTSPOT_THR}")
    print("=" * 78)

    resultados = {}
    todas = QUEBRADAS_FOCO + QUEBRADAS_CONTROL
    for qid in todas:
        if qid not in aois:
            print(f"[WARN] {qid} no está en la config"); continue
        res = analizar_quebrada(aois[qid], bbox, shape, delta, veg_mask, m_px)
        resultados[qid] = res
        tag = "FOCO" if qid in QUEBRADAS_FOCO else "control"
        print(f"\n{qid}  [{tag}]")
        print(f"  px máscara={res['n_mask_px']}  px vegetación válidos={res['n_valid_px']}")
        if res["n_valid_px"] == 0:
            print(f"  -> {res['diag']}"); continue
        print(f"  Δ medio          = {res['delta_medio']:+.4f}")
        print(f"  % greening>+0.10 = {res['frac_green']*100:.1f}%")
        print(f"  greening fuerte (>+0.15): {int(res.get('frac_strong',0)*res['n_valid_px'])} px "
              f"en {res['n_hotspot']} cluster(s); mayor={res['hotspot_px']} px "
              f"(~{res['hotspot_area_m2']/1e4:.2f} ha)")
        print(f"  concentración (mayor/total fuerte) = {res.get('concentracion',0)*100:.0f}%")
        c = centroide_mayor_hotspot(res)
        if c:
            print(f"  centro hotspot (row,col) = ({c[0]:.0f},{c[1]:.0f})")
        print(f"  DIAGNÓSTICO: {res['diag']}")

    png = figura_q8q9(delta, resultados, m_px)
    print("\n" + "=" * 78)
    print(f"Figura escrita en: {png}")
    print("=" * 78)
    return resultados


if __name__ == "__main__":
    main()
