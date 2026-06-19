# greeks.py
# greeks.py
import numpy as np
from config import *
from simulation import simulate_gbm, price_autocallable


def price_at_params(S0_adj=None, sigma_adj=None, r_adj=None):
    """
    在给定参数下重新定价（用于Greeks计算）
    只调整指定参数，其他保持默认
    """
    global r  # ✅ 必须在函数开头声明

    local_S0 = S0_adj if S0_adj is not None else S0
    local_sigma = sigma_adj if sigma_adj is not None else sigma
    local_r = r_adj if r_adj is not None else r

    paths = simulate_gbm(local_S0, mu, local_sigma, tenor_years, total_steps, n_paths)

    # 临时修改全局利率
    original_r = r
    r = local_r
    result = price_autocallable(paths)
    r = original_r  # 恢复原值

    return result['fair_value']


def compute_greeks(shift=0.01):
    """
    用中心差分法计算 Delta, Gamma, Vega, Rho
    shift: 扰动幅度（1%）
    """
    price_base = price_at_params()

    # Delta: dP/dS
    price_up = price_at_params(S0_adj=S0 * (1 + shift))
    price_down = price_at_params(S0_adj=S0 * (1 - shift))
    delta = (price_up - price_down) / (2 * S0 * shift)

    # Gamma: d²P/dS²
    gamma = (price_up - 2 * price_base + price_down) / ((S0 * shift) ** 2)

    # Vega: dP/dsigma
    price_up = price_at_params(sigma_adj=sigma * (1 + shift))
    price_down = price_at_params(sigma_adj=sigma * (1 - shift))
    vega = (price_up - price_down) / (2 * sigma * shift)

    # Rho: dP/dr
    price_up = price_at_params(r_adj=r * (1 + shift))
    price_down = price_at_params(r_adj=r * (1 - shift))
    rho = (price_up - price_down) / (2 * r * shift)

    return {
        'delta': delta,
        'gamma': gamma,
        'vega': vega,
        'rho': rho,
        'price_base': price_base
    }

def greeks_interpretation(greeks):
    """Generate interview-level Greeks interpretation"""
    msg = f"""
    === Greeks Interpretation ===
    Delta: {greeks['delta']:.4f} → Price changes by {greeks['delta']*100:.4f} HKD for every 1% move in underlying (per 100 notional)
    Gamma: {greeks['gamma']:.4f} → Rate of change of Delta, amplifies near knock-out barrier
    Vega:  {greeks['vega']:.4f} → Price changes by {greeks['vega']:.4f} HKD for every 1% move in implied volatility
    Rho:   {greeks['rho']:.4f} → Price changes by {greeks['rho']:.4f} HKD for every 1% move in interest rate

    ⚠️ Key Insight: Vega is typically negative (higher volatility → higher knock-in probability → lower product value)
    """
    return msg