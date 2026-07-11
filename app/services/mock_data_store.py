import hashlib
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta

def get_deterministic_rng(seed_str: str) -> random.Random:
    """Creates a random number generator seeded with the MD5 hash of seed_str."""
    hasher = hashlib.md5(seed_str.encode("utf-8"))
    seed_int = int(hasher.hexdigest(), 16) & 0xFFFFFFFF
    return random.Random(seed_int)

def generate_monthly_list(num_months: int = 12) -> List[str]:
    """Generates a list of month strings (YYYY-MM) ending at previous month."""
    months = []
    # Use static local time reference 2026-07-11 to keep evaluations reproducible
    current_date = datetime(2026, 7, 11)
    for i in range(num_months, 0, -1):
        prev_date = current_date - timedelta(days=i * 30)
        months.append(prev_date.strftime("%Y-%m"))
    return months

def get_raj_profile() -> Dict[str, Any]:
    months = generate_monthly_list(18)
    
    # Raj: Vegetable Vendor (Unregistered GST, high UPI volume, small EPFO, clean bank statement)
    gst_turnover = []
    gst_filings = []
    for m in months:
        # Base turnover around 8L, with some seasonal variation
        month_num = int(m.split("-")[1])
        seasonal_factor = 1.15 if month_num in [10, 11, 12, 5] else 0.95
        turnover = round(800000 * seasonal_factor + random.uniform(-30000, 30000), 2)
        gst_turnover.append({"month": m, "turnover": turnover})
    
    # UPI transaction volume: very active. ~1200 transactions/month, avg 650 INR
    upi_monthly = []
    total_vol = 0.0
    for m in months:
        tx_count = int(1200 + random.randint(-150, 150))
        vol = round(tx_count * (650 + random.uniform(-40, 40)), 2)
        upi_monthly.append({
            "month": m,
            "transaction_count": tx_count,
            "volume": vol,
            "avg_transaction_size": round(vol / tx_count, 2)
        })
        total_vol += vol

    # EPFO: 2 employees, consistent INR 3000 contributions, paid on time
    epfo_history = []
    for m in months:
        epfo_history.append({
            "month": m,
            "employee_count": 2,
            "amount_paid": 3200.0,
            "payment_status": "Paid_On_Time",
            "payment_date": f"{m}-15"
        })

    # Bank: 25k average balance, zero bounces, credits ~8.2L, debits ~7.9L
    bank_monthly = []
    for m in months:
        credits = round(820000 + random.uniform(-20000, 20000), 2)
        debits = round(790000 + random.uniform(-20000, 20000), 2)
        bank_monthly.append({
            "month": m,
            "avg_daily_balance": round(25000 + random.uniform(-5000, 5000), 2),
            "total_credits": credits,
            "total_debits": debits,
            "overdraft_usage_days": 0
        })

    return {
        "gst": {
            "entity_name": "Raj Wholesale Vegetables",
            "gstin": None,
            "is_registered": False,
            "registration_date": None,
            "sector": "Retail & Wholesale",
            "turnover_history": gst_turnover,
            "filing_history": gst_filings
        },
        "upi": {
            "total_transactions": len(months) * 1200,
            "total_volume": round(total_vol, 2),
            "monthly_metrics": upi_monthly,
            "unique_customers": 450,
            "customer_retention_rate": 0.72,
            "velocity_score": 1.08  # Steady growth
        },
        "epfo": {
            "establishment_id": "DLCPM0001234000",
            "company_name": "Raj Wholesale Vegetables",
            "current_employee_count": 2,
            "history": epfo_history
        },
        "bank": {
            "account_number": "91029384756",
            "bank_name": "State Bank of India",
            "kyc_status": "Verified",
            "average_daily_balance": 25000.00,
            "monthly_metrics": bank_monthly,
            "bounces_count": 0,
            "bounce_history": []
        }
    }

def get_priya_profile() -> Dict[str, Any]:
    months = generate_monthly_list(18)
    
    # Priya: SaaS Startup (Registered GST, high GST/EPFO compliance, lumpy/contract UPI, clean bank statement)
    gst_turnover = []
    gst_filings = []
    base_turnover = 4000000  # 40L
    for idx, m in enumerate(months):
        # 30% YoY growth simulated
        growth_factor = 1.0 + (idx * 0.015) 
        turnover = round(base_turnover * growth_factor + random.uniform(-100000, 100000), 2)
        gst_turnover.append({"month": m, "turnover": turnover})
        
        # Perfect filing records
        gst_filings.append({
            "month": m,
            "filing_type": "GSTR-1",
            "filed_on_time": True,
            "filing_date": f"{m}-10"
        })
        gst_filings.append({
            "month": m,
            "filing_type": "GSTR-3B",
            "filed_on_time": True,
            "filing_date": f"{m}-18"
        })

    # UPI: lumpy contract-based payments. ~15 transactions/month, avg 1.3L INR
    upi_monthly = []
    total_vol = 0.0
    for m in months:
        tx_count = random.randint(10, 20)
        vol = round(tx_count * (130000 + random.uniform(-10000, 10000)), 2)
        upi_monthly.append({
            "month": m,
            "transaction_count": tx_count,
            "volume": vol,
            "avg_transaction_size": round(vol / tx_count, 2)
        })
        total_vol += vol

    # EPFO: 25 employees, strong consistent payroll compliance
    epfo_history = []
    for m in months:
        epfo_history.append({
            "month": m,
            "employee_count": 25,
            "amount_paid": 95000.0,
            "payment_status": "Paid_On_Time",
            "payment_date": f"{m}-12"
        })

    # Bank: 5L average balance, credits ~42L, debits ~38L, zero bounces
    bank_monthly = []
    for m in months:
        credits = round(4200000 + random.uniform(-100000, 100000), 2)
        debits = round(3800000 + random.uniform(-100000, 100000), 2)
        bank_monthly.append({
            "month": m,
            "avg_daily_balance": round(500000 + random.uniform(-50000, 50000), 2),
            "total_credits": credits,
            "total_debits": debits,
            "overdraft_usage_days": 0
        })

    return {
        "gst": {
            "entity_name": "Priya SaaS Technologies Pvt Ltd",
            "gstin": "27AAAAA1111A1Z1",
            "is_registered": True,
            "registration_date": "2024-01-15",
            "sector": "Information Technology",
            "turnover_history": gst_turnover,
            "filing_history": gst_filings
        },
        "upi": {
            "total_transactions": len(months) * 15,
            "total_volume": round(total_vol, 2),
            "monthly_metrics": upi_monthly,
            "unique_customers": 45,
            "customer_retention_rate": 0.88,
            "velocity_score": 1.25  # Fast growth
        },
        "epfo": {
            "establishment_id": "MHBAN0009876000",
            "company_name": "Priya SaaS Technologies Pvt Ltd",
            "current_employee_count": 25,
            "history": epfo_history
        },
        "bank": {
            "account_number": "10092837465",
            "bank_name": "IDBI Bank",
            "kyc_status": "Verified",
            "average_daily_balance": 500000.00,
            "monthly_metrics": bank_monthly,
            "bounces_count": 0,
            "bounce_history": []
        }
    }

def get_high_risk_profile() -> Dict[str, Any]:
    months = generate_monthly_list(18)
    
    # Default High Risk: Declining revenues, poor compliance, multiple bounces
    gst_turnover = []
    gst_filings = []
    base_turnover = 3000000  # 30L initial
    for idx, m in enumerate(months):
        # Declining: drops by 10% each month in the last 8 months
        decline_factor = 1.0 if idx < 10 else 1.0 - ((idx - 10) * 0.1)
        decline_factor = max(decline_factor, 0.15)
        turnover = round(base_turnover * decline_factor + random.uniform(-50000, 50000), 2)
        gst_turnover.append({"month": m, "turnover": turnover})
        
        # Terrible filing records (filed on time only in early months)
        filed_on_time = idx < 10 or (idx % 3 == 0)
        gst_filings.append({
            "month": m,
            "filing_type": "GSTR-1",
            "filed_on_time": filed_on_time,
            "filing_date": f"{m}-10" if filed_on_time else f"{m}-28"
        })
        gst_filings.append({
            "month": m,
            "filing_type": "GSTR-3B",
            "filed_on_time": filed_on_time,
            "filing_date": f"{m}-18" if filed_on_time else f"{m}-30"
        })

    # UPI: Low transaction count, declining volume
    upi_monthly = []
    total_vol = 0.0
    for idx, m in enumerate(months):
        decline_factor = 1.0 if idx < 10 else 1.0 - ((idx - 10) * 0.1)
        decline_factor = max(decline_factor, 0.10)
        tx_count = max(int(50 * decline_factor), 5)
        vol = round(tx_count * (5000 + random.uniform(-1000, 1000)), 2)
        upi_monthly.append({
            "month": m,
            "transaction_count": tx_count,
            "volume": vol,
            "avg_transaction_size": round(vol / tx_count, 2)
        })
        total_vol += vol

    # EPFO: Employee count dropping (15 down to 2), unpaid/late contributions
    epfo_history = []
    for idx, m in enumerate(months):
        emp_count = 15 if idx < 10 else max(15 - (idx - 10) * 2, 2)
        status = "Paid_On_Time" if idx < 10 else ("Paid_Late" if idx % 2 == 0 else "Unpaid")
        epfo_history.append({
            "month": m,
            "employee_count": emp_count,
            "amount_paid": emp_count * 1500.0 if status != "Unpaid" else 0.0,
            "payment_status": status,
            "payment_date": f"{m}-15" if status == "Paid_On_Time" else (f"{m}-29" if status == "Paid_Late" else None)
        })

    # Bank: Maxed out overdraft, average daily balance negative/near zero, 5 bounces
    bank_monthly = []
    for idx, m in enumerate(months):
        # Credits < Debits
        credits = round(500000 * (1.0 if idx < 10 else 0.3), 2)
        debits = round(credits * 1.15, 2)  # running a deficit
        bank_monthly.append({
            "month": m,
            "avg_daily_balance": round(10000 - (idx * 2000) if idx < 10 else -50000.0, 2),
            "total_credits": credits,
            "total_debits": debits,
            "overdraft_usage_days": 0 if idx < 5 else 30
        })

    # Bounces
    bounces = [
        {"date": f"{months[-1]}-05", "amount": 45000.0, "reason": "Insufficient_Funds"},
        {"date": f"{months[-2]}-12", "amount": 12000.0, "reason": "Insufficient_Funds"},
        {"date": f"{months[-2]}-14", "amount": 35000.0, "reason": "Insufficient_Funds"},
        {"date": f"{months[-3]}-20", "amount": 8000.0, "reason": "Insufficient_Funds"},
        {"date": f"{months[-4]}-02", "amount": 55000.0, "reason": "Insufficient_Funds"}
    ]

    return {
        "gst": {
            "entity_name": "Struggling Retail Outlets Ltd",
            "gstin": "27BBBBB2222B2Z2",
            "is_registered": True,
            "registration_date": "2020-05-20",
            "sector": "Retail",
            "turnover_history": gst_turnover,
            "filing_history": gst_filings
        },
        "upi": {
            "total_transactions": len(months) * 20,
            "total_volume": round(total_vol, 2),
            "monthly_metrics": upi_monthly,
            "unique_customers": 12,
            "customer_retention_rate": 0.25,
            "velocity_score": 0.45  # Declining
        },
        "epfo": {
            "establishment_id": "DLCPM0009999000",
            "company_name": "Struggling Retail Outlets Ltd",
            "current_employee_count": 2,
            "history": epfo_history
        },
        "bank": {
            "account_number": "50019283746",
            "bank_name": "ICICI Bank",
            "kyc_status": "Verified",
            "average_daily_balance": -35000.00,
            "monthly_metrics": bank_monthly,
            "bounces_count": 5,
            "bounce_history": bounces
        }
    }

def generate_synthetic_profile(msme_id: str) -> Dict[str, Any]:
    """Generates a deterministic synthetic profile based on the hash of msme_id."""
    rng = get_deterministic_rng(msme_id)
    months = generate_monthly_list(12)
    
    # Determine base parameters using deterministic random choice
    is_gst_registered = rng.choice([True, True, False])  # 66% chance of registration
    base_turnover = rng.choice([500000, 1500000, 3000000, 6000000])  # 5L to 60L/month
    growth_trend = rng.uniform(-0.02, 0.05)  # monthly trend (-2% to +5%)
    compliance_rate = rng.uniform(0.6, 1.0)  # GSTR filing rate
    employee_count = rng.randint(0, 40)
    bank_bounces = rng.choice([0, 0, 0, 1, 3])  # most have 0, some have 1 or 3
    avg_balance_ratio = rng.uniform(0.01, 0.15)  # daily balance as % of average monthly credits
    
    # 1. GST
    gst_turnover = []
    gst_filings = []
    if is_gst_registered:
        gstin = f"27{rng.choice(['A','B','C']) * 5}{rng.randint(1000, 9999)}{rng.choice(['A','B','C']) * 1}1Z{rng.randint(1,9)}"
        entity_name = f"MSME {msme_id.capitalize()} Enterprise"
        sector = rng.choice(["Manufacturing", "Retail & Wholesale", "Services", "Information Technology"])
        
        for idx, m in enumerate(months):
            trend_multiplier = (1.0 + growth_trend) ** idx
            volatility = rng.uniform(-0.08, 0.08)
            turnover = round(base_turnover * trend_multiplier * (1.0 + volatility), 2)
            gst_turnover.append({"month": m, "turnover": turnover})
            
            # Filings
            filed_on_time = rng.random() <= compliance_rate
            gst_filings.append({
                "month": m,
                "filing_type": "GSTR-1",
                "filed_on_time": filed_on_time,
                "filing_date": f"{m}-10" if filed_on_time else f"{m}-25"
            })
            gst_filings.append({
                "month": m,
                "filing_type": "GSTR-3B",
                "filed_on_time": filed_on_time,
                "filing_date": f"{m}-18" if filed_on_time else f"{m}-29"
            })
    else:
        gstin = None
        entity_name = f"MSME {msme_id.capitalize()} Retailer"
        sector = "Retail & Wholesale"
        # still simulate turnover for cashflow calculations, even if unregistered
        for idx, m in enumerate(months):
            trend_multiplier = (1.0 + growth_trend) ** idx
            volatility = rng.uniform(-0.15, 0.15)
            turnover = round(base_turnover * trend_multiplier * (1.0 + volatility), 2)
            gst_turnover.append({"month": m, "turnover": turnover})

    # 2. UPI
    upi_monthly = []
    total_vol = 0.0
    tx_count_base = rng.choice([100, 500, 1500])
    avg_tx_size = rng.choice([200, 800, 3000])
    for idx, m in enumerate(months):
        trend_multiplier = (1.0 + growth_trend) ** idx
        tx_count = max(int(tx_count_base * trend_multiplier * rng.uniform(0.85, 1.15)), 5)
        vol = round(tx_count * avg_tx_size * rng.uniform(0.9, 1.1), 2)
        upi_monthly.append({
            "month": m,
            "transaction_count": tx_count,
            "volume": vol,
            "avg_transaction_size": round(vol / tx_count, 2)
        })
        total_vol += vol

    # 3. EPFO
    epfo_history = []
    if employee_count > 0:
        estab_id = f"DLCPM000{rng.randint(1000000, 9999999)}"
        for idx, m in enumerate(months):
            # Employees can change slightly
            emp_change = rng.choice([-1, 0, 0, 0, 1])
            curr_emp = max(employee_count + emp_change, 1)
            status = rng.choice(["Paid_On_Time", "Paid_On_Time", "Paid_Late"]) if compliance_rate > 0.8 else rng.choice(["Paid_On_Time", "Paid_Late", "Unpaid"])
            epfo_history.append({
                "month": m,
                "employee_count": curr_emp,
                "amount_paid": curr_emp * 1600.0 if status != "Unpaid" else 0.0,
                "payment_status": status,
                "payment_date": f"{m}-15" if status == "Paid_On_Time" else (f"{m}-28" if status == "Paid_Late" else None)
            })
    else:
        estab_id = None

    # 4. Bank Statement
    avg_credits = base_turnover
    bank_monthly = []
    for idx, m in enumerate(months):
        credits = round(avg_credits * rng.uniform(0.9, 1.1), 2)
        debits = round(credits * rng.uniform(0.9, 1.05), 2)
        avg_bal = round(credits * avg_balance_ratio + rng.uniform(-1000, 5000), 2)
        bank_monthly.append({
            "month": m,
            "avg_daily_balance": max(avg_bal, 500.0),
            "total_credits": credits,
            "total_debits": debits,
            "overdraft_usage_days": rng.choice([0, 0, 0, 0, 5])
        })
    
    bounces = []
    for b in range(bank_bounces):
        bounce_month = rng.choice(months)
        bounces.append({
            "date": f"{bounce_month}-12",
            "amount": round(rng.uniform(5000, 50000), 2),
            "reason": "Insufficient_Funds"
        })

    return {
        "gst": {
            "entity_name": entity_name,
            "gstin": gstin,
            "is_registered": is_gst_registered,
            "registration_date": "2022-03-01" if is_gst_registered else None,
            "sector": sector if is_gst_registered else "Retail & Wholesale",
            "turnover_history": gst_turnover,
            "filing_history": gst_filings
        },
        "upi": {
            "total_transactions": len(months) * tx_count_base,
            "total_volume": round(total_vol, 2),
            "monthly_metrics": upi_monthly,
            "unique_customers": rng.randint(20, 500),
            "customer_retention_rate": round(rng.uniform(0.3, 0.9), 2),
            "velocity_score": round(1.0 + growth_trend * 10, 2)
        },
        "epfo": {
            "establishment_id": estab_id,
            "company_name": entity_name,
            "current_employee_count": employee_count,
            "history": epfo_history
        },
        "bank": {
            "account_number": f"900{rng.randint(10000000, 99999999)}",
            "bank_name": rng.choice(["IDBI Bank", "State Bank of India", "HDFC Bank", "ICICI Bank"]),
            "kyc_status": "Verified" if rng.random() > 0.05 else "Pending",
            "average_daily_balance": round(sum(m["avg_daily_balance"] for m in bank_monthly) / len(bank_monthly), 2),
            "monthly_metrics": bank_monthly,
            "bounces_count": len(bounces),
            "bounce_history": bounces
        }
    }

class MockDataStore:
    @staticmethod
    def get_profile(msme_id: str) -> Dict[str, Any]:
        """Retrieves profile based on MSME ID. Returns seeded profile or generates synthetic."""
        cleaned_id = msme_id.strip().lower()
        if cleaned_id == "raj_vendor":
            return get_raj_profile()
        elif cleaned_id == "priya_saas":
            return get_priya_profile()
        elif cleaned_id == "default_high_risk":
            return get_high_risk_profile()
        else:
            return generate_synthetic_profile(msme_id)
