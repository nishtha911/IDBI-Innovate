import numpy as np
from typing import Dict, Any, List, Tuple

class ScoringEngine:
    @staticmethod
    def calculate_score(
        gst_data: Dict[str, Any],
        upi_data: Dict[str, Any],
        epfo_data: Dict[str, Any],
        bank_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processes financial data from GST, UPI, EPFO, and Bank Statements to calculate:
        - Component scores
        - Overall composite Financial Health Score (0-100)
        - Decision category (Green, Amber, Red)
        - Reason codes / Explainability report
        - Suggested credit limit
        """
        reasons = []
        
        # ----------------------------------------------------
        # 1. REVENUE STABILITY (30% Weight)
        # ----------------------------------------------------
        rev_stability_score = 100.0
        rev_reasons = []
        
        # Determine turnover history
        is_registered = gst_data.get("is_registered", False)
        turnovers = []
        if is_registered and gst_data.get("turnover_history"):
            turnovers = [t["turnover"] for t in gst_data["turnover_history"]]
        elif bank_data.get("monthly_metrics"):
            # Fallback to bank statement total credits if GST unregistered
            turnovers = [m["total_credits"] for m in bank_data["monthly_metrics"]]
            rev_stability_score -= 10.0  # Unregistered penalty
            rev_reasons.append({
                "code": "REV_UNREGISTERED_GST",
                "type": "negative",
                "impact": -10,
                "text": "Entity is not registered for GST; assessed using bank statement credit proxies."
            })
        
        if turnovers:
            # Trend calculation (recent 3 months vs first 3 months)
            if len(turnovers) >= 6:
                recent_avg = sum(turnovers[-3:]) / 3.0
                early_avg = sum(turnovers[:3]) / 3.0
                trend_ratio = recent_avg / early_avg if early_avg > 0 else 1.0
            else:
                trend_ratio = 1.0
                
            if trend_ratio >= 1.15:
                trend_score = 100
                rev_reasons.append({
                    "code": "REV_TREND_GROWTH",
                    "type": "positive",
                    "impact": 5,
                    "text": "Strong upward trend in monthly revenue/credits."
                })
            elif trend_ratio >= 0.95:
                trend_score = 90
            elif trend_ratio >= 0.75:
                trend_score = 70
                rev_reasons.append({
                    "code": "REV_TREND_DECLINE_MODERATE",
                    "type": "negative",
                    "impact": -5,
                    "text": "Moderate decline in recent monthly revenues."
                })
            else:
                trend_score = 40
                rev_reasons.append({
                    "code": "REV_TREND_DECLINE_SEV",
                    "type": "negative",
                    "impact": -15,
                    "text": "Severe revenue/credit contraction over the assessment period."
                })
                
            # Volatility calculation (Coefficient of Variation)
            mean_turnover = sum(turnovers) / len(turnovers)
            if mean_turnover > 0:
                std_turnover = float(np.std(turnovers))
                cv = std_turnover / mean_turnover
            else:
                cv = 1.0
                
            if cv <= 0.12:
                volatility_score = 100
                rev_reasons.append({
                    "code": "REV_VOLATILITY_LOW",
                    "type": "positive",
                    "impact": 5,
                    "text": "High revenue stability with minimal month-on-month volatility."
                })
            elif cv <= 0.25:
                volatility_score = 85
            elif cv <= 0.45:
                volatility_score = 65
                rev_reasons.append({
                    "code": "REV_VOLATILITY_MOD",
                    "type": "negative",
                    "impact": -5,
                    "text": "Moderate fluctuations in monthly revenue."
                })
            else:
                volatility_score = 30
                rev_reasons.append({
                    "code": "REV_VOLATILITY_HIGH",
                    "type": "negative",
                    "impact": -15,
                    "text": "High month-on-month cash flow/revenue volatility."
                })
                
            # Blend components: 40% Trend, 60% Volatility
            raw_rev_score = (0.4 * trend_score) + (0.6 * volatility_score)
            rev_stability_score = max(0.0, min(100.0, rev_stability_score * (raw_rev_score / 100.0)))
        else:
            rev_stability_score = 50.0  # Neutral score if no data
            rev_reasons.append({
                "code": "REV_NO_DATA",
                "type": "negative",
                "impact": 0,
                "text": "Insufficient revenue historical data available."
            })
            
        reasons.extend(rev_reasons)

        # ----------------------------------------------------
        # 2. TAX COMPLIANCE (25% Weight)
        # ----------------------------------------------------
        tax_compliance_score = 100.0
        tax_reasons = []
        
        # GST Filings (40% of component)
        gst_filing_score = 100.0
        if is_registered and gst_data.get("filing_history"):
            filings = gst_data["filing_history"]
            on_time = sum(1 for f in filings if f.get("filed_on_time", False))
            total_filings = len(filings)
            on_time_rate = on_time / total_filings if total_filings > 0 else 1.0
            gst_filing_score = on_time_rate * 100.0
            
            if on_time_rate == 1.0:
                tax_reasons.append({
                    "code": "TAX_GST_PERFECT",
                    "type": "positive",
                    "impact": 5,
                    "text": "Perfect track record of timely GST returns (GSTR-1 & GSTR-3B) filing."
                })
            elif on_time_rate < 0.75:
                tax_reasons.append({
                    "code": "TAX_GST_LATE_FREQUENT",
                    "type": "negative",
                    "impact": -10,
                    "text": f"Frequent delays in GST filing; on-time rate is {on_time_rate:.1%}."
                })
        else:
            # Neutral baseline for unregistered GST
            gst_filing_score = 75.0
            tax_reasons.append({
                "code": "TAX_GST_UNREG_NEUTRAL",
                "type": "positive",
                "impact": 0,
                "text": "No active GSTIN registration required for entity class."
            })
            
        # EPFO Payments (40% of component)
        epfo_score = 100.0
        epfo_history = epfo_data.get("history", [])
        if epfo_history:
            total_months = len(epfo_history)
            on_time_months = sum(1 for h in epfo_history if h.get("payment_status") == "Paid_On_Time")
            late_months = sum(1 for h in epfo_history if h.get("payment_status") == "Paid_Late")
            
            # 1.0 weight for on-time, 0.4 for late, 0 for unpaid
            weighted_rate = (on_time_months + 0.4 * late_months) / total_months if total_months > 0 else 1.0
            epfo_score = weighted_rate * 100.0
            
            if on_time_months == total_months:
                tax_reasons.append({
                    "code": "TAX_EPFO_PERFECT",
                    "type": "positive",
                    "impact": 5,
                    "text": "Excellent EPFO payroll contribution filing consistency."
                })
            elif weighted_rate < 0.70:
                tax_reasons.append({
                    "code": "TAX_EPFO_COMPLIANCE_GAP",
                    "type": "negative",
                    "impact": -10,
                    "text": "Missed or severely delayed employee provident fund contributions."
                })
        else:
            # Neutral baseline if no employees / no EPFO registration
            epfo_score = 80.0
            tax_reasons.append({
                "code": "TAX_EPFO_NONE_NEUTRAL",
                "type": "positive",
                "impact": 0,
                "text": "No EPFO payroll obligations; employee threshold not met."
            })
            
        # Bank KYC status (20% of component)
        kyc_status = bank_data.get("kyc_status", "Pending")
        if kyc_status == "Verified":
            kyc_score = 100.0
        elif kyc_status == "Pending":
            kyc_score = 50.0
            tax_reasons.append({
                "code": "TAX_KYC_PENDING",
                "type": "negative",
                "impact": -5,
                "text": "Entity bank account KYC status is currently pending verification."
            })
        else:
            kyc_score = 0.0
            tax_reasons.append({
                "code": "TAX_KYC_FAILED",
                "type": "negative",
                "impact": -15,
                "text": "KYC compliance checks failed or details incomplete."
            })
            
        # Composite Compliance Score
        tax_compliance_score = (0.4 * gst_filing_score) + (0.4 * epfo_score) + (0.2 * kyc_score)
        reasons.extend(tax_reasons)

        # ----------------------------------------------------
        # 3. CASH FLOW HEALTH (25% Weight)
        # ----------------------------------------------------
        cash_flow_score = 100.0
        cash_reasons = []
        
        # UPI Transaction Velocity (30% of component)
        velocity_score = 80.0
        raw_velocity = upi_data.get("velocity_score", 1.0)
        if raw_velocity >= 1.2:
            velocity_score = 100.0
            cash_reasons.append({
                "code": "CASH_UPI_VELOCITY_FAST",
                "type": "positive",
                "impact": 5,
                "text": "UPI transactions showing strong positive velocity and volume expansion."
            })
        elif raw_velocity >= 0.95:
            velocity_score = 90.0
        elif raw_velocity >= 0.70:
            velocity_score = 65.0
            cash_reasons.append({
                "code": "CASH_UPI_VELOCITY_SLUGGISH",
                "type": "negative",
                "impact": -5,
                "text": "Declining UPI transaction volume over the last quarter."
            })
        else:
            velocity_score = 30.0
            cash_reasons.append({
                "code": "CASH_UPI_VELOCITY_CONTRACTION",
                "type": "negative",
                "impact": -12,
                "text": "Severe contraction in customer UPI transaction volumes."
            })
            
        # Average Daily Balance (ADB) buffer relative to spending (40% of component)
        adb_score = 100.0
        bank_metrics = bank_data.get("monthly_metrics", [])
        if bank_metrics:
            avg_adb = bank_data.get("average_daily_balance", 0.0)
            avg_debits = sum(m["total_debits"] for m in bank_metrics) / len(bank_metrics)
            
            balance_buffer_ratio = avg_adb / avg_debits if avg_debits > 0 else 1.0
            
            if avg_adb < 0:
                adb_score = 0.0
                cash_reasons.append({
                    "code": "CASH_ADB_NEGATIVE",
                    "type": "negative",
                    "impact": -20,
                    "text": "Average daily balance is negative; running on over-utilized credit limits."
                })
            elif balance_buffer_ratio >= 0.12:
                adb_score = 100.0
                cash_reasons.append({
                    "code": "CASH_ADB_BUFFER_HEALTHY",
                    "type": "positive",
                    "impact": 5,
                    "text": "Healthy cash buffer maintained relative to monthly spend."
                })
            elif balance_buffer_ratio >= 0.05:
                adb_score = 80.0
            elif balance_buffer_ratio >= 0.02:
                adb_score = 50.0
                cash_reasons.append({
                    "code": "CASH_ADB_BUFFER_THIN",
                    "type": "negative",
                    "impact": -5,
                    "text": "Thin daily balance buffer; business highly vulnerable to payment friction."
                })
            else:
                adb_score = 20.0
                cash_reasons.append({
                    "code": "CASH_ADB_BUFFER_CRITICAL",
                    "type": "negative",
                    "impact": -15,
                    "text": "Critical cash flow buffer levels; operating on near-empty reserves."
                })
        else:
            adb_score = 50.0
            
        # Bounces (30% of component)
        bounces_count = bank_data.get("bounces_count", 0)
        if bounces_count == 0:
            bounce_score = 100.0
            cash_reasons.append({
                "code": "CASH_BOUNCES_NONE",
                "type": "positive",
                "impact": 10,
                "text": "Exceptional banking discipline with zero outward clearing bounces."
            })
        elif bounces_count <= 1:
            bounce_score = 75.0
            cash_reasons.append({
                "code": "CASH_BOUNCES_LOW",
                "type": "negative",
                "impact": -5,
                "text": f"Minor bounce risk observed ({bounces_count} event in past 12 months)."
            })
        elif bounces_count <= 3:
            bounce_score = 40.0
            cash_reasons.append({
                "code": "CASH_BOUNCES_MOD",
                "type": "negative",
                "impact": -15,
                "text": f"Moderate clearing bounces ({bounces_count}) indicating recurring payment shortfalls."
            })
        else:
            bounce_score = 0.0
            cash_reasons.append({
                "code": "CASH_BOUNCES_HIGH",
                "type": "negative",
                "impact": -30,
                "text": f"Severe credit risk: {bounces_count} transaction bounces in last 12 months."
            })
            
        cash_flow_score = (0.3 * velocity_score) + (0.4 * adb_score) + (0.3 * bounce_score)
        reasons.extend(cash_reasons)

        # ----------------------------------------------------
        # 4. GROWTH TRAJECTORY (20% Weight)
        # ----------------------------------------------------
        growth_score = 100.0
        growth_reasons = []
        
        # YoY Growth Rate (50% of component)
        yoy_score = 75.0
        if len(turnovers) >= 12:
            midpoint = len(turnovers) // 2
            recent_half = turnovers[midpoint:]
            older_half = turnovers[:midpoint]
            
            recent_sum = sum(recent_half)
            older_sum = sum(older_half)
            
            growth_rate = (recent_sum - older_sum) / older_sum if older_sum > 0 else 0.0
            
            if growth_rate >= 0.20:
                yoy_score = 100.0
                growth_reasons.append({
                    "code": "GROWTH_YOY_EXCEPTIONAL",
                    "type": "positive",
                    "impact": 5,
                    "text": f"Exceptional Year-over-Year revenue expansion ({growth_rate:.1%})."
                })
            elif growth_rate >= 0.05:
                yoy_score = 90.0
                growth_reasons.append({
                    "code": "GROWTH_YOY_STEADY",
                    "type": "positive",
                    "impact": 3,
                    "text": f"Steady business revenue growth ({growth_rate:.1%})."
                })
            elif growth_rate >= -0.05:
                yoy_score = 75.0
            elif growth_rate >= -0.20:
                yoy_score = 50.0
                growth_reasons.append({
                    "code": "GROWTH_YOY_CONTRACTION",
                    "type": "negative",
                    "impact": -8,
                    "text": f"Revenue contraction of {abs(growth_rate):.1%} over assessment window."
                })
            else:
                yoy_score = 25.0
                growth_reasons.append({
                    "code": "GROWTH_YOY_SEVERE_DROP",
                    "type": "negative",
                    "impact": -15,
                    "text": f"Critical revenue drop of {abs(growth_rate):.1%} observed."
                })
        else:
            yoy_score = 75.0
            
        # Customer Concentration & Retention (50% of component)
        unique_cust = upi_data.get("unique_customers", 1)
        retention = upi_data.get("customer_retention_rate", 0.5)
        
        if unique_cust >= 80:
            concentration_score = 100.0
            growth_reasons.append({
                "code": "GROWTH_CUST_DIVERSIFIED",
                "type": "positive",
                "impact": 5,
                "text": f"Highly diversified customer base with {unique_cust} unique UPI payers."
            })
        elif unique_cust >= 25:
            concentration_score = 85.0
        elif unique_cust >= 8:
            concentration_score = 65.0
            growth_reasons.append({
                "code": "GROWTH_CUST_CONC_MOD",
                "type": "negative",
                "impact": -5,
                "text": "Moderate customer concentration; vulnerable to client loss."
            })
        else:
            concentration_score = 30.0
            growth_reasons.append({
                "code": "GROWTH_CUST_CONC_HIGH",
                "type": "negative",
                "impact": -15,
                "text": f"Severe customer concentration: only {unique_cust} unique paying entities."
            })
            
        # Adjust for retention rate
        if retention >= 0.80:
            concentration_score = min(100.0, concentration_score + 10.0)
            growth_reasons.append({
                "code": "GROWTH_RETENTION_STRONG",
                "type": "positive",
                "impact": 3,
                "text": f"Excellent customer retention rate ({retention:.1%}) indicates business loyalty."
            })
        elif retention < 0.35:
            concentration_score = max(0.0, concentration_score - 10.0)
            growth_reasons.append({
                "code": "GROWTH_RETENTION_WEAK",
                "type": "negative",
                "impact": -5,
                "text": f"Poor customer retention rate ({retention:.1%}); relying heavily on new client acquisition."
            })
            
        growth_score = (0.5 * yoy_score) + (0.5 * concentration_score)
        reasons.extend(growth_reasons)

        # ----------------------------------------------------
        # 5. COMPOSITE CALCULATION
        # ----------------------------------------------------
        composite_score = (
            (0.30 * rev_stability_score) +
            (0.25 * tax_compliance_score) +
            (0.25 * cash_flow_score) +
            (0.20 * growth_score)
        )
        
        # Clip score
        composite_score = round(max(0.0, min(100.0, composite_score)), 2)
        
        # Classification Category
        if composite_score >= 75.0:
            category = "Green"
            recommendation = "Approve; offer best-rate credit products."
        elif composite_score >= 50.0:
            category = "Amber"
            recommendation = "Conditional approval; require additional documentation or a co-guarantor."
        else:
            category = "Red"
            recommendation = "Decline or refer to SME specialist team."
            
        # Recommended Credit Limit
        # Base it on average monthly turnover (using past 6 months to be conservative)
        if turnovers:
            avg_monthly_turnover = sum(turnovers[-6:]) / min(len(turnovers), 6)
        else:
            avg_monthly_turnover = 0.0
            
        credit_limit = 0
        if category == "Green":
            # 1.5x to 2.5x of monthly turnover, scaled by score
            factor = 1.5 + (1.0 * (composite_score - 75.0) / 25.0)
            credit_limit = int((avg_monthly_turnover * factor) // 10000 * 10000)
        elif category == "Amber":
            # 0.4x to 1.0x of monthly turnover, scaled by score
            factor = 0.4 + (0.6 * (composite_score - 50.0) / 25.0)
            credit_limit = int((avg_monthly_turnover * factor) // 10000 * 10000)
        else:
            credit_limit = 0
            
        # Confidence score based on data completeness
        has_gst = 1 if is_registered else 0
        has_upi = 1 if upi_data.get("monthly_metrics") else 0
        has_epfo = 1 if epfo_history else 0
        has_bank = 1 if bank_metrics else 0
        
        confidence_score = round(((has_gst + has_upi + has_epfo + has_bank) / 4.0) * 100.0, 2)
        # Ensure minimum confidence if at least bank statement exists
        if has_bank and confidence_score < 50.0:
            confidence_score = 50.0

        return {
            "composite_score": composite_score,
            "category": category,
            "recommendation": recommendation,
            "confidence_score": confidence_score,
            "recommended_credit_limit_inr": credit_limit,
            "breakdown": {
                "revenue_stability": round(rev_stability_score, 2),
                "tax_compliance": round(tax_compliance_score, 2),
                "cash_flow_health": round(cash_flow_score, 2),
                "growth_trajectory": round(growth_score, 2)
            },
            "reason_codes": reasons
        }
