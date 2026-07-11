import json
import pandas as pd

# Load the raw synthetic dataset
with open("msme_synthetic_data.json", "r") as f:
    data = json.load(f)

# 1. Extract and flatten Profiles
df_profiles = pd.json_normalize([item['profile'] for item in data])

# 2. Extract and flatten Time-Series Data
gst_list = []
upi_list = []
epfo_list = []

for item in data:
    b_id = item['profile']['business_id']
    
    # Process GST
    for record in item['gst_data']:
        record['business_id'] = b_id
        gst_list.append(record)
        
    # Process UPI
    for record in item['upi_data']:
        record['business_id'] = b_id
        upi_list.append(record)
        
    # Process EPFO
    for record in item['epfo_data']:
        record['business_id'] = b_id
        epfo_list.append(record)

df_gst = pd.DataFrame(gst_list)
df_upi = pd.DataFrame(upi_list)
df_epfo = pd.DataFrame(epfo_list)

print("Profiles Shape:", df_profiles.shape)
print("GST Records Shape:", df_gst.shape)

df_profiles.to_csv("msme_profiles.csv", index=False)
df_gst.to_csv("msme_gst_data.csv", index=False)
df_upi.to_csv("msme_upi_data.csv", index=False)
df_epfo.to_csv("msme_epfo_data.csv", index=False)

print("Success! All files saved to your current directory.")