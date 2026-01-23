import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
import os
import warnings

# 基础配置
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def run_prediction():
    # 1. 指定你的项目目录
    current_dir = "/Users/mac/PyCharmMiscProject/PythonProject_副本/"
    # 直接使用你列表里显示的文件名
    target_file = os.path.join(current_dir, "以太币 1 分钟级数据文件.xlsx")

    if not os.path.exists(target_file):
        print(f"❌ 错误：依然找不到文件 {target_file}")
        return

    print(f"✅ 成功锁定文件: {target_file}")

    try:
        # 2. 读取 Excel (注意：这里用 read_excel)
        print("正在从 Excel 提取数据，请稍候...")
        df = pd.read_excel(target_file)

        # 确保列名统一（根据你之前上传的片段，列名应该是 datetime, close 等）
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')

        # 3. 特征工程
        window = 10
        for i in range(1, window + 1):
            df[f'lag_{i}'] = df['close'].shift(i)
        df = df.dropna()

        # 4. 训练集 (2025.12.28 - 2026.01.06)
        train_df = df[(df['datetime'] >= '2025-12-28') & (df['datetime'] < '2026-01-07')]

        if train_df.empty:
            print("数据范围内没有找到训练数据，请检查 Excel 里的日期。")
            return

        features = [f'lag_{i}' for i in range(1, window + 1)]
        X_train = train_df[features]
        y_train = train_df['close']

        # 5. 训练模型
        print(f"训练集样本数: {len(X_train)}。正在训练随机森林...")
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # 6. 滚动预测 1月7日 0点开始的 120 分钟
        print("正在生成 1月7日 预测曲线...")
        last_row = train_df.iloc[-1:]
        current_features = last_row[features].values

        preds = []
        for _ in range(120):
            p = model.predict(current_features)[0]
            preds.append(p)
            # 这里的滚动逻辑：[p, lag_1, lag_2 ... lag_9]
            current_features = np.roll(current_features, 1)
            current_features[0, 0] = p

        last_time = train_df['datetime'].max()
        pred_times = [last_time + pd.Timedelta(minutes=i + 1) for i in range(120)]

        # 7. 绘图
        plt.figure(figsize=(12, 6))
        # 画出 1月6日 最后 2 小时历史
        history_plot = train_df.tail(120)
        plt.plot(history_plot['datetime'], history_plot['close'], label='1月6日 历史价格', color='blue')
        plt.plot(pred_times, preds, label='1月7日 预测走势', color='red', linestyle='--')

        plt.title('ETH 价格预测走势 (1月7日预测)')
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        print("🚀 绘图成功！正在弹出窗口...")
        plt.show()

    except Exception as e:
        print(f"运行失败: {e}")
        print("提示：如果报 openpyxl 错误，请运行 pip install openpyxl")


if __name__ == "__main__":
    run_prediction()