# src/data_loader.py
"""
Módulo de carga de datos.
Carga y unifica los archivos anuales de adjudicaciones del OSCE/OECE.
"""

import logging
import os

import pandas as pd

from .config import ARCHIVOS_ADJUDICACIONES, RUTA_DATOS_RAW

logger = logging.getLogger(__name__)


def cargar_adjudicaciones(ruta_datos: str = RUTA_DATOS_RAW) -> pd.DataFrame:
    """
    Carga y concatena los archivos Excel anuales de adjudicaciones.

    Parameters
    ----------
    ruta_datos : str
        Ruta a la carpeta que contiene los archivos Excel.

    Returns
    -------
    pd.DataFrame
        DataFrame unificado con todos los registros anuales.

    Raises
    ------
    FileNotFoundError
        Si ningún archivo de datos está disponible en la ruta indicada.
    """
    dfs = []

    for año, nombre_archivo in ARCHIVOS_ADJUDICACIONES.items():
        ruta_archivo = os.path.join(ruta_datos, nombre_archivo)

        if not os.path.exists(ruta_archivo):
            logger.warning("Archivo no encontrado, se omite: %s", ruta_archivo)
            continue

        logger.info("Cargando datos %d desde: %s", año, ruta_archivo)
        df = pd.read_excel(ruta_archivo)
        df["anio_fuente"] = año  # columna auxiliar para trazabilidad
        dfs.append(df)

    if not dfs:
        raise FileNotFoundError(
            f"No se encontró ningún archivo de adjudicaciones en '{ruta_datos}'. "
            "Consulta la sección 'Fuente de datos' del README."
        )

    df_total = pd.concat(dfs, ignore_index=True)
    logger.info(
        "Dataset unificado: %d registros, %d columnas.", *df_total.shape
    )
    return df_total