import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta

# 1. 配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def forecast_full_day():
    file_path = '第四周大数据分析作业.xlsx'
    try:
        # 读取并处理数据
        df = pd.read_excel(file_path).sort_values('datetime')

        # 设定分割点：4月8日 早上 05:00
        split_time = pd.to_datetime('2019-04-08 05:00:00')
        train_df = df[df['datetime'] <= split_time].copy()

        print(f"✅ 训练数据截止至: {split_time}")

        # 2. 特征准备 (使用 Close, Open, High)
        window_size = 30  # 使用过去30分钟预测未来
        feature_cols = ['close', 'open', 'high']
        train_data = train_df[feature_cols].values

        X, y = [], []
        for i in range(len(train_data) - window_size):
            X.append(train_data[i: i + window_size].flatten())
            y.append(train_data[i + window_size, 0])  # 预测 close

        X, y = np.array(X), np.array(y)

        # 3. 训练随机森林
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        print("🌲 模型训练完成，开始滚动预测全天...")

        # 4. 滚动预测 (从 05:00 预测到 23:59)
        # 预测次数 = 19小时 * 60分钟 = 1140次
        prediction_steps = 19 * 60
        current_window = train_data[-window_size:].tolist()  # 初始窗口

        forecasted_prices = []
        forecast_times = []
        last_time = split_time

        for _ in range(prediction_steps):
            # 准备当前输入
            input_data = np.array(current_window[-window_size:]).flatten().reshape(1, -1)
            pred_close = model.predict(input_data)[0]

            # 将预测值加入结果
            forecasted_prices.append(pred_close)
            last_time += timedelta(minutes=1)
            forecast_times.append(last_time)

            # 模拟生成下一分钟的特征 (简单假设 open/high 与预测的 close 一致)
            current_window.append([pred_close, pred_close, pred_close])

        # 5. 可视化
        plt.figure(figsize=(15, 7))

        # 画出 4月8日之前的历史
        history_show = train_df.tail(200)
        plt.plot(history_show['datetime'], history_show['close'], label='历史实际价格', color='gray', alpha=0.5)

        # 画出预测的 4月8日全天走势
        plt.plot(forecast_times, forecasted_prices, label='预测 4月8日(05:00-24:00) 走势', color='orange', linewidth=2)

        plt.axvline(x=split_time, color='red', linestyle='--', label='预测起点')
        plt.title('以太币 4月8日全天价格走势预测 (随机森林滚动模拟)', fontsize=14)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    forecast_full_day()