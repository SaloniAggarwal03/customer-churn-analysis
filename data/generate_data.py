"""
generate_data.py
================
Generates a realistic UK online retail transaction dataset (~500K rows).
Run this first before churn_analysis.py

Usage:
    python generate_data.py

Output:
    retail_data.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

print("Generating retail dataset... (this takes ~15 seconds)")

# ─── Config ───────────────────────────────────────────────────────────────────
N_CUSTOMERS = 4500
N_TRANSACTIONS = 520000
START_DATE = datetime(2010, 12, 1)
END_DATE = datetime(2011, 12, 9)
DATE_RANGE = (END_DATE - START_DATE).days

# ─── Products ─────────────────────────────────────────────────────────────────
products = [
    ("85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 2.55),
    ("71053",  "WHITE METAL LANTERN", 3.39),
    ("84406B", "CREAM CUPID HEARTS COAT HANGER", 2.75),
    ("84029G", "KNITTED UNION FLAG HOT WATER BOTTLE", 3.39),
    ("84029E", "RED WOOLLY HOTTIE WHITE HEART", 3.39),
    ("22752",  "SET 7 BABUSHKA NESTING BOXES", 7.65),
    ("21730",  "GLASS STAR FROSTED T-LIGHT HOLDER", 4.25),
    ("22633",  "HAND WARMER UNION JACK", 1.85),
    ("22632",  "HAND WARMER RED POLKA DOT", 1.85),
    ("37370",  "RETRO COFFEE MUGS ASSORTED", 5.45),
    ("20727",  "LUNCH BAG BLACK SKULL", 1.65),
    ("23203",  "JUMBO BAG BAROQUE BLACK WHITE", 2.08),
    ("23209",  "JUMBO SHOPPER VINTAGE RED PAISLEY", 2.08),
    ("22961",  "JAM MAKING SET PRINTED", 4.25),
    ("22086",  "PAPER CHAIN KIT RETRO SPOT", 2.95),
    ("22197",  "POPCORN HOLDER", 0.85),
    ("84997C", "CHILDRENS CUTLERY DOLLY GIRL", 4.15),
    ("85099B", "JUMBO BAG RED RETROSPOT", 1.95),
    ("22386",  "JUMBO BAG PINK POLKADOT", 1.95),
    ("21212",  "PACK OF 72 RETROSPOT CAKE CASES", 0.55),
    ("23298",  "SPOTTY BUNTING", 4.95),
    ("22111",  "SCOTTIE DOG HOT WATER BOTTLE", 4.25),
    ("21977",  "PACK OF 60 PINK PAISLEY CAKE CASES", 0.55),
    ("22112",  "CHOCOLATE HOT WATER BOTTLE", 4.25),
    ("22469",  "HEART OF WICKER SMALL", 1.65),
    ("21232",  "STRAWBERRY CERAMIC TRINKET BOX", 1.25),
    ("22067",  "BERRY SCENTED DRAWER SACHETS", 1.25),
    ("84991",  "60 TEATIME FAIRY CAKE CASES", 0.55),
    ("22423",  "REGENCY CAKESTAND 3 TIER", 12.75),
    ("47566B", "TEA TIME OVEN GLOVE", 3.39),
]

# ─── Countries ────────────────────────────────────────────────────────────────
countries = ["United Kingdom"] * 80 + ["Germany", "France", "Netherlands",
             "Australia", "Spain", "Belgium", "Switzerland", "Portugal",
             "Italy", "Finland", "Denmark", "Norway", "Sweden", "USA"]

# ─── Customer segments (hidden ground truth) ──────────────────────────────────
# Champions: buy often, recently, high value
# Loyal: buy often, moderate recency
# At Risk: used to buy, haven't recently
# Lost: last purchase was long ago

segment_weights = {
    "Champion":  0.18,
    "Loyal":     0.22,
    "AtRisk":    0.24,
    "Lost":      0.36,
}

customer_segments = np.random.choice(
    list(segment_weights.keys()),
    size=N_CUSTOMERS,
    p=list(segment_weights.values())
)

# ─── Build customer profiles ───────────────────────────────────────────────────
def last_purchase_days(seg):
    if seg == "Champion":  return np.random.randint(1, 30)
    if seg == "Loyal":     return np.random.randint(20, 60)
    if seg == "AtRisk":    return np.random.randint(60, 120)
    if seg == "Lost":      return np.random.randint(120, 365)

def purchase_frequency(seg):
    if seg == "Champion":  return np.random.randint(15, 40)
    if seg == "Loyal":     return np.random.randint(8, 18)
    if seg == "AtRisk":    return np.random.randint(3, 9)
    if seg == "Lost":      return np.random.randint(1, 4)

def avg_order_value(seg):
    if seg == "Champion":  return np.random.uniform(120, 400)
    if seg == "Loyal":     return np.random.uniform(60, 150)
    if seg == "AtRisk":    return np.random.uniform(30, 90)
    if seg == "Lost":      return np.random.uniform(10, 50)

customer_ids = [f"C{str(10000 + i)}" for i in range(N_CUSTOMERS)]

# ─── Generate transactions ─────────────────────────────────────────────────────
rows = []
invoice_num = 536365

for i, cust_id in enumerate(customer_ids):
    seg = customer_segments[i]
    n_purchases = purchase_frequency(seg)
    last_days = last_purchase_days(seg)
    last_purchase = END_DATE - timedelta(days=last_days)
    country = np.random.choice(countries)

    for _ in range(n_purchases):
        # Spread purchases over the year, with most recent near last_purchase
        days_back = np.random.randint(0, DATE_RANGE)
        inv_date = END_DATE - timedelta(days=days_back)
        # Bias toward last_purchase window
        inv_date = min(inv_date, last_purchase + timedelta(days=np.random.randint(0, 30)))
        inv_date = max(inv_date, START_DATE)

        n_items = np.random.randint(1, 8)
        invoice_num += 1
        inv_str = str(invoice_num)

        for _ in range(n_items):
            prod = random.choice(products)
            qty = np.random.randint(1, 20)
            price = prod[2] * np.random.uniform(0.9, 1.1)  # slight variation

            rows.append({
                "InvoiceNo":   inv_str,
                "StockCode":   prod[0],
                "Description": prod[1],
                "Quantity":    qty,
                "InvoiceDate": inv_date.strftime("%Y-%m-%d %H:%M"),
                "UnitPrice":   round(price, 2),
                "CustomerID":  cust_id,
                "Country":     country,
            })

# ─── Add ~2% cancelled invoices (negative quantities) ─────────────────────────
n_cancels = int(len(rows) * 0.02)
cancel_indices = np.random.choice(len(rows), n_cancels, replace=False)
for idx in cancel_indices:
    rows[idx]["Quantity"] = -abs(rows[idx]["Quantity"])
    rows[idx]["InvoiceNo"] = "C" + rows[idx]["InvoiceNo"]

# ─── Add ~1% null CustomerIDs (guest checkouts) ───────────────────────────────
null_indices = np.random.choice(len(rows), int(len(rows) * 0.01), replace=False)
for idx in null_indices:
    rows[idx]["CustomerID"] = None

df = pd.DataFrame(rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

output_path = "retail_data.csv"
df.to_csv(output_path, index=False)

print(f"Done! Saved {len(df):,} rows to '{output_path}'")
print(f"Customers: {df['CustomerID'].nunique():,}")
print(f"Products:  {df['StockCode'].nunique():,}")
print(f"Date range: {df['InvoiceDate'].min()} → {df['InvoiceDate'].max()}")
print(f"Cancelled invoices: {df[df['InvoiceNo'].str.startswith('C')].shape[0]:,}")
print(f"Null CustomerIDs:   {df['CustomerID'].isna().sum():,}")
