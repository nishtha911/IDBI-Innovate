"""
ML Pipeline Configuration
=========================
Central configuration for the MSME Financial Health Scoring ML pipeline.
All paths, hyperparameters, thresholds, and feature definitions live here.
"""

import os
from pathlib import Path
from typing import Dict, Any

# ──────────────────────────────────────────────────────────────
# 1. PATH CONFIGURATION
# ──────────────────────────────────────────────────────────────

# Project root (parent of ml/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ML_ROOT = Path(__file__).resolve().parent

# Dataset paths
DATASET_DIR = PROJECT_ROOT / "Dataset"
RAW_DATA_PATHS = {
    "profiles": DATASET_DIR / "msme_profiles.csv",
    "gst": DATASET_DIR / "msme_gst_data.csv",
    "upi": DATASET_DIR / "msme_upi_data.csv",
    "epfo": DATASET_DIR / "msme_epfo_data.csv",
    "master_features": DATASET_DIR / "msme_master_features.csv",
}

# Output paths
DATA_DIR = ML_ROOT / "data"
SAVED_MODELS_DIR = ML_ROOT / "saved_models"
NOTEBOOKS_DIR = ML_ROOT / "notebooks"

PROCESSED_FEATURES_PATH = DATA_DIR / "processed_features.csv"

# Model artifacts
MODEL_PATH = SAVED_MODELS_DIR / "model.pkl"
SCALER_PATH = SAVED_MODELS_DIR / "scaler.pkl"
FEATURE_NAMES_PATH = SAVED_MODELS_DIR / "feature_names.json"
LABEL_ENCODER_PATH = SAVED_MODELS_DIR / "label_encoder.pkl"
TRAINING_METRICS_PATH = SAVED_MODELS_DIR / "training_metrics.json"

# ──────────────────────────────────────────────────────────────
# 2. TARGET CONFIGURATION
# ──────────────────────────────────────────────────────────────

TARGET_COLUMN = "risk_target"
COHORT_COLUMN = "simulated_cohort"
BUSINESS_ID_COLUMN = "business_id"

# Label mapping: lower number = lower risk
LABEL_MAP: Dict[str, int] = {
    "Green": 0,
    "Amber": 1,
    "Red": 2,
}

INVERSE_LABEL_MAP: Dict[int, str] = {v: k for k, v in LABEL_MAP.items()}

# ──────────────────────────────────────────────────────────────
# 3. SCORING THRESHOLDS
# ──────────────────────────────────────────────────────────────

SCORE_THRESHOLDS = {
    "green_min": 75,
    "amber_min": 50,
    # Red: < 50
}

# Weights for probability-weighted health score:
# score = P(Green)*100 + P(Amber)*50 + P(Red)*0
SCORE_WEIGHTS = {0: 100.0, 1: 50.0, 2: 0.0}

# ──────────────────────────────────────────────────────────────
# 4. TRAINING CONFIGURATION
# ──────────────────────────────────────────────────────────────

RANDOM_SEED = 42
TEST_SIZE = 0.20
N_CV_FOLDS = 5
OPTUNA_N_TRIALS = 50

# Columns to exclude from features (identifiers, targets, metadata)
EXCLUDE_COLUMNS = [
    "business_id",
    "business_name",
    "simulated_cohort",
    "risk_target",
]

# Categorical columns from profiles
CATEGORICAL_COLUMNS = [
    "industry_sector",
    "entity_type",
    "kyc_status",
]

# Correlation threshold for feature selection
CORRELATION_THRESHOLD = 0.95

# Winsorize percentiles for outlier capping
WINSORIZE_LOWER = 0.01
WINSORIZE_UPPER = 0.99

# ──────────────────────────────────────────────────────────────
# 5. HYPERPARAMETER SEARCH SPACES
# ──────────────────────────────────────────────────────────────

XGBOOST_PARAM_SPACE: Dict[str, Any] = {
    "n_estimators": (100, 500),
    "max_depth": (3, 8),
    "learning_rate": (0.01, 0.3),
    "subsample": (0.6, 1.0),
    "colsample_bytree": (0.6, 1.0),
    "min_child_weight": (1, 10),
    "gamma": (0.0, 5.0),
    "reg_alpha": (0.0, 10.0),
    "reg_lambda": (0.0, 10.0),
}

LIGHTGBM_PARAM_SPACE: Dict[str, Any] = {
    "n_estimators": (100, 500),
    "max_depth": (3, 8),
    "learning_rate": (0.01, 0.3),
    "subsample": (0.6, 1.0),
    "colsample_bytree": (0.6, 1.0),
    "min_child_samples": (5, 50),
    "num_leaves": (15, 127),
    "reg_alpha": (0.0, 10.0),
    "reg_lambda": (0.0, 10.0),
}

# ──────────────────────────────────────────────────────────────
# 6. FEATURE NAME MAPPING (for human-readable explainability)
# ──────────────────────────────────────────────────────────────

FEATURE_DISPLAY_NAMES: Dict[str, str] = {
    # Revenue features
    "revenue_mean": "Average Monthly Revenue",
    "revenue_std": "Revenue Standard Deviation",
    "revenue_cv": "Revenue Volatility (CV)",
    "revenue_trend_slope": "Revenue Growth Trend",
    "revenue_last3_avg": "Recent 3-Month Avg Revenue",
    "revenue_first3_avg": "Initial 3-Month Avg Revenue",
    "revenue_recent_vs_early": "Recent vs. Early Revenue Ratio",
    "revenue_min": "Minimum Monthly Revenue",
    "revenue_max": "Maximum Monthly Revenue",
    # Compliance features
    "total_filing_delay_days": "Total GST Filing Delay (Days)",
    "avg_delay_per_month": "Avg Monthly Filing Delay",
    "late_filing_count": "Late Filing Count",
    "late_filing_ratio": "Late Filing Rate",
    "itc_claim_ratio": "ITC Claim Ratio",
    "epfo_delayed_ratio": "EPFO Delayed Payment Rate",
    "epfo_ontime_streak": "EPFO On-Time Streak (Months)",
    # Cash flow features
    "avg_upi_inflow": "Avg Monthly UPI Inflow",
    "avg_upi_outflow": "Avg Monthly UPI Outflow",
    "net_cashflow_avg": "Avg Net Cash Flow",
    "inflow_outflow_ratio": "Inflow-to-Outflow Ratio",
    "inflow_trend_slope": "UPI Inflow Growth Trend",
    "avg_ticket_size": "Avg UPI Transaction Size",
    "avg_counterparties": "Avg Unique Counterparties",
    "avg_failed_txn_rate": "Avg Failed Transaction Rate (%)",
    "avg_txn_count": "Avg Monthly Transaction Count",
    # Growth features
    "yoy_growth_pct": "Year-over-Year Revenue Growth (%)",
    "employee_growth_rate": "Employee Growth Rate",
    "pf_contribution_growth": "PF Contribution Growth",
    "avg_employee_count": "Avg Active Employees",
    # Profile features
    "vintage_months": "Business Vintage (Months)",
    "location_tier": "City Tier",
    "kyc_verified": "KYC Verified",
}

# ──────────────────────────────────────────────────────────────
# 7. LOGGING
# ──────────────────────────────────────────────────────────────

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
