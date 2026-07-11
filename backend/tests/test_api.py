import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services_connected" in data

def test_score_raj_vendor():
    # Temporarily disable delay to speed up tests
    from app.core.config import settings
    original_delay = settings.ENABLE_MOCK_DELAY
    settings.ENABLE_MOCK_DELAY = False
    
    try:
        response = client.post("/score", json={"msme_id": "raj_vendor"})
        assert response.status_code == 200
        data = response.json()
        assert data["msme_id"] == "raj_vendor"
        assert "composite_score" in data
        assert data["category"] in ["Green", "Amber", "Red"]
        assert "breakdown" in data
        assert len(data["api_audit_logs"]) == 4
        
        # Verify the logs show SUCCESS
        for log in data["api_audit_logs"]:
            assert log["status"] == "SUCCESS"
            assert log["data_retrieved"] is True
    finally:
        settings.ENABLE_MOCK_DELAY = original_delay

def test_score_missing_msme_id():
    response = client.post("/score", json={})
    assert response.status_code == 422  # Validation Error

def test_score_custom_override():
    payload = {
        "msme_id": "custom_override_test",
        "custom_override_data": {
            "gst": {
                "is_registered": True,
                "turnover_history": [{"month": "2026-01", "turnover": 1000000.0}],
                "filing_history": [{"month": "2026-01", "filing_type": "GSTR-1", "filed_on_time": True}]
            },
            "upi": {
                "unique_customers": 50,
                "customer_retention_rate": 0.85,
                "velocity_score": 1.2
            },
            "epfo": {
                "history": []
            },
            "bank": {
                "account_number": "12345",
                "bank_name": "Test Bank",
                "kyc_status": "Verified",
                "average_daily_balance": 150000.0,
                "bounces_count": 0,
                "monthly_metrics": [
                    {
                        "month": "2026-01",
                        "avg_daily_balance": 150000.0,
                        "total_credits": 1000000.0,
                        "total_debits": 900000.0,
                        "overdraft_usage_days": 0
                    }
                ]
            }
        }
    }
    
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["msme_id"] == "custom_override_test"
    assert data["category"] == "Green"  # High balance, zero bounces, growth = green
    assert len(data["api_audit_logs"]) == 1
    assert data["api_audit_logs"][0]["service_name"] == "CustomOverride"
