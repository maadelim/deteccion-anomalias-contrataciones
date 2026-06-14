import pandas as pd


def cargar_adjudicaciones(ruta_datos='../data/raw/'):
    """
    Carga y une los archivos de adjudicaciones de los años 2022-2025.

    Parámetros:
        ruta_datos (str): ruta a la carpeta donde están los archivos Excel

    Retorna:
        DataFrame con todos los registros unidos
    """
    df_2022 = pd.read_excel(f'{ruta_datos}CONOSCE_ADJUDICACIONES2022_0.xlsx')
    df_2023 = pd.read_excel(f'{ruta_datos}CONOSCE_ADJUDICACIONES2023_0.xlsx')
    df_2024 = pd.read_excel(f'{ruta_datos}CONOSCE_ADJUDICACIONES2024_0.xlsx')
    df_2025 = pd.read_excel(f'{ruta_datos}CONOSCE_ADJUDICACIONES2025_0.xlsx')

    df_total = pd.concat([df_2022, df_2023, df_2024, df_2025], ignore_index=True)

    return df_total 