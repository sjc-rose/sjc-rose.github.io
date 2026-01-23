import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from datetime import timedelta

# 1. 环境配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac 中文支持
plt.rcParams['axes.unicode_minus'] = False


def xgboost_30min_forecast():
    file_path = '第四周大数据分析作业.xlsx'
    try:
        # 读取数据并排序
        df = pd.read_excel(file_path).sort_values('datetime')

        # 设定预测起点
        start_time = pd.to_datetime('2019-04-08 05:04:00')

        # 准备训练集：使用起点之前的所有数据
        train_df = df[df['datetime'] <= start_time].copy()

        print(f"✅ XGBoost 准备就绪，预测起点: {start_time}")

        # 2. 特征工程
        # 使用过去 15 分钟的 [close, open, high] 预测下一分钟的 close
        window_size = 15
        feature_cols = ['close', 'open', 'high']
        train_data = train_df[feature_cols].values

        X, y = [], []
        for i in range(len(train_data) - window_size):
            # 将 15*3 的矩阵拉平为一维向量作为输入
            X.append(train_data[i: i + window_size].flatten())
            y.append(train_data[i + window_size, 0])  # 目标是下一分钟的 close

        X, y = np.array(X), np.array(y)

        # 3. 训练 XGBoost 模型
        # 参数优化：较小的学习率有助于平滑预测
        model = XGBRegressor(
            n_estimators=200,
            learning_rate=0.03,
            max_depth=5,
            objective='reg:squarederror'
        )
        model.fit(X, y)

        # 4. 递归滚动预测未来 30 分钟
        prediction_steps = 30
        current_window = train_data[-window_size:].tolist()

        forecast_prices = []
        forecast_times = []
        curr_time = start_time

        for _ in range(prediction_steps):
            # 准备输入
            input_x = np.array(current_window[-window_size:]).flatten().reshape(1, -1)
            # 预测
            pred_close = model.predict(input_x)[0]

            # 记录结果
            forecast_prices.append(pred_close)
            curr_time += timedelta(minutes=1)
            forecast_times.append(curr_time)

            # 更新窗口：将预测值作为新的“已知”数据（假设 open/high 趋同于 close）
            current_window.append([pred_close, pred_close, pred_close])

        # 5. 可视化
        plt.figure(figsize=(12, 6))

        # 历史走势（最后 45 分钟）
        recent_history = train_df.tail(45)
        plt.plot(recent_history['datetime'], recent_history['close'],
                 label='历史实际价格', color='#2c3e50', linewidth=2)

        # XGBoost 预测走势
        plt.plot(forecast_times, forecast_prices,
                 label='XGBoost 30分钟预测', color='#e74c3c',
                 linestyle='--', marker='^', markersize=5)

        # 辅助线
        plt.axvline(x=start_time, color='gray', linestyle=':', label='预测起点')

        plt.title('以太币 (ETH) 30分钟短期预测 - XGBoost 多特征模型', fontsize=14)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.gcf().autofmt_xdate()
        plt.show()

        # 输出预测详情
        print("\n" + "📊 预测简报 " + "-" * 20)
        print(f"起点价格: {train_data[-1, 0]:.2f}")
        print(f"30分钟后价格预测: {forecast_prices[-1]:.2f}")
        change = forecast_prices[-1] - train_data[-1, 0]
        print(f"预期波动: {change:+.2f} ({(change / train_data[-1, 0] * 100):.4f}%)")

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    xgboost_30min_forecast()