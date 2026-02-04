import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os


def generate_final_wordcloud(file_path):
    # 1. 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 错误：找不到文件 {file_path}，请检查文件名或路径。")
        return

    # 2. 读取 Excel 数据
    print("📖 正在读取 Excel 数据...")
    df = pd.read_excel(file_path)

    # 确保‘评论内容’这一列存在，并合并文本
    if '评论内容' not in df.columns:
        print("❌ 错误：Excel 中没找到‘评论内容’这一列，请检查表头。")
        return

    text = " ".join(df['评论内容'].astype(str))

    # 3. 中文分词 (使用 jieba)
    print("✂️ 正在进行中文分词...")
    words = jieba.cut(text)

    # 定义停用词（过滤掉无意义的虚词）
    stopwords = {
        '的', '了', '在', '是', '我', '有', '一个', '个人', '看', '这', '那', '都', '和', '就',
        '电影', '这部', '真的', '太', '被', '说', '这种', '感觉', '觉得', '还', '让', '去'
    }

    # 过滤词汇：只保留长度大于1的词，且不在停用词列表中
    filtered_words = [word for word in words if len(word) > 1 and word not in stopwords]
    result_text = " ".join(filtered_words)

    # 4. 寻找 Mac 系统中文字体 (解决 OSError: cannot open resource)
    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',  # 苹方
        '/System/Library/Fonts/STHeiti Light.ttc',  # 华文细黑
        '/Library/Fonts/Arial Unicode.ttf',  # 通用 unicode
        '/System/Library/Fonts/Supplemental/Songti.ttc'  # 宋体
    ]

    target_font = None
    for f in font_paths:
        if os.path.exists(f):
            target_font = f
            break

    if not target_font:
        print("❌ 错误：在你的 Mac 上没找到中文字体文件，请确认路径。")
        return
    else:
        print(f"✅ 使用字体: {target_font}")

    # 5. 配置并生成词云
    print("🎨 正在绘制词云图...")
    wc = WordCloud(
        font_path=target_font,
        background_color='white',
        width=1200,
        height=800,
        max_words=100,  # 最多显示100个关键词
        colormap='viridis',  # 颜色主题：可以换成 'plasma', 'inferno', 'magma'
        random_state=42  # 固定随机种子，保证每次生成的布局一致
    )

    wc.generate(result_text)

    # 6. 显示并保存图片
    plt.figure(figsize=(15, 10))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')  # 隐藏坐标轴

    output_image = "movie_wordcloud_result.png"
    wc.to_file(output_image)
    print(f"🎉 大功告成！词云图已保存为: {output_image}")
    plt.show()


if __name__ == "__main__":
    # 填入你之前生成的 Excel 文件名
    generate_final_wordcloud('douban_300_comments_26861685.xlsx')