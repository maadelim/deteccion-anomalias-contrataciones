import pandas as pd
import numpy as np


def limpiar_y_preparar(df_total):
    """
    Limpia el dataset y crea las variables (features) necesarias
    para el análisis de clustering.

    Parámetros:
        df_total (DataFrame): dataset crudo de adjudicaciones

    Retorna:
        df_model (DataFrame): dataset limpio con variables nuevas,
                               sin los casos de monto_referencial = 0
    """
    # Eliminar filas con nulos en columnas críticas
    df_clean = df_total.dropna(subset=[
        'cantidad_adjudicado_item',
        'monto_referencial_item_soles',
        'monto_adjudicado_item_soles',
        'tipo_proveedor',
        'fecha_buenapro'
    ])

    # Separar casos con monto referencial = 0
    df_model = df_clean[df_clean['monto_referencial_item_soles'] != 0].copy()

    # Crear variables de diferencia
    df_model['diferencia_monto'] = (
        df_model['monto_adjudicado_item_soles'] - df_model['monto_referencial_item_soles']
    )
    df_model['diferencia_pct'] = (
        df_model['diferencia_monto'] / df_model['monto_referencial_item_soles']
    ) * 100

    # Capear diferencia_pct entre -100% y 500%
    df_model['diferencia_pct_cap'] = df_model['diferencia_pct'].clip(lower=-100, upper=500)

    # Convertir fechas y calcular días de proceso
    df_model['fecha_convocatoria'] = pd.to_datetime(df_model['fecha_convocatoria'], dayfirst=True)
    df_model['fecha_buenapro'] = pd.to_datetime(df_model['fecha_buenapro'], dayfirst=True)
    df_model['dias_proceso'] = (
        df_model['fecha_buenapro'] - df_model['fecha_convocatoria']
    ).dt.days

    return df_model