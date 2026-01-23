import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta

# 1. 环境配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def forecast_30_minutes():
    file_path = '第四周大数据分析作业.xlsx'
    try:
        # 读取数据并排序
        df = pd.read_excel(file_path).sort_values('datetime')

        # 设定预测起点：2019-04-08 05:04:00
        start_time = pd.to_datetime('2019-04-08 05:04:00')

        # 准备训练集：使用起点之前的所有数据
        train_df = df[df['datetime'] <= start_time].copy()

        print(f"✅ 训练数据准备就绪，截止时间: {start_time}")

        # 2. 特征工程
        # 使用过去 15 分钟的 [close, open, high] 预测下一分钟的 close
        window_size = 15
        feature_cols = ['close', 'open', 'high']
        train_data = train_df[feature_cols].values

        X, y = [], []
        for i in range(len(train_data) - window_size):
            X.append(train_data[i: i + window_size].flatten())
            y.append(train_data[i + window_size, 0])  # 预测目标是 close

        X, y = np.array(X), np.array(y)

        # 3. 训练模型
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # 4. 滚动预测未来 30 分钟
        prediction_steps = 30
        current_window = train_data[-window_size:].tolist()

        forecast_prices = []
        forecast_times = []
        curr_time = start_time

        for _ in range(prediction_steps):
            # 获取当前输入窗口
            input_x = np.array(current_window[-window_size:]).flatten().reshape(1, -1)
            # 预测下一分钟价格
            pred_close = model.predict(input_x)[0]

            # 记录结果
            forecast_prices.append(pred_close)
            curr_time += timedelta(minutes=1)
            forecast_times.append(curr_time)

            # 将预测值作为下一分钟的输入（假设 open 和 high 与 close 接近）
            current_window.append([pred_close, pred_close, pred_close])

        # 5. 可视化对比图
        plt.figure(figsize=(12, 6))

        # 画出预测点之前的真实走势（展示最后 60 分钟）
        recent_history = train_df.tail(60)
        plt.plot(recent_history['datetime'], recent_history['close'],
                 label='历史真实价格', color='#1f77b4', linewidth=2)

        # 画出预测的 30 分钟走势
        plt.plot(forecast_times, forecast_prices,
                 label='未来 30 分钟预测', color='#e67e22', linestyle='--', marker='o', markersize=4)

        # 装饰图表
        plt.axvline(x=start_time, color='red', linestyle=':', label='预测起点 (05:04)')
        plt.title('以太币 (ETH) 未来 30 分钟价格预测 (基于 4/8 05:04 数据)', fontsize=14)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 设置横坐标格式
        plt.gcf().autofmt_xdate()

        plt.show()

        print("-" * 30)
        print(f"预测完成！起点价格: {train_data[-1, 0]:.2f}")
        print(f"30分钟后预计价格: {forecast_prices[-1]:.2f}")
        print(f"预计总变动: {forecast_prices[-1] - train_data[-1, 0]:+.2f}")
        print("-" * 30)

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    forecast_30_minutes()