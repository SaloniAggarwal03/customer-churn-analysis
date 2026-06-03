# Customer Churn Analysis & Retention Strategy
### A Data Analytics Project by Saloni Aggarwal

---

## Project Overview

This project analyzes customer transaction data from a UK-based online retail company to identify churned customers, segment active ones using **RFM analysis**, and propose a data-driven retention strategy.

The dataset contains **500,000+ transactions** spanning 2010–2011 from the [UCI Online Retail II Dataset](https://archive.ics.uci.edu/ml/datasets/Online+Retail+II).

---

## Business Problem

> *"Which customers are at risk of leaving, and what should the marketing team do about it?"*

Acquiring a new customer costs **5x more** than retaining an existing one. This analysis helps the retail team focus retention budgets on the right customer segments.

---

## Skills Demonstrated

- Data cleaning & preprocessing (handling nulls, duplicates, negative values)
- Exploratory Data Analysis (EDA)
- RFM (Recency, Frequency, Monetary) customer segmentation
- Data visualization and business storytelling
- Actionable recommendation writing

---

## Project Structure

```
project1-customer-churn/
│
├── data/
│   └── generate_data.py         # Generates realistic retail dataset
│
├── analysis/
│   └── churn_analysis.py        # Full EDA + RFM segmentation script
│
├── dashboard/
│   └── index.html               # Interactive dashboard (open in browser)
│
└── README.md
```

---

## How to Run

### Step 1 — Generate the dataset
```bash
cd data
python generate_data.py
```
This creates `retail_data.csv` (~500K rows of realistic transaction data).

### Step 2 — Run the analysis
```bash
cd analysis
pip install pandas numpy matplotlib seaborn
python churn_analysis.py
```
This prints segment statistics and saves charts to the `analysis/` folder.

### Step 3 — View the dashboard
Open `dashboard/index.html` in any browser. No server needed.

---

## Key Findings

| Segment | % of Customers | Revenue Share | Action |
|---|---|---|---|
| Champions | 18% | 52% | Reward & upsell |
| Loyal | 22% | 28% | Nurture with exclusives |
| At Risk | 24% | 14% | Win-back campaigns |
| Lost | 36% | 6% | Low-cost reactivation |

---

## Retention Strategy Recommendations

1. **Champions (18%)** — Launch a VIP loyalty program with early access to new products. These customers drive 52% of revenue and respond well to exclusivity.

2. **Loyal Customers (22%)** — Send personalized "thank you" emails with 10% loyalty discounts. Cross-sell complementary product categories based on their purchase history.

3. **At-Risk Customers (24%)** — Trigger automated win-back emails when a customer hasn't purchased in 60+ days. Offer a limited-time 15% discount with urgency messaging.

4. **Lost Customers (36%)** — Run a low-budget SMS/email reactivation campaign. If no response after 2 attempts, deprioritize to reduce marketing spend waste.

**Projected Impact**: Retaining just 5% of At-Risk customers can increase overall revenue by ~3.2% based on their average order value.

---

## Tools & Technologies

`Python` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `HTML/CSS/JavaScript` · `Chart.js`

---

## Certifications Referenced

This project applies skills from:
- **Deloitte Data Analytics Job Simulation** (Forage, March 2026) — data analysis & forensic technology
- **Quantium Data Analytics Job Simulation** (Forage, April 2026) — customer analytics & commercial application

---

*Dataset simulated for portfolio purposes based on UCI Online Retail II dataset structure.*
