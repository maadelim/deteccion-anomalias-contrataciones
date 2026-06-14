import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN


def aplicar_kmeans(df_model, columnas, n_clusters=4, random_state=42):
    """
    Escala las columnas indicadas y aplica K-means.

    Parámetros:
        df_model (DataFrame): dataset con las columnas a usar
        columnas (list): nombres de las columnas para el clustering
        n_clusters (int): número de clusters
        random_state (int): semilla para reproducibilidad

    Retorna:
        df_model (DataFrame): el mismo dataset, con una columna nueva 'cluster'
        X_scaled (array): los datos escalados usados para el clustering
        scaler (StandardScaler): el escalador entrenado
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_model[columnas])

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    df_model = df_model.copy()
    df_model['cluster'] = kmeans.fit_predict(X_scaled)

    return df_model, X_scaled, scaler


def aplicar_dbscan_muestra(X_scaled, tamano_muestra=10000, eps=0.5, min_samples=10, random_state=42):
    """
    Aplica DBSCAN sobre una muestra aleatoria de los datos escalados,
    debido a las limitaciones de memoria con datasets grandes.

    Parámetros:
        X_scaled (array): datos escalados (todo el dataset)
        tamano_muestra (int): cantidad de registros a muestrear
        eps (float): radio de vecindad para DBSCAN
        min_samples (int): mínimo de puntos para formar un cluster denso
        random_state (int): semilla para reproducibilidad

    Retorna:
        muestra_idx (array): índices de las filas seleccionadas
        clusters_dbscan (array): etiquetas de cluster para cada fila de la muestra
    """
    np.random.seed(random_state)
    muestra_idx = np.random.choice(X_scaled.shape[0], size=tamano_muestra, replace=False)
    X_muestra = X_scaled[muestra_idx]

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters_dbscan = dbscan.fit_predict(X_muestra)

    return muestra_idx, clusters_dbscan
