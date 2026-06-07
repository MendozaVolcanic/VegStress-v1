"""
find_clear_dates.py — Escanea un rango histórico y reporta las fechas Sentinel-2
con mejor cobertura válida (poca nube) para un volcán, a baja resolución (rápido/barato).

Sirve para alimentar la serie temporal (>=4 fechas) que necesita el detector por 2ª
derivada (Guinn 2024) y el control climático, sin gastar cuota en descargas full-res
de imágenes nubladas.

Uso:
    python find_clear_dates.py --volcan "Laguna del Maule" --desde 2024-11-01 --hasta 2026-04-30 --paso 10
    # luego: python spatial_mapper.py --volcan "Laguna del Maule" --fecha <fecha_despejada>
"""
import sys
import time
import argparse
from io import BytesIO
from datetime import datetime, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import requests
import tifffile
from spatial_mapper import get_token, create_bbox, VOLCANES, PROCESS_API_URL

EVAL = """
//VERSION=3
function setup() { return { input:[{bands:["B04","B08","SCL"]}], output:{bands:3,sampleType:"FLOAT32"} } }
function evaluatePixel(s) {
  let valid = (s.SCL>=4 && s.SCL<=6) ? 1.0 : 0.0;
  let cloud = (s.SCL>=8 && s.SCL<=10) ? 1.0 : 0.0;
  return [(s.B08-s.B04)/(s.B08+s.B04+0.0001), valid, cloud];
}
"""


def probe(token, bbox, fecha):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        "input": {"bounds": {"bbox": bbox, "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}},
                  "data": [{"type": "sentinel-2-l2a", "dataFilter": {
                      "timeRange": {"from": f"{fecha}T00:00:00Z", "to": f"{fecha}T23:59:59Z"},
                      "maxCloudCoverage": 90}}]},
        "output": {"width": 128, "height": 128,
                   "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]},
        "evalscript": EVAL,
    }
    try:
        r = requests.post(PROCESS_API_URL, headers=headers, json=payload, timeout=30)
        if r.status_code != 200:
            return None
        arr = tifffile.imread(BytesIO(r.content))
        if arr.ndim == 3 and arr.shape[2] >= 3:
            return float(arr[:, :, 1].mean() * 100), float(arr[:, :, 2].mean() * 100)
    except Exception:
        return None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--volcan', default='Laguna del Maule')
    ap.add_argument('--desde', required=True, help='YYYY-MM-DD')
    ap.add_argument('--hasta', required=True, help='YYYY-MM-DD')
    ap.add_argument('--paso', type=int, default=10, help='dias entre sondeos')
    ap.add_argument('--min_valid', type=float, default=60, help='%% valido minimo para listar')
    args = ap.parse_args()

    v = VOLCANES[args.volcan]
    bbox = create_bbox(v['lat'], v['lon'], v['buffer_km'])
    token = get_token()
    print(f"  Escaneando {args.volcan} de {args.desde} a {args.hasta} cada {args.paso} dias...")

    d = datetime.strptime(args.desde, '%Y-%m-%d')
    end = datetime.strptime(args.hasta, '%Y-%m-%d')
    good = []
    while d <= end:
        f = d.strftime('%Y-%m-%d')
        res = probe(token, bbox, f)
        if res:
            valid, cloud = res
            if valid >= args.min_valid:
                good.append((f, valid, cloud))
                print(f"    ✓ {f}: valido={valid:.0f}% nubes={cloud:.0f}%")
        d += timedelta(days=args.paso)
        time.sleep(0.25)

    print(f"\n  {len(good)} fecha(s) despejada(s) (>={args.min_valid}% valido):")
    for f, vp, cp in sorted(good, key=lambda x: -x[1]):
        print(f"    {f}  valido={vp:.0f}%  nubes={cp:.0f}%")
    if good:
        print("\n  Descargar las mejores con:")
        for f, vp, cp in sorted(good, key=lambda x: -x[1])[:6]:
            print(f"    python spatial_mapper.py --volcan \"{args.volcan}\" --fecha {f}")


if __name__ == '__main__':
    main()
