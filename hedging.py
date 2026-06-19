# hedging.py
"""
Delta对冲回测模块
模拟银行发行Autocallable后的动态对冲过程
"""

import numpy as np
import matplotlib.pyplot as plt
from config import S0, r, sigma, barrier_out, barrier_in, coupon_rate, tenor_years, total_steps, n_obs

def calculate_delta_autocallable(path, S0, barrier_out, barrier_in, coupon_rate, tenor_years, n_obs):
    """
    计算单条路径在某一天的Delta（用有限差分法）
    简化版：用路径当前位置计算Delta
    """
    # 这是一个简化实现，实际中需要用完整的定价引擎
    # 这里返回一个近似的Delta值
    current_price = path[-1] if isinstance(path, np.ndarray) else path

    # 简单近似：如果接近敲出线，Delta急剧上升
    if current_price >= S0 * barrier_out * 0.95:
        return 1.0  # 接近敲出，Delta接近1
    elif current_price <= S0 * barrier_in * 1.05:
        return 0.0  # 接近敲入，Delta接近0
    else:
        # 中间区域，Delta约等于 (current_price - barrier_in*S0) / (barrier_out*S0 - barrier_in*S0)
        return max(0, min(1, (current_price - S0 * barrier_in) / (S0 * (barrier_out - barrier_in))))


def run_delta_hedging_backtest(paths, rebalance_freq='daily'):
    """
    运行Delta对冲回测

    Parameters:
    -----------
    paths : ndarray, shape (n_paths, n_days), 模拟的价格路径
    rebalance_freq : str, 'daily' 或 'weekly'

    Returns:
    --------
    hedging_results : dict, 包含对冲成本、误差等
    """
    n_paths, n_days = paths.shape
    dt = tenor_years / n_days

    # 选择一条代表性路径进行展示
    # 选择中位数路径（按最终价格排序）
    final_prices = paths[:, -1]
    median_idx = np.argsort(final_prices)[n_paths // 2]
    path = paths[median_idx]

    # 初始化对冲组合
    cash = 0.0  # 现金账户
    position = 0.0  # 持有指数数量
    hedge_costs = []
    portfolio_values = []
    deltas = []

    # 初始时刻：发行产品，收到本金100
    # 同时买入Delta份指数进行对冲
    initial_delta = calculate_delta_autocallable(path[0], S0, barrier_out, barrier_in,
                                                 coupon_rate, tenor_years, n_obs)
    position = initial_delta * 100 / S0  # 买入指数
    cash -= position * S0  # 支付现金
    portfolio_value = cash + position * path[0]

    hedge_costs.append(0)
    portfolio_values.append(portfolio_value)
    deltas.append(initial_delta)

    # 确定再平衡日期
    if rebalance_freq == 'weekly':
        rebalance_days = np.arange(5, n_days, 5)  # 每周再平衡
    else:
        rebalance_days = np.arange(1, n_days, 1)  # 每日再平衡

    # 模拟对冲
    for t in range(1, n_days):
        # 检查是否敲出（产品终止）
        if t in rebalance_days or t == n_days - 1:
            # 重新计算Delta
            current_price = path[t]
            new_delta = calculate_delta_autocallable(current_price, S0, barrier_out, barrier_in,
                                                     coupon_rate, tenor_years, n_obs)

            # 调整持仓
            target_position = new_delta * 100 / current_price
            trade_size = target_position - position

            # 执行交易（支付交易成本，假设0.1%）
            transaction_cost = abs(trade_size * current_price) * 0.001
            cash -= trade_size * current_price + transaction_cost

            position = target_position
            deltas.append(new_delta)
            hedge_costs.append(abs(trade_size * current_price) + transaction_cost)
        else:
            deltas.append(deltas[-1])
            hedge_costs.append(0)

        # 更新组合价值（现金+持仓）
        portfolio_value = cash + position * path[t]
        portfolio_values.append(portfolio_value)

    # 计算对冲误差
    final_portfolio_value = portfolio_values[-1]
    # 理论上，对冲组合应该等于产品的价值
    # 如果路径未敲出，应该支付本金+票息；如果敲出，应该提前终止
    expected_payout = calculate_expected_payout(path, S0, barrier_out, barrier_in,
                                                coupon_rate, tenor_years, n_obs)

    hedging_error = final_portfolio_value - expected_payout

    return {
        'path': path,
        'deltas': deltas,
        'portfolio_values': portfolio_values,
        'hedge_costs': hedge_costs,
        'total_hedge_cost': sum(hedge_costs),
        'hedging_error': hedging_error,
        'final_portfolio_value': final_portfolio_value,
        'expected_payout': expected_payout
    }


def calculate_expected_payout(path, S0, barrier_out, barrier_in, coupon_rate, tenor_years, n_obs):
    """
    计算单条路径的期望赔付（用于计算对冲误差）
    """
    out_threshold = S0 * barrier_out
    in_threshold = S0 * barrier_in
    n_days = len(path)
    obs_indices = np.linspace(0, n_days - 1, n_obs, dtype=int)

    knocked_in = np.any(path < in_threshold)

    for day_idx in obs_indices:
        if path[day_idx] >= out_threshold:
            quarter_passed = int(day_idx / (n_days / n_obs)) + 1
            coupon_payment = coupon_rate * quarter_passed / 4
            return 100 * (1 + coupon_payment)

    # 未敲出
    if knocked_in:
        return 100 * (path[-1] / S0)
    else:
        return 100 * (1 + coupon_rate * tenor_years)


def plot_hedging_results(hedging_results):
    """
    可视化对冲结果
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    path = hedging_results['path']
    deltas = hedging_results['deltas']
    portfolio_values = hedging_results['portfolio_values']
    hedge_costs = hedging_results['hedge_costs']

    # 图1：价格路径 + 阈值线
    ax1 = axes[0, 0]
    ax1.plot(path, label='HSI Path', color='blue', alpha=0.7)
    ax1.axhline(y=S0 * barrier_out, color='green', linestyle='--', label=f'Knock-Out ({barrier_out * 100:.0f}%)')
    ax1.axhline(y=S0 * barrier_in, color='red', linestyle='--', label=f'Knock-In ({barrier_in * 100:.0f}%)')
    ax1.axhline(y=S0, color='gray', linestyle=':', alpha=0.5, label='Initial')
    ax1.set_xlabel('Trading Days')
    ax1.set_ylabel('Index Level')
    ax1.set_title('Underlying Price Path')
    ax1.legend()

    # 图2：Delta变化
    ax2 = axes[0, 1]
    ax2.plot(deltas, color='orange', label='Delta')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax2.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Trading Days')
    ax2.set_ylabel('Delta')
    ax2.set_title(f'Delta Evolution (Final: {deltas[-1]:.4f})')
    ax2.legend()

    # 图3：组合价值 vs 理论赔付
    ax3 = axes[1, 0]
    ax3.plot(portfolio_values, label='Hedged Portfolio', color='green')
    expected = hedging_results['expected_payout']
    ax3.axhline(y=expected, color='red', linestyle='--', label=f'Theoretical Payout: {expected:.2f}')
    ax3.axhline(y=100, color='gray', linestyle=':', alpha=0.5, label='Principal')
    ax3.set_xlabel('Trading Days')
    ax3.set_ylabel('Portfolio Value')
    ax3.set_title(f'Hedging Error: {hedging_results["hedging_error"]:.4f}')
    ax3.legend()

    # 图4：累计对冲成本
    ax4 = axes[1, 1]
    cumulative_costs = np.cumsum(hedge_costs)
    ax4.plot(cumulative_costs, color='red', label='Cumulative Hedge Cost')
    ax4.axhline(y=cumulative_costs[-1], color='purple', linestyle='--',
                label=f'Total: {cumulative_costs[-1]:.2f}')
    ax4.set_xlabel('Trading Days')
    ax4.set_ylabel('Cumulative Cost')
    ax4.set_title('Hedging Transaction Costs')
    ax4.legend()

    plt.tight_layout()
    plt.savefig('outputs/hedging_backtest.png', dpi=150)
    plt.show()

    return fig


def run_full_hedging_analysis(n_paths_hedge=1000):
    """
    运行完整的对冲分析
    """
    from simulation import simulate_gbm

    print("\n" + "=" * 60)
    print("📊 Delta Hedging Backtest")
    print("=" * 60)

    # 生成路径（使用较少的路径用于对冲分析）
    print("\n🔄 Generating paths for hedging backtest...")
    paths = simulate_gbm(S0, r, sigma, tenor_years, total_steps, n_paths_hedge)

    # 运行对冲（每日再平衡）
    print("🔄 Running daily rebalancing...")
    results_daily = run_delta_hedging_backtest(paths, rebalance_freq='daily')

    # 运行对冲（每周再平衡）
    print("🔄 Running weekly rebalancing...")
    results_weekly = run_delta_hedging_backtest(paths, rebalance_freq='weekly')

    # 输出结果
    print(f"""
    ┌────────────────────────────────┬─────────────┬─────────────┐
    │ Metric                         │ Daily       │ Weekly      │
    ├────────────────────────────────┼─────────────┼─────────────┤
    │ Total Hedge Cost               │ {results_daily['total_hedge_cost']:.2f}     │ {results_weekly['total_hedge_cost']:.2f}     │
    │ Hedging Error                  │ {results_daily['hedging_error']:.4f}    │ {results_weekly['hedging_error']:.4f}    │
    │ Final Portfolio Value          │ {results_daily['final_portfolio_value']:.2f}    │ {results_weekly['final_portfolio_value']:.2f}    │
    │ Expected Payout                │ {results_daily['expected_payout']:.2f}    │ {results_weekly['expected_payout']:.2f}    │
    └────────────────────────────────┴─────────────┴─────────────┘

    💡 关键洞察：
    - 每日再平衡的对冲误差更小，但交易成本更高
    - 每周再平衡成本更低，但误差更大
    - 银行需要在准确性和成本之间找到平衡
    """)

    # 可视化
    print("\n🎨 Generating hedging visualization...")
    plot_hedging_results(results_daily)

    return results_daily, results_weekly


if __name__ == "__main__":
    run_full_hedging_analysis()