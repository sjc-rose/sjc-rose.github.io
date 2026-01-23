import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_percentage_error
from datetime import timedelta

# 1. 环境配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac环境，Windows建议改为 'SimHei'
plt.rcParams['axes.unicode_minus'] = False


def run_minute_by_minute_iteration():
    # 文件路径
    train_file = '第四周大数据分析作业.xlsx'  # 训练集：4.1-4.8 05:04
    truth_file = '4.8 all day.xlsx'  # 验证集：4.8 全天真实走势

    try:
        # 加载数据
        df_train = pd.read_excel(train_file).sort_values('datetime')
        df_truth = pd.read_excel(truth_file).sort_values('datetime')

        df_train['datetime'] = pd.to_datetime(df_train['datetime'])
        df_truth['datetime'] = pd.to_datetime(df_truth['datetime'])

        # 设定预测区间：05:04 -> 06:04 (共60步)
        start_time = pd.to_datetime('2019-04-08 05:04:00')
        end_time = pd.to_datetime('2019-04-08 06:04:00')

        # 截取真实的对比段
        truth_segment = df_truth[(df_truth['datetime'] >= start_time) & (df_truth['datetime'] <= end_time)].copy()
        target_steps = len(truth_segment)

        print(f"✅ 目标：逐分钟递归预测 {target_steps} 个点...")

        # 2. 特征工程 (滑动窗口 30 分钟)
        window_size = 30

        def create_xy(data):
            X, y = [], []
            prices = data['close'].values
            for i in range(len(prices) - window_size):
                X.append(prices[i: i + window_size])
                y.append(prices[i + window_size])
            return np.array(X), np.array(y)

        X_train, y_train = create_xy(df_train)

        # 3. 初始化四个主流算法
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.05),
            'LightGBM': LGBMRegressor(n_estimators=100, verbose=-1),
            'CatBoost': CatBoostRegressor(iterations=100, verbose=0)
        }

        results = {}
        model_colors = {
            'Random Forest': '#1f77b4',  # 蓝色
            'XGBoost': '#d62728',  # 红色
            'LightGBM': '#2ca02c',  # 绿色
            'CatBoost': '#ff7f0e'  # 橙色
        }

        # 4. 核心逻辑：逐分钟递归
        for name, model in models.items():
            print(f"正在计算 {name} 的逐分钟路径...")
            model.fit(X_train, y_train)

            # 获取训练集最后的窗口作为起点
            history_window = list(df_train['close'].values[-window_size:])
            preds = []

            for _ in range(target_steps):
                # 用当前的窗口预测下一分钟
                current_input = np.array(history_window[-window_size:]).reshape(1, -1)
                next_val = model.predict(current_input)[0]

                preds.append(next_val)
                # 关键：将预测出的“下一分钟价格”存入窗口，用于预测“下下分钟”
                history_window.append(next_val)

            results[name] = preds

        # 5. 计算 MAPE 误差率
        actual_prices = truth_segment['close'].values
        mape_scores = {}
        for name, pred_list in results.items():
            score = mean_absolute_percentage_error(actual_prices, pred_list)
            mape_scores[name] = score

        # 6. 绘图对比
        plt.figure(figsize=(15, 8))

        # 绘制真实全天文件的截取段
        plt.plot(truth_segment['datetime'], actual_prices,
                 label='真实走势 (4.8 all day)', color='black', linewidth=3, zorder=5)

        # 绘制各模型预测路径
        for name, pred_list in results.items():
            plt.plot(truth_segment['datetime'], pred_list,
                     label=f'{name} (MAPE: {mape_scores[name]:.4%})',
                     color=model_colors[name], alpha=0.8, linestyle='--')

        plt.title('以太币 05:04-06:04 逐分钟递归预测对比', fontsize=16)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend(loc='best')
        plt.grid(True, alpha=0.2)
        plt.gcf().autofmt_xdate()

        plt.show()

        # 输出统计结果
        print("\n" + "=" * 45)
        print(f"🏆 05:04-06:04 阶段性误差分析 (MAPE)")
        print("-" * 45)
        # 按误差从小到大排序输出
        sorted_scores = sorted(mape_scores.items(), key=lambda x: x[1])
        for name, score in sorted_scores:
            print(f"{name:15} : {score:.4%}")
        print("=" * 45)

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    run_minute_by_minute_iteration()