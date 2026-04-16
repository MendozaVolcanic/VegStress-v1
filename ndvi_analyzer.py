"""
NDVI Analyzer — VegStress-v1
Descarga y analiza NDVI desde Sentinel-2 via Sentinel Hub API.
Reutiliza credenciales de Copernicus-v1.

Uso:
    python ndvi_analyzer.py                    # Laguna del Maule, último año
    python ndvi_analyzer.py --volcan Villarrica --meses 6
"""

import requests
import numpy as np
import os
import sys
import json
import math
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO

# Fix encoding en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Cargar .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass

# ============================================
# CONFIGURACIÓN
# ============================================

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_API_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

# Evalscript que retorna NDVI como float32 single-band
EVALSCRIPT_NDVI = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: ["B04", "B08", "SCL"]
    }],
    output: {
      bands: 4,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  // NDVI = (NIR - Red) / (NIR + Red)
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04 + 0.0001);

  // Scene Classification Layer:
  // 4 = vegetation, 5 = bare soil, 6 = water
  // 8 = cloud medium, 9 = cloud high, 10 = cirrus, 11 = snow
  let scl = sample.SCL;
  let is_valid = (scl >= 4 && scl <= 6);  // solo vegetación, suelo, agua
  let is_cloud = (scl >= 8 && scl <= 10);
  let is_snow = (scl == 11);

  return [ndvi, is_valid ? 1.0 : 0.0, is_cloud ? 1.0 : 0.0, is_snow ? 1.0 : 0.0];
}
"""

# Evalscript para imagen NDVI coloreada (visualización)
EVALSCRIPT_NDVI_COLOR = """
//VERSION=3
function setup() {
  return {
    input: [{bands: ["B04", "B08", "SCL"]}],
    output: {bands: 3, sampleType: "AUTO"}
  };
}

function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04 + 0.0001);
  let scl = sample.SCL;

  // Nubes: blanco
  if (scl >= 8 && scl <= 10) return [0.9, 0.9, 0.9];
  // Nieve: cian claro
  if (scl == 11) return [0.7, 0.9, 1.0];
  // Agua: azul
  if (scl == 6) return [0.0, 0.2, 0.6];

  // Paleta NDVI: rojo (estrés) -> amarillo -> verde (sano)
  if (ndvi < -0.1) return [0.5, 0.5, 0.5];  // sin vegetación
  if (ndvi < 0.1)  return [0.8, 0.6, 0.4];   // suelo
  if (ndvi < 0.2)  return [0.9, 0.3, 0.1];   // estrés severo
  if (ndvi < 0.3)  return [0.95, 0.6, 0.1];  // estrés moderado
  if (ndvi < 0.4)  return [0.9, 0.9, 0.2];   // vegetación baja
  if (ndvi < 0.5)  return [0.6, 0.8, 0.2];   // vegetación media
  if (ndvi < 0.6)  return [0.3, 0.7, 0.1];   // vegetación buena
  return [0.0, 0.5, 0.0];                     // vegetación densa
}
"""

# Volcanes con coordenadas (subset del config de Copernicus-v1)
VOLCANES = {
    "Laguna del Maule": {"lat": -36.07100, "lon": -70.49828, "buffer_km": 9.0, "zona": "Centro"},
    "Villarrica": {"lat": -39.42052, "lon": -71.93939, "buffer_km": 5.0, "zona": "Sur"},
    "Copahue": {"lat": -37.85715, "lon": -71.16836, "buffer_km": 5.0, "zona": "Sur"},
    "Llaima": {"lat": -38.71238, "lon": -71.73447, "buffer_km": 6.0, "zona": "Sur"},
    "Nevados de Chillan": {"lat": -37.41096, "lon": -71.35231, "buffer_km": 5.0, "zona": "Centro"},
    "Calbuco": {"lat": -41.32863, "lon": -72.61131, "buffer_km": 5.0, "zona": "Sur"},
    "Lascar": {"lat": -23.36726, "lon": -67.73611, "buffer_km": 5.0, "zona": "Norte"},
    "Puyehue - Cordon Caulle": {"lat": -40.55879, "lon": -72.12476, "buffer_km": 7.0, "zona": "Sur"},
    "Chaiten": {"lat": -42.83938, "lon": -72.64987, "buffer_km": 5.0, "zona": "Sur"},
    "Osorno": {"lat": -41.13500, "lon": -72.49700, "buffer_km": 5.0, "zona": "Sur"},
}


# ============================================
# AUTENTICACIÓN
# ============================================

class SentinelAuth:
    def __init__(self):
        self.client_id = os.getenv('SH_CLIENT_ID')
        self.client_secret = os.getenv('SH_CLIENT_SECRET')
        if not self.client_id or not self.client_secret:
            raise ValueError("Variables SH_CLIENT_ID y SH_CLIENT_SECRET requeridas")
        self.access_token = None
        self.token_expiry = 0

    def get_headers(self):
        import time
        if not self.access_token or time.time() >= self.token_expiry:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            resp = requests.post(TOKEN_URL, data=data, timeout=30)
            resp.raise_for_status()
            token_data = resp.json()
            self.access_token = token_data['access_token']
            import time as t
            self.token_expiry = t.time() + token_data.get('expires_in', 3600) - 300
            print(f"  Token obtenido (expira en {token_data.get('expires_in', 3600)//60} min)")
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }


# ============================================
# DESCARGA NDVI
# ============================================

def create_bbox(lat, lon, buffer_km):
    delta_lat = buffer_km / 111.0
    delta_lon = buffer_km / (111.0 * abs(math.cos(math.radians(lat))))
    return [lon - delta_lon, lat - delta_lat, lon + delta_lon, lat + delta_lat]


def download_ndvi_stats(auth, lat, lon, fecha, buffer_km):
    """Descarga NDVI como array float32 y calcula estadísticas."""
    bbox = create_bbox(lat, lon, buffer_km)

    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{fecha}T00:00:00Z",
                        "to": f"{fecha}T23:59:59Z"
                    },
                    "maxCloudCoverage": 100
                }
            }]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]
        },
        "evalscript": EVALSCRIPT_NDVI
    }

    resp = requests.post(PROCESS_API_URL, headers=auth.get_headers(),
                         json=payload, timeout=60)

    if resp.status_code != 200:
        return None

    # Parsear TIFF float32 con 4 bandas
    try:
        import tifffile

        arr = tifffile.imread(BytesIO(resp.content))

        if arr.ndim == 3 and arr.shape[2] >= 4:
            # tifffile retorna (height, width, bands)
            ndvi = arr[:, :, 0].astype(np.float32)
            valid_mask = arr[:, :, 1] > 0.5
            cloud_mask = arr[:, :, 2] > 0.5
            snow_mask = arr[:, :, 3] > 0.5
        elif arr.ndim == 3 and arr.shape[0] == 4:
            # formato alternativo (bands, height, width)
            ndvi = arr[0].astype(np.float32)
            valid_mask = arr[1] > 0.5
            cloud_mask = arr[2] > 0.5
            snow_mask = arr[3] > 0.5
        else:
            ndvi = arr.astype(np.float32)
            valid_mask = np.ones_like(ndvi, dtype=bool)
            cloud_mask = np.zeros_like(ndvi, dtype=bool)
            snow_mask = np.zeros_like(ndvi, dtype=bool)

        total_pixels = ndvi.size
        valid_pixels = valid_mask.sum()
        cloud_pixels = cloud_mask.sum()
        snow_pixels = snow_mask.sum()

        if valid_pixels < 10:
            return {
                'fecha': fecha,
                'ndvi_mean': None,
                'ndvi_median': None,
                'ndvi_std': None,
                'ndvi_min': None,
                'ndvi_max': None,
                'valid_pct': float(valid_pixels / total_pixels * 100),
                'cloud_pct': float(cloud_pixels / total_pixels * 100),
                'snow_pct': float(snow_pixels / total_pixels * 100),
                'status': 'NUBLADO' if cloud_pixels > total_pixels * 0.5 else 'NIEVE' if snow_pixels > total_pixels * 0.3 else 'SIN_DATOS'
            }

        ndvi_valid = ndvi[valid_mask]

        return {
            'fecha': fecha,
            'ndvi_mean': float(np.mean(ndvi_valid)),
            'ndvi_median': float(np.median(ndvi_valid)),
            'ndvi_std': float(np.std(ndvi_valid)),
            'ndvi_min': float(np.percentile(ndvi_valid, 5)),
            'ndvi_max': float(np.percentile(ndvi_valid, 95)),
            'valid_pct': float(valid_pixels / total_pixels * 100),
            'cloud_pct': float(cloud_pixels / total_pixels * 100),
            'snow_pct': float(snow_pixels / total_pixels * 100),
            'status': 'OK'
        }
    except Exception as e:
        print(f"    Error procesando TIFF: {e}")
        return None


def download_ndvi_image(auth, lat, lon, fecha, buffer_km, output_path):
    """Descarga imagen NDVI coloreada (PNG) para visualización."""
    bbox = create_bbox(lat, lon, buffer_km)

    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{fecha}T00:00:00Z",
                        "to": f"{fecha}T23:59:59Z"
                    },
                    "maxCloudCoverage": 100
                }
            }]
        },
        "output": {
            "width": 800,
            "height": 800,
            "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
        },
        "evalscript": EVALSCRIPT_NDVI_COLOR
    }

    resp = requests.post(PROCESS_API_URL, headers=auth.get_headers(),
                         json=payload, timeout=60)

    if resp.status_code == 200:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(resp.content)
        return True
    return False


# ============================================
# ANÁLISIS DE SERIE TEMPORAL
# ============================================

def analyze_volcano(volcan_name, meses=12, save_images=True):
    """Analiza NDVI temporal para un volcán."""

    if volcan_name not in VOLCANES:
        print(f"Volcán '{volcan_name}' no encontrado. Disponibles: {list(VOLCANES.keys())}")
        return None

    config = VOLCANES[volcan_name]
    lat, lon = config['lat'], config['lon']
    buffer_km = config['buffer_km']

    print(f"\n{'='*60}")
    print(f" VegStress-v1 — Análisis NDVI: {volcan_name}")
    print(f" Coordenadas: {lat:.4f}, {lon:.4f} | Buffer: {buffer_km} km")
    print(f" Período: últimos {meses} meses")
    print(f"{'='*60}\n")

    # Directorio de salida
    output_dir = Path(__file__).parent / "datos" / volcan_name.replace(" ", "_")
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "ndvi_images"
    if save_images:
        images_dir.mkdir(parents=True, exist_ok=True)

    auth = SentinelAuth()

    # Generar lista de fechas (cada 5 días para no sobrecargar API)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=meses * 30)

    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=5)

    print(f"  Consultando {len(dates)} fechas...\n")

    results = []
    for i, fecha in enumerate(dates):
        print(f"  [{i+1}/{len(dates)}] {fecha}...", end=" ", flush=True)

        stats = download_ndvi_stats(auth, lat, lon, fecha, buffer_km)

        if stats:
            results.append(stats)
            status = stats['status']
            if status == 'OK':
                ndvi_str = f"NDVI={stats['ndvi_mean']:.3f} ±{stats['ndvi_std']:.3f}"
                cloud_str = f"nubes={stats['cloud_pct']:.0f}%"
                print(f"✓ {ndvi_str} | {cloud_str}")

                if save_images:
                    img_path = images_dir / f"{fecha}_NDVI.png"
                    download_ndvi_image(auth, lat, lon, fecha, buffer_km, str(img_path))
            else:
                print(f"⚠ {status} (nubes={stats['cloud_pct']:.0f}%, nieve={stats['snow_pct']:.0f}%)")
        else:
            print("✗ Sin imagen disponible")

        # Rate limiting
        import time
        time.sleep(0.5)

    if not results:
        print("\n  No se obtuvieron datos.")
        return None

    # Guardar CSV
    csv_path = output_dir / "ndvi_timeseries.csv"
    import csv
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n  Serie temporal guardada: {csv_path}")

    # Análisis de anomalías
    ok_results = [r for r in results if r['status'] == 'OK' and r['ndvi_mean'] is not None]

    if len(ok_results) >= 5:
        ndvi_values = [r['ndvi_mean'] for r in ok_results]
        mean_ndvi = np.mean(ndvi_values)
        std_ndvi = np.std(ndvi_values)

        print(f"\n  {'='*50}")
        print(f"  RESUMEN — {volcan_name}")
        print(f"  {'='*50}")
        print(f"  Imágenes válidas: {len(ok_results)}/{len(results)}")
        print(f"  NDVI promedio:    {mean_ndvi:.4f}")
        print(f"  NDVI std:         {std_ndvi:.4f}")
        print(f"  NDVI rango:       {min(ndvi_values):.4f} — {max(ndvi_values):.4f}")

        # Detectar anomalías (>2σ)
        anomalies = []
        for r in ok_results:
            z_score = (r['ndvi_mean'] - mean_ndvi) / (std_ndvi + 0.0001)
            if abs(z_score) > 2.0:
                anomalies.append({
                    'fecha': r['fecha'],
                    'ndvi': r['ndvi_mean'],
                    'z_score': z_score,
                    'tipo': 'BROWNING' if z_score < -2 else 'GREENING'
                })

        if anomalies:
            print(f"\n  ⚠ ANOMALÍAS DETECTADAS ({len(anomalies)}):")
            for a in anomalies:
                print(f"    {a['fecha']}: NDVI={a['ndvi']:.4f} (z={a['z_score']:.1f}) → {a['tipo']}")
        else:
            print(f"\n  ✓ Sin anomalías significativas (umbral: ±2σ)")

        # Generar gráfico
        try:
            generate_plot(volcan_name, ok_results, mean_ndvi, std_ndvi, anomalies, output_dir)
        except Exception as e:
            print(f"\n  Nota: No se pudo generar gráfico ({e})")

    return results


def generate_plot(volcan_name, results, mean_ndvi, std_ndvi, anomalies, output_dir):
    """Genera gráfico de serie temporal NDVI."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    fechas = [datetime.strptime(r['fecha'], '%Y-%m-%d') for r in results]
    ndvi_vals = [r['ndvi_mean'] for r in results]

    fig, ax = plt.subplots(figsize=(14, 6))

    # Banda de ±2σ
    ax.axhspan(mean_ndvi - 2*std_ndvi, mean_ndvi + 2*std_ndvi,
               alpha=0.15, color='green', label=f'±2σ ({mean_ndvi:.3f} ± {2*std_ndvi:.3f})')
    ax.axhline(y=mean_ndvi, color='green', linestyle='--', alpha=0.5, linewidth=1)

    # Serie temporal
    ax.plot(fechas, ndvi_vals, 'o-', color='#2E86C1', markersize=4, linewidth=1.5, label='NDVI medio')

    # Anomalías
    for a in anomalies:
        fecha = datetime.strptime(a['fecha'], '%Y-%m-%d')
        color = 'red' if a['tipo'] == 'BROWNING' else 'orange'
        marker = 'v' if a['tipo'] == 'BROWNING' else '^'
        ax.plot(fecha, a['ndvi'], marker, color=color, markersize=12, zorder=5,
                label=a['tipo'] if a['tipo'] not in [x.get_label() for x in ax.get_children()] else '')

    ax.set_title(f'VegStress-v1 — Serie Temporal NDVI: {volcan_name}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('NDVI (media del área)')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.1, 0.8)

    plt.tight_layout()
    plot_path = output_dir / f"{volcan_name.replace(' ', '_')}_NDVI_timeseries.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"\n  Gráfico guardado: {plot_path}")


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VegStress-v1 — Análisis NDVI volcánico')
    parser.add_argument('--volcan', default='Laguna del Maule', help='Nombre del volcán')
    parser.add_argument('--meses', type=int, default=12, help='Meses hacia atrás')
    parser.add_argument('--no-images', action='store_true', help='No descargar imágenes NDVI')
    args = parser.parse_args()

    results = analyze_volcano(args.volcan, args.meses, save_images=not args.no_images)
