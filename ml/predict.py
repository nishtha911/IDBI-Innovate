"""
Model Inference Module
======================
Primary integration point for the backend.
Provides the predict(data) function that processes raw JSON payloads,
transforms them into model-ready features, runs the calibrated model,
and returns structured health score, risk categories, PD, confidence,
and explanation reasons.

Usage:
    from ml.predict import predict
    results = predict(msme_data)
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Union

import numpy as np
import pandas as pd

# Allow running as script or module
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml import config
from ml.utils import setup_logging, load_artifact, load_json
from ml.explain import explain_prediction, get_top_risk_factors

logger = setup_logging("predict")


# ──────────────────────────────────────────────────────────────
# 1. ARTIFACTS LOADERS (LAZY SINGLETON PATTERN)
# ──────────────────────────────────────────────────────────────

_MODEL = None
_SCALER = None
_FEATURE_NAMES = None
_LABEL_ENCODER = None


def _load_model_artifacts():
    """Load model, scaler, feature names, and label encoder once."""
    global _MODEL, _SCALER, _FEATURE_NAMES, _LABEL_ENCODER
    if _MODEL is None:
        try:
            _MODEL = load_artifact(config.MODEL_PATH)
            _SCALER = load_artifact(config.SCALER_PATH)
            _FEATURE_NAMES = load_json(config.FEATURE_NAMES_PATH)
            _LABEL_ENCODER = load_artifact(config.LABEL_ENCODER_PATH)
            logger.info("Successfully loaded all ML model artifacts.")
        except FileNotFoundError as e:
            logger.error(
                f"Artifact file missing: {e}. Make sure you run training first "
                "to generate the model files."
            )
            raise


# ──────────────────────────────────────────────────────────────
# 2. FEATURE EXTRACTION FOR SINGLE BUSINESS
# ──────────────────────────────────────────────────────────────


def _linear_trend_slope(values: np.ndarray) -> float:
    """Compute the slope of a linear fit over values."""
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values))
    try:
        slope, _ = np.polyfit(x, values, 1)
        return float(slope)
    except (np.linalg.LinAlgError, ValueError):
        return 0.0


def _max_consecutive(values: List[str], target: str) -> int:
    """Count the maximum consecutive occurrences of a target value."""
    max_count = 0
    current = 0
    for v in values:
        if v == target:
            current += 1
            max_count = max(max_count, current)
        else:
            current = 0
    return max_count


def extract_features_from_dict(
    gst_data: Dict[str, Any],
    upi_data: Dict[str, Any],
    epfo_data: Dict[str, Any],
    bank_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Process raw nested dictionaries into aggregated numeric and categorical features
    matching the training dataset logic.
    """
    features = {}

    # ────────────────────────────────────────────────────────
    # 2.1 Profile / Bank KYC metadata
    # ────────────────────────────────────────────────────────
    # Extract sector from gst or bank
    sector = gst_data.get("sector") or gst_data.get("industry_sector") or "Services"
    features["industry_sector"] = sector

    # Entity type & vintage (default to safe baselines if missing from mock schemas)
    features["entity_type"] = gst_data.get("entity_type") or "Private Limited"
    features["vintage_months"] = int(gst_data.get("vintage_months") or 60)
    features["location_tier"] = int(bank_data.get("location_tier") or 2)

    # KYC verified check
    kyc_status = bank_data.get("kyc_status") or "Pending"
    features["kyc_verified"] = 1 if kyc_status == "Verified" else 0

    # ────────────────────────────────────────────────────────
    # 2.2 GST turnover and filing aggregations
    # ────────────────────────────────────────────────────────
    turnover_history = gst_data.get("turnover_history") or []
    is_registered = gst_data.get("is_registered", False)

    # Extract turnovers (or credit proxies from bank statements if unregistered)
    if is_registered and turnover_history:
        turnovers = [float(t.get("turnover", 0)) for t in turnover_history]
    else:
        bank_metrics = bank_data.get("monthly_metrics") or []
        turnovers = [float(m.get("total_credits", 0)) for m in bank_metrics]

    if turnovers:
        turnovers_arr = np.array(turnovers)
        features["revenue_mean"] = float(np.mean(turnovers_arr))
        features["revenue_std"] = float(np.std(turnovers_arr))
        features["revenue_min"] = float(np.min(turnovers_arr))
        features["revenue_max"] = float(np.max(turnovers_arr))
        features["revenue_cv"] = (
            features["revenue_std"] / features["revenue_mean"]
            if features["revenue_mean"] > 0
            else 0.0
        )
        features["revenue_trend_slope"] = _linear_trend_slope(turnovers_arr)

        # Recent 3 months vs first 3 months averages
        k = min(3, len(turnovers_arr))
        first_k = float(np.mean(turnovers_arr[:k])) if k > 0 else 0.0
        last_k = float(np.mean(turnovers_arr[-k:])) if k > 0 else 0.0
        features["revenue_first3_avg"] = first_k
        features["revenue_last3_avg"] = last_k
        features["revenue_recent_vs_early"] = (
            last_k / first_k if first_k > 0 else 1.0
        )
    else:
        features["revenue_mean"] = 0.0
        features["revenue_std"] = 0.0
        features["revenue_min"] = 0.0
        features["revenue_max"] = 0.0
        features["revenue_cv"] = 0.0
        features["revenue_trend_slope"] = 0.0
        features["revenue_first3_avg"] = 0.0
        features["revenue_last3_avg"] = 0.0
        features["revenue_recent_vs_early"] = 1.0

    # GST Filings
    filing_history = gst_data.get("filing_history") or []
    if filing_history:
        total_delay = sum(int(f.get("filing_delay_days", 0)) for f in filing_history)
        on_time_count = sum(
            1 for f in filing_history if f.get("filed_on_time", False)
        )
        total_filings = len(filing_history)
        features["total_filing_delay_days"] = float(total_delay)
        features["avg_delay_per_month"] = total_delay / total_filings
        features["late_filing_count"] = float(total_filings - on_time_count)
        features["late_filing_ratio"] = (total_filings - on_time_count) / total_filings
    else:
        # Default to clean baseline for unregistered/no history
        features["total_filing_delay_days"] = 0.0
        features["avg_delay_per_month"] = 0.0
        features["late_filing_count"] = 0.0
        features["late_filing_ratio"] = 0.0

    # ITC Claim Ratio
    itcs = [float(f.get("itc_claimed_inr", 0)) for f in filing_history]
    taxes = [float(f.get("tax_paid_inr", 0)) for f in filing_history]
    total_itc = sum(itcs)
    total_tax = sum(taxes)
    features["itc_claim_ratio"] = (
        total_itc / total_tax if total_tax > 0 else 0.0
    )

    # ────────────────────────────────────────────────────────
    # 2.3 UPI cash flow aggregations
    # ────────────────────────────────────────────────────────
    upi_metrics = upi_data.get("monthly_metrics") or []
    if upi_metrics:
        inflows = [float(m.get("volume", 0) or m.get("total_inflow_volume_inr", 0)) for m in upi_metrics]
        outflows = [float(m.get("total_outflow_volume_inr", 0)) for m in upi_metrics]
        tickets = [float(m.get("avg_transaction_size", 0) or m.get("average_ticket_size_inr", 0)) for m in upi_metrics]
        cps = [float(m.get("unique_counterparties_in", 0)) for m in upi_metrics]
        failures = [float(m.get("failed_transaction_rate_pct", 0)) for m in upi_metrics]
        counts = [float(m.get("transaction_count", 0) or m.get("inflow_transaction_count", 0)) for m in upi_metrics]

        features["avg_upi_inflow"] = float(np.mean(inflows))
        features["avg_upi_outflow"] = float(np.mean(outflows))
        features["avg_ticket_size"] = float(np.mean(tickets))
        features["avg_counterparties"] = float(np.mean(cps))
        features["avg_failed_txn_rate"] = float(np.mean(failures))
        features["avg_txn_count"] = float(np.mean(counts))

        features["net_cashflow_avg"] = (
            features["avg_upi_inflow"] - features["avg_upi_outflow"]
        )
        features["inflow_outflow_ratio"] = (
            features["avg_upi_inflow"] / features["avg_upi_outflow"]
            if features["avg_upi_outflow"] > 0
            else 1.0
        )
        features["inflow_trend_slope"] = _linear_trend_slope(np.array(inflows))
    else:
        features["avg_upi_inflow"] = 0.0
        features["avg_upi_outflow"] = 0.0
        features["avg_ticket_size"] = 0.0
        features["avg_counterparties"] = 0.0
        features["avg_failed_txn_rate"] = 0.0
        features["avg_txn_count"] = 0.0
        features["net_cashflow_avg"] = 0.0
        features["inflow_outflow_ratio"] = 1.0
        features["inflow_trend_slope"] = 0.0

    # Customer retention & YoY growth
    features["yoy_growth_pct"] = float(upi_data.get("yoy_growth_pct") or 5.0)

    # ────────────────────────────────────────────────────────
    # 2.4 EPFO payroll compliance aggregations
    # ────────────────────────────────────────────────────────
    epfo_history = epfo_data.get("history") or []
    if epfo_history:
        employees = [int(h.get("employee_count", 0) or h.get("active_employee_count", 0)) for h in epfo_history]
        contributions = [float(h.get("amount_paid", 0) or h.get("total_pf_contribution_inr", 0)) for h in epfo_history]
        statuses = [h.get("payment_status") or h.get("compliance_status") for h in epfo_history]

        features["avg_employee_count"] = float(np.mean(employees))

        # Employee count trend
        k = min(3, len(employees))
        first_emp = float(np.mean(employees[:k])) if k > 0 else 1.0
        last_emp = float(np.mean(employees[-k:])) if k > 0 else 1.0
        features["employee_growth_rate"] = (
            (last_emp - first_emp) / first_emp if first_emp > 0 else 0.0
        )

        # Contribution growth
        first_contrib = float(np.mean(contributions[:k])) if k > 0 else 1.0
        last_contrib = float(np.mean(contributions[-k:])) if k > 0 else 1.0
        features["pf_contribution_growth"] = (
            (last_contrib - first_contrib) / first_contrib if first_contrib > 0 else 0.0
        )

        # EPFO Compliance
        late_or_unpaid = sum(1 for s in statuses if s in ["Paid_Late", "Delayed", "Late", "Unpaid"])
        features["epfo_delayed_ratio"] = late_or_unpaid / len(statuses)
        features["epfo_ontime_streak"] = float(
            _max_consecutive(statuses, "Paid_On_Time") or _max_consecutive(statuses, "On-Time")
        )
    else:
        features["avg_employee_count"] = 0.0
        features["employee_growth_rate"] = 0.0
        features["pf_contribution_growth"] = 0.0
        features["epfo_delayed_ratio"] = 0.0
        features["epfo_ontime_streak"] = 12.0  # Assumed clean baseline

    return features


# ──────────────────────────────────────────────────────────────
# 3. CORE PREDICT INTERFACE
# ──────────────────────────────────────────────────────────────


def predict(
    data: Dict[str, Any],
    upi_data: Dict[str, Any] = None,
    epfo_data: Dict[str, Any] = None,
    bank_data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Accepts raw MSME records, aggregates features, scales them,
    and runs the prediction.

    Parameters
    ----------
    data : dict
        Either a unified dictionary containing keys: 'gst', 'upi', 'epfo', 'bank',
        OR the raw 'gst' dictionary if upi_data, epfo_data, and bank_data are passed individually.
    """
    # 1. Resolve unified dict or separate arguments
    if upi_data is not None and epfo_data is not None and bank_data is not None:
        gst_dict = data
        upi_dict = upi_data
        epfo_dict = epfo_data
        bank_dict = bank_data
    else:
        gst_dict = data.get("gst") or {}
        upi_dict = data.get("upi") or {}
        epfo_dict = data.get("epfo") or {}
        bank_dict = data.get("bank") or {}

    # 2. Extract features
    raw_features = extract_features_from_dict(
        gst_dict, upi_dict, epfo_dict, bank_dict
    )

    # 3. Lazy load model artifacts
    _load_model_artifacts()

    # 4. Align features with final feature column order (including one-hot cols)
    # Initialize zero feature vector with final model structure
    feature_row = pd.Series(0.0, index=_FEATURE_NAMES)

    # Fill numeric variables directly
    for col in _FEATURE_NAMES:
        if col in raw_features:
            feature_row[col] = float(raw_features[col])

    # Fill categorical one-hot values
    # e.g. for industry_sector='Retail', set industry_sector_Retail=1.0
    for cat_col in config.CATEGORICAL_COLUMNS:
        val = raw_features.get(cat_col)
        if val is not None:
            one_hot_col = f"{cat_col}_{val}"
            if one_hot_col in feature_row.index:
                feature_row[one_hot_col] = 1.0

    # Convert to 2D DataFrame for transform/predict
    features_df = pd.DataFrame([feature_row])

    # 5. Scaling (StandardScaler)
    # Scaler was fitted on all features (including one-hot encoded fields)
    features_df[_FEATURE_NAMES] = _SCALER.transform(features_df[_FEATURE_NAMES])

    X = features_df.values

    # 6. Model Prediction & Probabilities
    pred_class_idx = int(_MODEL.predict(X)[0])
    probas = _MODEL.predict_proba(X)[0]  # probabilities for Green, Amber, Red

    # Mapping class probabilities
    class_probs = {
        config.INVERSE_LABEL_MAP[i]: float(probas[i])
        for i in range(len(probas))
    }

    # Strictest interpretation of Probability of Default (PD) is P(Red)
    probability_of_default = float(class_probs.get("Red", 0.0))

    # Calculate Probability-Weighted Score (0-100)
    # score = P(Green)*100 + P(Amber)*50 + P(Red)*0
    composite_score = float(
        probas[0] * config.SCORE_WEIGHTS[0] +
        probas[1] * config.SCORE_WEIGHTS[1] +
        probas[2] * config.SCORE_WEIGHTS[2]
    )
    composite_score = round(composite_score, 2)

    # Resolve risk category from score thresholds
    if composite_score >= config.SCORE_THRESHOLDS["green_min"]:
        category = "Green"
        recommendation = "Approve; offer best-rate credit products."
    elif composite_score >= config.SCORE_THRESHOLDS["amber_min"]:
        category = "Amber"
        recommendation = "Conditional approval; require additional documentation or co-guarantor."
    else:
        category = "Red"
        recommendation = "Decline or refer to SME specialist team."

    # 7. Confidence Score based on data completeness
    has_gst = 1 if gst_dict.get("turnover_history") else 0
    has_upi = 1 if upi_dict.get("monthly_metrics") else 0
    has_epfo = 1 if epfo_dict.get("history") else 0
    has_bank = 1 if bank_dict.get("monthly_metrics") else 0
    confidence_score = ((has_gst + has_upi + has_epfo + has_bank) / 4.0) * 100.0
    if has_bank and confidence_score < 50.0:
        confidence_score = 50.0

    # 8. SHAP Explainability Reasons
    explanation = explain_prediction(_MODEL, X[0], _FEATURE_NAMES)
    top_risk_factors = get_top_risk_factors(
        explanation["shap_values"], _FEATURE_NAMES, pred_class_idx
    )

    # 9. Format Breakdown (subcomponent score approximations for API compatibility)
    # We approximate component-level health using specific probas or sub-features
    breakdown = {
        "revenue_stability": round(float(class_probs.get("Green", 0.0) * 100.0), 2),
        "tax_compliance": round(float((1.0 - raw_features.get("late_filing_ratio", 0.0)) * 100.0), 2),
        "cash_flow_health": round(float((1.0 - raw_features.get("avg_failed_txn_rate", 0.0)/100.0) * 100.0), 2),
        "growth_trajectory": round(float(max(0.0, min(100.0, 50.0 + raw_features.get("yoy_growth_pct", 0.0)))), 2),
    }

    # Recommended Credit Limit (API compatibility)
    # Base on monthly revenue credit proxy (revenue_mean)
    avg_monthly_turnover = raw_features.get("revenue_mean", 0.0)
    credit_limit = 0
    if category == "Green":
        factor = 1.5 + (1.0 * (composite_score - config.SCORE_THRESHOLDS["green_min"]) / 25.0)
        credit_limit = int((avg_monthly_turnover * factor) // 10000 * 10000)
    elif category == "Amber":
        factor = 0.4 + (0.6 * (composite_score - config.SCORE_THRESHOLDS["amber_min"]) / 25.0)
        credit_limit = int((avg_monthly_turnover * factor) // 10000 * 10000)

    return {
        "composite_score": composite_score,
        "category": category,
        "recommendation": recommendation,
        "confidence_score": round(confidence_score, 2),
        "probability_of_default": round(probability_of_default, 4),
        "recommended_credit_limit_inr": max(0, credit_limit),
        "breakdown": breakdown,
        "class_probabilities": class_probs,
        "top_risk_factors": top_risk_factors,
    }


if __name__ == "__main__":
    # Test prediction with mock data store if file runs directly
    try:
        from app.services.mock_data_store import MockDataStore
        logger.info("MockDataStore imported successfully.")
        
        test_profiles = ["raj_vendor", "priya_saas", "default_high_risk"]
        for pid in test_profiles:
            profile = MockDataStore.get_profile(pid)
            res = predict(profile)
            print(f"\nMSME ID: {pid}")
            print(f"  Score:         {res['composite_score']}")
            print(f"  Category:      {res['category']}")
            print(f"  PD (P(Red)):   {res['probability_of_default']:.4f}")
            print(f"  Top Risk Factor: {res['top_risk_factors'][0]['display_name']} ({res['top_risk_factors'][0]['direction']})")
    except ImportError:
        logger.warning("Could not import app.services.mock_data_store for tests.")
