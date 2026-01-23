try:
    import pandas as pd

    print("✅ Pandas 安装成功！")
    print("版本号:", pd.__version__)

    # 尝试创建一个小型测试表
    data = {'币种': ['ETH', 'BTC'], '价格': [2400, 65000]}
    df = pd.DataFrame(data)
    print("\n测试数据表如下：")
    print(df)
except ImportError:
    print("❌ Pandas 未安装成功，请检查环境。")
