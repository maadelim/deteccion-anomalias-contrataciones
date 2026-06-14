# src/preprocessing.py
"""
Módulo de limpieza de datos y feature engineering.
"""

import logging

import pandas as pd

from .config import (
    CAPPING_MAX_PCT,
    CAPPING_MIN_PCT,
    COL_FECHA_BP,
    COL_FECHA_CONV,
    COL_MONTO_ADJ,
    COL_MONTO_REF,
    COLUMNAS_CRITICAS,
)

logger = logging.getLogger(__name__)


def limpiar_y_preparar(df_total: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Limpia el dataset y genera las variables de comportamiento para clustering.

    Pasos:
    1. Elimina registros con nulos en columnas críticas.
    2. Separa registros con monto referencial = 0 (posibles errores de registro).
    3. Crea variables de diferencia de monto (absoluta, porcentual y capeada).
    4. Calcula días de proceso entre convocatoria y buena pro.
    5. Descarta registros con días de proceso negativos (errores de fecha).

    Parameters
    ----------
    df_total : pd.DataFrame
        Dataset crudo de adjudicaciones.

    Returns
    -------
    df_model : pd.DataFrame
        Dataset limpio con variables nuevas, listo para clustering.
    df_monto_cero : pd.DataFrame
        Registros separados con monto referencial = 0.
    """
    n_inicial = len(df_total)
    logger.info("Registros iniciales: %d", n_inicial)

    # 1. Eliminar nulos en columnas críticas
    df_clean = df_total.dropna(subset=COLUMNAS_CRITICAS).copy()
    n_tras_dropna = len(df_clean)
    logger.info(
        "Registros tras eliminar nulos: %d (eliminados: %d)",
        n_tras_dropna,
        n_inicial - n_tras_dropna,
    )

    # 2. Separar casos con monto referencial = 0
    mask_cero = df_clean[COL_MONTO_REF] == 0
    df_monto_cero = df_clean[mask_cero].copy()
    df_model = df_clean[~mask_cero].copy()
    logger.info(
        "Registros con monto referencial = 0 separados: %d", len(df_monto_cero)
    )

    # 3. Feature engineering: diferencias de monto
    df_model["diferencia_monto"] = (
        df_model[COL_MONTO_ADJ] - df_model[COL_MONTO_REF]
    )
    df_model["diferencia_pct"] = (
        df_model["diferencia_monto"] / df_model[COL_MONTO_REF]
    ) * 100

    # Capping entre CAPPING_MIN_PCT% y CAPPING_MAX_PCT%
    # Justificación: el 0.02% de registros con montos referenciales casi nulos
    # generan porcentajes del orden de 10^10%, distorsionando el clustering.
    # El rango [-100%, 500%] cubre desde "se pagó nada" hasta "se pagó 6x lo presupuestado",
    # capturando los sobrecostos extremos sin que los outliers colapsen la escala.
    df_model["diferencia_pct_cap"] = df_model["diferencia_pct"].clip(
        lower=CAPPING_MIN_PCT, upper=CAPPING_MAX_PCT
    )
    n_capeados = (
        (df_model["diferencia_pct"] < CAPPING_MIN_PCT)
        | (df_model["diferencia_pct"] > CAPPING_MAX_PCT)
    ).sum()
    logger.info(
        "Registros con diferencia_pct fuera del rango [%.0f%%, %.0f%%]: %d (%.2f%%)",
        CAPPING_MIN_PCT,
        CAPPING_MAX_PCT,
        n_capeados,
        100 * n_capeados / len(df_model),
    )

    # 4. Calcular días de proceso
    df_model[COL_FECHA_CONV] = pd.to_datetime(
        df_model[COL_FECHA_CONV], dayfirst=True, errors="coerce"
    )
    df_model[COL_FECHA_BP] = pd.to_datetime(
        df_model[COL_FECHA_BP], dayfirst=True, errors="coerce"
    )
    df_model["dias_proceso"] = (
        df_model[COL_FECHA_BP] - df_model[COL_FECHA_CONV]
    ).dt.days

    # 5. Descartar registros con fechas inválidas o días negativos
    n_antes_fecha = len(df_model)
    df_model = df_model[df_model["dias_proceso"] >= 0].copy()
    n_fechas_invalidas = n_antes_fecha - len(df_model)
    if n_fechas_invalidas > 0:
        logger.warning(
            "Registros eliminados por dias_proceso negativos o nulos: %d",
            n_fechas_invalidas,
        )

    logger.info("Dataset final para clustering: %d registros.", len(df_model))
    return df_model, df_monto_cero