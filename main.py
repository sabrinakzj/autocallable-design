# main.py（整合版）
import os
import numpy as np
from config import *
from simulation import run_pricing
from greeks import compute_greeks, greeks_interpretation
from analysis import scenario_analysis, plot_paths, plot_distribution
from generate_termsheet import generate_full_termsheet
from heston import compare_gbm_vs_heston
from hedging import run_full_hedging_analysis

# 创建输出文件夹
os.makedirs('outputs', exist_ok=True)

print("=" * 60)
print("🚀 Autocallable Structured Product Pricing Model")
print("=" * 60)

# 1. GBM Pricing
print("\n📊 Running GBM Monte Carlo simulation...")
results, paths = run_pricing()

print(f"""
=== Pricing Results (GBM) ===
📌 Product Fair Value (per 100 notional): {results['fair_value']:.4f}
📌 Knock-Out Probability: {results['knock_out_prob']*100:.2f}%
📌 Knock-In Probability: {results['knock_in_prob']*100:.2f}%
""")

# 2. Greeks
print("\n📐 Computing Greeks risk exposures...")
greeks = compute_greeks()
print(greeks_interpretation(greeks))

# 3. Scenario Analysis
print("\n📈 Running scenario analysis...")
scenario_df = scenario_analysis()
print(scenario_df.to_string(index=False))

# 4. Visualizations
print("\n🎨 Generating charts...")
plot_paths(paths, num_samples=50)
plot_distribution(results['payoffs'])

# 5. Termsheet Generation
print("\n📄 Generating Termsheet...")
generate_full_termsheet(results, greeks, scenario_df)

# 6. Heston Model Comparison
print("\n" + "=" * 60)
print("📊 Extension 1: Heston Stochastic Volatility Model")
print("=" * 60)
gbm_res, heston_res, heston_paths = compare_gbm_vs_heston()

# 7. Delta Hedging Backtest
print("\n" + "=" * 60)
print("📊 Extension 2: Delta Hedging Backtest")
print("=" * 60)
hedge_daily, hedge_weekly = run_full_hedging_analysis(n_paths_hedge=5000)

print("\n" + "=" * 60)
print("✅ All analyses complete!")
print("   📄 Termsheet.txt / Termsheet.pdf")
print("   📊 path_simulation.png")
print("   📊 payoff_distribution.png")
print("   📊 hedging_backtest.png")
print("=" * 60)