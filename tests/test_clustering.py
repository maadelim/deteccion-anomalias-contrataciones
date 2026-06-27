# tests/test_clustering.py
import numpy as np
import pandas as pd
import pytest
from src.clustering import aplicar_kmeans, evaluar_clustering, aplicar_isolation_forest


# ── Fixture compartido ────────────────────────────────────────────────────────

def _crear_df_clustering():
    """DataFrame mínimo con las columnas que esperan las funciones de clustering."""
    np.random.seed(42)
    return pd.DataFrame({
        "diferencia_pct_cap": np.concatenate([
            np.random.normal(0, 5, 80),      # cluster normal
            np.random.normal(300, 20, 10),    # cluster sobrecosto
            np.random.normal(-50, 5, 10),     # cluster descuento
        ]),
        "dias_proceso": np.concatenate([
            np.random.normal(25, 5, 80),
            np.random.normal(50, 10, 10),
            np.random.normal(300, 30, 10),
        ]),
    })


COLUMNAS = ["diferencia_pct_cap", "dias_proceso"]


# ── Tests de aplicar_kmeans ───────────────────────────────────────────────────

def test_kmeans_agrega_columna_cluster():
    """K-Means debe añadir la columna 'cluster' al dataframe."""
    df = _crear_df_clustering()
    df_result, _, _ = aplicar_kmeans(df, COLUMNAS, n_clusters=3)
    assert "cluster" in df_result.columns


def test_kmeans_numero_correcto_de_clusters():
    """El número de clusters únicos debe ser igual al k pedido."""
    df = _crear_df_clustering()
    for k in [2, 3, 4]:
        df_result, _, _ = aplicar_kmeans(df, COLUMNAS, n_clusters=k)
        assert df_result["cluster"].nunique() == k


def test_kmeans_reproducible_con_mismo_random_state():
    """Con el mismo random_state, el resultado debe ser idéntico."""
    df = _crear_df_clustering()
    df1, _, _ = aplicar_kmeans(df, COLUMNAS, n_clusters=3, random_state=42)
    df2, _, _ = aplicar_kmeans(df, COLUMNAS, n_clusters=3, random_state=42)
    assert (df1["cluster"].values == df2["cluster"].values).all()


def test_kmeans_no_modifica_df_original():
    """aplicar_kmeans no debe modificar el dataframe de entrada."""
    df = _crear_df_clustering()
    columnas_originales = list(df.columns)
    aplicar_kmeans(df, COLUMNAS, n_clusters=3)
    assert list(df.columns) == columnas_originales


def test_kmeans_retorna_scaler_y_xscaled():
    """Debe retornar exactamente (df, X_scaled, scaler)."""
    df = _crear_df_clustering()
    resultado = aplicar_kmeans(df, COLUMNAS, n_clusters=3)
    assert len(resultado) == 3
    df_out, X_scaled, scaler = resultado
    assert X_scaled.shape == (len(df), len(COLUMNAS))


# ── Tests de evaluar_clustering ───────────────────────────────────────────────

def test_evaluar_clustering_retorna_tres_metricas():
    """Debe retornar exactamente las 3 métricas esperadas."""
    df = _crear_df_clustering()
    df_result, X_scaled, _ = aplicar_kmeans(df, COLUMNAS, n_clusters=3)
    metricas = evaluar_clustering(X_scaled, df_result["cluster"].values)
    assert set(metricas.keys()) == {"silhouette_score", "davies_bouldin_index", "calinski_harabasz_score"}


def test_evaluar_clustering_silhouette_en_rango():
    """Silhouette Score debe estar entre -1 y 1."""
    df = _crear_df_clustering()
    df_result, X_scaled, _ = aplicar_kmeans(df, COLUMNAS, n_clusters=3)
    metricas = evaluar_clustering(X_scaled, df_result["cluster"].values)
    assert -1 <= metricas["silhouette_score"] <= 1


def test_evaluar_clustering_davies_bouldin_positivo():
    """Davies-Bouldin Index debe ser >= 0."""
    df = _crear_df_clustering()
    df_result, X_scaled, _ = aplicar_kmeans(df, COLUMNAS, n_clusters=3)
    metricas = evaluar_clustering(X_scaled, df_result["cluster"].values)
    assert metricas["davies_bouldin_index"] >= 0


def test_evaluar_clustering_un_solo_cluster_retorna_vacio():
    """Si todos los puntos son del mismo cluster, debe retornar dict vacío."""
    X = np.random.randn(50, 2)
    labels = np.zeros(50, dtype=int)  # todos en cluster 0
    metricas = evaluar_clustering(X, labels)
    assert metricas == {}


def test_evaluar_clustering_excluye_ruido_dbscan():
    """Con labels que incluyen -1 (ruido DBSCAN), no debe lanzar error."""
    X = np.random.randn(50, 2)
    labels = np.array([-1] * 5 + [0] * 25 + [1] * 20)
    metricas = evaluar_clustering(X, labels)
    assert "silhouette_score" in metricas


# ── Tests de aplicar_isolation_forest ────────────────────────────────────────

def test_isolation_forest_agrega_columna_anomalia():
    """Debe añadir la columna 'anomalia_if' al dataframe."""
    df = _crear_df_clustering()
    df_result = aplicar_isolation_forest(df, COLUMNAS)
    assert "anomalia_if" in df_result.columns


def test_isolation_forest_columna_es_booleana():
    """La columna 'anomalia_if' debe ser de tipo booleano."""
    df = _crear_df_clustering()
    df_result = aplicar_isolation_forest(df, COLUMNAS)
    assert df_result["anomalia_if"].dtype == bool


def test_isolation_forest_detecta_anomalias():
    """Con contamination=0.1 debe detectar aproximadamente el 10% como anomalías."""
    df = _crear_df_clustering()
    df_result = aplicar_isolation_forest(df, COLUMNAS, contamination=0.1)
    pct_anomalias = df_result["anomalia_if"].mean()
    assert 0.05 <= pct_anomalias <= 0.20  # margen razonable
    