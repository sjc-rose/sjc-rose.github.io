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
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac字体，Windows可改为'SimHei'
plt.rcParams['axes.unicode_minus'] = False


def run_all_day_comparison():
    # 文件路径（请确保这两个文件在同一个文件夹下）
    train_file = '第四周大数据分析作业.xlsx'  # 包含4.1-4.8 05:00数据
    truth_file = '4.8 all day.xlsx'  # 包含4.8全天真实数据

    try:
        # 加载数据
        df_train = pd.read_excel(train_file).sort_values('datetime')
        df_truth = pd.read_excel(truth_file).sort_values('datetime')

        # 统一时间格式
        df_train['datetime'] = pd.to_datetime(df_train['datetime'])
        df_truth['datetime'] = pd.to_datetime(df_truth['datetime'])

        # 确定预测起点 (4月8日 05:04)
        start_time = pd.to_datetime('2019-04-08 05:04:00')
        # 截取预测部分（从05:04到当天结束）
        truth_segment = df_truth[df_truth['datetime'] >= start_time].copy()
        prediction_steps = len(truth_segment)

        print(f"✅ 数据加载成功。预测步数: {prediction_steps} 分钟")

        # 2. 特征工程 (滑动窗口)
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
            'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.1),
            'LightGBM': LGBMRegressor(n_estimators=100, verbose=-1),
            'CatBoost': CatBoostRegressor(iterations=100, verbose=0)
        }

        colors = {
            'Truth': 'black',
            'Random Forest': 'blue',
            'XGBoost': 'red',
            'LightGBM': 'green',
            'CatBoost': 'orange'
        }

        results = {}

        # 4. 训练与递归预测
        for name, model in models.items():
            print(f"正在训练并滚动预测: {name}...")
            model.fit(X_train, y_train)

            # 初始窗口：训练集最后30分钟的价格
            current_window = list(df_train['close'].values[-window_size:])
            predictions = []

            for _ in range(prediction_steps):
                input_data = np.array(current_window[-window_size:]).reshape(1, -1)
                pred = model.predict(input_data)[0]
                predictions.append(pred)
                current_window.append(pred)  # 递归：将预测值加入窗口

            results[name] = predictions

        # 5. 计算误差 (MAPE)
        actual = truth_segment['close'].values
        error_rates = {}
        for name, pred in results.items():
            error = mean_absolute_percentage_error(actual, pred)
            error_rates[name] = error

        # 6. 可视化
        plt.figure(figsize=(15, 8))

        # 绘制真实走势
        plt.plot(truth_segment['datetime'], actual, label='真实全天走势', color=colors['Truth'], linewidth=2, zorder=5)

        # 绘制各模型预测走势
        for name, pred in results.items():
            plt.plot(truth_segment['datetime'], pred, label=f'{name} (MAPE: {error_rates[name]:.2%})',
                     color=colors[name], alpha=0.8)

        plt.title('4月8日全天走势预测对比：四种算法递归模拟', fontsize=16)
        plt.xlabel('时间')
        plt.ylabel('价格 (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('全天预测对比图.png', dpi=300)
        plt.show()

        # 打印误差总结表格
        print("\n" + "=" * 30)
        print("📊 模型误差率统计 (MAPE)")
        print("-" * 30)
        for name, err in error_rates.items():
            print(f"{name:15}: {err:.4%}")
        print("=" * 30)

    except Exception as e:
        print(f"❌ 运行错误: {e}")


if __name__ == "__main__":
    run_all_day_comparison()