"""
aoi_geometry.py — Geometría pura de máscaras AOI (sin I/O).

Define cómo un AOI (zona de interés) se convierte en una máscara booleana sobre el
array NDVI, dado el bbox y el shape de la escena. Soporta dos geometrías:

  - CÍRCULO  : {lat, lon, radio_m}  → elipse en espacio-pixel (compat. histórica).
  - LÍNEA    : {waypoints: [[lat,lon], ...], buffer_m} → banda alrededor de una
               polilínea. Representa una QUEBRADA: el CO2 difuso se concentra a
               ≤30 m de la estructura (Guinn et al. 2024, PD-001, L1012/1616), así
               que una AOI estrecha que sigue el drenaje evita diluir la señal en
               roca pelada (a diferencia de un círculo grande sobre la caldera).

Funciones puras y testeables (ver tests/test_aoi_geometry.py). El motor de
detección (change_detector.aoi_mask) delega aquí para no duplicar geometría.
"""
from __future__ import annotations
import math
import numpy as np


def lonlat_to_px(lon: float, lat: float, bbox, shape) -> tuple[float, float]:
    """Convierte (lon, lat) a coordenadas pixel (cx, cy) sub-pixel.

    bbox = (lon_w, lat_s, lon_e, lat_n); origen pixel (0,0) en la esquina NO.
    """
    lon_w, lat_s, lon_e, lat_n = bbox
    H, W = shape
    cx = (lon - lon_w) / (lon_e - lon_w) * W
    cy = (lat_n - lat) / (lat_n - lat_s) * H
    return cx, cy


def meters_to_px_xy(metros: float, bbox, shape, lat: float) -> tuple[float, float]:
    """Convierte una distancia en metros a radios pixel (rx, ry).

    Usa la misma aproximación que la fórmula histórica de change_detector:
    111 km/° de latitud, y 111 km·cos(lat)/° de longitud.
    """
    lon_w, lat_s, lon_e, lat_n = bbox
    H, W = shape
    km_per_px_x = (lon_e - lon_w) * 111.0 * abs(math.cos(math.radians(lat))) / W
    km_per_px_y = (lat_n - lat_s) * 111.0 / H
    rx = (metros / 1000.0) / km_per_px_x
    ry = (metros / 1000.0) / km_per_px_y
    return rx, ry


def circle_mask(lat: float, lon: float, radio_m: float, bbox, shape) -> np.ndarray:
    """Máscara elíptica (círculo en metros, elipse en píxeles por la proyección).

    Idéntica a la fórmula original de change_detector.aoi_mask (ver test de paridad).
    """
    H, W = shape
    cx, cy = lonlat_to_px(lon, lat, bbox, shape)
    r_px_x, r_px_y = meters_to_px_xy(radio_m, bbox, shape, lat)
    Y, X = np.ogrid[:H, :W]
    return ((X - cx) / r_px_x) ** 2 + ((Y - cy) / r_px_y) ** 2 <= 1.0


def polyline_mask(waypoints_px, buffer_px: float, shape) -> np.ndarray:
    """Máscara de banda de ancho `buffer_px` alrededor de una polilínea.

    Args:
        waypoints_px: lista de (x, y) en píxeles (orden = recorrido de la línea).
        buffer_px: radio de la banda en píxeles (0 = solo la línea rasterizada).
        shape: (H, W) de la escena.

    Implementación: rasteriza los segmentos (Bresenham), luego umbraliza la
    transformada de distancia euclídea. Robusto a codos y a líneas oblicuas.
    """
    from skimage.draw import line as sk_line
    from scipy.ndimage import distance_transform_edt

    H, W = shape
    base = np.zeros((H, W), dtype=bool)
    wp = list(waypoints_px)
    if len(wp) == 1:
        x, y = wp[0]
        xi, yi = int(round(x)), int(round(y))
        if 0 <= yi < H and 0 <= xi < W:
            base[yi, xi] = True
    for (x0, y0), (x1, y1) in zip(wp[:-1], wp[1:]):
        rr, cc = sk_line(int(round(y0)), int(round(x0)),
                         int(round(y1)), int(round(x1)))
        ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
        base[rr[ok], cc[ok]] = True

    if buffer_px <= 0:
        return base
    if not base.any():
        return base
    dist = distance_transform_edt(~base)
    return dist <= buffer_px


def aoi_to_mask(aoi: dict, bbox, shape) -> tuple[np.ndarray, dict]:
    """Dispatcher: devuelve (máscara, info) según la geometría del AOI.

    - Si el AOI trae 'waypoints' → geometría LÍNEA (quebrada): polilínea + buffer.
      buffer_m por defecto 30 m (Guinn 2024). El buffer pixel usa el radio-y
      (latitud) como referencia isotrópica conservadora.
    - Si no → geometría CÍRCULO con {lat, lon, radio_m}.

    info incluye geometria y, para línea, el centro (px) para etiquetar mapas.
    """
    wps = aoi.get('waypoints')
    if wps:
        # convertir [lat, lon] → (x, y) px
        wp_px = [lonlat_to_px(lon, lat, bbox, shape) for (lat, lon) in wps]
        buffer_m = aoi.get('buffer_m', 30)
        # latitud media para el factor metros→px
        lat_med = sum(p[0] for p in wps) / len(wps)
        _, ry = meters_to_px_xy(buffer_m, bbox, shape, lat_med)
        rx, _ = meters_to_px_xy(buffer_m, bbox, shape, lat_med)
        buffer_px = max(rx, ry)  # banda al menos tan ancha como el buffer real
        mask = polyline_mask(wp_px, buffer_px, shape)
        cx = sum(p[0] for p in wp_px) / len(wp_px)
        cy = sum(p[1] for p in wp_px) / len(wp_px)
        return mask, {'geometria': 'linea', 'center_px': (cx, cy),
                      'buffer_px': buffer_px, 'wp_px': wp_px}

    mask = circle_mask(aoi['lat'], aoi['lon'], aoi['radio_m'], bbox, shape)
    cx, cy = lonlat_to_px(aoi['lon'], aoi['lat'], bbox, shape)
    return mask, {'geometria': 'circulo', 'center_px': (cx, cy)}
