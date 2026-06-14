# src/logging_config.py
"""Configuración de logging para notebooks y scripts."""

import logging


def configurar_logging(nivel: int = logging.INFO) -> None:
    """
    Activa el sistema de logging del proyecto.
    Llama a esta función al inicio de cada notebook.

    Usage
    -----
    from src.logging_config import configurar_logging
    configurar_logging()
    """
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )