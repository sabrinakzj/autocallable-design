# config.py
import os
import numpy as np
import yfinance as yf
from datetime import datetime
import time

# ========== 代理配置（适配你的代理端口） ==========
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:33210'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:33210'
os.environ['ALL_PROXY'] = 'socks5://127.0.0.1:33211'


# ========== 自动获取恒生指数最新价格（使用 yfinance + 代理） ==========
def get_hsi_price_with_retry(max_retries=3, timeout=15):
    """
    使用 yfinance 获取恒生指数 (^HSI) 的最新价格
    支持自动重试，通过代理访问
    """
    for attempt in range(max_retries):
        try:
            print(f"🔄 Fetching HSI data via proxy... (Attempt {attempt + 1}/{max_retries})")

            ticker = yf.Ticker("^HSI")
            data = ticker.history(period="5d", timeout=timeout)

            if len(data) == 0:
                print(f"⚠️ No data fetched on attempt {attempt + 1}")
                time.sleep(2)
                continue

            latest_close = data['Close'].iloc[-1]
            latest_date = data.index[-1]

            print(f"✅ Fetched HSI latest closing price: {latest_close:.2f} (as of {latest_date.strftime('%Y-%m-%d')})")
            return latest_close

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting 3 seconds before retry...")
                time.sleep(3)
            else:
                print(f"❌ All {max_retries} attempts failed.")

    print("⚠️ Using fallback value: 20000.0")
    return 20000.0


# ========== 备选方案：手动设置 ==========
def get_hsi_price_manual():
    """
    手动输入恒生指数价格（当网络不可用时使用）
    """
    manual_price = 23000.0  # 👈 手动更新这个数字
    print(f"ℹ️ Using manual price: {manual_price:.2f}")
    return manual_price


# ========== 初始化 ==========
print("\n" + "=" * 50)
print("📊 Initializing Autocallable Pricing Model")
print("=" * 50)

# 尝试自动获取
S0 = get_hsi_price_with_retry(max_retries=3, timeout=15)

# 如果获取失败，使用手动值
if S0 == 20000.0:
    print("\n⚠️ Automatic fetch failed. Switching to manual mode.")
    S0 = get_hsi_price_manual()

print(f"✅ Final S0 (Initial Level): {S0:.2f}")
print("=" * 50 + "\n")

# ========== 产品条款 ==========
barrier_out = 1.00
barrier_in = 0.70
coupon_rate = 0.12
tenor_years = 2.0
n_obs = 8

# ========== 市场参数 ==========
mu = 0.08
sigma = 0.22
r = 0.035

# ========== 模拟参数 ==========
n_paths = 100000
steps_per_year = 252
total_steps = int(tenor_years * steps_per_year)
obs_indices = np.linspace(steps_per_year // 4, total_steps, n_obs, dtype=int) - 1