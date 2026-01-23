import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def plot_eth_chart(file_path):
    try:
        # 1. 读取 Excel 数据
        df = pd.read_excel(file_path)

        # 2. 预处理：将时间设为索引，并确保列名为英文小写（mplfinance的要求）
        # 假设你的列名是 'datetime', 'open', 'high', 'low', 'close', 'volume'
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)

        # 3. 绘制 K 线图
        # type='candle' 表示 K 线图, mav=(5, 10) 表示 5日和 10日均线
        # volume=True 表示显示成交量
        print("正在生成 ETH 走势图...")

        mpf.plot(df,
                 type='candle',
                 style='charles',
                 title='以太币 (ETH/USD) 2019年4月走势图',
                 ylabel='价格 (USD)',
                 ylabel_lower='成交量',
                 volume=True,
                 mav=(5, 10),
                 figsize=(14, 8))

    except Exception as e:
        print(f"读取或绘图失败: {e}")
        print("提示：请检查 Excel 的列名是否包含 datetime, open, high, low, close")


if __name__ == "__main__":
    # 替换成你的文件名
    file_name = "ETH_USD_2019_04.xlsx"
    plot_eth_chart(file_name)