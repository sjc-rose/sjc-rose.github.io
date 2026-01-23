import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta

# 1. 环境配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def run_comparison_forecast():
    file_path = '第四周大数据分析作业.xlsx'
    try:
        df = pd.read_excel(file_path).sort_values('datetime')
        print(f"✅ 数据加载成功。使用特征：close, open, high")

        # 2. 特征工程：多列输入
        # 我们使用过去 20 组 (close, open, high) 来预测下一个 close
        window_size = 20
        # 提取三列数据
        feature_cols = ['close', 'open', 'high']
        data_matrix = df[feature_cols].values
        target_vector = df['close'].values

        X, y = [], []
        for i in range(len(data_matrix) - window_size):
            # 将 20 行 * 3 列的数据拉平为 60 个特征的一行
            X.append(data_matrix[i: i + window_size].flatten())
            y.append(target_vector[i + window_size])

        X, y = np.array(X), np.array(y)

        # 3. 训练两个模型
        print("🌲 正在训练随机森林 (Random Forest)...")
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X, y)

        print("🚀 正在训练 XGBoost...")
        xgb_model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6)
        xgb_model.fit(X, y)

        # 4. 预测未来一个点
        last_window = data_matrix[-window_size:].flatten().reshape(1, -1)
        rf_pred = rf_model.predict(last_window)[0]
        xgb_pred = xgb_model.predict(last_window)[0]

        last_date = df['datetime'].iloc[-1]
        next_date = last_date + timedelta(minutes=1)

        # 5. 打印对比
        print("\n" + "=" * 40)
        print(f"最后实际收盘价: {target_vector[-1]:.2f}")
        print(f"随机森林预测值: {rf_pred:.2f} (颜色: 橙色)")
        print(f"XGBoost 预测值: {xgb_pred:.2f} (颜色: 红色)")
        print("=" * 40 + "\n")

        # 6. 绘图对比
        plt.figure(figsize=(12, 7))

        # 画出最后一段真实走势
        show_range = 80
        recent_dates = df['datetime'].iloc[-show_range:]
        plt.plot(recent_dates, df['close'].iloc[-show_range:], label='实际收盘价 (Actual)', color='#1f77b4',
                 linewidth=3, alpha=0.8)

        # 标记最后一点
        plt.scatter(last_date, target_vector[-1], color='black', s=50, zorder=6)

        # 画出随机森林预测点
        plt.scatter(next_date, rf_pred, color='orange', s=150, label='RF 预测点', edgecolors='black', marker='D',
                    zorder=7)
        # 画出 XGBoost 预测点
        plt.scatter(next_date, xgb_pred, color='red', s=150, label='XGBoost 预测点', edgecolors='black', marker='^',
                    zorder=7)

        # 连接趋势线
        plt.plot([last_date, next_date], [target_vector[-1], rf_pred], color='orange', linestyle='--', alpha=0.5)
        plt.plot([last_date, next_date], [target_vector[-1], xgb_pred], color='red', linestyle='--', alpha=0.5)

        plt.title('ETH 价格预测对比：多特征输入 (Close/Open/High)', fontsize=14)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.6)

        # 自动调整布局，防止文字重叠
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    run_comparison_forecast()