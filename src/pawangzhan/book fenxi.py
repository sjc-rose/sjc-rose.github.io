import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- 1. 环境配置 ---
# 设置可视化风格
sns.set_theme(style="whitegrid")
# 解决 Mac 系统中文字体显示问题
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def analyze_books_data(file_path):
    if not os.path.exists(file_path):
        print(f"❌ 错误：在当前目录下找不到文件 {file_path}")
        return

    # --- 2. 加载数据 ---
    print("📖 正在读取数据并进行统计分析...")
    df = pd.read_excel(file_path)

    # --- 3. 核心统计计算 ---
    # 按类别分组，计算平均价格、中位数和书籍数量
    stats = df.groupby('类别')['价格 (GBP)'].agg(['mean', 'median', 'count']).reset_index()
    stats.columns = ['类别', '平均价格', '价格中位数', '书籍数量']

    # 按平均价格从高到低排序，方便后续绘图展示
    stats = stats.sort_values(by='平均价格', ascending=False)

    print("\n--- 各类别统计摘要 ---")
    print(stats.to_string(index=False))

    # --- 4. 可视化分析 ---
    print("\n🎨 正在生成可视化图表...")

    # 图表 A：各类别平均价格对比 (条形图)
    plt.figure(figsize=(12, 8))
    sns.barplot(data=stats, x='平均价格', y='类别', palette='viridis')
    plt.title('各类别书籍平均价格对比', fontsize=16, pad=20)
    plt.xlabel('平均价格 (单位: £)', fontsize=12)
    plt.ylabel('书籍分类', fontsize=12)
    plt.tight_layout()
    plt.savefig('avg_price_comparison.png', dpi=300)
    print("✅ 已保存：avg_price_comparison.png")

    # 图表 B：各类别价格分布状况 (箱线图)
    # 箱线图可以直观看到价格的波动区间和中位数
    plt.figure(figsize=(12, 10))
    sns.boxplot(data=df, x='价格 (GBP)', y='类别', order=stats['类别'], palette='Set3')
    plt.title('各类别书籍价格分布箱线图', fontsize=16, pad=20)
    plt.xlabel('价格区间 (单位: £)', fontsize=12)
    plt.ylabel('书籍分类', fontsize=12)
    plt.tight_layout()
    plt.savefig('price_boxplot.png', dpi=300)
    print("✅ 已保存：price_boxplot.png")

    # --- 5. 结果导出 ---
    summary_filename = 'category_analysis_summary.xlsx'
    stats.to_excel(summary_filename, index=False)
    print(f"\n💾 详细统计报表已保存至: {summary_filename}")

    plt.show()


if __name__ == "__main__":
    # 确保文件名与你之前抓取生成的文件名完全一致
    analyze_books_data('books_fixed_data.xlsx')