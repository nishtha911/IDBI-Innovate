"""
Model Explainability Module
============================
SHAP-based explanations for individual predictions and global
feature importance analysis.

Provides:
- Per-prediction SHAP value computation
- Top risk factor extraction with human-readable names
- Global feature importance summary
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Allow running as script or module
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml import config
from ml.utils import setup_logging

logger = setup_logging("explain")


def _get_shap_explainer(model: Any) -> Any:
    """
    Create a SHAP explainer appropriate for the model type.

    Handles both raw tree models and CalibratedClassifierCV wrappers.
    """
    import shap

    # If it's a calibrated model, extract the base estimator
    base_model = model
    if hasattr(model, "calibrated_classifiers_"):
        try:
            base_model = model.calibrated_classifiers_[0].estimator
        except (AttributeError, IndexError):
            base_model = model
    elif hasattr(model, "estimators_"):
        try:
            base_model = model.estimators_[0].estimator
        except (AttributeError, IndexError):
            base_model = model

    # Try TreeExplainer first (fast), fall back to KernelExplainer
    try:
        explainer = shap.TreeExplainer(base_model)
        logger.debug("Using SHAP TreeExplainer")
    except Exception:
        logger.warning("TreeExplainer failed, falling back to Explainer")
        explainer = shap.Explainer(model)

    return explainer


def explain_prediction(
    model: Any,
    features: np.ndarray,
    feature_names: List[str],
) -> Dict[str, Any]:
    """
    Compute SHAP values for a single prediction.

    Parameters
    ----------
    model : trained model
    features : np.ndarray
        1D or 2D array of feature values (single sample).
    feature_names : list of str
        Feature column names.

    Returns
    -------
    dict with keys:
        'shap_values': array of SHAP values per class
        'base_values': array of base values per class
        'feature_names': list of feature names
    """
    if features.ndim == 1:
        features = features.reshape(1, -1)

    explainer = _get_shap_explainer(model)

    try:
        shap_values = explainer.shap_values(features)
    except Exception as e:
        logger.warning(f"SHAP computation failed: {e}. Returning empty explanation.")
        return {
            "shap_values": np.zeros((1, len(feature_names), 3)),
            "base_values": np.zeros(3),
            "feature_names": feature_names,
        }

    # shap_values shape: (n_classes, n_samples, n_features) or list of arrays
    if isinstance(shap_values, list):
        # Convert list of (n_samples, n_features) to (n_samples, n_features, n_classes)
        shap_values = np.stack(shap_values, axis=-1)
    elif shap_values.ndim == 3 and shap_values.shape[0] == 3:
        # Shape: (n_classes, n_samples, n_features) → (n_samples, n_features, n_classes)
        shap_values = np.transpose(shap_values, (1, 2, 0))

    base_values = getattr(explainer, "expected_value", np.zeros(3))
    if isinstance(base_values, (list, np.ndarray)):
        base_values = np.array(base_values)
    else:
        base_values = np.array([base_values] * 3)

    return {
        "shap_values": shap_values,
        "base_values": base_values,
        "feature_names": feature_names,
    }


def get_top_risk_factors(
    shap_values: np.ndarray,
    feature_names: List[str],
    predicted_class: int,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Extract top-K features driving the prediction.

    Parameters
    ----------
    shap_values : np.ndarray
        Shape: (1, n_features, n_classes) or (n_features, n_classes)
    feature_names : list of str
    predicted_class : int
        The predicted class index.
    top_k : int
        Number of top features to return.

    Returns
    -------
    list of dict
        Each dict: {'feature', 'display_name', 'importance', 'direction'}
    """
    # Get SHAP values for the predicted class
    if shap_values.ndim == 3:
        sv = shap_values[0, :, predicted_class]  # (n_features,)
    elif shap_values.ndim == 2:
        sv = shap_values[:, predicted_class]
    else:
        sv = shap_values

    # Sort by absolute SHAP value
    abs_sv = np.abs(sv)
    top_indices = np.argsort(abs_sv)[::-1][:top_k]

    factors = []
    for idx in top_indices:
        feature = feature_names[idx]
        display_name = config.FEATURE_DISPLAY_NAMES.get(feature, feature)
        importance = float(abs_sv[idx])
        direction = "positive" if sv[idx] > 0 else "negative"

        factors.append({
            "feature": feature,
            "display_name": display_name,
            "importance": round(importance, 4),
            "direction": direction,
            "shap_value": round(float(sv[idx]), 4),
        })

    return factors


def generate_global_report(
    model: Any,
    X: np.ndarray,
    feature_names: List[str],
    max_samples: int = 200,
) -> Dict[str, Any]:
    """
    Generate global feature importance using SHAP.

    Parameters
    ----------
    model : trained model
    X : np.ndarray
        Feature matrix (test or full dataset).
    feature_names : list of str
    max_samples : int
        Max number of samples to use for SHAP computation.

    Returns
    -------
    dict
        Global importance report with per-class and overall rankings.
    """
    # Subsample for speed
    if X.shape[0] > max_samples:
        indices = np.random.RandomState(config.RANDOM_SEED).choice(
            X.shape[0], max_samples, replace=False
        )
        X_sample = X[indices]
    else:
        X_sample = X

    explainer = _get_shap_explainer(model)

    try:
        shap_values = explainer.shap_values(X_sample)
    except Exception as e:
        logger.warning(f"Global SHAP computation failed: {e}")
        return {"error": str(e)}

    # Normalize shape
    if isinstance(shap_values, list):
        shap_values = np.stack(shap_values, axis=-1)  # (n_samples, n_features, n_classes)
    elif shap_values.ndim == 3 and shap_values.shape[0] == 3:
        shap_values = np.transpose(shap_values, (1, 2, 0))

    # Overall importance: mean absolute SHAP across all classes and samples
    overall_importance = np.mean(np.abs(shap_values), axis=(0, 2))  # (n_features,)

    # Per-class importance
    class_importance = {}
    for cls_idx, cls_name in config.INVERSE_LABEL_MAP.items():
        cls_imp = np.mean(np.abs(shap_values[:, :, cls_idx]), axis=0)
        sorted_idx = np.argsort(cls_imp)[::-1]
        class_importance[cls_name] = [
            {
                "feature": feature_names[i],
                "display_name": config.FEATURE_DISPLAY_NAMES.get(feature_names[i], feature_names[i]),
                "importance": round(float(cls_imp[i]), 4),
            }
            for i in sorted_idx[:10]
        ]

    # Overall ranking
    sorted_overall = np.argsort(overall_importance)[::-1]
    overall_ranking = [
        {
            "feature": feature_names[i],
            "display_name": config.FEATURE_DISPLAY_NAMES.get(feature_names[i], feature_names[i]),
            "importance": round(float(overall_importance[i]), 4),
        }
        for i in sorted_overall[:15]
    ]

    report = {
        "overall_ranking": overall_ranking,
        "per_class_ranking": class_importance,
        "n_samples_used": X_sample.shape[0],
    }

    logger.info("Global SHAP report generated")
    logger.info(f"Top 5 overall features: {[f['feature'] for f in overall_ranking[:5]]}")

    return report


if __name__ == "__main__":
    from ml.utils import load_artifact, load_json

    # Load model and features for a quick test
    model = load_artifact(config.MODEL_PATH)
    feature_names = load_json(config.FEATURE_NAMES_PATH)

    # Load test data
    df = pd.read_csv(config.PROCESSED_FEATURES_PATH)

    from ml.feature_engineering import run_feature_engineering
    df_eng, feat_cols, _ = run_feature_engineering(df)

    X = df_eng[feat_cols].values[:5]

    # Explain first 5 predictions
    for i in range(min(5, X.shape[0])):
        pred = model.predict(X[i:i+1])[0]
        explanation = explain_prediction(model, X[i], feature_names)
        factors = get_top_risk_factors(
            explanation["shap_values"], feature_names, pred
        )
        print(f"\nSample {i}: Predicted={config.INVERSE_LABEL_MAP.get(pred, pred)}")
        for f in factors:
            print(f"  {f['display_name']}: {f['shap_value']:+.4f} ({f['direction']})")
