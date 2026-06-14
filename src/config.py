# src/config.py
"""
Constantes de configuración del proyecto.
Centraliza nombres de columnas y parámetros para evitar strings dispersos.
"""

# --- Rutas por defecto ---
RUTA_DATOS_RAW = "../data/raw/"
RUTA_RESULTADOS = "../results/"

# --- Archivos de datos por año ---
ARCHIVOS_ADJUDICACIONES = {
    2022: "CONOSCE_ADJUDICACIONES2022_0.xlsx",
    2023: "CONOSCE_ADJUDICACIONES2023_0.xlsx",
    2024: "CONOSCE_ADJUDICACIONES2024_0.xlsx",
    2025: "CONOSCE_ADJUDICACIONES2025_0.xlsx",
}

# --- Columnas críticas ---
COLUMNAS_CRITICAS = [
    "cantidad_adjudicado_item",
    "monto_referencial_item_soles",
    "monto_adjudicado_item_soles",
    "tipo_proveedor",
    "fecha_buenapro",
]

COL_MONTO_REF = "monto_referencial_item_soles"
COL_MONTO_ADJ = "monto_adjudicado_item_soles"
COL_FECHA_CONV = "fecha_convocatoria"
COL_FECHA_BP = "fecha_buenapro"
COL_RUC = "ruc_proveedor"
COL_CODIGO_CONV = "codigoconvocatoria"

# --- Parámetros de feature engineering ---
CAPPING_MIN_PCT = -100.0   # Límite inferior para diferencia_pct_cap
CAPPING_MAX_PCT = 500.0    # Límite superior. Cubre sobrecostos de hasta 5x el presupuesto

# --- Parámetros de clustering ---
KMEANS_N_CLUSTERS = 4
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 10

DBSCAN_EPS = 0.5
DBSCAN_MIN_SAMPLES = 10
DBSCAN_SAMPLE_SIZE = 10_000
DBSCAN_RANDOM_STATE = 42

# --- Variables para el modelo de comportamiento ---
FEATURES_COMPORTAMIENTO = ["diferencia_pct_cap", "dias_proceso"]