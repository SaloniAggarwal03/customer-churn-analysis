"""
churn_analysis.py
=================
Full EDA + RFM Segmentation for the Online Retail dataset.

Run from the project1-customer-churn/analysis/ directory.

Usage:
    pip install pandas numpy matplotlib seaborn
    python churn_analysis.py

Outputs:
    Prints segment stats to console.
    Saves charts: rfm_segments.png, revenue_trend.png, top_products.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from datetime import datetime
import warnings
import os

warnings.filterwarnings("ignore")

# ─── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0f0f11",
    "axes.facecolor":   "#0f0f11",
    "axes.edgecolor":   "#2a2a35",
    "axes.labelcolor":  "#c8c8d4",
    "xtick.color":      "#7a7a8c",
    "ytick.color":      "#7a7a8c",
    "text.color":       "#e8e8f0",
    "grid.color":       "#1e1e2a",
    "grid.linestyle":   "--",
    "font.family":      "monospace",
    "figure.dpi":       120,
})

PALETTE = {
    "Champion": "#7c6af5",
    "Loyal":    "#3ecfb2",
    "AtRisk":   "#f5a623",
    "Lost":     "#e05c5c",
}

# ─── Load data ────────────────────────────────────────────────────────────────
data_path = os.path.join(os.path.dirname(__file__), "../data/retail_data.csv")
print("Loading data...")
df = pd.read_csv(data_path, parse_dates=["InvoiceDate"])
print(f"  Raw rows: {len(df):,}")

# ─── Clean ────────────────────────────────────────────────────────────────────
print("\nCleaning data...")
original_len = len(df)

# Drop null CustomerIDs (guest checkouts — can't track churn)
df = df.dropna(subset=["CustomerID"])
print(f"  Dropped {original_len - len(df):,} rows with null CustomerID")

# Drop cancelled invoices (negative quantities)
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
print(f"  Removed cancelled invoices. Rows remaining: {len(df):,}")

# Drop zero/negative prices and quantities
df = df[(df["UnitPrice"] > 0) & (df["Quantity"] > 0)]
print(f"  Removed invalid prices/quantities. Rows remaining: {len(df):,}")

# Drop duplicates
df = df.drop_duplicates()
print(f"  Removed duplicates. Final rows: {len(df):,}")

# Calculate revenue per row
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

# ─── EDA Summary ─────────────────────────────────────────────────────────────
print("\n── EDA Summary ─────────────────────────────────────────────────────")
print(f"  Total revenue:       £{df['Revenue'].sum():>12,.2f}")
print(f"  Total customers:     {df['CustomerID'].nunique():>12,}")
print(f"  Total transactions:  {df['InvoiceNo'].nunique():>12,}")
print(f"  Avg order value:     £{(df.groupby('InvoiceNo')['Revenue'].sum().mean()):>12,.2f}")
print(f"  Date range:          {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}")
print(f"  Countries:           {df['Country'].nunique():>12,}")

# ─── RFM Analysis ────────────────────────────────────────────────────────────
print("\nCalculating RFM scores...")
SNAPSHOT_DATE = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("CustomerID").agg(
    Recency   = ("InvoiceDate", lambda x: (SNAPSHOT_DATE - x.max()).days),
    Frequency = ("InvoiceNo",   "nunique"),
    Monetary  = ("Revenue",     "sum"),
).reset_index()

# Score 1-4 (4 = best)
rfm["R_Score"] = pd.qcut(rfm["Recency"],   4, labels=[4, 3, 2, 1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"),  4, labels=[1, 2, 3, 4]).astype(int)
rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

# Assign segments
def segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 3 and f >= 3 and m >= 3:   return "Champion"
    if r >= 2 and f >= 2:               return "Loyal"
    if r <= 2 and f >= 2:               return "AtRisk"
    return "Lost"

rfm["Segment"] = rfm.apply(segment, axis=1)

# ─── Segment Stats ────────────────────────────────────────────────────────────
print("\n── RFM Segment Summary ─────────────────────────────────────────────")
seg_stats = rfm.groupby("Segment").agg(
    Count     = ("CustomerID", "count"),
    Avg_Recency   = ("Recency",    "mean"),
    Avg_Frequency = ("Frequency",  "mean"),
    Avg_Monetary  = ("Monetary",   "mean"),
    Total_Revenue = ("Monetary",   "sum"),
).reset_index()

total_rev = seg_stats["Total_Revenue"].sum()
seg_stats["Revenue_Share_%"] = (seg_stats["Total_Revenue"] / total_rev * 100).round(1)
seg_stats["Customer_Share_%"] = (seg_stats["Count"] / seg_stats["Count"].sum() * 100).round(1)

for _, row in seg_stats.iterrows():
    print(f"\n  [{row['Segment']:10s}]")
    print(f"    Customers:    {int(row['Count']):,} ({row['Customer_Share_%']}%)")
    print(f"    Avg Recency:  {row['Avg_Recency']:.0f} days since last purchase")
    print(f"    Avg Orders:   {row['Avg_Frequency']:.1f}")
    print(f"    Avg Spend:    £{row['Avg_Monetary']:,.2f}")
    print(f"    Revenue Share: {row['Revenue_Share_%']}%")

# ─── Save RFM data for dashboard ─────────────────────────────────────────────
rfm_out = os.path.join(os.path.dirname(__file__), "../data/rfm_segments.csv")
rfm.to_csv(rfm_out, index=False)
print(f"\nSaved RFM data to: {rfm_out}")

# ─── Chart 1: Segment Distribution (donut) ───────────────────────────────────
print("\nGenerating charts...")
seg_counts = rfm["Segment"].value_counts()
colors = [PALETTE[s] for s in seg_counts.index]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Customer Segmentation — RFM Analysis", fontsize=14, color="#e8e8f0", y=1.01)

# Donut
wedges, texts, autotexts = axes[0].pie(
    seg_counts.values, labels=seg_counts.index,
    colors=colors, autopct="%1.1f%%", pctdistance=0.8,
    wedgeprops={"width": 0.5, "edgecolor": "#0f0f11", "linewidth": 2},
)
for t in texts:    t.set_color("#c8c8d4")
for t in autotexts: t.set_color("#0f0f11"); t.set_fontweight("bold")
axes[0].set_title("Customer Count by Segment", color="#e8e8f0", pad=10)

# Revenue bar
rev_by_seg = rfm.groupby("Segment")["Monetary"].sum().sort_values(ascending=True)
bar_colors = [PALETTE[s] for s in rev_by_seg.index]
bars = axes[1].barh(rev_by_seg.index, rev_by_seg.values, color=bar_colors, height=0.5)
axes[1].set_title("Total Revenue by Segment", color="#e8e8f0", pad=10)
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))
axes[1].grid(axis="x", alpha=0.3)
for bar, val in zip(bars, rev_by_seg.values):
    axes[1].text(val + 500, bar.get_y() + bar.get_height()/2,
                 f"£{val:,.0f}", va="center", fontsize=9, color="#c8c8d4")

plt.tight_layout()
chart1_path = os.path.join(os.path.dirname(__file__), "rfm_segments.png")
plt.savefig(chart1_path, bbox_inches="tight", facecolor="#0f0f11")
print(f"  Saved: {chart1_path}")
plt.close()

# ─── Chart 2: Monthly Revenue Trend ─────────────────────────────────────────
df["Month"] = df["InvoiceDate"].dt.to_period("M")
monthly = df.groupby("Month")["Revenue"].sum().reset_index()
monthly["Month"] = monthly["Month"].astype(str)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly["Month"], monthly["Revenue"], color="#7c6af5", linewidth=2.5, marker="o", markersize=5)
ax.fill_between(monthly["Month"], monthly["Revenue"], alpha=0.15, color="#7c6af5")
ax.set_title("Monthly Revenue Trend", fontsize=13, color="#e8e8f0", pad=12)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))
ax.grid(alpha=0.3)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
chart2_path = os.path.join(os.path.dirname(__file__), "revenue_trend.png")
plt.savefig(chart2_path, bbox_inches="tight", facecolor="#0f0f11")
print(f"  Saved: {chart2_path}")
plt.close()

# ─── Chart 3: Top Products by Revenue ───────────────────────────────────────
top_products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(12, 6))
colors_bar = [plt.cm.plasma(i / 10) for i in range(10)]
bars = ax.barh(top_products["Description"][::-1], top_products["Revenue"][::-1],
               color=colors_bar[::-1], height=0.6)
ax.set_title("Top 10 Products by Revenue", fontsize=13, color="#e8e8f0", pad=12)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
chart3_path = os.path.join(os.path.dirname(__file__), "top_products.png")
plt.savefig(chart3_path, bbox_inches="tight", facecolor="#0f0f11")
print(f"  Saved: {chart3_path}")
plt.close()

print("\nAll charts saved. Open dashboard/index.html for the interactive view.")
print("Analysis complete!")
