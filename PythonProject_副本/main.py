import sys


def check_installations():
    libraries = [
        ("numpy", "np"),
        ("pandas", "pd"),
        ("matplotlib", "plt"),
        ("sklearn", "sk"),
        ("tensorflow", "tf")
    ]

    print(f"{'库名':<15} | {'状态':<10} | {'版本号':<15}")
    print("-" * 45)

    for lib_name, alias in libraries:
        try:
            # 动态导入库
            module = __import__(lib_name)

            # 特殊处理 sklearn 的版本获取
            version = module.__version__ if hasattr(module, '__version__') else "已安装"

            print(f"{lib_name:<15} | {'✅ 成功':<10} | {version:<15}")
        except ImportError:
            print(f"{lib_name:<15} | {'❌ 失败':<10} | {'未找到模块':<15}")


if __name__ == "__main__":
    check_installations()
    print("\nPython 解释器路径:", sys.executable)
