import pandas as pd
import duckdb
import os

# 1. Load the dataset using the absolute path to your Downloads folder
file_path = "/Users/parasbadhran/Downloads/blinkit_hyperlocal_inventory (1).xlsx"

print(f"Loading data from {file_path}...\n")

# Verify the file exists before trying to load it
if not os.path.exists(file_path):
    print(f"Error: Could not find the file at {file_path}. Please check the filename and path.")
    exit()

df_inventory = pd.read_excel(file_path)

# 2. Run Query 1: Overall Stockout Rate
print("--- QUERY 1: Overall Stockout Rate ---")
query1 = """
SELECT 
    Darkstore_Name,
    Pincode,
    COUNT(*) AS total_sku_logs,
    SUM(CASE WHEN Status = 'Out of Stock' THEN 1 ELSE 0 END) AS oos_logs,
    ROUND(SUM(CASE WHEN Status = 'Out of Stock' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS oos_percentage
FROM df_inventory
GROUP BY Darkstore_Name, Pincode
ORDER BY oos_percentage DESC;
"""
print(duckdb.query(query1).to_df())
print("\n")

# 3. Run Query 2: Peak Hour Stockout Surge (6 PM – 9 PM)
print("--- QUERY 2: Hourly Stockout Surge ---")
query2 = """
SELECT 
    EXTRACT(HOUR FROM Timestamp) AS hour_of_day,
    COUNT(*) AS total_items,
    SUM(CASE WHEN Status = 'Out of Stock' THEN 1 ELSE 0 END) AS oos_count,
    ROUND(SUM(CASE WHEN Status = 'Out of Stock' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS oos_percentage
FROM df_inventory
GROUP BY hour_of_day
ORDER BY hour_of_day ASC;
"""
print(duckdb.query(query2).to_df())
print("\n")

# 4. Run Query 3: Lost Revenue at Risk (Lost GMV)
print("--- QUERY 3: Estimated Lost GMV (6 PM - 9 PM) ---")
query3 = """
SELECT 
    Category,
    Darkstore_Name,
    SUM(Selling_Price * Daily_Avg_Demand) AS estimated_lost_gmv_rupees
FROM df_inventory
WHERE Status = 'Out of Stock' 
  AND EXTRACT(HOUR FROM Timestamp) BETWEEN 18 AND 21
GROUP BY Category, Darkstore_Name
ORDER BY estimated_lost_gmv_rupees DESC;
"""
print(duckdb.query(query3).to_df())
print("\n")

# 5. Run Query 4: Reorder Point (ROP) & Safety Stock Breaches
print("--- QUERY 4: ROP Breaches (Showing Top 10) ---")
query4 = """
SELECT 
    Product_Name,
    Darkstore_Name,
    Current_Stock_Units,
    Reorder_Point,
    (Daily_Avg_Demand * Lead_Time_Days) AS lead_time_demand,
    CASE 
        WHEN Current_Stock_Units < Reorder_Point THEN 'TRIGGER REORDER'
        ELSE 'OPTIMAL'
    END AS replenishment_status
FROM df_inventory
WHERE Current_Stock_Units < Reorder_Point
LIMIT 10;
"""
print(duckdb.query(query4).to_df())