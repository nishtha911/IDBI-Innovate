"""
Feature Engineering Module
===========================
Transforms the preprocessed DataFrame into a model-ready feature matrix.
Handles one-hot encoding, feature scaling, feature selection (correlation
pruning), and exports feature metadata for reproducibility.

Usage:
    python -m ml.feature_engineering
"""

import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Allow running as script or module
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml import config
from ml.utils import (
    setup_logging,
    ensure_dirs,
    save_artifact,
    save_json,
    auto_detect_column_types,
)

logger = setup_logging("feature_engineering")


# ──────────────────────────────────────────────────────────────
# 1. CATEGORICAL ENCODING
# ──────────────────────────────────────────────────────────────


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode categorical columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with categorical columns replaced by one-hot columns.
    """
    cat_cols = [c for c in config.CATEGORICAL_COLUMNS if c in df.columns]

    if not cat_cols:
        logger.info("No categorical columns to encode")
        return df

    logger.info(f"One-hot encoding columns: {cat_cols}")
    df = pd.get_dummies(df, columns=cat_cols, drop_first=False, dtype=int)

    return df


# ──────────────────────────────────────────────────────────────
# 2. FEATURE SELECTION
# ──────────────────────────────────────────────────────────────


def drop_zero_variance(df: pd.DataFrame, feature_cols: list) -> Tuple[pd.DataFrame, list]:
    """Drop columns with zero variance."""
    zero_var = [col for col in feature_cols if df[col].std() == 0]
    if zero_var:
        logger.info(f"Dropping {len(zero_var)} zero-variance features: {zero_var}")
        df = df.drop(columns=zero_var)
        feature_cols = [c for c in feature_cols if c not in zero_var]
    return df, feature_cols


def drop_highly_correlated(
    df: pd.DataFrame,
    feature_cols: list,
    threshold: float = 0.95,
) -> Tuple[pd.DataFrame, list]:
    """
    Drop one of each pair of features with correlation above threshold.
    Keeps the feature that appears first in the list.
    """
    corr_matrix = df[feature_cols].corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    to_drop = set()
    for col in upper.columns:
        high_corr = upper.index[upper[col] > threshold].tolist()
        if high_corr:
            to_drop.add(col)

    if to_drop:
        logger.info(
            f"Dropping {len(to_drop)} highly correlated features "
            f"(threshold={threshold}): {sorted(to_drop)}"
        )
        df = df.drop(columns=list(to_drop))
        feature_cols = [c for c in feature_cols if c not in to_drop]

    return df, feature_cols


# ──────────────────────────────────────────────────────────────
# 3. SCALING
# ──────────────────────────────────────────────────────────────


def scale_features(
    df: pd.DataFrame,
    feature_cols: list,
    scaler: StandardScaler | None = None,
    fit: bool = True,
) -> Tuple[pd.DataFrame, StandardScaler]:
    """
    Apply StandardScaler to numeric feature columns.

    Parameters
    ----------
    df : pd.DataFrame
    feature_cols : list of str
    scaler : StandardScaler, optional
        If provided and fit=False, uses this scaler for transform only.
    fit : bool
        If True, fits a new scaler; otherwise uses the provided one.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with scaled features.
    scaler : StandardScaler
        Fitted scaler.
    """
    if scaler is None:
        scaler = StandardScaler()

    # Only scale actually numeric columns
    numeric_feature_cols = [
        c for c in feature_cols
        if pd.api.types.is_numeric_dtype(df[c])
    ]

    if fit:
        df[numeric_feature_cols] = scaler.fit_transform(df[numeric_feature_cols])
        logger.info(f"Fitted and transformed {len(numeric_feature_cols)} numeric features")
    else:
        df[numeric_feature_cols] = scaler.transform(df[numeric_feature_cols])
        logger.info(f"Transformed {len(numeric_feature_cols)} numeric features with existing scaler")

    return df, scaler


# ──────────────────────────────────────────────────────────────
# 4. MAIN PIPELINE
# ──────────────────────────────────────────────────────────────


def get_feature_columns(df: pd.DataFrame) -> list:
    """Get the list of feature columns (excluding IDs, targets, metadata)."""
    exclude = set(config.EXCLUDE_COLUMNS)
    return [c for c in df.columns if c not in exclude]


def run_feature_engineering(
    df: pd.DataFrame | None = None,
) -> Tuple[pd.DataFrame, list, StandardScaler]:
    """
    Execute the full feature engineering pipeline.

    Parameters
    ----------
    df : pd.DataFrame, optional
        If None, loads from processed_features.csv.

    Returns
    -------
    df : pd.DataFrame
        Feature-engineered DataFrame.
    feature_cols : list of str
        Ordered list of feature column names.
    scaler : StandardScaler
        Fitted scaler object.
    """
    ensure_dirs()

    logger.info("=" * 60)
    logger.info("STARTING FEATURE ENGINEERING")
    logger.info("=" * 60)

    # Load if not provided
    if df is None:
        if not config.PROCESSED_FEATURES_PATH.exists():
            raise FileNotFoundError(
                f"Processed features not found at {config.PROCESSED_FEATURES_PATH}. "
                "Run preprocessing first."
            )
        df = pd.read_csv(config.PROCESSED_FEATURES_PATH)
        logger.info(f"Loaded processed features: {df.shape}")

    # Step 1: One-hot encode categoricals
    logger.info("-" * 40)
    logger.info("Step 1: Encoding categorical features...")
    df = encode_categoricals(df)

    # Step 2: Identify feature columns
    feature_cols = get_feature_columns(df)
    logger.info(f"Initial feature count: {len(feature_cols)}")

    # Step 3: Drop zero-variance features
    logger.info("-" * 40)
    logger.info("Step 2: Dropping zero-variance features...")
    df, feature_cols = drop_zero_variance(df, feature_cols)

    # Step 4: Drop highly correlated features
    logger.info("-" * 40)
    logger.info("Step 3: Dropping highly correlated features...")
    df, feature_cols = drop_highly_correlated(
        df, feature_cols, threshold=config.CORRELATION_THRESHOLD
    )

    # Step 5: Scale features
    logger.info("-" * 40)
    logger.info("Step 4: Scaling features...")
    df, scaler = scale_features(df, feature_cols)

    # Save artifacts
    save_artifact(scaler, config.SCALER_PATH)
    logger.info(f"Saved scaler to: {config.SCALER_PATH}")

    save_json(feature_cols, config.FEATURE_NAMES_PATH)
    logger.info(f"Saved feature names to: {config.FEATURE_NAMES_PATH}")

    logger.info(f"Final feature count: {len(feature_cols)}")
    logger.info("=" * 60)
    logger.info("FEATURE ENGINEERING COMPLETE")
    logger.info("=" * 60)

    return df, feature_cols, scaler


if __name__ == "__main__":
    run_feature_engineering()
