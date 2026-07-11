import json
import numpy as np
from faker import Faker
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Initialize Faker with Indian locale
fake = Faker('en_IN')

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
    
# Configuration
NUM_MSMES = 1000
MONTHS_OF_HISTORY = 24
CURRENT_DATE = datetime(2026, 7, 1) # Aligning with your project timeline

def generate_msme_data(num_records):
    dataset = []
    
    for _ in range(num_records):
        # 1. Base Profile & Risk Cohort Assignment
        business_id = fake.bothify(text="MSME_#########")
        cohort = np.random.choice(['Green', 'Amber', 'Red'], p=[0.5, 0.3, 0.2])
        
        # Faker for static metadata
        profile = {
            "business_id": business_id,
            "business_name": fake.company(),
            "entity_type": np.random.choice(["Private Limited", "Proprietorship", "Partnership", "LLP"]),
            "industry_sector": np.random.choice(["B2B Software", "Retail", "Manufacturing", "Services", "Wholesale"]),
            "vintage_months": np.random.randint(24, 120),
            "location": {
                "state": fake.state(),
                "city": fake.city(),
                "tier": np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
            },
            "kyc_status": np.random.choice(["Verified", "Pending"], p=[0.95, 0.05]),
            "credit_history_length_months": 0,
            "simulated_cohort": cohort # Included for your testing/validation later
        }

        # 2. Financial Base Metrics (NumPy)
        base_revenue = np.random.uniform(500000, 5000000)
        base_employees = max(2, int(base_revenue / 200000)) # roughly 1 employee per 2L revenue
        
        # Adjust trends based on cohort
        if cohort == 'Green':
            trend = np.linspace(0, 0.20, MONTHS_OF_HISTORY) # 20% growth over 2 years
            volatility = 0.05
            delay_prob = 0.05
        elif cohort == 'Amber':
            trend = np.linspace(0, 0.05, MONTHS_OF_HISTORY) # 5% growth
            volatility = 0.15 # High variance
            delay_prob = 0.30
        else: # Red
            trend = np.linspace(0, -0.20, MONTHS_OF_HISTORY) # 20% decline
            volatility = 0.10
            delay_prob = 0.70

        gst_records = []
        upi_records = []
        epfo_records = []

        # 3. Time Series Generation Loop
        for i in range(MONTHS_OF_HISTORY):
            # Calculate date working backwards
            record_date = CURRENT_DATE - relativedelta(months=MONTHS_OF_HISTORY - i)
            month_str = record_date.strftime("%m")
            year_str = record_date.strftime("%Y")
            
            # --- GST Data Math ---
            noise = np.random.normal(0, volatility)
            current_revenue = base_revenue * (1 + trend[i] + noise)
            current_revenue = max(50000, current_revenue) # Floor to prevent negative revenue
            
            tax_paid = current_revenue * 0.18 # Assume 18% GST bracket
            itc_claimed = tax_paid * np.random.uniform(0.1, 0.4)
            
            # Simulate compliance discipline
            is_delayed = np.random.random() < delay_prob
            delay_days = np.random.randint(1, 45) if is_delayed else 0
            
            gst_records.append({
                "month": month_str,
                "year": year_str,
                "gross_turnover_inr": round(current_revenue, 2),
                "tax_paid_inr": round(tax_paid, 2),
                "filing_status": "Filed" if delay_days < 30 else "Late",
                "filing_delay_days": delay_days,
                "itc_claimed_inr": round(itc_claimed, 2)
            })

            # --- UPI Data Math ---
            # Assume 60-90% of revenue flows through UPI depending on sector
            upi_ratio = np.random.uniform(0.6, 0.9)
            upi_volume = current_revenue * upi_ratio
            
            # Determine transaction frequency
            avg_ticket = np.random.uniform(500, 15000)
            txn_count = max(1, int(upi_volume / avg_ticket))
            
            upi_records.append({
                "month": month_str,
                "year": year_str,
                "total_inflow_volume_inr": round(upi_volume, 2),
                "inflow_transaction_count": txn_count,
                "average_ticket_size_inr": round(upi_volume / txn_count, 2) if txn_count > 0 else 0,
                "total_outflow_volume_inr": round(upi_volume * np.random.uniform(0.5, 0.8), 2),
                "outflow_transaction_count": int(txn_count * np.random.uniform(0.8, 1.2)),
                "unique_counterparties_in": max(1, int(txn_count * np.random.uniform(0.3, 0.7))),
                "failed_transaction_rate_pct": round(np.random.uniform(0.1, 3.0), 2)
            })

            # --- EPFO Data Math ---
            # Fluctuate employees slightly based on trend
            current_employees = max(1, int(base_employees * (1 + trend[i])))
            
            # Standard PF calculation (assume approx 15k basic salary average, 12% contribution)
            pf_contribution = current_employees * 15000 * 0.12
            
            epfo_records.append({
                "month": month_str,
                "year": year_str,
                "active_employee_count": current_employees,
                "total_pf_contribution_inr": round(pf_contribution, 2),
                "compliance_status": "On-Time" if not is_delayed else "Delayed"
            })

        # Compile full MSME record
        msme_record = {
            "profile": profile,
            "gst_data": gst_records,
            "upi_data": upi_records,
            "epfo_data": epfo_records
        }
        
        dataset.append(msme_record)
        
    return dataset

# Execute and Save
if __name__ == "__main__":
    print(f"Generating synthetic data for {NUM_MSMES} MSMEs...")
    mock_dataset = generate_msme_data(NUM_MSMES)
    
    output_filename = "msme_synthetic_data.json"
    with open(output_filename, "w") as f:
        json.dump(mock_dataset, f, indent=4, cls=NpEncoder)
        
    print(f"Success! Data saved to {output_filename}")