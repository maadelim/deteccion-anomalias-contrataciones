import logging
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
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
