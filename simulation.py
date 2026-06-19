from config import *


def simulate_gbm(S0, mu, sigma, T, steps, n_paths):
    """
    几何布朗运动模拟
    返回: shape (n_paths, steps) 的价格路径矩阵
    """
    dt = T / steps
    # 提前生成所有随机数（向量化，速度快）
    Z = np.random.normal(0, 1, size=(n_paths, steps))
    dW = Z * np.sqrt(dt)

    # 对数收益率： (mu - 0.5*sigma^2)*dt + sigma*dW
    log_returns = (mu - 0.5 * sigma ** 2) * dt + sigma * dW
    log_price = np.log(S0) + np.cumsum(log_returns, axis=1)

    # 把初始价格拼回去（第0列为S0）
    paths = np.concatenate([np.full((n_paths, 1), S0), np.exp(log_price)], axis=1)
    return paths

# simulation.py 中的 price_autocallable 函数
def price_autocallable(paths):
    """
    定价核心：遍历每条路径，判断敲出/敲入，计算赔付
    返回: (平均现值, 敲出概率, 敲入概率, 各路径赔付数组)
    """
    n_paths, n_days = paths.shape
    payoffs = np.zeros(n_paths)
    knocked_out_count = 0
    knocked_in_count = 0

    out_threshold = S0 * barrier_out
    in_threshold = S0 * barrier_in

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
        'std_error': np.std(disc_payoffs) / np.sqrt(n_paths)  # ✅ 添加这一行
    }


def run_pricing():
    """一键运行定价"""
    paths = simulate_gbm(S0, mu, sigma, tenor_years, total_steps, n_paths)
    results = price_autocallable(paths)
    return results, paths