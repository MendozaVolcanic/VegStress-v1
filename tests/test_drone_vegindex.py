"""
Tests de drone_vegindex.py — pipeline de índices de vegetación sobre ortomosaicos de dron.

Usa un GeoTIFF SINTÉTICO georreferenciado (UTM 19S, la zona de Laguna del Maule) con un
parche de "vegetación" conocido, para validar sin datos reales de dron:
  - cálculo de índices (NDVI con NIR; VARI con solo RGB),
  - reproyección de un punto lat/lon al CRS del raster y extracción de la ventana,
  - estadística sobre el parche.

Correr: python -m pytest tests/test_drone_vegindex.py -v
"""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
rasterio = pytest.importorskip("rasterio")
from rasterio.transform import from_origin
from rasterio.crs import CRS

from drone_vegindex import (
    compute_index, latlon_to_rowcol, analyze_window, load_ortho, INDEX_DEFS,
)


def _make_synthetic(path, with_nir=True):
    """GeoTIFF UTM 19S, 100x100 px @ 0.1 m, con un parche vegetal en el centro."""
    res = 0.1  # 10 cm/px (escala dron)
    # origen UTM aprox de Laguna del Maule (zona 19S). x este, y norte.
    x0, y0 = 320000.0, 6005000.0
    transform = from_origin(x0, y0, res, res)
    H = Wd = 100
    R = np.full((H, Wd), 120, np.float32)
    G = np.full((H, Wd), 110, np.float32)
    B = np.full((H, Wd), 100, np.float32)
    NIR = np.full((H, Wd), 90, np.float32)   # suelo: NIR ~ R (NDVI bajo)
    # parche vegetal 40:60,40:60: G alto, R bajo, NIR muy alto
    R[40:60, 40:60] = 60; G[40:60, 40:60] = 150; B[40:60, 40:60] = 50
    NIR[40:60, 40:60] = 220
    bands = [R, G, B] + ([NIR] if with_nir else [])
    crs = CRS.from_epsg(32719)  # WGS84 / UTM 19S
    with rasterio.open(path, "w", driver="GTiff", height=H, width=Wd,
                       count=len(bands), dtype="float32", crs=crs, transform=transform) as ds:
        for i, b in enumerate(bands, 1):
            ds.write(b, i)
    return transform, crs


def test_ndvi_patch_higher_than_soil(tmp_path):
    p = tmp_path / "ortho_ms.tif"
    _make_synthetic(p, with_nir=True)
    arr, transform, crs = load_ortho(str(p))
    bandmap = {"R": 0, "G": 1, "B": 2, "NIR": 3}
    ndvi = compute_index(arr, bandmap, "ndvi")
    assert ndvi.shape == (100, 100)
    veg = ndvi[40:60, 40:60].mean()
    soil = ndvi[:20, :20].mean()
    assert veg > 0.4 and soil < 0.1 and veg > soil + 0.3


def test_vari_rgb_only(tmp_path):
    p = tmp_path / "ortho_rgb.tif"
    _make_synthetic(p, with_nir=False)
    arr, transform, crs = load_ortho(str(p))
    bandmap = {"R": 0, "G": 1, "B": 2}
    vari = compute_index(arr, bandmap, "vari")
    assert vari[40:60, 40:60].mean() > vari[:20, :20].mean()


def test_index_needs_nir_raises(tmp_path):
    p = tmp_path / "ortho_rgb2.tif"
    _make_synthetic(p, with_nir=False)
    arr, _, _ = load_ortho(str(p))
    with pytest.raises(ValueError):
        compute_index(arr, {"R": 0, "G": 1, "B": 2}, "ndvi")  # sin NIR


def test_latlon_to_rowcol_center(tmp_path):
    p = tmp_path / "o.tif"
    transform, crs = _make_synthetic(p, with_nir=True)
    # centro del raster en UTM -> lat/lon -> debe volver al centro (±1 px)
    from rasterio.warp import transform as warp_transform
    cx_utm = 320000.0 + 50 * 0.1
    cy_utm = 6005000.0 - 50 * 0.1
    lon, lat = warp_transform(crs, CRS.from_epsg(4326), [cx_utm], [cy_utm])
    row, col = latlon_to_rowcol(lat[0], lon[0], transform, crs)
    assert abs(row - 50) <= 1 and abs(col - 50) <= 1


def test_analyze_window_stats(tmp_path):
    p = tmp_path / "o.tif"
    _make_synthetic(p, with_nir=True)
    arr, transform, crs = load_ortho(str(p))
    ndvi = compute_index(arr, {"R": 0, "G": 1, "B": 2, "NIR": 3}, "ndvi")
    st = analyze_window(ndvi, 50, 50, radius_px=12, veg_thr=0.4)
    assert st["n_total"] > 0
    assert st["pct_veg"] > 50          # el parche central es vegetación
    assert st["mean"] > 0.3


def test_index_defs_documented():
    # cada índice declara qué bandas necesita (para fallar claro si faltan)
    for name, d in INDEX_DEFS.items():
        assert "needs" in d and isinstance(d["needs"], (list, tuple))


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    import tempfile
    passed = failed = 0
    for fn in fns:
        try:
            with tempfile.TemporaryDirectory() as d:
                fn(Path(d)) if fn.__code__.co_argcount else fn()
            passed += 1; print(f"  PASS {fn.__name__}")
        except Exception:
            failed += 1; print(f"  FAIL {fn.__name__}"); traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
