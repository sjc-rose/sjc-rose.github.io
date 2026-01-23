import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. 环境配置：解决中文显示问题
# Mac用户使用 'Arial Unicode MS'，Windows用户建议改为 'SimHei'
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def plot_eth_trends(file_path):
    try:
        # 2. 读取数据
        print(f"正在读取文件: {file_path}...")
        df = pd.read_excel(file_path)

        # 确保时间列是日期格式并排序
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')

        # 3. 创建画布
        plt.figure(figsize=(15, 8))

        # 4. 绘制不同颜色的曲线
        # 使用不同的颜色和线型以便区分
        plt.plot(df['datetime'], df['high'], label='最高价 (High)', color='#e74c3c', linewidth=1, alpha=0.7)
        plt.plot(df['datetime'], df['open'], label='开盘价 (Open)', color='#3498db', linewidth=1, alpha=0.7)
        plt.plot(df['datetime'], df['close'], label='收盘价 (Close)', color='black', linewidth=2)

        # 5. 图表修饰
        plt.title('以太币 (ETH) 价格走势图 - 多维度对比', fontsize=16)
        plt.xlabel('时间', fontsize=12)
        plt.ylabel('价格 (USD)', fontsize=12)

        # 优化时间轴显示
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.gcf().autofmt_xdate()  # 自动倾斜日期标签防止重叠

        plt.legend(loc='best')
        plt.grid(True, linestyle='--', alpha=0.3)

        # 6. 展示与保存
        plt.tight_layout()
        plt.savefig('ETH_Price_Trend.png', dpi=300)
        print("✅ 绘图成功！图片已保存为: ETH_Price_Trend.png")
        plt.show()

    except Exception as e:
        print(f"❌ 运行失败，错误信息: {e}")


if __name__ == "__main__":
    # 请确保文件名与你的文件完全一致
    plot_eth_trends("以太币有时间.xlsx")