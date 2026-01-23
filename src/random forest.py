import pandas as pd
import matplotlib.pyplot as plt
# 1. 设置文件路径
# 如果文件在同一个文件夹，直接写文件名；如果在别处，请写完整路径
file_path = '第四周大数据分析作业.xlsx'

try:
    # 2. 读取 Excel 文件
    # 如果有多个 Sheet，可以用 sheet_name='Sheet1' 指定
    df = pd.read_excel(file_path)

    # 3. 查看数据
    print("✅ 文件读取成功！")
    print("-" * 30)
    print("数据前 5 行：")
    print(df.head())  # 显示前 5 行

    print("-" * 30)
    print("数据的基本信息：")
    print(df.info())  # 查看列名、数据类型、是否有缺失值

except FileNotFoundError:
    print(f"❌ 错误：在当前目录下没找到文件 '{file_path}'")
    print("请确认文件是否已经移动到 PyCharm 项目文件夹中。")
except Exception as e:
    print(f"❌ 读取出错: {e}")
    import matplotlib.pyplot as plt

# 假设你的列名叫 'Date' 和 'Close'
df.plot(x='datetime', y='close', title='以太币价格走势')
plt.show()
# 2. 如果要进行随机森林预测
data = df['close'].values  # 同样使用小写的 close
# ... 接下来的预测代码 ...