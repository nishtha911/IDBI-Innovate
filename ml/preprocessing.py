"""
Data Preprocessing Module
=========================
Loads raw CSVs (profiles, GST, UPI, EPFO), aggregates monthly time-series
into per-MSME feature vectors, handles missing values and outliers,
and exports a single processed DataFrame ready for feature engineering.

Usage:
    python -m ml.preprocessing
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow running as script or module
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml import config
from ml.utils import setup_logging, ensure_dirs

logger = setup_logging("preprocessing")


# ──────────────────────────────────────────────────────────────
# 1. DATA LOADING
# ──────────────────────────────────────────────────────────────


def load_raw_data() -> dict:
    """
    Load all raw CSV files into DataFrames.

    Returns
    -------
    dict
        Keys: 'profiles', 'gst', 'upi', 'epfo', 'master_features'
    """
    data = {}
    for name, path in config.RAW_DATA_PATHS.items():
        if not path.exists():
            logger.warning(f"Data file not found: {path}")
            continue
        df = pd.read_csv(path)
        logger.info(f"Loaded {name}: {df.shape[0]} rows, {df.shape[1]} columns")
        data[name] = df
    return data


# ──────────────────────────────────────────────────────────────
# 2. TIME-SERIES AGGREGATION
# ──────────────────────────────────────────────────────────────


def _linear_trend_slope(series: pd.Series) -> float:
    """Compute the slope of a linear fit over the series."""
    if len(series) < 2:
        return 0.0
    x = np.arange(len(series))
    try:
        slope, _ = np.polyfit(x, series.values, 1)
        return float(slope)
    except (np.linalg.LinAlgError, ValueError):
        return 0.0


def _max_consecutive(series: pd.Series, value: str) -> int:
    """Count the maximum consecutive occurrences of `value` in a series."""
    max_count = 0
    current = 0
    for v in series:
        if v == value:
            current += 1
            max_count = max(max_count, current)
        else:
            current = 0
    return max_count


def aggregate_gst(df_gst: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate monthly GST data per business.

    Features produced:
    - revenue_mean, revenue_std, revenue_cv, revenue_min, revenue_max
    - revenue_trend_slope
    - revenue_last3_avg, revenue_first3_avg, revenue_recent_vs_early
    - total_filing_delay_days, avg_delay_per_month
    - late_filing_count, late_filing_ratio
    - itc_claim_ratio
    """
    bid = config.BUSINESS_ID_COLUMN

    # Sort by business_id and time
    df_gst = df_gst.copy()
    df_gst["date"] = pd.to_datetime(
        df_gst["year"].astype(str) + "-" + df_gst["month"].astype(str),
        format="%Y-%m",
    )
    df_gst = df_gst.sort_values([bid, "date"])

    agg = df_gst.groupby(bid).agg(
        revenue_mean=("gross_turnover_inr", "mean"),
        revenue_std=("gross_turnover_inr", "std"),
        revenue_min=("gross_turnover_inr", "min"),
        revenue_max=("gross_turnover_inr", "max"),
        total_filing_delay_days=("filing_delay_days", "sum"),
        avg_delay_per_month=("filing_delay_days", "mean"),
        late_filing_count=("filing_status", lambda x: (x == "Late").sum()),
        total_tax_paid=("tax_paid_inr", "sum"),
        total_itc_claimed=("itc_claimed_inr", "sum"),
    ).reset_index()

    # Revenue CV
    agg["revenue_cv"] = agg["revenue_std"] / agg["revenue_mean"].replace(0, np.nan)
    agg["revenue_cv"] = agg["revenue_cv"].fillna(0.0)

    # Late filing ratio
    month_counts = df_gst.groupby(bid).size().reset_index(name="n_months")
    agg = agg.merge(month_counts, on=bid)
    agg["late_filing_ratio"] = agg["late_filing_count"] / agg["n_months"]

    # ITC claim ratio (ITC / tax paid)
    agg["itc_claim_ratio"] = agg["total_itc_claimed"] / agg["total_tax_paid"].replace(0, np.nan)
    agg["itc_claim_ratio"] = agg["itc_claim_ratio"].fillna(0.0)

    # Revenue trend slope
    trend_slopes = (
        df_gst.groupby(bid)["gross_turnover_inr"]
        .apply(_linear_trend_slope)
        .reset_index(name="revenue_trend_slope")
    )
    agg = agg.merge(trend_slopes, on=bid)

    # Recent vs early revenue
    def _recent_vs_early(group: pd.DataFrame) -> pd.Series:
        vals = group["gross_turnover_inr"].values
        n = len(vals)
        k = min(3, n)
        first_k = vals[:k].mean() if k > 0 else 0
        last_k = vals[-k:].mean() if k > 0 else 0
        ratio = last_k / first_k if first_k > 0 else 1.0
        return pd.Series({
            "revenue_first3_avg": first_k,
            "revenue_last3_avg": last_k,
            "revenue_recent_vs_early": ratio,
        })

    recent_early = df_gst.groupby(bid).apply(_recent_vs_early).reset_index()
    agg = agg.merge(recent_early, on=bid)

    # Drop intermediate columns
    agg = agg.drop(columns=["total_tax_paid", "total_itc_claimed", "n_months"], errors="ignore")

    logger.info(f"GST aggregation: {agg.shape[1]} features for {agg.shape[0]} businesses")
    return agg


def aggregate_upi(df_upi: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate monthly UPI data per business.

    Features produced:
    - avg_upi_inflow, avg_upi_outflow, net_cashflow_avg
    - inflow_outflow_ratio, inflow_trend_slope
    - avg_ticket_size, avg_counterparties, avg_failed_txn_rate
    - avg_txn_count
    """
    bid = config.BUSINESS_ID_COLUMN

    df_upi = df_upi.copy()
    df_upi["date"] = pd.to_datetime(
        df_upi["year"].astype(str) + "-" + df_upi["month"].astype(str),
        format="%Y-%m",
    )
    df_upi = df_upi.sort_values([bid, "date"])

    agg = df_upi.groupby(bid).agg(
        avg_upi_inflow=("total_inflow_volume_inr", "mean"),
        avg_upi_outflow=("total_outflow_volume_inr", "mean"),
        avg_ticket_size=("average_ticket_size_inr", "mean"),
        avg_counterparties=("unique_counterparties_in", "mean"),
        avg_failed_txn_rate=("failed_transaction_rate_pct", "mean"),
        avg_txn_count=("inflow_transaction_count", "mean"),
    ).reset_index()

    # Net cashflow
    agg["net_cashflow_avg"] = agg["avg_upi_inflow"] - agg["avg_upi_outflow"]

    # Inflow/outflow ratio
    agg["inflow_outflow_ratio"] = agg["avg_upi_inflow"] / agg["avg_upi_outflow"].replace(0, np.nan)
    agg["inflow_outflow_ratio"] = agg["inflow_outflow_ratio"].fillna(1.0)

    # Inflow trend
    inflow_trends = (
        df_upi.groupby(bid)["total_inflow_volume_inr"]
        .apply(_linear_trend_slope)
        .reset_index(name="inflow_trend_slope")
    )
    agg = agg.merge(inflow_trends, on=bid)

    logger.info(f"UPI aggregation: {agg.shape[1]} features for {agg.shape[0]} businesses")
    return agg


def aggregate_epfo(df_epfo: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate monthly EPFO data per business.

    Features produced:
    - avg_employee_count, employee_growth_rate
    - pf_contribution_growth
    - epfo_delayed_ratio, epfo_ontime_streak
    """
    bid = config.BUSINESS_ID_COLUMN

    df_epfo = df_epfo.copy()
    df_epfo["date"] = pd.to_datetime(
        df_epfo["year"].astype(str) + "-" + df_epfo["month"].astype(str),
        format="%Y-%m",
    )
    df_epfo = df_epfo.sort_values([bid, "date"])

    agg = df_epfo.groupby(bid).agg(
        avg_employee_count=("active_employee_count", "mean"),
    ).reset_index()

    # Employee growth rate (last quarter vs first quarter)
    def _employee_growth(group: pd.DataFrame) -> float:
        vals = group["active_employee_count"].values
        n = len(vals)
        k = min(3, n)
        first_k = vals[:k].mean() if k > 0 else 1
        last_k = vals[-k:].mean() if k > 0 else 1
        return (last_k - first_k) / first_k if first_k > 0 else 0.0

    emp_growth = (
        df_epfo.groupby(bid)
        .apply(_employee_growth)
        .reset_index(name="employee_growth_rate")
    )
    agg = agg.merge(emp_growth, on=bid)

    # PF contribution growth
    def _pf_growth(group: pd.DataFrame) -> float:
        vals = group["total_pf_contribution_inr"].values
        n = len(vals)
        k = min(3, n)
        first_k = vals[:k].mean() if k > 0 else 1
        last_k = vals[-k:].mean() if k > 0 else 1
        return (last_k - first_k) / first_k if first_k > 0 else 0.0

    pf_growth = (
        df_epfo.groupby(bid)
        .apply(_pf_growth)
        .reset_index(name="pf_contribution_growth")
    )
    agg = agg.merge(pf_growth, on=bid)

    # EPFO compliance
    delayed_ratio = (
        df_epfo.groupby(bid)["compliance_status"]
        .apply(lambda x: (x == "Delayed").sum() / len(x))
        .reset_index(name="epfo_delayed_ratio")
    )
    agg = agg.merge(delayed_ratio, on=bid)

    # Max consecutive on-time streak
    ontime_streak = (
        df_epfo.groupby(bid)["compliance_status"]
        .apply(lambda x: _max_consecutive(x, "On-Time"))
        .reset_index(name="epfo_ontime_streak")
    )
    agg = agg.merge(ontime_streak, on=bid)

    logger.info(f"EPFO aggregation: {agg.shape[1]} features for {agg.shape[0]} businesses")
    return agg


# ──────────────────────────────────────────────────────────────
# 3. PROFILE EXTRACTION
# ──────────────────────────────────────────────────────────────


def extract_profile_features(df_profiles: pd.DataFrame) -> pd.DataFrame:
    """
    Extract useful features from the profiles table.

    Features produced:
    - business_id, industry_sector, entity_type
    - vintage_months, kyc_verified, location_tier
    - simulated_cohort, risk_target
    """
    bid = config.BUSINESS_ID_COLUMN

    df = df_profiles[[
        bid, "industry_sector", "entity_type", "vintage_months",
        "kyc_status", "simulated_cohort",
    ]].copy()

    # Binary KYC
    df["kyc_verified"] = (df["kyc_status"] == "Verified").astype(int)
    df = df.drop(columns=["kyc_status"])

    # Location tier (handle the column name from json_normalize)
    if "location.tier" in df_profiles.columns:
        df["location_tier"] = df_profiles["location.tier"].values
    else:
        df["location_tier"] = 2  # default to tier 2

    # Target encoding
    df[config.TARGET_COLUMN] = df[config.COHORT_COLUMN].map(config.LABEL_MAP)

    logger.info(f"Profile features: {df.shape[1]} columns for {df.shape[0]} businesses")
    return df


# ──────────────────────────────────────────────────────────────
# 4. MERGE & CLEAN
# ──────────────────────────────────────────────────────────────


def merge_all_features(
    profile_df: pd.DataFrame,
    gst_df: pd.DataFrame,
    upi_df: pd.DataFrame,
    epfo_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge all feature DataFrames on business_id."""
    bid = config.BUSINESS_ID_COLUMN

    merged = profile_df.merge(gst_df, on=bid, how="left")
    merged = merged.merge(upi_df, on=bid, how="left")
    merged = merged.merge(epfo_df, on=bid, how="left")

    logger.info(f"Merged DataFrame: {merged.shape[0]} rows, {merged.shape[1]} columns")
    return merged


def winsorize_column(series: pd.Series, lower: float, upper: float) -> pd.Series:
    """Clip values to specified percentiles."""
    lo = series.quantile(lower)
    hi = series.quantile(upper)
    return series.clip(lo, hi)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values and outliers.

    - Numeric NaN → median imputation
    - Categorical NaN → mode imputation
    - Winsorize numeric columns at 1st/99th percentile
    """
    df = df.copy()

    # Identify column types (excluding non-feature columns)
    exclude = config.EXCLUDE_COLUMNS + ["business_id"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in exclude]

    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    cat_cols = [c for c in cat_cols if c not in exclude]

    # Impute numeric
    for col in numeric_cols:
        if df[col].isna().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.debug(f"Imputed {col} with median={median_val:.4f}")

    # Impute categorical
    for col in cat_cols:
        if df[col].isna().any():
            mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)
            logger.debug(f"Imputed {col} with mode={mode_val}")

    # Winsorize numeric features
    for col in numeric_cols:
        df[col] = winsorize_column(df[col], config.WINSORIZE_LOWER, config.WINSORIZE_UPPER)

    logger.info(f"Cleaned DataFrame: {df.isna().sum().sum()} remaining NaN values")
    return df


# ──────────────────────────────────────────────────────────────
# 5. MAIN PIPELINE
# ──────────────────────────────────────────────────────────────


def run_preprocessing() -> pd.DataFrame:
    """
    Execute the full preprocessing pipeline.

    Returns
    -------
    pd.DataFrame
        Processed features DataFrame with one row per MSME.
    """
    ensure_dirs()

    # Load raw data
    logger.info("=" * 60)
    logger.info("STARTING PREPROCESSING PIPELINE")
    logger.info("=" * 60)

    raw = load_raw_data()

    if "profiles" not in raw or "gst" not in raw or "upi" not in raw or "epfo" not in raw:
        raise FileNotFoundError(
            "One or more required data files are missing. "
            f"Expected files in: {config.DATASET_DIR}"
        )

    # Aggregate time-series
    logger.info("-" * 40)
    logger.info("Aggregating time-series data...")
    gst_features = aggregate_gst(raw["gst"])
    upi_features = aggregate_upi(raw["upi"])
    epfo_features = aggregate_epfo(raw["epfo"])

    # Extract profile features
    logger.info("-" * 40)
    logger.info("Extracting profile features...")
    profile_features = extract_profile_features(raw["profiles"])

    # Merge
    logger.info("-" * 40)
    logger.info("Merging all features...")
    merged = merge_all_features(profile_features, gst_features, upi_features, epfo_features)

    # Add YoY growth from master features if available
    if "master_features" in raw:
        master = raw["master_features"]
        if "yoy_growth_pct" in master.columns:
            yoy = master[[config.BUSINESS_ID_COLUMN, "yoy_growth_pct"]]
            merged = merged.merge(yoy, on=config.BUSINESS_ID_COLUMN, how="left")
            logger.info("Added yoy_growth_pct from master features")

    # Clean
    logger.info("-" * 40)
    logger.info("Cleaning data...")
    cleaned = clean_dataframe(merged)

    # Save
    cleaned.to_csv(config.PROCESSED_FEATURES_PATH, index=False)
    logger.info(f"Saved processed features to: {config.PROCESSED_FEATURES_PATH}")
    logger.info(f"Final shape: {cleaned.shape[0]} rows × {cleaned.shape[1]} columns")
    logger.info("=" * 60)
    logger.info("PREPROCESSING COMPLETE")
    logger.info("=" * 60)

    return cleaned


if __name__ == "__main__":
    run_preprocessing()
