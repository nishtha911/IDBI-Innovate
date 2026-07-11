"""
ML Pipeline Utilities
=====================
Shared helper functions for logging, serialization, column detection,
and directory management.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from . import config


def setup_logging(name: str = "ml_pipeline") -> logging.Logger:
    """Configure and return a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, config.LOG_LEVEL))
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, config.LOG_LEVEL))
        formatter = logging.Formatter(
            fmt=config.LOG_FORMAT,
            datefmt=config.LOG_DATE_FORMAT,
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def ensure_dirs() -> None:
    """Create required output directories if they don't exist."""
    for dir_path in [config.DATA_DIR, config.SAVED_MODELS_DIR, config.NOTEBOOKS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def save_artifact(obj: Any, path: Path) -> None:
    """Serialize an object to disk using pickle."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_artifact(path: Path) -> Any:
    """Deserialize an object from disk."""
    with open(path, "rb") as f:
        return pickle.load(f)


def save_json(data: Any, path: Path) -> None:
    """Save a JSON-serializable object to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=_json_default)


def load_json(path: Path) -> Any:
    """Load a JSON file from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _json_default(obj: Any) -> Any:
    """Custom JSON serializer for numpy types."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def auto_detect_column_types(
    df: pd.DataFrame,
    exclude_cols: List[str] | None = None,
) -> Tuple[List[str], List[str]]:
    """
    Automatically detect numeric and categorical columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    exclude_cols : list of str, optional
        Columns to exclude from detection.

    Returns
    -------
    numeric_cols : list of str
    categorical_cols : list of str
    """
    if exclude_cols is None:
        exclude_cols = []

    numeric_cols = []
    categorical_cols = []

    for col in df.columns:
        if col in exclude_cols:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            categorical_cols.append(col)

    return numeric_cols, categorical_cols


def compute_class_weights(y: pd.Series) -> Dict[int, float]:
    """
    Compute inverse-frequency class weights for imbalanced classification.

    Parameters
    ----------
    y : pd.Series
        Target labels (integer-encoded).

    Returns
    -------
    dict
        Mapping from class label to weight.
    """
    counts = y.value_counts()
    total = len(y)
    n_classes = len(counts)
    weights = {}
    for cls, count in counts.items():
        weights[cls] = total / (n_classes * count)
    return weights


def get_sample_weights(y: pd.Series) -> np.ndarray:
    """
    Compute per-sample weights from class weights.

    Parameters
    ----------
    y : pd.Series
        Target labels (integer-encoded).

    Returns
    -------
    np.ndarray
        Array of per-sample weights.
    """
    class_weights = compute_class_weights(y)
    return np.array([class_weights[label] for label in y])
