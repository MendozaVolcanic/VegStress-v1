"""
Tests del cableado del control climático (climate_control) al detector de cambios
(change_detector.analyze_timeseries). Casos sintéticos de respuesta conocida, SIN red.

Estrategia de aislamiento de red:
  - change_detector.analyze_timeseries usa una referencia de módulo a build_climate_series.
    Los tests la monkeypatchean por una función pura que devuelve una serie climática fija.
  - regress_out_climate (en vegstress_signal) ya es pura y testeada; aquí se valida el
    cableado: que la serie corregida y los campos r2_clima / clima_removido se generen y
    persistan bien, y que un fallo de red caiga a la serie cruda sin romper el pipeline.

Correr:  python -m pytest tests/ -q
"""
import sys
import json
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import change_detector as cd


# ── Fixtures sintéticos ──────────────────────────────────────────────

FECHAS = ["2025-01-01", "2025-02-01", "2025-03-01", "2025-04-01", "2025-05-01"]


def _make_volcan(tmp_path, monkeypatch, ndvi_por_fecha, bbox=(0.0, 0.0, 1.0, 1.0)):
    """
    Construye un volcán sintético en disco con un AOy círculo que cubre todo el bbox,
    y arrays .npy cuyos píxeles de vegetación (NDVI>=0.4) tienen el valor medio deseado
    por fecha. Devuelve (volcan_name, aoi_def).

    ndvi_por_fecha: dict {fecha: valor_ndvi_medio}.
    """
    datos = tmp_path / "datos"
    vname = "TestVolcan"
    vdir = datos / vname.replace(" ", "_")
    vdir.mkdir(parents=True)

    # array 40x40 enteramente vegetación con el valor pedido (uniforme → media exacta)
    for f, val in ndvi_por_fecha.items():
        arr = np.full((40, 40), float(val), dtype=float)
        np.save(vdir / f"ndvi_raw_{f}.npy", arr)
        with open(vdir / f"ndvi_meta_{f}.json", "w") as fh:
            json.dump({"bbox": list(bbox)}, fh)

    aoi = {
        "id": "aoi_test",
        "nombre": "AOI Test",
        "lat": 0.5, "lon": 0.5, "radio_m": 200000,  # cubre todo el bbox de 1°
        "activo": True, "tipo_esperado": "GREENING",
        "descripcion": "zona sintética de prueba",
    }

    # Redirigir las rutas de datos del módulo al tmp_path
    monkeypatch.setattr(cd, "DATOS", datos)
    monkeypatch.setattr(cd, "DOCS", tmp_path / "docs")
    monkeypatch.setattr(cd, "load_config", lambda: {
        "volcanes": {vname: {"aois": [aoi]}},
        "umbrales_globales": {"ndvi_min_valido": 0.4},
    })
    return vname, aoi


# ── 1. Centro lat/lon del AOI (círculo y línea) ─────────────────────

def test_centro_aoi_circulo():
    aoi = {"lat": -36.0, "lon": -70.5}
    lat, lon = cd.aoi_center_latlon(aoi)
    assert lat == -36.0 and lon == -70.5


def test_centro_aoi_linea_promedia_waypoints():
    aoi = {"waypoints": [[-36.0, -70.0], [-36.2, -70.4]]}
    lat, lon = cd.aoi_center_latlon(aoi)
    assert lat == pytest.approx(-36.1)
    assert lon == pytest.approx(-70.2)


# ── 2. Clima correlaciona fuerte → se remueve y la serie se aplana ──

def test_clima_correlacionado_se_remueve_y_aplana(tmp_path, monkeypatch):
    # NDVI = 0.5 + 0.001*precip (correlación perfecta con precip) → r²≈1 > 0.1
    precip = {"2025-01-01": 0.0, "2025-02-01": 50.0, "2025-03-01": 100.0,
              "2025-04-01": 150.0, "2025-05-01": 200.0}
    ndvi = {f: 0.5 + 0.001 * p for f, p in precip.items()}
    vname, aoi = _make_volcan(tmp_path, monkeypatch, ndvi)

    def fake_clima(lat, lon, fechas):
        return {f: {"precip_antecedente": precip[f], "temp_media": 10.0} for f in fechas}
    monkeypatch.setattr(cd, "build_climate_series", fake_clima)

    out = cd.analyze_timeseries(vname, [aoi], clima=True)
    r = out[aoi["id"]]

    assert r["clima_removido"] is True
    assert r["r2_clima"] > 0.1
    # La serie corregida debe ser MÁS PLANA que la cruda (menor std).
    std_cruda = np.std(r["ndvi_serie"])
    std_corr  = np.std(r["ndvi_serie_corregida"])
    assert std_corr < std_cruda
    # campos de 2ª derivada corregida presentes
    assert "d2_corregida" in r
    assert "spike_fechas_corregidas" in r


# ── 3. Clima NO correlaciona → serie corregida ~ cruda, no se remueve ──

def test_clima_no_correlacionado_no_remueve(tmp_path, monkeypatch):
    # NDVI con variación propia, precip constante → r²≈0 < 0.1
    ndvi = {"2025-01-01": 0.50, "2025-02-01": 0.60, "2025-03-01": 0.52,
            "2025-04-01": 0.65, "2025-05-01": 0.55}
    vname, aoi = _make_volcan(tmp_path, monkeypatch, ndvi)

    def fake_clima(lat, lon, fechas):
        return {f: {"precip_antecedente": 100.0, "temp_media": 10.0} for f in fechas}
    monkeypatch.setattr(cd, "build_climate_series", fake_clima)

    out = cd.analyze_timeseries(vname, [aoi], clima=True)
    r = out[aoi["id"]]

    assert r["clima_removido"] is False
    assert r["r2_clima"] <= 0.1
    # serie corregida idéntica (o casi) a la cruda
    assert r["ndvi_serie_corregida"] == r["ndvi_serie"]


# ── 4. Fallo de red en build_climate_series → cae a serie cruda, no rompe ──

def test_fallo_red_cae_a_serie_cruda(tmp_path, monkeypatch):
    ndvi = {"2025-01-01": 0.50, "2025-02-01": 0.55, "2025-03-01": 0.52,
            "2025-04-01": 0.58, "2025-05-01": 0.54}
    vname, aoi = _make_volcan(tmp_path, monkeypatch, ndvi)

    def boom(lat, lon, fechas):
        raise ConnectionError("Open-Meteo no responde")
    monkeypatch.setattr(cd, "build_climate_series", boom)

    out = cd.analyze_timeseries(vname, [aoi], clima=True)  # NO debe lanzar
    r = out[aoi["id"]]

    assert r["clima_removido"] is False
    assert r["r2_clima"] is None
    assert r["ndvi_serie_corregida"] == r["ndvi_serie"]


# ── 5. clima=False → no se intenta clima en absoluto ─────────────────

def test_sin_clima_no_llama_openmeteo(tmp_path, monkeypatch):
    ndvi = {"2025-01-01": 0.50, "2025-02-01": 0.55, "2025-03-01": 0.52,
            "2025-04-01": 0.58, "2025-05-01": 0.54}
    vname, aoi = _make_volcan(tmp_path, monkeypatch, ndvi)

    def boom(lat, lon, fechas):
        raise AssertionError("no debió llamarse build_climate_series con clima=False")
    monkeypatch.setattr(cd, "build_climate_series", boom)

    out = cd.analyze_timeseries(vname, [aoi], clima=False)
    r = out[aoi["id"]]
    assert r["clima_removido"] is False
    assert r["r2_clima"] is None
    assert r["ndvi_serie_corregida"] == r["ndvi_serie"]


# ── 6. La alerta anota el confusor climático cuando r²>0.1 ───────────

def test_alerta_anota_confusor_climatico(tmp_path, monkeypatch):
    # Serie con r2_clima alto persistida en el JSON de timeseries; el AOI debe gatillar
    # alerta (delta grande). Verificamos que el markdown incluya la nota de confusor.
    datos = tmp_path / "datos"
    docs = tmp_path / "docs"
    vname = "TestVolcan"
    vdir = datos / vname
    vdir.mkdir(parents=True)
    monkeypatch.setattr(cd, "DATOS", datos)
    monkeypatch.setattr(cd, "DOCS", docs)
    monkeypatch.setattr(cd, "ROOT", tmp_path)
    monkeypatch.setattr(cd, "load_config", lambda: {"umbrales_globales": {}})

    # timeseries con r2_clima alto para el AOI
    with open(vdir / "timeseries_2da_deriv.json", "w", encoding="utf-8") as fh:
        json.dump({"aoi_test": {"nombre": "AOI Test", "r2_clima": 0.42,
                                "clima_removido": True}}, fh)

    aoi_results = [{
        "id": "aoi_test", "nombre": "AOI Test", "delta_mean": 0.30,
        "delta_std": 0.05, "valid_pct": 90.0, "tipo": "GREENING",
        "nivel": "CRITICAL", "ndvi_a": 0.40, "ndvi_b": 0.70,
        "descripcion": "zona", "tipo_esperado": "GREENING",
        "coincide_esperado": True, "relevancia_volcanica": "ALTA",
        "pct_coincide_esperado": 80.0,
    }]

    delta_result = {"delta_mean": 0.30, "delta_std": 0.05, "valid_pct": 90.0,
                    "greening_pct": 50.0, "browning_pct": 0.0}

    alert = cd.generate_alerts(vname, "2025-01-01", "2025-05-01",
                               delta_result, aoi_results, {})
    assert alert is not None
    md_text = (docs / "alertas").glob("*.md")
    contenido = next(md_text).read_text(encoding="utf-8")
    assert "confusor climático" in contenido
    assert "0.42" in contenido
