import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# 1. 配置信息
MOVIE_ID = '26861685'
# 请确保使用你刚才获取的完整 Cookie
MY_COOKIE = 'viewed="1270071"; bid=vycjtVrP1_M; _vwo_uuid_v2=DE373CB067B81FEC080D9A303F3B8B3AF|a261524f07708fe8ea346b1ac864d944; ll="108235"; dbcl2="121620847:hQhkNTHNENY"; ck=xhpM; frodotk_db="7f5b5ac580d16bb07e12105082744310";'


def scrape_300_comments():
    all_comments = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': MY_COOKIE,
        'Referer': f'https://movie.douban.com/subject/{MOVIE_ID}/comments'
    }

    # 300条数据需要爬取 15 页 (0到14)
    total_pages = 15

    for page in range(total_pages):
        start = page * 20
        # sort=new_score 表示按热门排序，也可以改为 time 按时间排序
        url = f'https://movie.douban.com/subject/{MOVIE_ID}/comments?start={start}&limit=20&status=P&sort=new_score'

        try:
            print(f"进度: [{page + 1}/{total_pages}] 正在爬取第 {page + 1} 页...")
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"停止抓取：状态码 {response.status_code}。可能是 Cookie 失效或被暂时封禁。")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.comment-item')

            if not items:
                print("本页未找到评论，可能已达到抓取上限。")
                break

            for item in items:
                # 尝试抓取各项数据，若某项缺失则填充默认值
                try:
                    user = item.select_one('.comment-info a').text
                    rating_tag = item.select_one('.rating')
                    rating = rating_tag['title'] if rating_tag else "未评分"
                    votes = item.select_one('.votes').text
                    time_str = item.select_one('.comment-time')['title']
                    content = item.select_one('.short').text.strip().replace('\n', ' ')

                    all_comments.append({
                        '页码': page + 1,
                        '用户': user,
                        '评分': rating,
                        '有用数': votes,
                        '发布日期': time_str,
                        '评论内容': content
                    })
                except Exception:
                    continue  # 某条评论解析出错则跳过，继续下一条

            # 关键：为了安全，每页抓取后随机休息 3-6 秒
            # 爬 300 条大约需要 1 分钟左右
            time.sleep(random.uniform(3, 6))

        except Exception as e:
            print(f"网络请求出错: {e}")
            break

    # 2. 导出数据
    if all_comments:
        df = pd.DataFrame(all_comments)
        # 按照“有用数”从高到低排序，方便你查看最有价值的评论
        df['有用数'] = pd.to_numeric(df['有用数'], errors='coerce')
        df = df.sort_values(by='有用数', ascending=False)

        output_file = f'douban_300_comments_{MOVIE_ID}.xlsx'
        df.to_excel(output_file, index=False)
        print("\n" + "=" * 30)
        print(f"抓取成功！")
        print(f"实际抓取总数: {len(all_comments)} 条")
        print(f"结果已保存至: {output_file}")
        print("=" * 30)
    else:
        print("未抓取到任何数据，请检查网络或 Cookie。")


if __name__ == "__main__":
    scrape_300_comments()