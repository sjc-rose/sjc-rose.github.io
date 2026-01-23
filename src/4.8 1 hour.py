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
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac环境
plt.rcParams['axes.unicode_minus'] = False


def run_hourly_iteration():
    # 文件路径
    train_file = '第四周大数据分析作业.xlsx'  # 4.1-4.8 05:00 数据
    truth_file = '4.8 all day.xlsx'  # 4.8 全天真实数据

    try:
        # 加载数据
        df_train = pd.read_excel(train_file).sort_values('datetime')
        df_truth = pd.read_excel(truth_file).sort_values('datetime')

        df_train['datetime'] = pd.to_datetime(df_train['datetime'])
        df_truth['datetime'] = pd.to_datetime(df_truth['datetime'])

        # 设定时间点
        start_time = pd.to_datetime('2019-04-08 05:04:00')
        end_time = pd.to_datetime('2019-04-08 06:04:00')  # 预测到6点04分

        # 截取真实走势作为对比
        truth_segment = df_truth[(df_truth['datetime'] >= start_time) & (df_truth['datetime'] <= end_time)].copy()
        total_minutes = len(truth_segment)

        print(f"✅ 准备预测从 {start_time} 到 {end_time}，共 {total_minutes} 分钟")

        # 2. 特征工程 (窗口30分钟)
        window_size = 30

        def prepare_data(data):
            X, y = [], []
            vals = data['close'].values
            for i in range(len(vals) - window_size):
                X.append(vals[i: i + window_size])
                y.append(vals[i + window_size])
            return np.array(X), np.array(y)

        X_train, y_train = prepare_data(df_train)

        # 3. 初始化模型
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.08),
            'LightGBM': LGBMRegressor(n_estimators=100, verbose=-1),
            'CatBoost': CatBoostRegressor(iterations=100, verbose=0)
        }

        results = {}
        colors = {'RF': 'blue', 'XGB': 'red', 'LGBM': 'green', 'Cat': 'orange'}

        # 4. 迭代预测逻辑 (每10分钟为一个预测块)
        for name, model in models.items():
            print(f"正在训练并迭代预测: {name}...")
            model.fit(X_train, y_train)

            # 初始数据窗口
            current_window = list(df_train['close'].values[-window_size:])
            all_preds = []

            # 以10分钟为一个周期进行迭代
            for _ in range(0, total_minutes, 10):
                # 预测接下来的10步（如果剩余不足10步则取剩余步数）
                steps_to_predict = min(10, total_minutes - len(all_preds))

                for _ in range(steps_to_predict):
                    input_x = np.array(current_window[-window_size:]).reshape(1, -1)
                    pred = model.predict(input_x)[0]
                    all_preds.append(pred)
                    current_window.append(pred)  # 递归输入

            results[name] = all_preds

        # 5. 计算 MAPE 误差
        actual_vals = truth_segment['close'].values
        metrics = {}
        for name, pred in results.items():
            # 确保长度对齐
            error = mean_absolute_percentage_error(actual_vals, pred[:len(actual_vals)])
            metrics[name] = error

        # 6. 可视化
        plt.figure(figsize=(14, 7))

        # 真实走势
        plt.plot(truth_segment['datetime'], actual_vals, label='真实走势 (4.8 All Day)', color='black', linewidth=3)

        # 模型走势
        model_color_map = {'Random Forest': 'blue', 'XGBoost': 'red', 'LightGBM': 'green', 'CatBoost': 'orange'}
        for name, pred in results.items():
            plt.plot(truth_segment['datetime'], pred[:len(actual_vals)],
                     label=f'{name} (误差: {metrics[name]:.4%})',
                     color=model_color_map[name], alpha=0.8, linestyle='--')

        plt.title('4月8日 05:04-06:04 价格预测对比 (10分钟步进迭代)', fontsize=14)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.gcf().autofmt_xdate()
        plt.show()

        # 打印底部结果
        print("\n" + "=" * 40)
        print(f"📊 误差统计 (MAPE) - 截止 06:04")
        print("-" * 40)
        for name, err in metrics.items():
            print(f"{name:15}: {err:.4%}")
        print("=" * 40)

    except Exception as e:
        print(f"❌ 运行失败: {e}")


if __name__ == "__main__":
    run_hourly_iteration()