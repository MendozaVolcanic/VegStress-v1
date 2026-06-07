"""
Tests de vegstress_signal.py — casos sintéticos con respuesta conocida.
Validan la lógica de señal basada en Guinn 2024 (PD-001) y Biass 2022 (PD-002).

Correr:  python -m pytest tests/ -v    (o)    python tests/test_vegstress_signal.py
"""
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from vegstress_signal import (
    classify_change, pct_matching_sign,
    second_derivative_events, regress_out_climate,
)


# ── classify_change: el signo identifica el mecanismo (Guinn 2024) ──
# CONVENIO (corregido 2026-06-07): ΔNDVI = NDVI_b - NDVI_a (posterior - base).
#   ΔNDVI > 0  → NDVI SUBE → GREENING (ganancia de vigor; CO2/fertilización o lluvia)
#   ΔNDVI < 0  → NDVI BAJA → BROWNING (pérdida de vigor; tefra/SO2/ácido o sequía)
# Coherente con el path z-score (ndvi_analyzer / dashboard: z<0 = BROWNING).

def test_greening_en_zona_co2_es_alta_relevancia():
    # CO2 difuso → greening (NDVI sube, delta POSITIVO) en zona que espera greening
    r = classify_change(delta_mean=0.18, tipo_esperado="GREENING", umbral=0.10)
    assert r["tipo"] == "GREENING"
    assert r["coincide_esperado"] is True
    assert r["relevancia_volcanica"] == "ALTA"


def test_browning_en_zona_tefra_es_alta_relevancia():
    # Tefra/ácido → browning (NDVI baja, delta NEGATIVO) en zona que espera browning
    r = classify_change(delta_mean=-0.20, tipo_esperado="BROWNING", umbral=0.10)
    assert r["tipo"] == "BROWNING"
    assert r["coincide_esperado"] is True
    assert r["relevancia_volcanica"] == "ALTA"


def test_signo_inesperado_es_media_relevancia():
    # Browning (delta negativo) donde se esperaba greening → signo contrario → revisar
    r = classify_change(delta_mean=-0.20, tipo_esperado="GREENING", umbral=0.10)
    assert r["tipo"] == "BROWNING"
    assert r["coincide_esperado"] is False
    assert r["relevancia_volcanica"] == "MEDIA"


def test_sin_cambio_es_baja_relevancia():
    r = classify_change(delta_mean=0.03, tipo_esperado="GREENING", umbral=0.10)
    assert r["tipo"] == "NINGUNO"
    assert r["relevancia_volcanica"] == "BAJA"


def test_senescencia_otonal_es_browning():
    # Caso real LdM: NDVI baja de verano a otoño (Δ negativo) → DEBE ser BROWNING
    # (antes el bug lo marcaba GREENING). Es la prueba de regresión del bug de signo.
    r = classify_change(delta_mean=-0.25, tipo_esperado="GREENING", umbral=0.10)
    assert r["tipo"] == "BROWNING"


# ── pct_matching_sign: señal localizada (Guinn: gas en 30 m de la fuente) ──

def test_pct_matching_greening():
    # 60% de los píxeles tienen greening fuerte (NDVI sube → delta POSITIVO), 40% sin cambio
    arr = np.array([0.2, 0.2, 0.2, 0.0, 0.0], dtype=float)
    pct = pct_matching_sign(arr, "GREENING", umbral=0.10)
    assert abs(pct - 60.0) < 1e-6


def test_pct_matching_browning():
    # browning = NDVI baja = delta NEGATIVO
    arr = np.array([-0.2, -0.2, 0.0, 0.0], dtype=float)  # 2 de 4 browning
    pct = pct_matching_sign(arr, "BROWNING", umbral=0.10)
    assert abs(pct - 50.0) < 1e-6


def test_pct_matching_ignora_nan():
    arr = np.array([0.2, np.nan, 0.2, 0.0], dtype=float)  # 3 válidos, 2 greening
    pct = pct_matching_sign(arr, "GREENING", umbral=0.10)
    assert abs(pct - (2 / 3 * 100)) < 1e-6


def test_pct_matching_ninguno_es_cero():
    arr = np.array([-0.2, 0.2], dtype=float)
    assert pct_matching_sign(arr, "NINGUNO", umbral=0.10) == 0.0


# ── second_derivative_events: timing de recarga (Guinn 2024) ──

def test_2da_derivada_insuficientes_fechas():
    r = second_derivative_events(["2020-01-01", "2020-02-01"], [0.5, 0.6])
    assert r["ok"] is False
    assert "insuficiente" in r["motivo"]


def test_2da_derivada_detecta_spike():
    # Serie con un quiebre brusco en el medio (un pico de aceleración)
    dates = [f"2020-{m:02d}-01" for m in range(1, 8)]
    values = [0.50, 0.51, 0.52, 0.75, 0.53, 0.54, 0.55]  # salto en índice 3
    r = second_derivative_events(dates, values, spike_sigma=1.2)
    assert r["ok"] is True
    assert len(r["spike_idx"]) >= 1
    # El salto está alrededor del índice 3
    assert any(i in (2, 3, 4) for i in r["spike_idx"])


def test_2da_derivada_serie_lineal_sin_spikes():
    # Serie perfectamente lineal → 2ª derivada ~0 → sin spikes
    dates = [f"2020-{m:02d}-01" for m in range(1, 8)]
    values = [0.50 + 0.02 * i for i in range(7)]
    r = second_derivative_events(dates, values, spike_sigma=1.5)
    assert r["ok"] is True
    assert len(r["spike_idx"]) == 0


# ── regress_out_climate: control de confusor (Guinn: r²>0.1) ──

def test_regresion_remueve_clima_correlacionado():
    # NDVI = 0.5 + 0.3*clima (correlación perfecta) → r²=1 → debe remover
    clima = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ndvi = 0.5 + 0.3 * clima
    r = regress_out_climate(ndvi, clima, r2_threshold=0.1)
    assert r["removed"] is True
    assert r["r2"] > 0.9
    # El residual debe ser casi plano (varianza removida)
    assert np.nanstd(r["residual"]) < 1e-6


def test_regresion_no_remueve_si_no_correlaciona():
    # NDVI y clima independientes → r² bajo → no remover
    clima = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ndvi  = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])  # constante, r²~0
    r = regress_out_climate(ndvi, clima, r2_threshold=0.1)
    assert r["removed"] is False


if __name__ == "__main__":
    # Runner mínimo sin pytest
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
