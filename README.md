
# Autocallable Structured Product Design & Pricing Engine

This project implements a complete workflow—from market data fetching and Monte Carlo simulation to Greeks calculation and dynamic delta hedging backtesting. Designed for coursework reference.

---

## 📌 Key Features

- **Dual Pricing Models**: Supports both classic **Geometric Brownian Motion (GBM)** and the more market-realistic **Heston stochastic volatility model** for easy comparison.
- **Full Risk Metrics**: Computes **Delta, Gamma, Vega, and Rho** with intuitive risk interpretations.
- **Scenario Analysis**: Flexibly adjust volatility, interest rates, barrier levels, etc., to observe impacts on fair value and knock-out/in probabilities.
- **Dynamic Hedging Backtest**: Simulates the issuer's delta-hedging process, comparing **daily** vs. **weekly** rebalancing strategies in terms of cost and tracking error.
- **Automated Termsheet Generation**: Produces professional **TXT** and **PDF** product term sheets directly from pricing results.
- **Visual Outputs**: Automatically generates key charts including price paths, payoff distributions, and hedging performance.

---

## 📂 Project Structure
autocallable-design/
├── main.py # Main entry point – runs the entire pipeline  
├── config.py # Configuration (product terms, market params, proxy settings)  
├── simulation.py # GBM simulation & core pricing engine  
├── heston.py # Heston model simulation & pricing  
├── greeks.py # Greeks calculation (finite difference)  
├── analysis.py # Scenario analysis & charting  
├── hedging.py # Delta hedging backtest module  
├── generate_termsheet.py # Termsheet generator (TXT & PDF)  
├── outputs/ # Auto-generated after running (results, charts, term sheets)  
│ ├── Termsheet.txt  
│ ├── path_simulation.png  
│ ├── payoff_distribution.png  
│ └── hedging_backtest.png  
└── README.md  

---

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have Python 3.8 or higher installed.

```bash
git clone https://github.com/sabrinakzj/autocallable-design.git
cd autocallable-design
```

### 2. Run the Main Program
```python main.py
```

### The program will sequentially:
Fetch the latest Hang Seng Index price.
Run pricing under both GBM and Heston models.
Compute Greeks and scenario analysis.
Generate charts and term sheets.
Execute delta hedging backtest.

### Generated Termsheet

outputs.pdf will include:
Product summary and payoff mechanism.
Key definitions.
Pricing results and Greeks.
Scenario analysis table.
Important disclaimers.

**This code is for educational and research purposes only and does not constitute any investment advice or trading recommendation.
All pricing and risk data are indicative estimates only. Actual trading should reference official documents and market quotes.
The author assumes no responsibility for any investment decisions made based on this project.**
