import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from catboost import CatBoostRegressor
from datetime import timedelta

# 1. 环境配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac 字体
plt.rcParams['axes.unicode_minus'] = False


def catboost_30min_forecast():
    # 确保文件名与你的一致
    file_path = '第四周大数据分析作业.xlsx'

    try:
        # 读取并排序数据
        df = pd.read_excel(file_path).sort_values('datetime')
        df['datetime'] = pd.to_datetime(df['datetime'])

        # 设定预测起点
        start_time = pd.to_datetime('2019-04-08 05:04:00')
        train_df = df[df['datetime'] <= start_time].copy()

        print(f"✅ CatBoost 正在分析历史规律 (4月1日 - 4月8日 05:04)")

        # 2. 特征工程 (使用过去 30 分钟作为窗口)
        window_size = 30
        # 我们使用 close, open, high, low 以及成交量作为输入特征
        feature_cols = ['close', 'open', 'high', 'low', 'volume']
        train_data = train_df[feature_cols].values

        X, y = [], []
        for i in range(len(train_data) - window_size):
            # 将 window_size 分钟内的所有特征拉平作为一行输入
            X.append(train_data[i: i + window_size].flatten())
            y.append(train_data[i + window_size, 0])  # 预测下一分钟的 close

        X, y = np.array(X), np.array(y)

        # 3. 训练 CatBoost 模型
        # iterations: 迭代次数
        # learning_rate: 学习率
        # depth: 树的深度
        model = CatBoostRegressor(
            iterations=600,
            learning_rate=0.05,
            depth=6,
            l2_leaf_reg=3,
            loss_function='RMSE',
            random_seed=42,
            verbose=0  # 不打印训练过程
        )

        print("💡 CatBoost 正在训练中...")
        model.fit(X, y)

        # 4. 递归滚动预测未来 30 分钟
        prediction_steps = 30
        # 取最后 window_size 分钟的数据作为预测的起点输入
        current_window = train_data[-window_size:].tolist()

        forecast_prices = []
        forecast_times = []
        curr_time = start_time

        for _ in range(prediction_steps):
            # 准备输入数据
            input_x = np.array(current_window[-window_size:]).flatten().reshape(1, -1)

            # 获取预测值
            pred_close = model.predict(input_x)[0]
            forecast_prices.append(pred_close)

            # 时间推进
            curr_time += timedelta(minutes=1)
            forecast_times.append(curr_time)

            # 构造新的特征行：假设未来预测的 open/high/low/vol 与 close 接近（简化模拟）
            new_row = [pred_close, pred_close, pred_close, pred_close, current_window[-1][-1]]
            current_window.append(new_row)

        # 5. 可视化
        plt.figure(figsize=(12, 6))

        # 绘制预测起点前的部分真实数据
        recent_history = train_df.tail(60)
        plt.plot(recent_history['datetime'], recent_history['close'],
                 label='历史真实价格', color='#34495e', linewidth=2)

        # 绘制 CatBoost 预测走势
        plt.plot(forecast_times, forecast_prices,
                 label='CatBoost 30分钟预测', color='#e67e22',
                 linestyle='--', marker='o', markersize=4)

        plt.axvline(x=start_time, color='red', linestyle=':', label='预测分割线')
        plt.title('以太币 (ETH) 短期走势预测 - CatBoost (30min)', fontsize=14)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.gcf().autofmt_xdate()  # 自动优化时间显示
        plt.show()

        print(f"📊 预测完成！起点价格: {train_data[-1, 0]:.2f} -> 30分钟后预期价格: {forecast_prices[-1]:.2f}")

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    catboost_30min_forecast()