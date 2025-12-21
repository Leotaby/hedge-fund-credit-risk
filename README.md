# 📊 Hedge Fund Credit Risk Analysis Framework

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![pandas](https://img.shields.io/badge/pandas-1.5+-150458.svg?logo=pandas)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243.svg?logo=numpy)](https://numpy.org/)

> **Quantitative risk modeling toolkit for hedge funds and asset managers**  
> VaR calculations, scenario analysis, counterparty exposure, and regulatory reporting

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Modules](#-modules)
- [Examples](#-examples)
- [Methodology](#-methodology)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)

---

## 🎯 Overview

A comprehensive **credit risk analysis framework** designed for:

- **Hedge Funds** - Portfolio-level credit exposure and VaR
- **Asset Managers** - Counterparty risk assessment
- **Risk Teams** - Regulatory stress testing (Basel III/IV alignment)
- **Researchers** - Quantitative risk modeling experimentation

### Why This Project?

Traditional risk systems are often black boxes. This framework provides:

1. **Transparency** - Full visibility into risk calculations
2. **Flexibility** - Modular design for custom risk metrics
3. **Reproducibility** - Version-controlled, tested codebase
4. **Education** - Well-documented methodology

---

## ✨ Features

| Module | Description |
|--------|-------------|
| **VaR Engine** | Historical, Parametric, and Monte Carlo VaR |
| **Scenario Analysis** | Stress testing with custom shock scenarios |
| **Counterparty Risk** | PFE, CVA, and exposure-at-default calculations |
| **Portfolio Analytics** | Concentration risk, sector exposure, correlation |
| **Reporting** | Automated risk reports with visualizations |

---

## 🛠 Installation

### Prerequisites

- Python 3.9+
- pip or conda

### Install

```bash
# Clone the repository
git clone https://github.com/Leotaby/hedge-fund-credit-risk.git
cd hedge-fund-credit-risk

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
pandas>=1.5.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
yfinance>=0.2.0
pytest>=7.0.0
```

---

## 🚀 Quick Start

```python
from risk_engine import PortfolioRisk, VaRCalculator
from data_loader import load_portfolio

# Load sample portfolio
portfolio = load_portfolio("data/sample_portfolio.csv")

# Initialize risk calculator
risk = PortfolioRisk(portfolio)

# Calculate VaR at 95% confidence, 10-day horizon
var_95 = risk.calculate_var(confidence=0.95, horizon=10, method="historical")
print(f"10-day 95% VaR: ${var_95:,.2f}")

# Run stress test
stress_results = risk.stress_test(scenario="2008_financial_crisis")
print(f"Stress Loss: ${stress_results['total_loss']:,.2f}")

# Generate risk report
risk.generate_report(output_path="reports/risk_report.html")
```

---

## 📦 Modules

### 1. VaR Calculator (`risk_engine/var.py`)

Three methodologies for Value-at-Risk:

```python
from risk_engine.var import VaRCalculator

calc = VaRCalculator(returns_data)

# Historical VaR - uses actual return distribution
historical_var = calc.historical_var(confidence=0.99)

# Parametric VaR - assumes normal distribution
parametric_var = calc.parametric_var(confidence=0.99)

# Monte Carlo VaR - simulates price paths
monte_carlo_var = calc.monte_carlo_var(
    confidence=0.99,
    simulations=10000,
    horizon=10
)
```

### 2. Scenario Analysis (`risk_engine/scenarios.py`)

Pre-built and custom stress scenarios:

```python
from risk_engine.scenarios import ScenarioEngine

engine = ScenarioEngine(portfolio)

# Pre-built scenarios
results = engine.run_scenario("covid_march_2020")
results = engine.run_scenario("2008_financial_crisis")
results = engine.run_scenario("dot_com_bubble")

# Custom scenario
custom_shocks = {
    "equity": -0.30,      # 30% equity drop
    "credit_spread": 200,  # 200bps spread widening
    "rates": -0.50,       # 50bps rate cut
    "fx_usd": 0.10        # 10% USD appreciation
}
results = engine.run_custom_scenario(custom_shocks)
```

### 3. Counterparty Risk (`risk_engine/counterparty.py`)

Exposure metrics for OTC derivatives:

```python
from risk_engine.counterparty import CounterpartyRisk

cpty_risk = CounterpartyRisk(derivative_portfolio)

# Potential Future Exposure
pfe = cpty_risk.calculate_pfe(confidence=0.95, horizon=365)

# Credit Valuation Adjustment
cva = cpty_risk.calculate_cva(
    counterparty_pd=0.02,  # 2% probability of default
    lgd=0.60               # 60% loss given default
)

# Exposure at Default
ead = cpty_risk.calculate_ead()
```

### 4. Portfolio Analytics (`risk_engine/analytics.py`)

Concentration and correlation analysis:

```python
from risk_engine.analytics import PortfolioAnalytics

analytics = PortfolioAnalytics(portfolio)

# Sector concentration
sector_exposure = analytics.sector_concentration()

# Top N holdings
top_holdings = analytics.top_holdings(n=10)

# Correlation matrix
corr_matrix = analytics.correlation_matrix()

# Herfindahl-Hirschman Index (concentration)
hhi = analytics.calculate_hhi()
```

---

## 📈 Examples

### Example 1: Daily Risk Report

```python
from risk_engine import RiskReport
from datetime import date

report = RiskReport(portfolio, as_of_date=date.today())

# Generate comprehensive report
report.add_var_summary()
report.add_stress_tests()
report.add_concentration_analysis()
report.add_pnl_attribution()

report.export_html("reports/daily_risk_report.html")
report.export_pdf("reports/daily_risk_report.pdf")
```

### Example 2: Backtesting VaR Model

```python
from risk_engine.backtest import VaRBacktest

backtest = VaRBacktest(
    returns=historical_returns,
    var_confidence=0.99,
    lookback_window=250
)

results = backtest.run()

print(f"VaR Breaches: {results['breaches']}")
print(f"Breach Rate: {results['breach_rate']:.2%}")
print(f"Kupiec Test p-value: {results['kupiec_pvalue']:.4f}")

backtest.plot_breaches(save_path="reports/var_backtest.png")
```

### Example 3: Monte Carlo Simulation

```python
from risk_engine.simulation import MonteCarloSimulator

simulator = MonteCarloSimulator(
    portfolio=portfolio,
    num_simulations=10000,
    horizon_days=252  # 1 year
)

paths = simulator.simulate()

# Analyze distribution of terminal values
terminal_values = paths[:, -1]
print(f"Expected Value: ${terminal_values.mean():,.2f}")
print(f"5th Percentile: ${np.percentile(terminal_values, 5):,.2f}")
print(f"95th Percentile: ${np.percentile(terminal_values, 95):,.2f}")

simulator.plot_paths(num_paths=100)
```

---

## 📐 Methodology

### Value at Risk (VaR)

**Historical VaR:**
```
VaR_α = -Percentile(returns, 1-α)
```

**Parametric VaR:**
```
VaR_α = μ - σ × Φ⁻¹(α) × √t
```
Where Φ⁻¹ is the inverse standard normal CDF.

**Monte Carlo VaR:**
```
1. Estimate return distribution parameters
2. Generate N simulated price paths
3. Calculate portfolio value for each path
4. VaR = percentile of simulated losses
```

### Credit Valuation Adjustment (CVA)

```
CVA = LGD × Σ EE(tᵢ) × PD(tᵢ₋₁, tᵢ) × DF(tᵢ)
```

Where:
- `EE(t)` = Expected Exposure at time t
- `PD(t₁,t₂)` = Probability of Default between t₁ and t₂
- `DF(t)` = Discount Factor to time t
- `LGD` = Loss Given Default

---

## 📁 Project Structure

```
hedge-fund-credit-risk/
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── risk_engine/
│   ├── __init__.py
│   ├── var.py              # VaR calculations
│   ├── scenarios.py        # Stress testing
│   ├── counterparty.py     # Counterparty risk
│   ├── analytics.py        # Portfolio analytics
│   ├── simulation.py       # Monte Carlo
│   ├── backtest.py         # Model validation
│   └── report.py           # Report generation
├── data_loader/
│   ├── __init__.py
│   ├── portfolio.py        # Portfolio loading
│   └── market_data.py      # Market data fetching
├── data/
│   ├── sample_portfolio.csv
│   └── scenarios/
│       ├── 2008_crisis.json
│       └── covid_2020.json
├── tests/
│   ├── test_var.py
│   ├── test_scenarios.py
│   └── test_counterparty.py
├── notebooks/
│   ├── 01_var_analysis.ipynb
│   ├── 02_stress_testing.ipynb
│   └── 03_cva_calculation.ipynb
└── reports/
    └── .gitkeep
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=risk_engine --cov-report=html

# Run specific test module
pytest tests/test_var.py -v
```

---

## 🗺 Roadmap

- [x] Historical VaR
- [x] Parametric VaR
- [x] Monte Carlo VaR
- [x] Scenario Analysis
- [x] Basic Reporting
- [ ] Expected Shortfall (ES/CVaR)
- [ ] Incremental VaR
- [ ] Component VaR
- [ ] Real-time risk streaming
- [ ] Integration with Bloomberg API
- [ ] FRTB-compliant calculations

---

## 📚 References

- Hull, J.C. (2018). *Risk Management and Financial Institutions*
- Jorion, P. (2007). *Value at Risk: The New Benchmark for Managing Financial Risk*
- Gregory, J. (2020). *The xVA Challenge: Counterparty Risk, Funding, Collateral, Capital and Initial Margin*
- Basel Committee on Banking Supervision - [Minimum capital requirements for market risk](https://www.bis.org/bcbs/publ/d457.htm)

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Hatef Tabbakhian**  
MSc Economics & Finance | Risk & Quantitative Analysis

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://linkedin.com/in/hateftaby)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/Leotaby)
