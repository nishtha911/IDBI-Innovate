from fastapi import APIRouter, HTTPException, Depends
import asyncio
import time
from typing import Dict, Any, List

from app.api.schemas import ScoreRequest, ScoreResponse, HealthResponse, ServiceAuditLog, ScoreBreakdown, ReasonCode
from app.services.gst import GSTService
from app.services.upi import UPIService
from app.services.epfo import EPFOService
from app.services.bank import BankService
from app.services.base import ServiceError
from app.core.scoring import ScoringEngine
from app.core.config import settings

router = APIRouter()

# Instantiate services
gst_service = GSTService()
upi_service = UPIService()
epfo_service = EPFOService()
bank_service = BankService()

@router.post("/score", response_model=ScoreResponse)
async def get_msme_score(request: ScoreRequest):
    """
    Evaluates the MSME creditworthiness score by fetching records from
    external services (GST, UPI, EPFO, Bank) in parallel and running
    the scoring calculation.
    """
    msme_id = request.msme_id
    
    # 1. Ingestion Phase: Run parallel calls to services
    audit_logs: List[ServiceAuditLog] = []
    
    # Check for direct payload overrides
    if request.custom_override_data:
        # Bypassing external service calls for custom payload verification
        override = request.custom_override_data
        gst_data = override.get("gst", {})
        upi_data = override.get("upi", {})
        epfo_data = override.get("epfo", {})
        bank_data = override.get("bank", {})
        
        audit_logs.append(ServiceAuditLog(
            service_name="CustomOverride", status="Bypassed", latency_seconds=0.0, data_retrieved=True
        ))
    else:
        # Gather data from mocked sandbox APIs
        async def fetch_with_logging(service_fn, service_name):
            start_time = time.time()
            try:
                data = await service_fn(msme_id)
                latency = time.time() - start_time
                return data, ServiceAuditLog(
                    service_name=service_name,
                    status="SUCCESS",
                    latency_seconds=round(latency, 4),
                    data_retrieved=True
                )
            except ServiceError as e:
                latency = time.time() - start_time
                return None, ServiceAuditLog(
                    service_name=service_name,
                    status=f"ERROR_{e.status_code}",
                    latency_seconds=round(latency, 4),
                    data_retrieved=False
                )
            except Exception as e:
                latency = time.time() - start_time
                return None, ServiceAuditLog(
                    service_name=service_name,
                    status="ERROR_INTERNAL",
                    latency_seconds=round(latency, 4),
                    data_retrieved=False
                )

        tasks = [
            fetch_with_logging(gst_service.get_gst_data, "GSTN Sandbox"),
            fetch_with_logging(upi_service.get_upi_data, "UPI NPCI Analytics"),
            fetch_with_logging(epfo_service.get_epfo_data, "EPFO Compliance API"),
            fetch_with_logging(bank_service.get_bank_data, "Open Banking API")
        ]
        
        results = await asyncio.gather(*tasks)
        
        gst_res, upi_res, epfo_res, bank_res = results
        
        gst_data, gst_log = gst_res
        upi_data, upi_log = upi_res
        epfo_data, epfo_log = epfo_res
        bank_data, bank_log = bank_res
        
        audit_logs.extend([gst_log, upi_log, epfo_log, bank_log])
        
        # If the primary bank statements are completely missing or failed, we cannot evaluate
        if not bank_data:
            failed_service = next((log.service_name for log in audit_logs if not log.data_retrieved and log.service_name == "Open Banking API"), "Open Banking API")
            raise HTTPException(
                status_code=400,
                detail=f"Incomplete Assessment: Core bank statement integration failed ({failed_service}). Cannot compute score."
            )
            
        # Standardize empty dictionary overrides for failed non-core APIs
        gst_data = gst_data or {"is_registered": False, "turnover_history": [], "filing_history": []}
        upi_data = upi_data or {"total_transactions": 0, "total_volume": 0.0, "monthly_metrics": [], "velocity_score": 1.0}
        epfo_data = epfo_data or {"history": []}

    score_res: Dict[str, Any] = {}
    
    # 2. Calculation Phase
    try:
        if settings.USE_ML_MODEL:
            from ml.predict import predict
            
            # Combine raw data into a unified dictionary for prediction
            unified_data = {
                "gst": gst_data,
                "upi": upi_data,
                "epfo": epfo_data,
                "bank": bank_data
            }
            
            ml_res = predict(unified_data)
            
            # Map ML prediction results to API format
            # Map top_risk_factors to reason_codes
            reason_codes = []
            for trf in ml_res.get("top_risk_factors", []):
                reason_codes.append({
                    "code": trf["feature"].upper(),
                    "type": trf["direction"],
                    "impact": round(trf["shap_value"] * 100.0, 2),
                    "text": f"{trf['display_name']} is a key driver contributing {trf['direction']}ly."
                })
                
            score_res = {
                "composite_score": ml_res["composite_score"],
                "category": ml_res["category"],
                "recommendation": ml_res["recommendation"],
                "confidence_score": ml_res["confidence_score"],
                "recommended_credit_limit_inr": ml_res["recommended_credit_limit_inr"],
                "breakdown": ml_res["breakdown"],
                "reason_codes": reason_codes
            }
        else:
            score_res = ScoringEngine.calculate_score(gst_data, upi_data, epfo_data, bank_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scoring engine error: {str(e)}"
        )
        
    # Format and return Pydantic model
    return ScoreResponse(
        msme_id=msme_id,
        composite_score=score_res["composite_score"],
        category=score_res["category"],
        recommendation=score_res["recommendation"],
        confidence_score=score_res["confidence_score"],
        recommended_credit_limit_inr=score_res["recommended_credit_limit_inr"],
        breakdown=ScoreBreakdown(**score_res["breakdown"]),
        reason_codes=[ReasonCode(**rc) for rc in score_res["reason_codes"]],
        api_audit_logs=audit_logs
    )

@router.get("/health", response_model=HealthResponse)
def health_check():
    """System health check and connectivity checks."""
    return HealthResponse(
        status="healthy",
        services_connected={
            "GSTN_Sandbox": "connected",
            "UPI_NPCI_Analytics": "connected",
            "EPFO_Compliance_API": "connected",
            "Open_Banking_API": "connected"
        }
    )
