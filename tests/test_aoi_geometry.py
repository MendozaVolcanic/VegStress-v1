"""
Tests de aoi_geometry.py — geometría pura de máscaras AOI (círculo y polilínea+buffer).

Motivación (2026-06-07): las quebradas de desgasificación de Laguna del Maule son
features LINEALES; el motor solo soportaba círculos. Estos tests fijan el contrato de
la máscara de polilínea+buffer (buffer físico = 30 m, Guinn 2024 PD-001) y verifican
que la máscara circular sigue siendo idéntica a la fórmula previa de change_detector.

Correr:  python -m pytest tests/test_aoi_geometry.py -v
         python tests/test_aoi_geometry.py
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from aoi_geometry import (
    lonlat_to_px, meters_to_px_xy, circle_mask, polyline_mask, aoi_to_mask,
)

# bbox de prueba (lon_w, lat_s, lon_e, lat_n) y shape cuadrada
BBOX = (-70.6, -36.15, -70.4, -35.95)   # 0.2° lon × 0.2° lat
SHAPE = (200, 200)


# ── lonlat_to_px: esquinas y centro ──────────────────────────────────

def test_lonlat_to_px_esquina_noroeste():
    # lon_w, lat_n → pixel (0,0)
    cx, cy = lonlat_to_px(BBOX[0], BBOX[3], BBOX, SHAPE)
    assert abs(cx - 0.0) < 1e-6
    assert abs(cy - 0.0) < 1e-6


def test_lonlat_to_px_centro():
    lon_c = (BBOX[0] + BBOX[2]) / 2
    lat_c = (BBOX[1] + BBOX[3]) / 2
    cx, cy = lonlat_to_px(lon_c, lat_c, BBOX, SHAPE)
    assert abs(cx - 100.0) < 1e-6
    assert abs(cy - 100.0) < 1e-6


# ── meters_to_px_xy: 30 m a píxeles ──────────────────────────────────

def test_meters_to_px_positivo():
    rx, ry = meters_to_px_xy(30.0, BBOX, SHAPE, lat=-36.05)
    # 0.2° lat sobre 200 px ≈ 22.2 km / 200 px ≈ 111 m/px → 30 m < 1 px
    assert rx > 0 and ry > 0
    assert ry < 1.0  # 30 m es sub-pixel a esta resolución gruesa


# ── circle_mask: paridad con la fórmula previa de change_detector ─────

def _circle_mask_legacy(lat, lon, radio_m, bbox, shape):
    """Reproduce exactamente aoi_mask() original de change_detector (pre-refactor)."""
    import math
    H, W = shape
    lon_w, lat_s, lon_e, lat_n = bbox
    cx = (lon - lon_w) / (lon_e - lon_w) * W
    cy = (lat_n - lat) / (lat_n - lat_s) * H
    km_per_px_x = (lon_e - lon_w) * 111.0 * abs(math.cos(math.radians(lat))) / W
    km_per_px_y = (lat_n - lat_s) * 111.0 / H
    r_px_x = (radio_m / 1000.0) / km_per_px_x
    r_px_y = (radio_m / 1000.0) / km_per_px_y
    Y, X = np.ogrid[:H, :W]
    return ((X - cx) / r_px_x) ** 2 + ((Y - cy) / r_px_y) ** 2 <= 1.0


def test_circle_mask_identico_a_legacy():
    lat, lon, radio_m = -36.05, -70.5, 800
    nueva = circle_mask(lat, lon, radio_m, BBOX, SHAPE)
    legacy = _circle_mask_legacy(lat, lon, radio_m, BBOX, SHAPE)
    assert nueva.shape == SHAPE
    assert np.array_equal(nueva, legacy)


# ── polyline_mask: máscara de banda alrededor de una línea ────────────

def test_polyline_horizontal_buffer_cero_es_la_linea():
    # Línea horizontal en la fila 50, de col 10 a 40, buffer 0 → solo esos píxeles
    wp = [(10, 50), (40, 50)]  # (x, y)
    m = polyline_mask(wp, buffer_px=0.0, shape=(100, 100))
    assert m[50, 10] and m[50, 40] and m[50, 25]
    assert not m[51, 25]   # buffer 0 no toca filas vecinas
    assert not m[40, 25]


def test_polyline_horizontal_con_buffer_ensancha():
    wp = [(10, 50), (40, 50)]
    m = polyline_mask(wp, buffer_px=2.0, shape=(100, 100))
    # con buffer 2 px, las filas 48..52 deben estar pintadas en el tramo medio
    assert m[48, 25] and m[52, 25]
    assert not m[55, 25]   # más allá del buffer, no


def test_polyline_buffer_es_simetrico_y_acotado():
    wp = [(50, 10), (50, 40)]  # línea vertical
    m = polyline_mask(wp, buffer_px=3.0, shape=(100, 100))
    fila = 25
    cols = np.where(m[fila])[0]
    # centro en x=50, ancho ~ 2*3+1
    assert cols.min() >= 46 and cols.max() <= 54


def test_polyline_dos_segmentos_codo():
    # Codo: (10,10)->(10,50)->(50,50). Ambos brazos presentes.
    wp = [(10, 10), (10, 50), (50, 50)]
    m = polyline_mask(wp, buffer_px=1.0, shape=(80, 80))
    assert m[30, 10]   # brazo vertical
    assert m[50, 30]   # brazo horizontal
    assert not m[10, 50]  # esquina opuesta vacía


# ── aoi_to_mask: dispatcher círculo vs línea ─────────────────────────

def test_aoi_to_mask_circulo():
    aoi = {'lat': -36.05, 'lon': -70.5, 'radio_m': 800}
    m, info = aoi_to_mask(aoi, BBOX, SHAPE)
    assert m.shape == SHAPE and m.any()
    assert info['geometria'] == 'circulo'


def test_aoi_to_mask_linea():
    # quebrada con 3 waypoints [lat, lon] y buffer 30 m
    aoi = {
        'waypoints': [[-36.05, -70.50], [-36.06, -70.49], [-36.07, -70.49]],
        'buffer_m': 60,
    }
    m, info = aoi_to_mask(aoi, BBOX, SHAPE)
    assert m.shape == SHAPE and m.any()
    assert info['geometria'] == 'linea'
    # la máscara de línea debe ser bastante más chica que media escena
    assert m.sum() < SHAPE[0] * SHAPE[1] * 0.2


def test_aoi_to_mask_linea_pasa_por_los_waypoints():
    aoi = {'waypoints': [[-36.00, -70.55], [-36.10, -70.45]], 'buffer_m': 120}
    m, info = aoi_to_mask(aoi, BBOX, SHAPE)
    # cada waypoint debe caer dentro de la máscara
    for lat, lon in aoi['waypoints']:
        cx, cy = lonlat_to_px(lon, lat, BBOX, SHAPE)
        assert m[int(round(cy)), int(round(cx))]


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for fn in fns:
        try:
            fn(); passed += 1; print(f"  PASS  {fn.__name__}")
        except Exception:
            failed += 1; print(f"  FAIL  {fn.__name__}"); traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
