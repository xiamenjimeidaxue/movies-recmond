# 读取TXT文件
with open('D:/Users/asus/Desktop/output2.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 遍历每一行并检查是否有第三列
for index, line in enumerate(lines, start=1):
    parts = line.strip().split()
    if len(parts) < 3:  # 检查是否少于3列
        first_column = parts[0] if parts else None
        print(f"movieid:{first_column}")