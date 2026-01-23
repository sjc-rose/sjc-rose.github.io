import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from datetime import timedelta

# 1. 环境配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def xgboost_full_day_forecast():
    file_path = '第四周大数据分析作业.xlsx'
    try:
        # 读取并排序数据
        df = pd.read_excel(file_path).sort_values('datetime')

        # 设定分割点：4月8日 05:00
        split_time = pd.to_datetime('2019-04-08 05:00:00')
        train_df = df[df['datetime'] <= split_time].copy()

        print(f"✅ XGBoost 训练数据截断至: {split_time}")

        # 2. 特征工程 (使用 Close, Open, High)
        window_size = 30  # 观察过去30分钟
        feature_cols = ['close', 'open', 'high']
        train_data = train_df[feature_cols].values

        X, y = [], []
        for i in range(len(train_data) - window_size):
            X.append(train_data[i: i + window_size].flatten())
            y.append(train_data[i + window_size, 0])  # 预测 close

        X, y = np.array(X), np.array(y)

        # 3. 训练 XGBoost 模型
        # 调优参数以增强趋势捕捉能力
        model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            objective='reg:squarederror',
            n_jobs=-1
        )
        model.fit(X, y)
        print("🚀 XGBoost 训练完成，开始滚动预测全天走势...")

        # 4. 滚动预测 (05:00 - 23:59)
        prediction_steps = 19 * 60
        current_window = train_data[-window_size:].tolist()

        forecasted_prices = []
        forecast_times = []
        last_time = split_time

        for _ in range(prediction_steps):
            input_data = np.array(current_window[-window_size:]).flatten().reshape(1, -1)
            pred_close = model.predict(input_data)[0]

            forecasted_prices.append(pred_close)
            last_time += timedelta(minutes=1)
            forecast_times.append(last_time)

            # 将预测结果推入窗口，进行下一步迭代
            # 这里简单假设未来的 open/high 与预测的 close 相同
            current_window.append([pred_close, pred_close, pred_close])

        # 5. 可视化
        plt.figure(figsize=(15, 7))

        # 画出历史背景
        history_tail = train_df.tail(300)
        plt.plot(history_tail['datetime'], history_tail['close'], label='历史实际价格', color='gray', alpha=0.4)

        # 画出预测全天走势
        plt.plot(forecast_times, forecasted_prices, label='XGBoost 预测全天走势', color='red', linewidth=2)

        plt.axvline(x=split_time, color='black', linestyle='--', label='预测起点')
        plt.title('以太币 4月8日全天走势预测 (XGBoost 滚动模拟)', fontsize=14)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.2)
        plt.show()

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    xgboost_full_day_forecast()