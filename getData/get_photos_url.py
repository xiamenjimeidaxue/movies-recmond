import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

# 读取TXT文件
with open('D:/Users/asus/Desktop/output1.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36'
}

# 定义一个函数，用于爬取和保存数据
def fetch_and_save_data(line, index, output_file):
    time.sleep(random.uniform(2, 5))  # 随机等待时间，避免请求过于频繁
    parts = line.strip().split()
    if len(parts) > 1:
        movie_id = parts[0]
        movie_url = parts[1]
        try:
            response = requests.get(movie_url, headers=headers)
            html = response.content.decode('utf-8')
            soup = BeautifulSoup(html, "html.parser")
            temp1 = soup.select('[data-testid="hero-media__poster"] > div.ipc-media.ipc-media--poster-27x40.ipc-image-media-ratio--poster-27x40.ipc-media--media-radius.ipc-media--baseAlt.ipc-media--poster-l.ipc-poster__poster-image.ipc-media__img > img.ipc-image')
            image_url = None
            for el in temp1:
                image_url = el['src']
                print(el['src'])
                break

            # 将更新后的内容写入文件
            if image_url:
                output_file.write(f"{movie_id} {movie_url} {image_url}\n")
            else:
                output_file.write(f"{movie_id} {movie_url} \n")
        except requests.exceptions.RequestException as e:
            print(f"请求网页时遇到问题：{e}")
            print(f"URL: {movie_url}")
            print("请检查网页链接的合法性，并适当重试。")
            output_file.write(f"{movie_id} {movie_url} \n")

# 打开一个文件用于存储更新后的内容
with open('D:/Users/asus/Desktop/output2.txt', 'w', encoding='utf-8') as output_file:
    # 创建一个线程池，最大线程数为10
    with ThreadPoolExecutor(max_workers=20) as executor:
        # 提交任务到线程池
        futures = [executor.submit(fetch_and_save_data, line, index, output_file) for index, line in enumerate(lines)]

    # 等待所有线程完成
    for future in as_completed(futures):
        future.result()  # 获取结果，如果有异常会被抛出

print("更新完成，结果已保存至 output2.txt")