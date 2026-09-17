import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

# --- 1. Base Setup & Products ---
num_days = 7
skus_count = 42
start_date = datetime(2026, 9, 17) # Starting from today

# Geographic Info
store_name = "BD Mall, Manjit Nagar (Near Thapar Uni)"
city = "Patiala"
pincode = "147004"

# Generate 42 SKUs
categories = ["Dairy/Fresh", "Snacks & Beverages", "Staples", "Personal Care"]
base_products = []
for i in range(1, skus_count + 1):
    cat = np.random.choice(categories, p=[0.4, 0.3, 0.2, 0.1])
    base_products.append({
        "Product_ID": f"SKU_{i:03d}",
        "Product_Name": f"Product_{cat.split('/')[0]}_{i}",
        "Category": cat,
        "MRP": np.random.randint(20, 300),
        "Item_Volume_cm3": np.random.randint(100, 1500)
    })

df_products = pd.DataFrame(base_products)
df_products["Selling_Price"] = (df_products["MRP"] * np.random.uniform(0.85, 1.0, skus_count)).round()

# --- 2. Generate Time Series (Strictly 6 AM to 11 PM with random minutes/seconds) ---
timestamps = []
for day in range(num_days):
    current_day = start_date + timedelta(days=day)
    # 6 AM (6) to 11 PM (22:59)
    for hour in range(6, 23): 
        minute = np.random.randint(0, 60)
        second = np.random.randint(0, 60)
        ts = current_day.replace(hour=hour, minute=minute, second=second)
        timestamps.append(ts)

df_time = pd.DataFrame({"Timestamp": timestamps})

# Cross merge to get every SKU for every timestamp (42 SKUs * 119 timestamps = 4998 rows)
df = df_time.merge(df_products, how="cross")

# Add location fields
df["Darkstore_Name"] = store_name
df["City"] = city
df["Pincode"] = pincode

# --- 3. Apply Business Logic (Vectorized) ---
# Differentiate demand based on perishability
df["Daily_Avg_Demand"] = np.where(df["Category"] == "Dairy/Fresh", 
                                  np.random.randint(50, 150, len(df)), 
                                  np.random.randint(20, 80, len(df)))

# Lead times: 0.5 to 1.0 days for fresh, 1.0 to 2.0 days for others
df["Lead_Time_Days"] = np.where(df["Category"] == "Dairy/Fresh", 
                                np.random.uniform(0.5, 1.0, len(df)), 
                                np.random.uniform(1.0, 2.0, len(df))).round(2)

# Set Reorder Point (Fresh items get a tighter buffer)
df["Reorder_Point"] = np.where(df["Category"] == "Dairy/Fresh", 
                               (df["Daily_Avg_Demand"] * 0.2).astype(int), 
                               (df["Daily_Avg_Demand"] * 0.5).astype(int))

# Base Current Stock (assume initially well-stocked)
df["Current_Stock_Units"] = np.random.randint(df["Reorder_Point"], df["Daily_Avg_Demand"] + 20)

# --- 4. Apply Realistic 10-20% Stockout Rates ---
is_evening_peak = df["Timestamp"].dt.hour.isin([18, 19, 20, 21])
random_chance = np.random.random(len(df))

# ~8% chance of stockout during normal hours, ~35% chance during evening peak
# Blended together, this ensures an overall dataset stockout rate of ~12-15%
condition_peak_oos = is_evening_peak & (random_chance < 0.35)
condition_regular_oos = (~is_evening_peak) & (random_chance < 0.08)

# Force stock to 0 where conditions are met
df.loc[condition_peak_oos | condition_regular_oos, "Current_Stock_Units"] = 0

# Explicitly tag the status
df["Status"] = np.where(df["Current_Stock_Units"] == 0, "Out of Stock", "In Stock")

# Sort chronologically to make it realistic
df = df.sort_values(by=["Timestamp", "Product_ID"]).reset_index(drop=True)

# --- 5. Export and Verify ---
df.to_csv("blinkit_hyperlocal_inventory.csv", index=False)

# Verification Printouts
total_rows = len(df)
oos_count = len(df[df["Status"] == "Out of Stock"])
oos_percentage = (oos_count / total_rows) * 100

print(f"Dataset generated with {total_rows} rows.")
print(f"Overall Out of Stock Rate: {oos_percentage:.1f}%")
