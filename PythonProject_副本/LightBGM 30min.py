import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import lightgbm as lgb
from datetime import timedelta

# 1. 环境配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def lgbm_30min_forecast():
    file_path = '第四周大数据分析作业.xlsx'
    try:
        # 读取数据
        df = pd.read_excel(file_path).sort_values('datetime')

        # 设定预测起点
        start_time = pd.to_datetime('2019-04-08 05:04:00')
        train_df = df[df['datetime'] <= start_time].copy()

        print(f"✅ LightGBM 短期预测准备就绪，起点: {start_time}")

        # 2. 特征工程 (窗口大小设为 15 分钟)
        window_size = 15
        feature_cols = ['close', 'open', 'high']
        train_data = train_df[feature_cols].values

        X, y = [], []
        for i in range(len(train_data) - window_size):
            X.append(train_data[i: i + window_size].flatten())
            y.append(train_data[i + window_size, 0])

        X, y = np.array(X), np.array(y)

        # 3. 训练 LightGBM
        # 针对短时预测，我们增加树的数量并细化学习率
        model = lgb.LGBMRegressor(
            n_estimators=300,
            learning_rate=0.03,
            num_leaves=20,
            min_child_samples=5,  # 小样本下防止过拟合
            verbose=-1
        )
        model.fit(X, y)

        # 4. 滚动预测未来 30 分钟
        prediction_steps = 30
        current_window = train_data[-window_size:].tolist()

        forecast_prices = []
        forecast_times = []
        curr_time = start_time

        for _ in range(prediction_steps):
            input_x = np.array(current_window[-window_size:]).flatten().reshape(1, -1)
            pred_close = model.predict(input_x)[0]

            forecast_prices.append(pred_close)
            curr_time += timedelta(minutes=1)
            forecast_times.append(curr_time)

            # 更新滚动窗口
            current_window.append([pred_close, pred_close, pred_close])

        # 5. 可视化
        plt.figure(figsize=(12, 6))

        # 历史走势（最后 45 分钟）
        recent_history = train_df.tail(45)
        plt.plot(recent_history['datetime'], recent_history['close'],
                 label='历史真实价格', color='#2c3e50', linewidth=2)

        # LightGBM 30分钟预测
        plt.plot(forecast_times, forecast_prices,
                 label='LightGBM 短期预测', color='#27ae60',
                 linestyle='--', marker='s', markersize=4)

        plt.axvline(x=start_time, color='orange', linestyle=':', label='预测起点')
        plt.title('以太币 (ETH) 30分钟短期走势预测 - LightGBM', fontsize=14)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.gcf().autofmt_xdate()
        plt.show()

        # 打印预测结果
        change = forecast_prices[-1] - train_data[-1, 0]
        print(f"\n📊 30分钟预测总结:")
        print(f"起点 (05:04): {train_data[-1, 0]:.2f}")
        print(f"终点 (05:34): {forecast_prices[-1]:.2f}")
        print(f"预期涨跌: {change:+.2f} ({(change / train_data[-1, 0] * 100):.4f}%)")

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    lgbm_30min_forecast()