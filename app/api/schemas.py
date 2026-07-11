from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ScoreRequest(BaseModel):
    msme_id: str = Field(
        ..., 
        description="Unique identifier for the MSME (e.g. 'raj_vendor', 'priya_saas', or any test string)",
        json_schema_extra={"example": "raj_vendor"}
    )
    custom_override_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional object to override fetched mock database records for direct testing of the scoring engine.",
        json_schema_extra={"example": None}
    )

class ReasonCode(BaseModel):
    code: str = Field(..., description="Machine-readable code identifier")
    type: str = Field(..., description="Indicator of effect: 'positive' or 'negative'")
    impact: float = Field(..., description="Score points gained or lost")
    text: str = Field(..., description="Human-readable reason explanation")

class ScoreBreakdown(BaseModel):
    revenue_stability: float = Field(..., description="Revenue stability component score (0-100)")
    tax_compliance: float = Field(..., description="Tax compliance component score (0-100)")
    cash_flow_health: float = Field(..., description="Cash flow health component score (0-100)")
    growth_trajectory: float = Field(..., description="Growth trajectory component score (0-100)")

class ServiceAuditLog(BaseModel):
    service_name: str
    status: str
    latency_seconds: float
    data_retrieved: bool

class ScoreResponse(BaseModel):
    msme_id: str = Field(..., description="Evaluated MSME ID")
    composite_score: float = Field(..., description="Aggregate credit score (0-100)")
    category: str = Field(..., description="Risk tier: 'Green' (Low), 'Amber' (Medium), 'Red' (High)")
    recommendation: str = Field(..., description="Bank loan action recommendation")
    confidence_score: float = Field(..., description="Percentage indicating complete integration data availability")
    recommended_credit_limit_inr: int = Field(..., description="Suggested credit limit threshold in Indian Rupees")
    breakdown: ScoreBreakdown = Field(..., description="Component-level credit score breakdown")
    reason_codes: List[ReasonCode] = Field(..., description="Explainability reasons lists")
    api_audit_logs: List[ServiceAuditLog] = Field(..., description="Logs from upstream integration fetches")

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    services_connected: Dict[str, str]
