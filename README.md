Project Overview

This project analyzes why quick-commerce dark stores run out of stock during evening peak hours.

Why is it important?
Dark stores face a major problem where popular items run out of stock between 6 PM and 9 PM when people place the most orders. This study was done to find out why this happens, which items suffer the most, and how much money is lost.

How We Did It?
Data Generation: I started by writing a Python script to create a synthetic CSV dataset. The data includes important columns like status, category, product IDs, and timestamps, using built-in rules to mimic real-world inventory behavior. 

Database & SQL: The data was converted to Excel, and I used DuckDB inside the macOS terminal to run SQL queries and extract inventory insights.

Dashboard & Analysis: The final results were brought into Tableau to build an interactive dashboard tracking hourly inventory drops, category risks, and revenue at risk.

Key Findings

Stock levels drop steadily through the afternoon, leading to severe stockout surges hitting up to 35% to 50% between 6 PM and 9 PM.

Dairy, fresh items, and snacks are the hardest hit during these rush hours.

Static reorder triggers fail to keep up with the evening demand spike, causing significant revenue loss.

Recommendations
To fix the evening stockout problem, stores should use dynamic replenishment rules that automatically restock high-demand items before 6 PM based on predicted evening surges.

Limitations
I acknowledge that the dataset is synthetically generated over a short 7-day period and does not mirror complex real-life enterprise data. However, this analysis was still useful for building a complete end-to-end data pipeline, practicing SQL queries, and designing executive-level dashboards for quick-commerce supply chain management.
