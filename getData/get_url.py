import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# 定义下载图片的函数
def download_image(image_url, file_name):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # 确保请求成功
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"图片已下载：{file_name}")
    except requests.exceptions.RequestException as e:
        print(f"下载图片时遇到问题：{e}")

# 创建一个目录来存储图片
images_dir = 'D:/Users/asus/Desktop/images'
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# 读取TXT文件
with open('D:/Users/asus/Desktop/output2.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 使用线程池下载图片
def main():
    threads = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 3:  # 确保第三列存在
                movie_rating = parts[0]  # 第一列
                image_url = parts[2]  # 第三列
                file_name = os.path.join(images_dir, f"{movie_rating}.jpg")  # 使用第一列的数字作为文件名
                future = executor.submit(download_image, image_url, file_name)
                threads.append(future)
            else:
                print("第三列不存在，跳过这一行。")

    # 等待所有线程完成
    for future in as_completed(threads):
        future.result()  # 获取结果，如果有异常会被抛出

    print("所有图片处理完成。")

if __name__ == "__main__":
    main()