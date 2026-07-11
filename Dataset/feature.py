import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Assuming you already ran the flattening code and have:
# df_profiles, df_gst, df_upi, df_epfo

df_profiles = pd.read_csv("msme_profiles.csv")
df_gst = pd.read_csv("msme_gst_data.csv")
df_upi = pd.read_csv("msme_upi_data.csv")
df_epfo = pd.read_csv("msme_epfo_data.csv")

print("Engineering features...")

# 1. Revenue Volatility (GST Data)
# Calculate the Coefficient of Variation (Standard Deviation / Mean)
gst_stats = df_gst.groupby('business_id')['gross_turnover_inr'].agg(['mean', 'std']).reset_index()
gst_stats['revenue_volatility'] = gst_stats['std'] / gst_stats['mean']

# 2. Tax Compliance (GST Data)
# Total days delayed over the 24 months
compliance_stats = df_gst.groupby('business_id')['filing_delay_days'].sum().reset_index()
compliance_stats.rename(columns={'filing_delay_days': 'total_delay_days'}, inplace=True)

# 3. Cash Flow Health (UPI Data)
# Average monthly UPI inflow
upi_stats = df_upi.groupby('business_id')['total_inflow_volume_inr'].mean().reset_index()
upi_stats.rename(columns={'total_inflow_volume_inr': 'avg_monthly_upi_inflow'}, inplace=True)

# 4. Growth Trajectory (YoY Revenue Growth)
# Sort by year/month, then compare the first 12 months to the last 12 months
df_gst['date'] = pd.to_datetime(df_gst['year'].astype(str) + '-' + df_gst['month'].astype(str))
df_gst = df_gst.sort_values(by=['business_id', 'date'])

# Split into first year and second year
first_year = df_gst.groupby('business_id').head(12).groupby('business_id')['gross_turnover_inr'].mean().reset_index()
second_year = df_gst.groupby('business_id').tail(12).groupby('business_id')['gross_turnover_inr'].mean().reset_index()

# Merge and calculate YoY percentage change
growth_stats = pd.merge(first_year, second_year, on='business_id', suffixes=('_y1', '_y2'))
growth_stats['yoy_growth_pct'] = ((growth_stats['gross_turnover_inr_y2'] - growth_stats['gross_turnover_inr_y1']) / growth_stats['gross_turnover_inr_y1']) * 100

# --- MERGE INTO MASTER DATAFRAME ---
df_master = df_profiles[['business_id', 'business_name', 'industry_sector', 'simulated_cohort']].copy()
df_master = df_master.merge(gst_stats[['business_id', 'revenue_volatility']], on='business_id', how='left')
df_master = df_master.merge(compliance_stats, on='business_id', how='left')
df_master = df_master.merge(upi_stats, on='business_id', how='left')
df_master = df_master.merge(growth_stats[['business_id', 'yoy_growth_pct']], on='business_id', how='left')

print("Feature engineering complete!")
print(df_master.head())

# --- THE HEATMAP ---
# Convert cohorts to numbers so they show up on the correlation matrix (Green=0, Amber=1, Red=2)
# In this logic, a higher target number (2) means HIGHER RISK.
df_master['risk_target'] = df_master['simulated_cohort'].map({'Green': 0, 'Amber': 1, 'Red': 2})

# Select only the numeric features for the heatmap
features_for_heatmap = df_master[['revenue_volatility', 'total_delay_days', 'avg_monthly_upi_inflow', 'yoy_growth_pct', 'risk_target']]

df_master.to_csv("msme_master_features.csv", index=False)
print("Saved msme_master_features.csv successfully!")

# Plot it!
plt.figure(figsize=(10, 8))
sns.heatmap(features_for_heatmap.corr(), annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title("Feature Correlation with Risk Cohort (Synthetic Data)")
plt.tight_layout()
plt.show()