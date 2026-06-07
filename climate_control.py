"""
climate_control.py — Control del confusor climático (estacional/sequía) sobre NDVI.

Implementa la estrategia citada de remover la influencia del clima de la señal de
vegetación, para no confundir variabilidad meteorológica con señal volcánica:

  - Guinn 2024 (PD-001): remover por regresión lineal la influencia de lluvia/temp
    cuando r² > 0.1.
  - De Schutter 2015 (PD-014): la vegetación responde a la precipitación ANTECEDENTE
    con un lag óptimo de ~48 días → se acumula la lluvia de la ventana previa.
  - CAMELS-CL / CR2MET (PD-012, Alvarez-Garreton 2018): fuente autoritativa para Chile.

FUENTE DE DATOS:
  - Por defecto usa Open-Meteo Historical Archive (gratis, sin key, global) — funciona ya.
  - UPGRADE recomendado para Chile: CR2MET (más preciso, validado localmente). Para usarlo,
    implementar fetch_climate_cr2met() leyendo el NetCDF de CR2 (https://www.cr2.cl/datos-productos-grillados/).
    La interfaz (devolver dict {fecha: {precip_antecedente, temp_media}}) es la misma.

Uso como librería:
    from climate_control import build_climate_series, apply_climate_control
    clima = build_climate_series(lat, lon, fechas)              # dict por fecha
    res = apply_climate_control(ndvi_serie, fechas, clima, var='precip')  # serie corregida

Uso CLI (demo sobre un AOI):
    python climate_control.py --volcan "Laguna del Maule" --aoi sector_sur_co2
"""
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import requests
import numpy as np

from vegstress_signal import regress_out_climate

ROOT  = Path(__file__).parent
DATOS = ROOT / "datos"

OPEN_METEO = "https://archive-api.open-meteo.com/v1/archive"
LAG_ANTECEDENTE_DIAS = 48   # De Schutter 2015 (PD-014): lag óptimo lluvia→vegetación


def fetch_climate_openmeteo(lat, lon, start_date, end_date):
    """Devuelve dict {fecha_iso: {'precip': mm, 'temp': C}} diario de Open-Meteo."""
    r = requests.get(OPEN_METEO, params={
        'latitude': lat, 'longitude': lon,
        'start_date': start_date, 'end_date': end_date,
        'daily': 'precipitation_sum,temperature_2m_mean', 'timezone': 'auto',
    }, timeout=40)
    r.raise_for_status()
    d = r.json().get('daily', {})
    out = {}
    for i, t in enumerate(d.get('time', [])):
        out[t] = {
            'precip': d['precipitation_sum'][i] if d.get('precipitation_sum') else None,
            'temp':   d['temperature_2m_mean'][i] if d.get('temperature_2m_mean') else None,
        }
    return out


def build_climate_series(lat, lon, fechas, lag_dias=LAG_ANTECEDENTE_DIAS):
    """
    Para cada fecha NDVI, calcula la precipitación ANTECEDENTE acumulada (suma de los
    `lag_dias` previos) y la temperatura media de esa ventana (De Schutter 2015).

    Returns: dict {fecha: {'precip_antecedente': mm, 'temp_media': C}}
    """
    fechas = sorted(fechas)
    f0 = (datetime.strptime(fechas[0], '%Y-%m-%d') - timedelta(days=lag_dias + 2)).strftime('%Y-%m-%d')
    f1 = fechas[-1]
    diario = fetch_climate_openmeteo(lat, lon, f0, f1)

    out = {}
    for f in fechas:
        fin = datetime.strptime(f, '%Y-%m-%d')
        ini = fin - timedelta(days=lag_dias)
        precs, temps = [], []
        cur = ini
        while cur <= fin:
            k = cur.strftime('%Y-%m-%d')
            if k in diario:
                if diario[k]['precip'] is not None: precs.append(diario[k]['precip'])
                if diario[k]['temp']   is not None: temps.append(diario[k]['temp'])
            cur += timedelta(days=1)
        out[f] = {
            'precip_antecedente': round(float(np.sum(precs)), 1) if precs else None,
            'temp_media':         round(float(np.mean(temps)), 1) if temps else None,
        }
    return out


def apply_climate_control(ndvi_serie, fechas, clima, var='precip'):
    """
    Aplica regress_out_climate() para remover el confusor climático de la serie NDVI.

    Args:
        ndvi_serie: lista de NDVI medio por fecha.
        fechas: lista de fechas (mismo orden).
        clima: dict de build_climate_series.
        var: 'precip' (usa precip_antecedente) o 'temp' (usa temp_media).

    Returns: dict de regress_out_climate (r2, removed, residual, ...) + la serie climática usada.
    """
    key = 'precip_antecedente' if var == 'precip' else 'temp_media'
    clim_vals = [clima.get(f, {}).get(key) for f in fechas]
    clim_arr = np.array([np.nan if v is None else v for v in clim_vals], dtype=float)
    res = regress_out_climate(np.asarray(ndvi_serie, dtype=float), clim_arr, r2_threshold=0.1)
    res['clima_serie'] = [None if (v != v) else round(float(v), 1) for v in clim_arr]
    res['var'] = var
    return res


def _aoi_ndvi_series(volcan, aoi_id):
    """Construye la serie NDVI media (solo vegetación) de un AOI sobre todas las fechas."""
    from change_detector import load_config, list_available_dates, load_array, aoi_mask
    cfg = load_config()
    umbrales = cfg.get('umbrales_globales', {})
    ndvi_min = umbrales.get('ndvi_min_valido', 0.4)
    vcfg = cfg.get('volcanes', {}).get(volcan, {})
    aoi = next((a for a in vcfg.get('aois', []) if a['id'] == aoi_id), None)
    if not aoi:
        return None, None, None
    dates = list_available_dates(volcan)
    serie, fechas_ok = [], []
    bbox = None
    for f in dates:
        arr, meta = load_array(volcan, f)
        if arr is None:
            continue
        if bbox is None:
            bbox = meta.get('bbox')
        mask, _ = aoi_mask(aoi, bbox, arr.shape)
        vals = arr[mask]
        vals = vals[(~np.isnan(vals)) & (vals >= ndvi_min)]
        if len(vals) >= 20:
            serie.append(float(np.mean(vals)))
            fechas_ok.append(f)
    return aoi, serie, fechas_ok


def main():
    ap = argparse.ArgumentParser(description='Control climático del NDVI (demo por AOI)')
    ap.add_argument('--volcan', default='Laguna del Maule')
    ap.add_argument('--aoi', required=True, help='id del AOI en aoi_config.json')
    ap.add_argument('--var', default='precip', choices=['precip', 'temp'])
    args = ap.parse_args()

    aoi, serie, fechas = _aoi_ndvi_series(args.volcan, args.aoi)
    if not aoi:
        print(f"  AOI '{args.aoi}' no encontrada."); return
    if len(serie) < 3:
        print(f"  Serie muy corta ({len(serie)} fechas con vegetación). Se necesitan >=3.")
        print(f"  (El AOI puede estar sobre roca/nieve — ver aoi_finder.py)"); return

    print(f"\n  AOI: {aoi['nombre']}  ({len(serie)} fechas con vegetación)")
    clima = build_climate_series(aoi['lat'], aoi['lon'], fechas)
    res = apply_climate_control(serie, fechas, clima, var=args.var)

    print(f"  {'fecha':12s} {'NDVI':>7s} {'clima('+args.var+')':>14s}")
    for f, n, c in zip(fechas, serie, res['clima_serie']):
        print(f"  {f:12s} {n:>7.3f} {str(c):>14s}")
    print(f"\n  Regresión NDVI ~ {args.var}:  r²={res['r2']:.3f}  removido={res['removed']}")
    if res['removed']:
        print(f"  → El clima explicaba {res['r2']*100:.0f}% de la varianza NDVI; removido.")
        print(f"  NDVI corregido (sin clima): {[round(float(v),3) for v in res['residual']]}")
    else:
        print(f"  → r² < 0.1: el clima NO explica la señal. NDVI sin cambios (señal robusta).")


if __name__ == '__main__':
    main()
