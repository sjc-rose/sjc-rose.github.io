import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- 1. 环境配置 ---
sns.set_theme(style="whitegrid")
# Mac 系统中文字体配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def analyze_books_rating(file_path):
    if not os.path.exists(file_path):
        print(f"❌ 错误：在当前目录下找不到文件 {file_path}")
        return

    # --- 2. 加载数据 ---
    print("📖 正在读取数据并计算平均评分...")
    df = pd.read_excel(file_path)

    # --- 3. 核心统计计算 ---
    # 按类别分组，计算评分的平均值
    rating_stats = df.groupby('类别')['评分'].mean().reset_index()
    rating_stats.columns = ['类别', '平均评分']

    # 按评分从高到低排序
    rating_stats = rating_stats.sort_values(by='平均评分', ascending=False)

    print("\n--- 各类别平均评分榜单 ---")
    print(rating_stats.to_string(index=False))

    # --- 4. 可视化分析 ---
    print("\n🎨 正在生成评分分布图...")

    plt.figure(figsize=(12, 9))

    # 使用 color palette 增强视觉效果：评分越高，颜色越暖/深
    pal = sns.color_palette("YlGnBu", len(rating_stats))
    rank = rating_stats['平均评分'].argsort().argsort()  # 用于颜色排序

    sns.barplot(
        data=rating_stats,
        x='平均评分',
        y='类别',
        palette=np.array(pal)[rank]
    )

    # 在条形图末端标注具体分值
    for i, v in enumerate(rating_stats['平均评分']):
        plt.text(v + 0.05, i, f"{v:.2f}", va='center', fontsize=10, color='black')

    plt.title('各类别图书平均评分排行 (1-5星)', fontsize=16, pad=20)
    plt.xlabel('平均评分', fontsize=12)
    plt.ylabel('书籍分类', fontsize=12)
    plt.xlim(0, 5.5)  # 评分范围是1-5，稍微留白

    plt.tight_layout()

    # 保存图片
    output_img = 'category_avg_rating.png'
    plt.savefig(output_img, dpi=300)
    print(f"✅ 评分分析图已保存为：{output_img}")

    plt.show()


if __name__ == "__main__":
    import numpy as np  # 辅助颜色处理

    analyze_books_rating('books_fixed_data.xlsx')