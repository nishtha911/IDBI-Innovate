import pytest
from app.core.scoring import ScoringEngine
from app.services.mock_data_store import MockDataStore

def test_raj_vendor_scoring():
    profile = MockDataStore.get_profile("raj_vendor")
    res = ScoringEngine.calculate_score(
        gst_data=profile["gst"],
        upi_data=profile["upi"],
        epfo_data=profile["epfo"],
        bank_data=profile["bank"]
    )
    
    assert res["composite_score"] >= 50.0  # Should be Green or Amber
    assert res["confidence_score"] >= 50.0
    # Raj is unregistered for GST, so we expect the reason code for unregistered GST
    reasons = [r["code"] for r in res["reason_codes"]]
    assert "REV_UNREGISTERED_GST" in reasons
    
    if res["category"] == "Red":
        assert res["recommended_credit_limit_inr"] == 0
    else:
        assert res["recommended_credit_limit_inr"] > 0

def test_priya_saas_scoring():
    profile = MockDataStore.get_profile("priya_saas")
    res = ScoringEngine.calculate_score(
        gst_data=profile["gst"],
        upi_data=profile["upi"],
        epfo_data=profile["epfo"],
        bank_data=profile["bank"]
    )
    
    assert res["composite_score"] >= 75.0  # High compliance + revenue = Green
    assert res["category"] == "Green"
    assert res["confidence_score"] == 100.0  # All four datasets fully loaded
    
    reasons = [r["code"] for r in res["reason_codes"]]
    assert "TAX_GST_PERFECT" in reasons
    assert "TAX_EPFO_PERFECT" in reasons
    assert "CASH_BOUNCES_NONE" in reasons
    assert res["recommended_credit_limit_inr"] > 1000000  # High limit for SaaS with 40L monthly revenue

def test_default_high_risk_scoring():
    profile = MockDataStore.get_profile("default_high_risk")
    res = ScoringEngine.calculate_score(
        gst_data=profile["gst"],
        upi_data=profile["upi"],
        epfo_data=profile["epfo"],
        bank_data=profile["bank"]
    )
    
    assert res["composite_score"] < 50.0
    assert res["category"] == "Red"
    assert res["recommended_credit_limit_inr"] == 0
    
    reasons = [r["code"] for r in res["reason_codes"]]
    assert "CASH_BOUNCES_HIGH" in reasons
    assert "REV_VOLATILITY_HIGH" in reasons or "REV_TREND_DECLINE_SEV" in reasons

def test_synthetic_reproducibility():
    p1 = MockDataStore.get_profile("test_firm_abc")
    p2 = MockDataStore.get_profile("test_firm_abc")
    
    # Check deterministic output
    assert p1["bank"]["account_number"] == p2["bank"]["account_number"]
    assert len(p1["bank"]["monthly_metrics"]) == len(p2["bank"]["monthly_metrics"])
