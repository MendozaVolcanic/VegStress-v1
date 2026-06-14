"""
rededge_gas.py — NDRE (red-edge) sobre el área de desgasificación de Laguna del Maule.

Por qué red-edge (decisión 2026-06-13): el NDVI no mostró firma de la desgasificación en
el área de campo. El NDVI satura en vegetación densa y responde tarde; el RED-EDGE (banda
B05, 705 nm) es más sensible al contenido de clorofila y al estrés TEMPRANO (Eitel et al.
2006; ver GAPS/SYNTHESIS). NDRE = (B08 - B05)/(B08 + B05) puede captar un cambio fisiológico
que el NDVI no ve todavía.

NOTA de honestidad: NDRE es un índice ESTÁNDAR; acá lo usamos en modo RELATIVO/tendencia
(mismo-mes inter-anual, clima de la zona descontado), que NO requiere un umbral absoluto
citado. Un umbral absoluto de estrés sí requeriría cita (Eitel 2006, pendiente).

Descarga NDRE + NDVI a 10 m sobre un tile centrado en el polígono de gas, para los 6
febreros 2021-2026, y compara la tendencia de NDRE vs NDVI en la vegetación del área.

Uso:
    python rededge_gas.py                 # descarga (si faltan) + analiza
    python rededge_gas.py --solo_analisis # no descarga, usa lo que haya
"""
import sys
import json
import argparse
import numpy as np
from pathlib import Path
from io import BytesIO

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass

import requests
import tifffile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath

from spatial_mapper import get_token, PROCESS_API_URL

ROOT  = Path(__file__).parent
DATOS = ROOT / "datos" / "Laguna_del_Maule"
DOCS  = ROOT / "docs" / "maps"
REDIR = DATOS / "rededge"

FEBS = ["2021-02-19", "2022-02-19", "2023-02-19", "2024-02-19", "2025-02-18", "2026-02-16"]

EVAL = """
//VERSION=3
function setup(){return {input:[{bands:["B04","B05","B08","SCL"]}],output:{bands:3,sampleType:"FLOAT32"}}}
function evaluatePixel(s){
  let ndvi=(s.B08-s.B04)/(s.B08+s.B04+1e-6);
  let ndre=(s.B08-s.B05)/(s.B08+s.B05+1e-6);
  let valid=(s.SCL>=4 && s.SCL<=6)?1.0:0.0;
  return [ndre, ndvi, valid];
}
"""


def gas_bbox(pad=0.02):
    area = json.load(open(ROOT / "datos" / "area_desgasificacion.json", encoding="utf-8"))
    poly = area["poligono_latlon"]
    lons = [lo for la, lo in poly]; lats = [la for la, lo in poly]
    bbox = [min(lons)-pad, min(lats)-pad, max(lons)+pad, max(lats)+pad]
    return bbox, poly


def download(token, bbox, fecha):
    lon_w, lat_s, lon_e, lat_n = bbox
    w = int((lon_e-lon_w)*111000*abs(np.cos(np.radians((lat_s+lat_n)/2)))/10)
    h = int((lat_n-lat_s)*111000/10)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        "input": {"bounds": {"bbox": bbox, "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}},
                  "data": [{"type": "sentinel-2-l2a", "dataFilter": {
                      "timeRange": {"from": f"{fecha}T00:00:00Z", "to": f"{fecha}T23:59:59Z"},
                      "maxCloudCoverage": 100}}]},
        "output": {"width": w, "height": h, "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
        "evalscript": EVAL,
    }
    r = requests.post(PROCESS_API_URL, headers=headers, json=payload, timeout=120)
    if r.status_code != 200:
        print(f"    {fecha}: error {r.status_code} {r.text[:120]}"); return None
    arr = tifffile.imread(BytesIO(r.content)).astype(np.float32)  # (H,W,3) ndre,ndvi,valid
    valid = arr[:, :, 2] > 0.5
    ndre = np.where(valid, arr[:, :, 0], np.nan)
    ndvi = np.where(valid, arr[:, :, 1], np.nan)
    return ndre, ndvi, bbox, (h, w)


def ensure_downloads(solo_analisis):
    REDIR.mkdir(parents=True, exist_ok=True)
    bbox, poly = gas_bbox()
    token = None
    for f in FEBS:
        p = REDIR / f"rededge_{f}.npz"
        if p.exists():
            continue
        if solo_analisis:
            print(f"    {f}: falta (modo solo_analisis, se omite)"); continue
        if token is None:
            token = get_token(); print("  Auth OK")
        res = download(token, bbox, f)
        if res is None:
            continue
        ndre, ndvi, bb, shp = res
        np.savez_compressed(p, ndre=ndre, ndvi=ndvi, bbox=np.array(bb), shape=np.array(shp))
        cov = float(np.isfinite(ndvi).mean()*100)
        print(f"    {f}: descargado {shp[1]}x{shp[0]} px, válido {cov:.0f}%")
    return bbox, poly


def analyze(bbox, poly, min_frac=0.7):
    files = {f: REDIR / f"rededge_{f}.npz" for f in FEBS if (REDIR / f"rededge_{f}.npz").exists()}
    if len(files) < 4:
        print(f"  Solo {len(files)} febreros con red-edge; se necesitan >=4."); return
    feb_ok = sorted(files)
    data = {f: np.load(files[f]) for f in feb_ok}
    H, W = data[feb_ok[0]]['shape']
    ndre = np.stack([data[f]['ndre'] for f in feb_ok])   # (T,H,W)
    ndvi = np.stack([data[f]['ndvi'] for f in feb_ok])
    años = np.array([int(f[:4]) for f in feb_ok], float)

    # máscara polígono
    lon_w, lat_s, lon_e, lat_n = bbox
    ys, xs = np.mgrid[0:H, 0:W]
    lons = lon_w + (xs+0.5)/W*(lon_e-lon_w); lats = lat_n - (ys+0.5)/H*(lat_n-lat_s)
    mpoly = MplPath([(lo, la) for la, lo in poly])
    in_poly = mpoly.contains_points(np.column_stack([lons.ravel(), lats.ravel()])).reshape(H, W)

    # vegetación: NDVI>=0.41 en >=min_frac de los febreros
    with np.errstate(invalid='ignore'):
        veg = (np.nansum(ndvi >= 0.41, axis=0) / len(feb_ok)) >= min_frac
    veg_gas = veg & in_poly
    veg_tile = veg  # fondo local (todo el tile) para descontar clima

    print(f"\n  Febreros con red-edge ({len(feb_ok)}): {feb_ok}")
    print(f"  Vegetación en área de gas: {int(veg_gas.sum())} px | en tile (fondo): {int(veg_tile.sum())} px")
    if veg_gas.sum() < 10:
        print("  Muy poca vegetación en el área para una serie fiable."); return

    def serie(stack, mask):
        out = []
        for t in range(stack.shape[0]):
            v = stack[t][mask]
            v = v[np.isfinite(v)]
            out.append(float(np.mean(v)) if len(v) >= 5 else np.nan)
        return np.array(out)

    def fit(x, y):
        m = np.isfinite(y)
        if m.sum() < 4: return np.nan, np.nan
        s, b = np.polyfit(x[m], y[m], 1)
        pred = s*x[m]+b; sr = np.sum((y[m]-pred)**2); st = np.sum((y[m]-np.mean(y[m]))**2)
        return float(s), float(1-sr/st if st > 1e-12 else 0.0)

    # series del área de gas y del fondo (tile), para NDRE y NDVI
    res = {}
    for nombre, stack in [("NDRE", ndre), ("NDVI", ndvi)]:
        s_gas = serie(stack, veg_gas)
        s_bg  = serie(stack, veg_tile)
        resid = s_gas - s_bg
        sl_g, r2_g = fit(años, s_gas)
        sl_r, r2_r = fit(años, resid)
        res[nombre] = dict(gas=s_gas, bg=s_bg, resid=resid, slope_gas=sl_g, r2_gas=r2_g,
                           slope_resid=sl_r, r2_resid=r2_r)
        print(f"\n  {nombre}:")
        print(f"    serie gas:    {[round(float(v),3) for v in s_gas]}")
        print(f"    fondo tile:   {[round(float(v),3) for v in s_bg]}")
        print(f"    residuo:      {[round(float(v),3) for v in resid]}")
        print(f"    pend gas={sl_g:+.4f}/año (r²={r2_g:.2f}) | pend residuo={sl_r:+.4f}/año (r²={r2_r:.2f})")

    # veredicto comparativo
    print("\n  ── ¿Red-edge ve algo que NDVI no? ──")
    nd = res["NDRE"]["slope_resid"]; nv = res["NDVI"]["slope_resid"]
    print(f"    Pendiente residual NDRE={nd:+.4f} (r²={res['NDRE']['r2_resid']:.2f})  vs  "
          f"NDVI={nv:+.4f} (r²={res['NDVI']['r2_resid']:.2f})")
    if abs(nd) >= 0.008 and res["NDRE"]["r2_resid"] >= 0.5 and abs(nd) > 1.5*abs(nv):
        print("    -> NDRE muestra una tendencia residual que el NDVI NO capta. Señal candidata "
              "(estrés temprano red-edge). Requiere validación de campo + Eitel 2006 para umbral.")
    else:
        print("    -> NDRE NO aporta una tendencia residual robusta más allá del NDVI. "
              "Consistente con ausencia de firma detectable también en red-edge.")

    # figura
    fig, ax = plt.subplots(figsize=(9, 6), facecolor='#0f1117')
    for nombre, col in [("NDRE", '#00e5ff'), ("NDVI", '#7cc35a')]:
        ax.plot(años, res[nombre]['gas'], '-o', color=col, label=f"{nombre} área gas")
        ax.plot(años, res[nombre]['bg'], '--', color=col, alpha=0.5, label=f"{nombre} fondo tile")
    ax.set_title('Área de desgasificación — NDRE vs NDVI por febrero (2021-2026)\nLaguna del Maule',
                 color='#e2e8f0', fontweight='bold')
    ax.set_ylabel('índice', color='#8892a4'); ax.tick_params(colors='#8892a4')
    ax.set_facecolor('#1a1d26'); ax.grid(alpha=0.15)
    for sp in ax.spines.values(): sp.set_edgecolor('#2a2d3a')
    ax.legend(facecolor='#1a1d26', labelcolor='#e2e8f0', edgecolor='#2a2d3a', fontsize=8)
    out = DOCS / "Laguna_del_Maule_rededge_gas.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=140, facecolor='#0f1117', bbox_inches='tight'); plt.close()
    print(f"\n  Figura: {out}")

    out_json = DATOS / "rededge_gas.json"
    js = {"febreros": feb_ok}
    for k, v in res.items():
        js[k] = {kk: ([round(float(x),4) for x in vv] if isinstance(vv, np.ndarray) else round(float(vv),4))
                 for kk, vv in v.items()}
    json.dump(js, open(out_json, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"  JSON: {out_json}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--solo_analisis', action='store_true')
    args = ap.parse_args()
    print(f"\n{'='*64}\n NDRE (red-edge) — área de desgasificación LdM\n{'='*64}")
    bbox, poly = ensure_downloads(args.solo_analisis)
    analyze(bbox, poly)


if __name__ == '__main__':
    main()
