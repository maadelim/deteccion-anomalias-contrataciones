import pandas as pd
from src.preprocessing import limpiar_y_preparar


def _crear_df_base():
    return pd.DataFrame({
        "cantidad_adjudicado_item": [1, 1, 1, 1],
        "monto_referencial_item_soles": [1000.0, 500.0, 200.0, 0.0],
        "monto_adjudicado_item_soles": [1200.0, 300.0, 250.0, 100.0],
        "tipo_proveedor": ["Empresa", "Empresa", "Empresa", "Empresa"],
        "fecha_buenapro":     ["2023-06-01", "2023-08-15", "2023-09-01", "2023-06-01"],
        "fecha_convocatoria": ["2023-05-01", "2023-07-01", "2023-08-01", "2023-05-01"],
    })


def test_separa_monto_cero():
    df = _crear_df_base()
    df_model, df_cero = limpiar_y_preparar(df)
    # Verifica que se separan los de monto cero
    assert len(df_cero) == 1
    assert (df_cero["monto_referencial_item_soles"] == 0).all()
    # Verifica que df_model no tiene monto cero
    assert (df_model["monto_referencial_item_soles"] != 0).all()


def test_columnas_creadas():
    df = _crear_df_base()
    df_model, _ = limpiar_y_preparar(df)
    columnas = ["diferencia_monto", "diferencia_pct", "diferencia_pct_cap", "dias_proceso"]
    for col in columnas:
        assert col in df_model.columns


def test_no_dias_negativos():
    df = _crear_df_base()
    fila_mala = {
        "cantidad_adjudicado_item": 1,
        "monto_referencial_item_soles": 800.0,
        "monto_adjudicado_item_soles": 900.0,
        "tipo_proveedor": "Empresa",
        "fecha_buenapro": "2023-01-01",
        "fecha_convocatoria": "2023-06-01",
    }
    df = pd.concat([df, pd.DataFrame([fila_mala])], ignore_index=True)
    df_model, _ = limpiar_y_preparar(df)
    assert (df_model["dias_proceso"] >= 0).all()


def test_capping_diferencia_pct():
    df = _crear_df_base()
    df_model, _ = limpiar_y_preparar(df)
    assert df_model["diferencia_pct_cap"].max() <= 500
    assert df_model["diferencia_pct_cap"].min() >= -100