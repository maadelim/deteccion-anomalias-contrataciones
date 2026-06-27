import logging
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from .config import (DBSCAN_EPS, DBSCAN_MIN_SAMPLES, DBSCAN_RANDOM_STATE, DBSCAN_SAMPLE_SIZE, KMEANS_N_CLUSTERS, KMEANS_N_INIT, KMEANS_RANDOM_STATE)

logger = logging.getLogger(__name__)

def aplicar_kmeans(df_model, columnas, n_clusters=KMEANS_N_CLUSTERS, random_state=KMEANS_RANDOM_STATE):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[columnas])
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=KMEANS_N_INIT)
    df_model = df_model.copy()
    df_model['cluster'] = kmeans.fit_predict(X_scaled)
    return df_model, X_scaled, scaler

def evaluar_clustering(X_scaled, labels):
    """
    Calcula métricas internas de validación del clustering.

    Útil para comparar distintos valores de k o distintos algoritmos
    de forma cuantitativa, sin necesidad de ground truth.

    Métricas:
    - Silhouette Score: entre -1 y 1. Más cercano a 1 = clusters más
      compactos y separados. Valores > 0.2 son aceptables en datos reales.
    - Davies-Bouldin Index: más cercano a 0 = mejor. Mide la similitud
      promedio entre cada cluster y el más parecido.
    - Calinski-Harabasz Score: más alto = mejor. Mide la relación entre
      la dispersión inter-cluster e intra-cluster.

    Parameters
    ----------
    X_scaled : np.ndarray
        Matriz de features ya escalada (salida del StandardScaler).
    labels : np.ndarray
        Etiquetas de cluster asignadas por el modelo. El valor -1
        (ruido de DBSCAN) se excluye automáticamente del cálculo.

    Returns
    -------
    dict con las tres métricas. Vacío si hay menos de 2 clusters válidos.
    """
    mask = labels != -1  # excluir ruido de DBSCAN
    n_clusters_validos = len(set(labels[mask]))

    if mask.sum() < 2 or n_clusters_validos < 2:
        logger.warning("evaluar_clustering: no hay suficientes clusters para calcular métricas.")
        return {}

    metricas = {
        "silhouette_score": round(silhouette_score(X_scaled[mask], labels[mask], sample_size=10_000, random_state=42), 4),
        "davies_bouldin_index": round(davies_bouldin_score(X_scaled[mask], labels[mask]), 4),
        "calinski_harabasz_score": round(calinski_harabasz_score(X_scaled[mask], labels[mask]), 2),
    }

    logger.info("Silhouette Score:       %.4f  (↑ mejor, máx=1)", metricas["silhouette_score"])
    logger.info("Davies-Bouldin Index:   %.4f  (↓ mejor, mín=0)", metricas["davies_bouldin_index"])
    logger.info("Calinski-Harabasz:      %.2f  (↑ mejor)", metricas["calinski_harabasz_score"])

    return metricas

def calcular_eps_optimo(X_scaled, min_samples=DBSCAN_MIN_SAMPLES, muestra=5000, random_state=DBSCAN_RANDOM_STATE):
    np.random.seed(random_state)
    idx = np.random.choice(X_scaled.shape[0], size=min(muestra, X_scaled.shape[0]), replace=False)
    nbrs = NearestNeighbors(n_neighbors=min_samples).fit(X_scaled[idx])
    distancias, _ = nbrs.kneighbors(X_scaled[idx])
    dist_k = np.sort(distancias[:, -1])
    for p in [50, 75, 90, 95, 99]:
        logger.info('P%d: %.4f', p, np.percentile(dist_k, p))

def aplicar_dbscan_muestra(X_scaled, tamano_muestra=DBSCAN_SAMPLE_SIZE, eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES, random_state=DBSCAN_RANDOM_STATE):
    n_total = X_scaled.shape[0]
    tamano_muestra = min(tamano_muestra, n_total)
    np.random.seed(random_state)
    muestra_idx = np.random.choice(n_total, size=tamano_muestra, replace=False)
    clusters_dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X_scaled[muestra_idx])
    return muestra_idx, clusters_dbscan

def aplicar_isolation_forest(df_model, columnas, contamination=0.01, random_state=KMEANS_RANDOM_STATE):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[columnas])
    pred = IsolationForest(contamination=contamination, random_state=random_state, n_jobs=-1).fit_predict(X_scaled)
    df_model = df_model.copy()
    df_model['anomalia_if'] = pred == -1
    logger.info('Isolation Forest: %d anomalias.', df_model['anomalia_if'].sum())
    return df_model
import logging
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from .config import (DBSCAN_EPS, DBSCAN_MIN_SAMPLES, DBSCAN_RANDOM_STATE, DBSCAN_SAMPLE_SIZE, KMEANS_N_CLUSTERS, KMEANS_N_INIT, KMEANS_RANDOM_STATE)

logger = logging.getLogger(__name__)

def aplicar_kmeans(df_model, columnas, n_clusters=KMEANS_N_CLUSTERS, random_state=KMEANS_RANDOM_STATE):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[columnas])
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=KMEANS_N_INIT)
    df_model = df_model.copy()
    df_model['cluster'] = kmeans.fit_predict(X_scaled)
    return df_model, X_scaled, scaler

    idx = np.random.choice(X_scaled.shape[0], size=min(muestra, X_scaled.shape[0]), replace=False)
    nbrs = NearestNeighbors(n_neighbors=min_samples).fit(X_scaled[idx])
    distancias, _ = nbrs.kneighbors(X_scaled[idx])
    dist_k = np.sort(distancias[:, -1])
    for p in [50, 75, 90, 95, 99]:
        logger.info('P%d: %.4f', p, np.percentile(dist_k, p))

def aplicar_dbscan_muestra(X_scaled, tamano_muestra=DBSCAN_SAMPLE_SIZE, eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES, random_state=DBSCAN_RANDOM_STATE):
    n_total = X_scaled.shape[0]
    tamano_muestra = min(tamano_muestra, n_total)
    np.random.seed(random_state)
    muestra_idx = np.random.choice(n_total, size=tamano_muestra, replace=False)
    clusters_dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X_scaled[muestra_idx])
    return muestra_idx, clusters_dbscan

def aplicar_isolation_forest(df_model, columnas, contamination=0.01, random_state=KMEANS_RANDOM_STATE):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[columnas])
    pred = IsolationForest(contamination=contamination, random_state=random_state, n_jobs=-1).fit_predict(X_scaled)
    df_model = df_model.copy()
    df_model['anomalia_if'] = pred == -1
    logger.info('Isolation Forest: %d anomalias.', df_model['anomalia_if'].sum())
    return df_model
