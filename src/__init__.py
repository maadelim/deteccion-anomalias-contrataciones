# src/__init__.py
# Hace que src/ sea importable como paquete Python.
from .data_loader import cargar_adjudicaciones
from .preprocessing import limpiar_y_preparar
from .clustering import aplicar_kmeans, aplicar_dbscan_muestra
