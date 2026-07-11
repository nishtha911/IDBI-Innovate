from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np

# Initialize the API
app = FastAPI(title="IDBI MSME Financial Health Card API", version="1.0")

# Load our engineered "Database"
try:
    df_master = pd.read_csv("msme_master_features.csv")
except FileNotFoundError:
    print("Error: msme_master_features.csv not found. Run feature.py first.")

# Define the expected JSON input payload
class ScoreRequest(BaseModel):
    business_id: str
    api_key: str = "IDBI_HACK_2026"

@app.post("/score")
def generate_health_score(request: ScoreRequest):
    # 1. Lookup the MSME in our database
    msme = df_master[df_master['business_id'] == request.business_id]
    
    if msme.empty:
        raise HTTPException(status_code=404, detail="MSME ID not found in database")
    
    # Extract feature values
    volatility = msme['revenue_volatility'].values[0]
    delay_days = msme['total_delay_days'].values[0]
    upi_inflow = msme['avg_monthly_upi_inflow'].values[0]
    growth_pct = msme['yoy_growth_pct'].values[0]
    
    reason_codes = []
    
    # 2. SCORING LOGIC & EXPLAINABILITY (Weights: 30%, 25%, 25%, 20%)
    
    # A. Revenue Stability (30 points) - Lower volatility is better
    # Cap volatility penalty at 0.5 for scaling
    stab_score = max(0, (1 - min(volatility, 0.5) / 0.5)) * 30
    if volatility < 0.10:
        reason_codes.append("Highly stable revenue month-over-month (+Boost)")
    elif volatility > 0.25:
        reason_codes.append("High revenue volatility detected (-Penalty)")
        
    # B. Tax Compliance (25 points) - Fewer delayed days is better
    # Assume 180 total days delayed across 2 years completely wipes this score
    comp_score = max(0, (1 - min(delay_days, 180) / 180)) * 25
    if delay_days == 0:
        reason_codes.append("Perfect GST/EPFO filing discipline (+Boost)")
    elif delay_days > 60:
        reason_codes.append(f"Historical tax filing delays totaling {delay_days} days (-Penalty)")
        
    # C. Cash Flow Health (25 points) - High UPI volume is better
    # Scale against a 50 Lakh monthly benchmark
    cash_score = (min(upi_inflow, 5000000) / 5000000) * 25
    reason_codes.append(f"Average monthly digital cash flow verified at ₹{upi_inflow:,.2f}")
    
    # D. Growth Trajectory (20 points) - Positive YoY growth is better
    # Scale from -20% (0 points) to +20% (20 points)
    growth_score = min(max(growth_pct + 20, 0) / 40, 1) * 20
    if growth_pct > 10:
        reason_codes.append(f"Strong YoY revenue growth of {growth_pct:.1f}% (+Boost)")
    elif growth_pct < 0:
        reason_codes.append(f"Declining YoY revenue of {growth_pct:.1f}% (-Penalty)")

    # 3. COMPOSITE SCORE CALCULATION
    total_score = round(stab_score + comp_score + cash_score + growth_score)
    
    # 4. DECISION ROUTING
    if total_score >= 75:
        category = "Green"
        recommendation = "Approve - Best Rate Products"
    elif total_score >= 50:
        category = "Amber"
        recommendation = "Conditional Approval - Require Co-guarantor"
    else:
        category = "Red"
        recommendation = "Decline - Refer to SME Specialist"

    # 5. RETURN THE JSON PAYLOAD
    return {
        "business_id": request.business_id,
        "business_name": msme['business_name'].values[0],
        "financial_health_score": total_score,
        "risk_category": category,
        "recommendation": recommendation,
        "explainability_report": reason_codes
    }