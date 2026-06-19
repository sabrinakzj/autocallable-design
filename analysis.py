# analysis.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import *
from simulation import run_pricing


def scenario_analysis():
    """Multi-scenario analysis: volatility + interest rate + barrier levels"""
    global sigma, r, barrier_out, n_paths

    scenarios = {
        'Base Case': {'sigma': sigma, 'r': r, 'barrier_out': barrier_out},
        'High Vol': {'sigma': sigma * 1.3, 'r': r, 'barrier_out': barrier_out},
        'Low Vol': {'sigma': sigma * 0.7, 'r': r, 'barrier_out': barrier_out},
        'High Rate': {'sigma': sigma, 'r': r * 1.5, 'barrier_out': barrier_out},
        'Low Rate': {'sigma': sigma, 'r': r * 0.5, 'barrier_out': barrier_out},
        'Loose KO (105%)': {'sigma': sigma, 'r': r, 'barrier_out': 1.05},
        'Strict KO (95%)': {'sigma': sigma, 'r': r, 'barrier_out': 0.95},
    }

    results = []
    for name, params in scenarios.items():
        original_sigma, original_r, original_bo = sigma, r, barrier_out
        original_paths = n_paths

        sigma, r, barrier_out = params['sigma'], params['r'], params['barrier_out']
        n_paths = 30000

        res, _ = run_pricing()

        results.append({
            'Scenario': name,
            'Fair Value': res['fair_value'],
            'Knock-Out Prob': res['knock_out_prob'],
            'Knock-In Prob': res['knock_in_prob']
        })

        sigma, r, barrier_out = original_sigma, original_r, original_bo
        n_paths = original_paths

    return pd.DataFrame(results)


def plot_paths(paths, num_samples=50):
    """Plot random sampled paths with barrier lines"""
    plt.figure(figsize=(12, 6))
    sample_paths = paths[:num_samples, :]

    for path in sample_paths:
        plt.plot(path, color='blue', alpha=0.3, linewidth=0.8)

    # Barrier lines
    plt.axhline(y=S0 * barrier_out, color='green', linestyle='--', label=f'Knock-Out ({barrier_out * 100:.0f}%)')
    plt.axhline(y=S0 * barrier_in, color='red', linestyle='--', label=f'Knock-In ({barrier_in * 100:.0f}%)')
    plt.axhline(y=S0, color='gray', linestyle=':', alpha=0.5, label='Initial Level')

    # Observation dates
    for idx in obs_indices:
        plt.axvline(x=idx, color='orange', alpha=0.2, linestyle=':')

    plt.xlabel('Trading Days')
    plt.ylabel('Index Level')
    plt.title(f'Autocallable Path Simulation (n={num_samples} paths)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('outputs/path_simulation.png', dpi=150)
    plt.show()


def plot_distribution(payoffs):
    """Payoff distribution histogram"""
    plt.figure(figsize=(10, 5))
    plt.hist(payoffs, bins=50, color='steelblue', edgecolor='white', alpha=0.8)
    plt.axvline(x=100, color='red', linestyle='--', label='Principal (100)')
    plt.xlabel('Maturity Payoff (per 100 notional)')
    plt.ylabel('Number of Paths')
    plt.title('Autocallable Payoff Distribution')
    plt.legend()
    plt.tight_layout()
    plt.savefig('outputs/payoff_distribution.png', dpi=150)
    plt.show()