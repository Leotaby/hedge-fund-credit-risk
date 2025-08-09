# Hedge Fund Credit Risk Analysis Project

This repository contains a demonstration project designed to showcase skills relevant to the **Wholesale Credit Risk – EMEA Hedge Funds and Asset Managers** role at J.P. Morgan.  The goal is to emulate the workflow of an analyst who must assess a hedge fund’s counter‑party credit risk, quantify exposures to market factors and communicate results clearly to stakeholders.

## Project Overview

The project consists of two main stages:

1. **Data Ingestion and Storage.**  Using Python and SQLite, we ingest publicly available financial datasets and populate a relational database.  The database schema includes tables for Fama–French factor returns, daily equity price histories, hedge funds and their positions.  The data used come from widely cited academic and market sources.  For example, the Fama–French five‑factor data file contains daily returns for the market excess return and factors `SMB`, `HML`, `RMW` and `CMA` along with the risk‑free rate【773800767166952†L0-L44】.  Equity price files provide open, high, low, close, adjusted close and volume for each trading day.  All files reside under the `data/` directory and are loaded via the `scripts/create_database.py` program.

2. **Risk Analysis.**  The core analysis lives in `scripts/analyze_risk.py`.  This script reads data from the SQLite database, computes daily log returns for each asset and constructs portfolio returns for several example hedge funds based on their holdings.  It then aligns those returns with factor returns by harmonising date formats and estimates the funds’ exposures (betas) to the Fama–French factors through ordinary least squares regression.  The script also calculates historical 95 % **Value at Risk (VaR)** and **Expected Shortfall (ES)** for each fund, two key metrics used by credit risk managers to assess potential losses under adverse market conditions.  Finally, it produces visualisations of cumulative returns, return distributions annotated with VaR thresholds, and bar charts of factor exposures.  Results are written to the `results/` directory in both CSV and PNG formats.

## Files and Structure

```
credit_risk_project/
│
├─ data/                    # Source CSV files for factors and asset prices
├─ scripts/                 # Python scripts to create the database and run analysis
│   ├─ create_database.py   # Populates SQLite database with factors, prices and fund positions
│   └─ analyze_risk.py      # Performs risk analysis, produces summary statistics and plots
├─ results/                 # Generated outputs: portfolio returns, summary metrics and charts
└─ risk_management.db       # SQLite database created by create_database.py
```

## Methodology

### Database Construction

Running `python scripts/create_database.py` builds a fresh SQLite database (`risk_management.db`).  It defines four tables:

* **factor_returns** – stores the Fama–French five factor data with columns `date`, `mkt_rf`, `smb`, `hml`, `rmw`, `cma` and `rf`.
* **asset_prices** – daily price history for each asset with columns `date`, `asset`, `open`, `high`, `low`, `close`, `adj_close` and `volume`.  Data for the S&P 500 index (SPX), Apple (AAPL) and Amazon (AMZN) are included.  A sample from the SPX file shows the typical structure: date, open, high, low, close, adjusted close and volume【773800767166952†L0-L44】.
* **funds** – a simple reference table listing three hypothetical hedge funds.
* **positions** – the quantity of each asset held by each fund.  These positions are illustrative; in practice they would be obtained from internal books and records.

### Risk Analysis and Modelling

The analysis script demonstrates several techniques that are central to credit risk management:

1. **Return Computation:** Adjusted close prices are converted to daily log returns.  Log returns are additive over time and common in risk modelling.

2. **Portfolio Aggregation:** Asset returns are combined into fund‑level returns based on position weights.  The script normalises by total exposure to obtain a weighted average return for each day.

3. **Factor Exposure Estimation:** After aligning portfolio returns with factor returns by date, the script subtracts the risk‑free rate to obtain excess returns.  It then regresses excess returns on the five Fama–French factors to estimate betas (sensitivity to each factor) and alpha (unexplained return).  These coefficients help assess how market movements impact each fund’s performance.

4. **Risk Metrics:** The 95 % Value at Risk (VaR) and Expected Shortfall (ES) are computed using the empirical distribution of portfolio returns.  VaR represents the threshold loss not exceeded 95 % of the time, while ES measures the average loss in the worst 5 % of cases.  These metrics provide insight into tail risk and are widely used in counterparty credit analysis and regulatory capital calculations.

5. **Visual Communication:** Cumulative return charts summarise performance over time, return distribution histograms highlight skewness and fat tails, and factor exposure bar plots illustrate which systematic risks each fund carries.  Clear visualisations are essential when presenting risk assessments to senior management and regulators.

## Results Summary

The table below summarises key metrics for the example funds.  Betas greater than zero indicate positive exposure to the corresponding factor, while negative values indicate that the fund benefits when the factor underperforms.  Alpha reflects average excess return unexplained by the five factors.

| Fund | Alpha | Mkt‑RF β | SMB β | HML β | RMW β | CMA β | 95 % VaR | 95 % ES |
|-----:|------:|--------:|------:|------:|------:|------:|--------:|--------:|
| Equity Hedge Fund | 0.00046 | 0.99 | –0.21 | –0.28 | –0.02 | –0.58 | 0.0255 | 0.0340 |
| Long/Short Fund | 0.00040 | 1.02 | –0.23 | –0.34 | –0.06 | –0.59 | 0.0261 | 0.0348 |
| Tech Focused Fund | 0.00065 | 0.95 | –0.20 | –0.27 | 0.03 | –0.70 | 0.0267 | 0.0390 |

All three funds have market beta close to one, implying that their returns move broadly in line with the overall market.  Negative loadings on the value (`HML`) and profitability (`RMW`) factors suggest a growth‑oriented bias, which is typical for technology and long/short strategies.  The Tech Focused Fund exhibits the highest expected shortfall, reflecting greater tail risk compared with the other funds.  Such insights would inform credit approvals, limit setting and ongoing monitoring.

## How This Aligns With the Role

The responsibilities of a **Wholesale Credit Risk – EMEA Hedge Funds and Asset Managers** analyst include assessing counterparty exposure, analysing market events, building financial models, preparing presentations and collaborating with colleagues.  This project touches on each of these facets:

* **Data Sourcing and Management:** The scripts ingest free, reputable datasets into a structured database, mirroring how risk analysts gather and organise market and client data.
* **Quantitative Modelling:** By computing returns, estimating factor exposures and calculating VaR/ES, the project demonstrates the ability to build quantitative models that translate market information into risk metrics.
* **Scenario Analysis:** Although the sample analysis uses historical distributions, the modular functions could be extended to perform stress testing under hypothetical shocks or incorporate additional factors (e.g., liquidity, leverage) as would be expected in a real credit review.
* **Communication:** The generated charts and summary reports can be used in presentations to explain complex risk concepts to non‑experts, aligning with the requirement to prepare presentations and outline recommendations to senior management.
* **Collaboration:** The repository is organised for ease of understanding and extensibility, making it straightforward for teammates to reproduce and build upon the analysis.

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/Leotaby/credit_risk_project.git
cd credit_risk_project
```

2. Create a Python virtual environment (optional but recommended) and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy matplotlib
```

3. Build the SQLite database and run the analysis:

```bash
python scripts/create_database.py
python scripts/analyze_risk.py
```

Outputs will appear in the `results/` directory.

## Future Extensions

* Incorporate additional assets (e.g., bonds, derivatives) and risk factors (momentum, volatility) to enrich the analysis.
* Implement scenario analysis and stress testing, for example by shocking factor returns or simulating extreme market events.
* Add a front‑end interface (e.g., Jupyter notebooks or dashboards) to interactively explore results and tailor risk assessments for individual counterparties.

## License

This project is provided for educational purposes.  Data sources used herein originate from the public domain or freely available academic repositories; users should check the terms of use before applying them in a production setting.
