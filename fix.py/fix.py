codigo = """import logging
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from .config import (
    DBSCAN_EPS, DBSCAN_MIN_SAMPLES, DBSCAN_RANDOM_STATE,
    DBSCAN_SAMPLE_SIZE, KMEANS_N_CLUSTERS, KMEANS_N_INIT, KMEANS_RANDOM_STATE,
)

logger = logging.getLogger(__name__)

def aplicar_kmeans(df_model, columnas, n_clusters=KMEANS_N_CLUSTERS, random_state=KMEANS_RANDOM_STATE):
    logger.info("Aplicando K-Means: k=%d, n=%d registros.", n_clusters, len(df_model))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[columnas])
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=KMEANS_N_INIT)
    df_model = df_model.copy()
    df_model["cluster"] = kmeans.fit_predict(X_scaled)
    for c in range(n_clusters):
        n = (df_model["cluster"] == c).sum()
        logger.info("  Cluster %d: %d registros (%.1f%%)", c, n, 100 * n / len(df_model))
    return df_model, X_scaled, scaler

def calcular_eps_optimo(X_scaled, min_samples=DBSCAN_MIN_SAMPLES, muestra=5000, random_state=DBSCAN_RANDOM_STATE):
    np.random.seed(random_state)
    idx = np.random.choice(X_scaled.shape[0], size=min(muestra, X_scaled.shape[0]), replace=False)
    nbrs = NearestNeighbors(n_neighbors=min_samples).fit(X_scaled[idx])
    distancias, _ = nbrs.kneighbors(X_scaled[idx])
    dist_k = np.sort(distancias[:, -1])
    for p in [50, 75, 90, 95, 99]:
        logger.info("  P%d: %.4f", p, np.percentile(dist_k, p))

def aplicar_dbscan_muestra(X_scaled, tamano_muestra=DBSCAN_SAMPLE_SIZE, eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES, random_state=DBSCAN_RANDOM_STATE):
    n_total = X_scaled.shape[0]
    tamano_muestra = min(tamano_muestra, n_total)
    np.random.seed(random_state)
    muestra_idx = np.random.choice(n_total, size=tamano_muestra, replace=False)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters_dbscan = dbscan.fit_predict(X_scaled[muestra_idx])
    n_ruido = (clusters_dbscan == -1).sum()
    logger.info("DBSCAN: %d puntos de ruido (%.1f%%).", n_ruido, 100 * n_ruido / tamano_muestra)
    return muestra_idx, clusters_dbscan

def aplicar_isolation_forest(df_model, columnas, contamination=0.01, random_state=KMEANS_RANDOM_STATE):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[columnas])
    iso = IsolationForest(contamination=contamination, random_state=random_state, n_jobs=-1)
    pred = iso.fit_predict(X_scaled)
    df_model = df_model.copy()
    df_model["anomalia_if"] = pred == -1
    n_anomalos = df_model["anomalia_if"].sum()
    logger.info("Isolation Forest: %d anomalias (%.2f%%).", n_anomalos, 100 * n_anomalos / len(df_model))
    return df_model
"""

with open("src/clustering.py", "w", encoding="utf-8") as f:
    f.write(codigo)

print("Archivo escrito correctamente.")
print("Tiene isolation_forest:", "aplicar_isolation_forest" in open("src/clustering.py").read())
