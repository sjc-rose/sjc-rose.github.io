import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

# 设置中文字体（SimHei）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def backtest_strategy():
    # 1. 加载数据
    file_path = '第四周大数据分析作业.xlsx'
    try:
        df = pd.read_excel(file_path)
    except:
        # 如果找不到文件，模拟一段示例数据用于演示
        print("未找到文件，正在生成模拟数据...")
        df = pd.DataFrame({
            'datetime': pd.date_range(start='2023-01-01', periods=1000, freq='T'),
            'close': np.cumsum(np.random.randn(1000)) + 100
        })

    # 2. 特征工程：用过去5分钟预测未来3分钟
    lookback = 5
    forecast_step = 3

    # 构造过去5分钟的特征
    for i in range(1, lookback + 1):
        df[f'lag_{i}'] = df['close'].shift(i)

    # 构造目标值：未来第3分钟的价格
    df['target_price'] = df['close'].shift(-forecast_step)
    df.dropna(inplace=True)

    # 划分特征和标签
    features = [f'lag_{i}' for i in range(1, lookback + 1)]
    X = df[features]
    y = df['target_price']

    # 划分训练集和测试集 (前80%训练，后20%模拟回测)
    split = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    test_dates = df['datetime'].iloc[split:]
    current_prices = df['close'].iloc[split:]  # 买入时的价格

    # 3. XGBoost 模型训练
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
    model.fit(X_train, y_train)

    # 预测未来价格
    predicted_prices = model.predict(X_test)

    # 4. 投资逻辑模拟
    investment_per_trade = 100
    profits = []

    # 遍历测试集进行模拟
    for i in range(len(predicted_prices)):
        pred_future_price = predicted_prices[i]
        curr_price = current_prices.iloc[i]
        actual_future_price = y_test.iloc[i]

        # 逻辑：预测未来涨，则买入
        if pred_future_price > curr_price:
            # 计算收益率并乘以100元
            profit = investment_per_trade * (actual_future_price / curr_price - 1)
        else:
            profit = 0

        profits.append(profit)

    # 转换为 Series 方便计算
    profits_series = pd.Series(profits, index=test_dates.index)
    cumulative_profit = profits_series.cumsum()
    error = np.abs(predicted_prices - y_test.values)

    # 5. 可视化
    fig, axes = plt.subplots(3, 1, figsize=(12, 15), sharex=False)

    # 图1：实际价格与预测价格曲线
    axes[0].plot(test_dates, y_test.values, label='Actual Future Price', color='black', alpha=0.7)
    axes[0].plot(test_dates, predicted_prices, label='XGBoost Predicted', color='red', linestyle='--')
    axes[0].set_title('每日实际预测价格曲线 (Actual vs Predicted)')
    axes[0].legend()

    # 图2：误差曲线
    axes[1].plot(test_dates, error, label='Absolute Error', color='orange')
    axes[1].set_title('预测误差曲线 (Absolute Error)')
    axes[1].legend()

    # 图3：收益曲线
    axes[2].plot(test_dates, cumulative_profit, label='Cumulative Profit (RMB)', color='green')
    axes[2].set_title(f'策略总收益曲线 (每笔投入100元, 总收益: {cumulative_profit.iloc[-1]:.2f} 元)')
    axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    axes[2].legend()

    plt.tight_layout()
    plt.show()

    print(f"模拟结束。最终累计收益: {cumulative_profit.iloc[-1]:.2f} 元")


if __name__ == "__main__":
    backtest_strategy()