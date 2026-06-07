"""
vegstress_signal.py — Lógica de señal de VegStress, basada en evidencia bibliográfica.

Funciones puras (sin I/O) y testeables que implementan los hallazgos fichados:

  - PD-001 Guinn et al. 2024, Mt. Etna (DOI 10.1016/j.rse.2024.114408):
      * El CO2 volcánico difuso produce GREENING (fertilización), no browning.
        El SIGNO del cambio identifica el mecanismo.
      * Detección por 2ª derivada de la serie temporal de NDVI (no ΔNDVI absoluto).
      * El gas difuso se concentra en los primeros ~30 m de la fuente → la señal es
        localizada; promediar sobre un AOI grande la diluye.
      * Control de confusores climáticos: remover por regresión lineal la influencia
        de lluvia/temperatura/humedad cuando r² > 0.1.

  - PD-002 Biass et al. 2022, Cordón Caulle (DOI 10.5194/nhess-22-2829-2022):
      * El daño por tefra/ceniza produce BROWNING (otro mecanismo).
      * Confirma que el signo discrimina: CO2→greening vs tefra/ácido→browning.

Ver docs/bibliografia/BIBLIOGRAPHY_SYNTHESIS.md §1, §6.
"""

from __future__ import annotations
import numpy as np


# ════════════════════════════════════════════════════════════════════
# 1. Clasificación signo-consciente (Guinn 2024: el signo = el mecanismo)
# ════════════════════════════════════════════════════════════════════

def classify_change(delta_mean: float, tipo_esperado: str = "NINGUNO",
                    umbral: float = 0.10) -> dict:
    """
    Clasifica un cambio de NDVI por su SIGNO y lo contrasta con el tipo esperado
    de la zona (Guinn 2024: greening = CO2/fertilización; browning = tefra/ácido).

    Args:
        delta_mean: cambio medio de NDVI (B - A). Positivo = browning, negativo = greening.
        tipo_esperado: "GREENING" | "BROWNING" | "NINGUNO" — mecanismo previsto para la zona.
        umbral: magnitud mínima para considerar el cambio significativo.

    Returns:
        dict con:
          tipo: "GREENING" | "BROWNING" | "NINGUNO"
          coincide_esperado: True si el tipo observado == tipo_esperado (y no NINGUNO)
          relevancia_volcanica: "ALTA" | "MEDIA" | "BAJA"
            ALTA  = el cambio coincide con el mecanismo volcánico esperado de la zona
            MEDIA = cambio significativo pero de signo inesperado (revisar)
            BAJA  = sin cambio significativo
    """
    if delta_mean < -umbral:
        tipo = "GREENING"
    elif delta_mean > umbral:
        tipo = "BROWNING"
    else:
        tipo = "NINGUNO"

    coincide = (tipo != "NINGUNO" and tipo == tipo_esperado)

    if tipo == "NINGUNO":
        relevancia = "BAJA"
    elif coincide:
        relevancia = "ALTA"      # señal en la dirección del mecanismo esperado
    elif tipo_esperado in ("GREENING", "BROWNING"):
        relevancia = "MEDIA"     # hay señal pero del signo contrario al esperado
    else:
        relevancia = "MEDIA"     # zona sin expectativa (NINGUNO) pero hay cambio

    return {
        "tipo": tipo,
        "coincide_esperado": coincide,
        "relevancia_volcanica": relevancia,
    }


def pct_matching_sign(delta_array: np.ndarray, tipo_esperado: str,
                      umbral: float = 0.10) -> float:
    """
    Fracción (%) de píxeles válidos cuyo cambio coincide con el signo esperado.

    Operacionaliza el hallazgo de Guinn 2024 de que el gas difuso se concentra en
    ~30 m de la fuente: en un AOI grande, el promedio diluye la señal localizada, pero
    el % de píxeles con el signo esperado la revela mejor.

    Args:
        delta_array: array de ΔNDVI (puede contener NaN).
        tipo_esperado: "GREENING" | "BROWNING" | "NINGUNO".
        umbral: magnitud mínima por píxel.

    Returns:
        % de píxeles válidos que muestran el cambio del tipo esperado (0 si NINGUNO).
    """
    valid = ~np.isnan(delta_array)
    n = int(valid.sum())
    if n == 0 or tipo_esperado not in ("GREENING", "BROWNING"):
        return 0.0
    vals = delta_array[valid]
    if tipo_esperado == "GREENING":
        match = (vals < -umbral).sum()
    else:  # BROWNING
        match = (vals > umbral).sum()
    return float(match) / n * 100.0


# ════════════════════════════════════════════════════════════════════
# 2. Detección por 2ª derivada de serie temporal (Guinn 2024)
# ════════════════════════════════════════════════════════════════════

def second_derivative_events(dates, values, spike_sigma: float = 1.5) -> dict:
    """
    Calcula la 2ª derivada de una serie temporal de NDVI y marca los "spikes"
    (eventos de aceleración/recarga, sensu Guinn 2024 — detectaron 16 eventos de
    recarga de magma como picos de la 2ª derivada de NDVI).

    A diferencia del ΔNDVI entre 2 fechas, esto captura el *timing* de los ciclos.

    Args:
        dates: lista de fechas "YYYY-MM-DD" ordenadas ascendentemente.
        values: lista/array de NDVI medio por fecha (mismo largo que dates).
        spike_sigma: umbral en desviaciones estándar para marcar un spike.

    Returns:
        dict con:
          ok: bool (False si <4 fechas → insuficiente)
          motivo: str si no ok
          d2: array de 2ª derivada (mismo largo, bordes = NaN)
          spike_idx: índices donde |d2| supera spike_sigma·std
          spike_dates: fechas correspondientes
    """
    n = len(values)
    if n < 4:
        return {"ok": False, "motivo": f"insuficiente ({n} fechas, se necesitan >=4)"}

    v = np.asarray(values, dtype=float)
    # 2ª derivada discreta central: v[i+1] - 2 v[i] + v[i-1]
    d2 = np.full(n, np.nan)
    d2[1:-1] = v[2:] - 2.0 * v[1:-1] + v[:-2]

    interior = d2[1:-1]
    std = np.nanstd(interior)
    if std < 1e-9:
        return {"ok": True, "d2": d2, "spike_idx": [], "spike_dates": [],
                "motivo": "serie plana (std~0)"}

    spike_idx = [i for i in range(1, n - 1)
                 if abs(d2[i]) >= spike_sigma * std]
    return {
        "ok": True,
        "d2": d2,
        "spike_idx": spike_idx,
        "spike_dates": [dates[i] for i in spike_idx],
        "std": float(std),
    }


# ════════════════════════════════════════════════════════════════════
# 3. Control de confusores climáticos (Guinn 2024: regresión si r²>0.1)
# ════════════════════════════════════════════════════════════════════

def regress_out_climate(signal, climate, r2_threshold: float = 0.1) -> dict:
    """
    Remueve la influencia lineal de una variable climática (lluvia/temp/humedad)
    de una serie de NDVI, replicando el control de Guinn 2024: se elimina la
    regresión lineal cuando r² > 0.1, para minimizar el confusor estacional/climático.

    Es una utilidad pura: requiere que el llamador provea la serie climática alineada
    (p.ej. de CR2MET / CAMELS-CL). Si r² <= umbral, devuelve la señal sin cambios.

    Args:
        signal: array de NDVI (serie temporal).
        climate: array de la variable climática, mismo largo.
        r2_threshold: r² mínimo para que valga la pena remover (Guinn usa 0.1).

    Returns:
        dict con:
          r2: coef. de determinación de la regresión señal~clima
          removed: bool (True si se removió)
          residual: array de la señal con el clima removido (o la original si no se removió)
          slope, intercept: parámetros de la regresión
    """
    s = np.asarray(signal, dtype=float)
    c = np.asarray(climate, dtype=float)
    mask = ~(np.isnan(s) | np.isnan(c))
    if mask.sum() < 3:
        return {"r2": 0.0, "removed": False, "residual": s,
                "slope": 0.0, "intercept": 0.0, "motivo": "muy pocos pares válidos"}

    sx, sc = s[mask], c[mask]
    # Regresión lineal señal ~ clima
    slope, intercept = np.polyfit(sc, sx, 1)
    pred = slope * c + intercept
    ss_res = np.nansum((s - pred) ** 2)
    ss_tot = np.nansum((s - np.nanmean(s)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0

    if r2 > r2_threshold:
        residual = s - (slope * c + intercept) + np.nanmean(s)  # recentrar
        return {"r2": float(r2), "removed": True, "residual": residual,
                "slope": float(slope), "intercept": float(intercept)}
    return {"r2": float(r2), "removed": False, "residual": s,
            "slope": float(slope), "intercept": float(intercept)}
