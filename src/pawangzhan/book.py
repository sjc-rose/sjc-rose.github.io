import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


def get_books_data(target_count=500):
    base_url = "https://books.toscrape.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    all_books = []

    print("正在获取全部分类...")
    response = requests.get(base_url, headers=headers)
    response.encoding = 'utf-8'  # 强制指定编码，防止乱码
    soup = BeautifulSoup(response.text, 'html.parser')
    category_list = soup.select('.nav-list ul li a')

    for cat in category_list:
        if len(all_books) >= target_count:
            break

        category_name = cat.text.strip()
        category_url = base_url + cat['href']
        print(f"📂 正在进入分类: {category_name}")

        current_cat_url = category_url
        while current_cat_url and len(all_books) < target_count:
            try:
                cat_res = requests.get(current_cat_url, headers=headers)
                cat_res.encoding = 'utf-8'
                cat_soup = BeautifulSoup(cat_res.text, 'html.parser')

                books = cat_soup.select('.product_pod')
                for book in books:
                    if len(all_books) >= target_count:
                        break

                    title = book.h3.a['title']
                    price_text = book.select_one('.price_color').text

                    # --- 修复点：使用正则提取纯数字 ---
                    price_match = re.search(r"(\d+\.\d+)", price_text)
                    price = float(price_match.group(1)) if price_match else 0.0

                    rating_class = book.select_one('.star-rating')['class'][1]
                    rating = rating_map.get(rating_class, 0)

                    all_books.append({
                        '书籍名称': title,
                        '类别': category_name,
                        '价格 (GBP)': price,
                        '评分': rating
                    })

                next_button = cat_soup.select_one('.next a')
                if next_button:
                    current_cat_url = category_url.rsplit('/', 1)[0] + '/' + next_button['href']
                else:
                    current_cat_url = None
            except Exception as e:
                print(f"解析出错: {e}")
                break

        print(f"   已累计抓取: {len(all_books)} 本")

    if all_books:
        df = pd.DataFrame(all_books)
        df = df.sort_values(by=['类别', '评分'], ascending=[True, False])
        output_file = 'books_fixed_data.xlsx'
        df.to_excel(output_file, index=False)
        print(f"\n✨ 任务成功！数据已存入 {output_file}")
    else:
        print("未获取到数据。")


if __name__ == "__main__":
    get_books_data(500)
