"""
Model Training Module
=====================
End-to-end training pipeline:
1. Load preprocessed + feature-engineered data
2. Stratified train/test split
3. Optuna hyperparameter tuning for XGBoost and LightGBM
4. Probability calibration
5. Model evaluation and artifact saving

Usage:
    python -m ml.train
"""

import sys
import warnings
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

# Allow running as script or module
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml import config
from ml.utils import (
    ensure_dirs,
    get_sample_weights,
    load_json,
    save_artifact,
    save_json,
    setup_logging,
)
from ml.preprocessing import run_preprocessing
from ml.feature_engineering import run_feature_engineering

logger = setup_logging("training")

# Suppress non-critical warnings during tuning
warnings.filterwarnings("ignore", category=UserWarning)


# ──────────────────────────────────────────────────────────────
# 1. DATA PREPARATION
# ──────────────────────────────────────────────────────────────


def prepare_data() -> Tuple[pd.DataFrame, list]:
    """
    Run preprocessing and feature engineering, return the complete
    feature-engineered DataFrame and feature column list.
    """
    logger.info("Running preprocessing...")
    preprocessed_df = run_preprocessing()

    logger.info("Running feature engineering...")
    engineered_df, feature_cols, _ = run_feature_engineering(preprocessed_df)

    return engineered_df, feature_cols


def split_data(
    df: pd.DataFrame,
    feature_cols: list,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Stratified train/test split.

    Returns
    -------
    X_train, X_test, y_train, y_test
    """
    X = df[feature_cols].values
    y = df[config.TARGET_COLUMN].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_SEED,
        stratify=y,
    )

    logger.info(
        f"Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples"
    )
    logger.info(
        f"Train class distribution: {dict(zip(*np.unique(y_train, return_counts=True)))}"
    )
    logger.info(
        f"Test class distribution:  {dict(zip(*np.unique(y_test, return_counts=True)))}"
    )

    return X_train, X_test, y_train, y_test


# ──────────────────────────────────────────────────────────────
# 2. HYPERPARAMETER TUNING (OPTUNA)
# ──────────────────────────────────────────────────────────────


def _create_xgb_objective(X_train, y_train, sample_weights):
    """Create an Optuna objective for XGBoost."""
    import xgboost as xgb

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int(
                "n_estimators", *config.XGBOOST_PARAM_SPACE["n_estimators"]
            ),
            "max_depth": trial.suggest_int(
                "max_depth", *config.XGBOOST_PARAM_SPACE["max_depth"]
            ),
            "learning_rate": trial.suggest_float(
                "learning_rate", *config.XGBOOST_PARAM_SPACE["learning_rate"], log=True
            ),
            "subsample": trial.suggest_float(
                "subsample", *config.XGBOOST_PARAM_SPACE["subsample"]
            ),
            "colsample_bytree": trial.suggest_float(
                "colsample_bytree", *config.XGBOOST_PARAM_SPACE["colsample_bytree"]
            ),
            "min_child_weight": trial.suggest_int(
                "min_child_weight", *config.XGBOOST_PARAM_SPACE["min_child_weight"]
            ),
            "gamma": trial.suggest_float(
                "gamma", *config.XGBOOST_PARAM_SPACE["gamma"]
            ),
            "reg_alpha": trial.suggest_float(
                "reg_alpha", *config.XGBOOST_PARAM_SPACE["reg_alpha"]
            ),
            "reg_lambda": trial.suggest_float(
                "reg_lambda", *config.XGBOOST_PARAM_SPACE["reg_lambda"]
            ),
            "objective": "multi:softprob",
            "num_class": 3,
            "eval_metric": "mlogloss",
            "random_state": config.RANDOM_SEED,
            "use_label_encoder": False,
            "verbosity": 0,
        }

        model = xgb.XGBClassifier(**params)
        cv = StratifiedKFold(n_splits=config.N_CV_FOLDS, shuffle=True, random_state=config.RANDOM_SEED)
        scores = cross_val_score(
            model, X_train, y_train,
            cv=cv,
            scoring="f1_macro",
            fit_params={"sample_weight": sample_weights},
        )
        return scores.mean()

    return objective


def _create_lgbm_objective(X_train, y_train, sample_weights):
    """Create an Optuna objective for LightGBM."""
    import lightgbm as lgb

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int(
                "n_estimators", *config.LIGHTGBM_PARAM_SPACE["n_estimators"]
            ),
            "max_depth": trial.suggest_int(
                "max_depth", *config.LIGHTGBM_PARAM_SPACE["max_depth"]
            ),
            "learning_rate": trial.suggest_float(
                "learning_rate", *config.LIGHTGBM_PARAM_SPACE["learning_rate"], log=True
            ),
            "subsample": trial.suggest_float(
                "subsample", *config.LIGHTGBM_PARAM_SPACE["subsample"]
            ),
            "colsample_bytree": trial.suggest_float(
                "colsample_bytree", *config.LIGHTGBM_PARAM_SPACE["colsample_bytree"]
            ),
            "min_child_samples": trial.suggest_int(
                "min_child_samples", *config.LIGHTGBM_PARAM_SPACE["min_child_samples"]
            ),
            "num_leaves": trial.suggest_int(
                "num_leaves", *config.LIGHTGBM_PARAM_SPACE["num_leaves"]
            ),
            "reg_alpha": trial.suggest_float(
                "reg_alpha", *config.LIGHTGBM_PARAM_SPACE["reg_alpha"]
            ),
            "reg_lambda": trial.suggest_float(
                "reg_lambda", *config.LIGHTGBM_PARAM_SPACE["reg_lambda"]
            ),
            "objective": "multiclass",
            "num_class": 3,
            "metric": "multi_logloss",
            "random_state": config.RANDOM_SEED,
            "verbose": -1,
        }

        model = lgb.LGBMClassifier(**params)
        cv = StratifiedKFold(n_splits=config.N_CV_FOLDS, shuffle=True, random_state=config.RANDOM_SEED)
        scores = cross_val_score(
            model, X_train, y_train,
            cv=cv,
            scoring="f1_macro",
            fit_params={"sample_weight": sample_weights},
        )
        return scores.mean()

    return objective


def tune_model(
    model_name: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    sample_weights: np.ndarray,
) -> Dict[str, Any]:
    """
    Run Optuna hyperparameter tuning for a given model.

    Parameters
    ----------
    model_name : str
        'xgboost' or 'lightgbm'
    X_train, y_train : arrays
    sample_weights : array

    Returns
    -------
    dict
        Best hyperparameters.
    """
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    if model_name == "xgboost":
        objective = _create_xgb_objective(X_train, y_train, sample_weights)
    elif model_name == "lightgbm":
        objective = _create_lgbm_objective(X_train, y_train, sample_weights)
    else:
        raise ValueError(f"Unknown model: {model_name}")

    study = optuna.create_study(
        direction="maximize",
        study_name=f"{model_name}_tuning",
    )
    study.optimize(objective, n_trials=config.OPTUNA_N_TRIALS, show_progress_bar=True)

    logger.info(f"{model_name} best trial: F1={study.best_value:.4f}")
    logger.info(f"{model_name} best params: {study.best_params}")

    return study.best_params


# ──────────────────────────────────────────────────────────────
# 3. MODEL TRAINING & CALIBRATION
# ──────────────────────────────────────────────────────────────


def train_xgboost(
    best_params: Dict[str, Any],
    X_train: np.ndarray,
    y_train: np.ndarray,
    sample_weights: np.ndarray,
) -> Any:
    """Train XGBoost with best params."""
    import xgboost as xgb

    params = {
        **best_params,
        "objective": "multi:softprob",
        "num_class": 3,
        "eval_metric": "mlogloss",
        "random_state": config.RANDOM_SEED,
        "use_label_encoder": False,
        "verbosity": 0,
    }

    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train, sample_weight=sample_weights)
    return model


def train_lightgbm(
    best_params: Dict[str, Any],
    X_train: np.ndarray,
    y_train: np.ndarray,
    sample_weights: np.ndarray,
) -> Any:
    """Train LightGBM with best params."""
    import lightgbm as lgb

    params = {
        **best_params,
        "objective": "multiclass",
        "num_class": 3,
        "metric": "multi_logloss",
        "random_state": config.RANDOM_SEED,
        "verbose": -1,
    }

    model = lgb.LGBMClassifier(**params)
    model.fit(X_train, y_train, sample_weight=sample_weights)
    return model


def calibrate_model(model: Any, X_train: np.ndarray, y_train: np.ndarray) -> Any:
    """Apply isotonic probability calibration."""
    calibrated = CalibratedClassifierCV(
        estimator=model,
        method="isotonic",
        cv=3,
    )
    calibrated.fit(X_train, y_train)
    logger.info("Probability calibration complete (isotonic, 3-fold)")
    return calibrated


# ──────────────────────────────────────────────────────────────
# 4. EVALUATION
# ──────────────────────────────────────────────────────────────


def evaluate_model(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    model_name: str,
) -> Dict[str, Any]:
    """
    Evaluate a trained model on test data.

    Returns
    -------
    dict
        Metrics dictionary.
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    # Core metrics
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")
    logloss = log_loss(y_test, y_proba)

    # ROC-AUC (one-vs-rest)
    try:
        roc_auc = roc_auc_score(y_test, y_proba, multi_class="ovr", average="macro")
    except ValueError:
        roc_auc = 0.0

    # Classification report
    report = classification_report(
        y_test, y_pred,
        target_names=["Green", "Amber", "Red"],
        output_dict=True,
    )

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "model_name": model_name,
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "log_loss": round(logloss, 4),
        "roc_auc_ovr": round(roc_auc, 4),
        "classification_report": report,
        "confusion_matrix": cm,
    }

    logger.info(f"\n{'=' * 50}")
    logger.info(f"  {model_name} EVALUATION RESULTS")
    logger.info(f"{'=' * 50}")
    logger.info(f"  Accuracy:    {accuracy:.4f}")
    logger.info(f"  Macro F1:    {macro_f1:.4f}")
    logger.info(f"  Weighted F1: {weighted_f1:.4f}")
    logger.info(f"  Log Loss:    {logloss:.4f}")
    logger.info(f"  ROC-AUC:     {roc_auc:.4f}")
    logger.info(f"  Confusion Matrix:\n{np.array(cm)}")
    logger.info(f"{'=' * 50}")

    return metrics


# ──────────────────────────────────────────────────────────────
# 5. MAIN PIPELINE
# ──────────────────────────────────────────────────────────────


def run_training() -> Dict[str, Any]:
    """
    Execute the full training pipeline.

    Returns
    -------
    dict
        Training results including metrics and best model name.
    """
    ensure_dirs()

    logger.info("=" * 60)
    logger.info("STARTING MODEL TRAINING PIPELINE")
    logger.info("=" * 60)

    # Prepare data
    df, feature_cols = prepare_data()
    X_train, X_test, y_train, y_test = split_data(df, feature_cols)

    # Compute sample weights
    y_train_series = pd.Series(y_train)
    sample_weights = get_sample_weights(y_train_series)

    # ── Train XGBoost ──
    logger.info("-" * 50)
    logger.info("TUNING XGBOOST...")
    logger.info("-" * 50)
    xgb_best_params = tune_model("xgboost", X_train, y_train, sample_weights)
    xgb_model = train_xgboost(xgb_best_params, X_train, y_train, sample_weights)
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test, "XGBoost")

    # ── Train LightGBM ──
    logger.info("-" * 50)
    logger.info("TUNING LIGHTGBM...")
    logger.info("-" * 50)
    lgbm_best_params = tune_model("lightgbm", X_train, y_train, sample_weights)
    lgbm_model = train_lightgbm(lgbm_best_params, X_train, y_train, sample_weights)
    lgbm_metrics = evaluate_model(lgbm_model, X_test, y_test, "LightGBM")

    # ── Select best model ──
    if xgb_metrics["macro_f1"] >= lgbm_metrics["macro_f1"]:
        best_model = xgb_model
        best_name = "XGBoost"
        best_metrics = xgb_metrics
        best_params = xgb_best_params
    else:
        best_model = lgbm_model
        best_name = "LightGBM"
        best_metrics = lgbm_metrics
        best_params = lgbm_best_params

    logger.info(f"\nBest model: {best_name} (Macro F1: {best_metrics['macro_f1']:.4f})")

    # ── Calibrate probabilities ──
    logger.info("-" * 50)
    logger.info("CALIBRATING PROBABILITIES...")
    logger.info("-" * 50)
    calibrated_model = calibrate_model(best_model, X_train, y_train)

    # Evaluate calibrated model
    calibrated_metrics = evaluate_model(calibrated_model, X_test, y_test, f"{best_name} (Calibrated)")

    # ── Save artifacts ──
    save_artifact(calibrated_model, config.MODEL_PATH)
    logger.info(f"Saved model to: {config.MODEL_PATH}")

    # Save label encoder info
    save_artifact(config.LABEL_MAP, config.LABEL_ENCODER_PATH)

    # Save all metrics
    all_metrics = {
        "best_model": best_name,
        "best_params": best_params,
        "xgboost": xgb_metrics,
        "lightgbm": lgbm_metrics,
        "calibrated": calibrated_metrics,
        "feature_count": len(feature_cols),
        "train_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
    }
    save_json(all_metrics, config.TRAINING_METRICS_PATH)
    logger.info(f"Saved metrics to: {config.TRAINING_METRICS_PATH}")

    logger.info("=" * 60)
    logger.info("TRAINING PIPELINE COMPLETE")
    logger.info("=" * 60)

    return all_metrics


if __name__ == "__main__":
    results = run_training()
    print(f"\nBest model: {results['best_model']}")
    print(f"Calibrated Macro F1: {results['calibrated']['macro_f1']}")
    print(f"Calibrated Accuracy: {results['calibrated']['accuracy']}")
