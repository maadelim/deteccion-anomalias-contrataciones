# src/clustering.py
"""
Módulo de clustering.
Implementa K-Means sobre el dataset completo y DBSCAN sobre muestra.
"""

import logging

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from .config import (
    DBSCAN_EPS,
    DBSCAN_MIN_SAMPLES,
    DBSCAN_RANDOM_STATE,
    DBSCAN_SAMPLE_SIZE,
    KMEANS_N_CLUSTERS,
    KMEANS_N_INIT,
    KMEANS_RANDOM_STATE,
)

logger = logging.getLogger(__name__)


def aplicar_kmeans(
    df_model: pd.DataFrame,
    columnas: list[str],
    n_clusters: int = KMEANS_N_CLUSTERS,
    random_state: int = KMEANS_RANDOM_STATE,
) -> tuple[pd.DataFrame, np.ndarray, StandardScaler]:
    """
    Escala las columnas indicadas y aplica K-Means.

    Parameters
    ----------
    df_model : pd.DataFrame
        Dataset con las columnas a usar para clustering.
    columnas : list[str]
        Nombres de las columnas (features) para el modelo.
    n_clusters : int
        Número de clusters.
    random_state : int
        Semilla para reproducibilidad.

    Returns
    -------
    df_model : pd.DataFrame
        Dataset original con columna 'cluster' añadida.
    X_scaled : np.ndarray
        Datos escalados usados para el clustering.
    scaler : StandardScaler
        Scaler entrenado (para transformar nuevos datos).
    """
    logger.info(
        "Aplicando K-Means: k=%d, features=%s, n=%d registros.",
        n_clusters, columnas, len(df_model),
    )

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[columnas])

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=KMEANS_N_INIT)
    df_model = df_model.copy()
    df_model["cluster"] = kmeans.fit_predict(X_scaled)

    for c in range(n_clusters):
        n = (df_model["cluster"] == c).sum()
        logger.info("  Cluster %d: %d registros (%.1f%%)", c, n, 100 * n / len(df_model))

    return df_model, X_scaled, scaler


def calcular_eps_optimo(
    X_scaled: np.ndarray,
    min_samples: int = DBSCAN_MIN_SAMPLES,
    muestra: int = 5_000,
    random_state: int = DBSCAN_RANDOM_STATE,
) -> None:
    """
    Genera la curva de distancia al k-ésimo vecino para orientar la elección de eps.
    Imprime los percentiles clave; úsalos para ajustar DBSCAN_EPS en config.py.

    Parameters
    ----------
    X_scaled : np.ndarray
        Datos escalados.
    min_samples : int
        Igual al min_samples que usarás en DBSCAN (define k = min_samples).
    muestra : int
        Tamaño de muestra para el cálculo (NearestNeighbors es O(n²)).
    random_state : int
        Semilla para la muestra aleatoria.
    """
    np.random.seed(random_state)
    idx = np.random.choice(X_scaled.shape[0], size=min(muestra, X_scaled.shape[0]), replace=False)
    X_sample = X_scaled[idx]

    nbrs = NearestNeighbors(n_neighbors=min_samples).fit(X_sample)
    distancias, _ = nbrs.kneighbors(X_sample)
    dist_k = np.sort(distancias[:, -1])

    percentiles = [50, 75, 90, 95, 99]
    logger.info("Distancias al %d-ésimo vecino (percentiles):", min_samples)
    for p in percentiles:
        logger.info("  P%d: %.4f", p, np.percentile(dist_k, p))
    logger.info("  Sugerencia: usa el valor donde la curva 'coda' como eps.")


def aplicar_dbscan_muestra(
    X_scaled: np.ndarray,
    tamano_muestra: int = DBSCAN_SAMPLE_SIZE,
    eps: float = DBSCAN_EPS,
    min_samples: int = DBSCAN_MIN_SAMPLES,
    random_state: int = DBSCAN_RANDOM_STATE,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Aplica DBSCAN sobre una muestra aleatoria de los datos escalados.

    DBSCAN tiene complejidad O(n²) en memoria, por lo que no es viable
    sobre los ~267k registros completos. Se aplica sobre una muestra
    con semilla fija para reproducibilidad.

    Parameters
    ----------
    X_scaled : np.ndarray
        Datos escalados (dataset completo).
    tamano_muestra : int
        Número de registros a muestrear.
    eps : float
        Radio de vecindad. Ajustar con `calcular_eps_optimo()`.
    min_samples : int
        Mínimo de puntos para formar un cluster denso.
    random_state : int
        Semilla para reproducibilidad.

    Returns
    -------
    muestra_idx : np.ndarray
        Índices de las filas seleccionadas en X_scaled.
    clusters_dbscan : np.ndarray
        Etiquetas de cluster para cada fila de la muestra (-1 = ruido).
    """
    n_total = X_scaled.shape[0]
    tamano_muestra = min(tamano_muestra, n_total)

    np.random.seed(random_state)
    muestra_idx = np.random.choice(n_total, size=tamano_muestra, replace=False)
    X_muestra = X_scaled[muestra_idx]

    logger.info(
        "Aplicando DBSCAN: eps=%.2f, min_samples=%d, muestra=%d/%d registros.",
        eps, min_samples, tamano_muestra, n_total,
    )

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters_dbscan = dbscan.fit_predict(X_muestra)

    n_clusters = len(set(clusters_dbscan)) - (1 if -1 in clusters_dbscan else 0)
    n_ruido = (clusters_dbscan == -1).sum()
    logger.info(
        "DBSCAN: %d clusters encontrados, %d puntos de ruido (%.1f%%).",
        n_clusters, n_ruido, 100 * n_ruido / tamano_muestra,
    )

    return muestra_idx, clusters_dbscan