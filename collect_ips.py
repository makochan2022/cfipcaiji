import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://api.uouin.com/cloudflare.html'
]

# 正则表达式用于匹配IP地址
ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ipv6_pattern = r'(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}|:?(?::[0-9a-fA-F]{1,4}){1,7})'

# 检查ip.txt和ipv6.txt文件是否存在，如果存在则删除
for file in ['ip.txt', 'ipv6.txt']:
    if os.path.exists(file):
        os.remove(file)

# 使用集合存储IP地址实现自动去重
unique_ipv4 = set()
unique_ipv6 = set()

for url in urls:
    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url, timeout=5)
        
        # 确保请求成功
        if response.status_code == 200:
            # 获取网页的文本内容
            html_content = response.text
            
            # 使用正则表达式查找IPv4地址
            ipv4_matches = re.findall(ipv4_pattern, html_content, re.IGNORECASE)
            unique_ipv4.update(ipv4_matches)
            
            # 使用正则表达式查找IPv6地址
            ipv6_matches = re.findall(ipv6_pattern, html_content, re.IGNORECASE)
            unique_ipv6.update(ipv6_matches)
    except requests.exceptions.RequestException as e:
        print(f'请求 {url} 失败: {e}')
        continue

# 将去重后的IPv4地址按数字顺序排序后写入文件
if unique_ipv4:
    sorted_ipv4 = sorted(unique_ipv4, key=lambda ip: [int(part) for part in ip.split('.')])
    with open('ip.txt', 'w') as file:
        for ip in sorted_ipv4:
            file.write(ip + '\n')
    print(f'已保存 {len(sorted_ipv4)} 个唯一IPv4地址到ip.txt文件。')
else:
    print('未找到有效的IPv4地址。')

# 将去重后的IPv6地址按字符串顺序排序后写入文件
if unique_ipv6:
    sorted_ipv6 = sorted(unique_ipv6)
    with open('ipv6.txt', 'w') as file:
        for ip in sorted_ipv6:
            file.write(ip + '\n')
    print(f'已保存 {len(sorted_ipv6)} 个唯一IPv6地址到ipv6.txt文件。')
else:
    print('未找到有效的IPv6地址。')
