import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta

# 1. 设置中文显示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 2. 读取数据
file_path = '第四周大数据分析作业.xlsx'
try:
    df = pd.read_excel(file_path)
    # 确保按时间排序
    df = df.sort_values('datetime')
    print("✅ 数据加载成功，总计数据量：", len(df))

    # 3. 特征工程：我们用过去 10 个数据点来预测下一个点
    window_size = 10
    prices = df['close'].values

    X = []
    y = []
    for i in range(len(prices) - window_size):
        X.append(prices[i: i + window_size])
        y.append(prices[i + window_size])

    X, y = np.array(X), np.array(y)

    # 4. 训练模型 (随机森林)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("✅ 模型训练已完成")

    # 5. 预测未来一天 (即数据最后一行之后的一个点)
    # 取数据中最后 window_size 个点作为输入
    last_window = prices[-window_size:].reshape(1, -1)
    next_day_pred = model.predict(last_window)[0]

    # 计算预测对应的时间
    last_date = df['datetime'].iloc[-1]
    next_date = last_date + timedelta(minutes=1)  # 如果是分钟线就加1分钟，天线就加1天

    print("-" * 30)
    print(f"📈 预测结果：")
    print(f"最后已知时间: {last_date} -> 价格: {prices[-1]:.2f}")
    print(f"预测未来时间: {next_date} -> 预计价格: {next_day_pred:.2f}")
    print("-" * 30)

    # 6. 可视化最后一段走势和预测点
    plt.figure(figsize=(10, 5))
    plot_range = 100  # 只画最后100个点，看得更清楚
    plt.plot(df['datetime'].iloc[-plot_range:], prices[-plot_range:], label='历史价格', color='blue')
    plt.scatter(next_date, next_day_pred, color='red', label='未来预测点', zorder=5)

    plt.title(f'以太币价格预测 - 未来一日预计: {next_day_pred:.2f}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

except Exception as e:
    print(f"❌ 运行中出现错误: {e}")