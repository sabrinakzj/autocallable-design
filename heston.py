# heston.py
"""
Heston随机波动率模型定价模块
替代GBM，用于更准确的Autocallable定价
"""
# heston.py
import numpy as np
from config import S0, r, sigma, tenor_years, total_steps, n_paths, barrier_out, barrier_in, coupon_rate, n_obs


def simulate_heston(S0, r, kappa, theta, xi, rho, T, steps, n_paths):
    """
    Heston模型蒙特卡洛模拟（Euler离散化）

    Parameters:
    -----------
    S0 : float, 初始价格
    r : float, 无风险利率
    kappa : float, 均值回归速度
    theta : float, 长期方差
    xi : float, 波动率的波动率 (vol-of-vol)
    rho : float, 价格与波动率的相关性
    T : float, 期限（年）
    steps : int, 时间步数
    n_paths : int, 路径数

    Returns:
    --------
    paths : ndarray, shape (n_paths, steps+1), 价格路径
    vols : ndarray, shape (n_paths, steps+1), 波动率路径
    """
    dt = T / steps

    # 初始化
    paths = np.zeros((n_paths, steps + 1))
    vols = np.zeros((n_paths, steps + 1))

    paths[:, 0] = S0
    vols[:, 0] = theta  # 初始方差 = 长期方差

    # 预生成随机数（相关性）
    Z1 = np.random.normal(0, 1, size=(n_paths, steps))
    Z2 = np.random.normal(0, 1, size=(n_paths, steps))
    # 引入相关性：dW1 = Z1, dW2 = rho*Z1 + sqrt(1-rho^2)*Z2
    dW1 = Z1 * np.sqrt(dt)
    dW2 = (rho * Z1 + np.sqrt(1 - rho ** 2) * Z2) * np.sqrt(dt)

    for t in range(steps):
        v = vols[:, t]
        v_positive = np.maximum(v, 1e-6)  # 防止方差为负

        # 方差过程 (CIR)
        dv = kappa * (theta - v) * dt + xi * np.sqrt(v_positive) * dW2[:, t]
        vols[:, t + 1] = np.maximum(v + dv, 1e-6)  # 保持方差为正

        # 价格过程
        ds = r * paths[:, t] * dt + np.sqrt(v_positive) * paths[:, t] * dW1[:, t]
        paths[:, t + 1] = paths[:, t] + ds

    return paths, vols


def price_autocallable_heston(paths):
    """
    使用Heston模拟的路径对Autocallable定价
    逻辑与GBM版本完全相同
    """
    n_paths, n_days = paths.shape
    payoffs = np.zeros(n_paths)
    knocked_out_count = 0
    knocked_in_count = 0

    out_threshold = S0 * barrier_out
    in_threshold = S0 * barrier_in

    # 观察日索引
    obs_indices = np.linspace(0, n_days - 1, n_obs, dtype=int)

    for i in range(n_paths):
        path = paths[i]
        knocked_in = np.any(path < in_threshold)
        if knocked_in:
            knocked_in_count += 1

        knocked_out = False
        for day_idx in obs_indices:
            if day_idx < len(path) and path[day_idx] >= out_threshold:
                quarter_passed = int(day_idx / (n_days / n_obs)) + 1
                coupon_payment = coupon_rate * quarter_passed / 4
                payoffs[i] = 100 * (1 + coupon_payment)
                knocked_out_count += 1
                knocked_out = True
                break

        if not knocked_out:
            if knocked_in:
                payoffs[i] = 100 * (path[-1] / S0)
            else:
                payoffs[i] = 100 * (1 + coupon_rate * tenor_years)

    disc_payoffs = payoffs * np.exp(-r * tenor_years)

    return {
        'fair_value': np.mean(disc_payoffs),
        'knock_out_prob': knocked_out_count / n_paths,
        'knock_in_prob': knocked_in_count / n_paths,
        'payoffs': payoffs,
        'disc_payoffs': disc_payoffs,
        'std_error': np.std(disc_payoffs) / np.sqrt(n_paths)
    }


def compare_gbm_vs_heston():
    """
    对比GBM和Heston的定价结果
    """
    from simulation import simulate_gbm, price_autocallable

    # Heston参数
    kappa = 2.0
    theta = 0.0484  # 22%^2
    xi = 0.30  # vol-of-vol
    rho = -0.70  # 杠杆效应

    print("\n" + "=" * 60)
    print("📊 GBM vs Heston Model Comparison")
    print("=" * 60)

    # 1. GBM定价
    print("\n🔄 Running GBM simulation...")
    gbm_paths = simulate_gbm(S0, r, sigma, tenor_years, total_steps, n_paths)
    gbm_results = price_autocallable(gbm_paths)

    # 2. Heston定价
    print("🔄 Running Heston simulation...")
    heston_paths, heston_vols = simulate_heston(
        S0, r, kappa, theta, xi, rho, tenor_years, total_steps, n_paths
    )
    heston_results = price_autocallable_heston(heston_paths)

    # 3. 对比结果
    print(f"""
    ┌────────────────────┬─────────────┬─────────────┬──────────────┐
    │ Metric             │ GBM         │ Heston      │ Difference   │
    ├────────────────────┼─────────────┼─────────────┼──────────────┤
    │ Fair Value         │ {gbm_results['fair_value']:.4f}    │ {heston_results['fair_value']:.4f}    │ {heston_results['fair_value'] - gbm_results['fair_value']:.4f}     │
    │ Knock-Out Prob     │ {gbm_results['knock_out_prob'] * 100:.2f}%   │ {heston_results['knock_out_prob'] * 100:.2f}%   │ {heston_results['knock_out_prob'] * 100 - gbm_results['knock_out_prob'] * 100:.2f}%    │
    │ Knock-In Prob      │ {gbm_results['knock_in_prob'] * 100:.2f}%   │ {heston_results['knock_in_prob'] * 100:.2f}%   │ {heston_results['knock_in_prob'] * 100 - gbm_results['knock_in_prob'] * 100:.2f}%    │
    │ Std Error          │ {gbm_results['std_error']:.4f}    │ {heston_results['std_error']:.4f}    │              │
    └────────────────────┴─────────────┴─────────────┴──────────────┘

    💡 关键洞察：
    - Heston模型的Fair Value通常比GBM更低（因为随机波动率增加了路径的极端值）
    - 如果Rho为负，敲入概率通常会更高（“杠杆效应”导致下跌时波动率上升）
    """)

    return gbm_results, heston_results, heston_paths


if __name__ == "__main__":
    # 独立运行对比
    compare_gbm_vs_heston()