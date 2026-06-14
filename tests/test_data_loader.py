# tests/test_data_loader.py
import pytest
from src.data_loader import cargar_adjudicaciones


def test_error_si_no_hay_archivos(tmp_path):
    """Si no hay archivos, debe lanzar FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        cargar_adjudicaciones(ruta_datos=str(tmp_path) + "/")