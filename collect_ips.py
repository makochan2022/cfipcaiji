import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://api.uouin.com/cloudflare.html'
]

# 正则表达式用于匹配IPv4地址（保持不变）
ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

# 更严格的IPv6正则表达式，匹配标准和压缩格式
ipv6_pattern = r'(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}|:(?::[0-9a-fA-F]{1,4}){1,7}|::)'

# 检查ip.txt和ipv6.txt文件是否存在，如果存在则删除
for file in ['ip.txt', 'ipv6.txt']:
    if os.path.exists(file):
        os.remove(file)

# 使用集合存储IP地址实现自动去重
unique_ipv4 = set()
unique_ipv6 = set()

def is_valid_ipv6(ip):
    """验证IPv6地址是否合法"""
    try:
        # 分割地址并检查每组是否有效
        parts = ip.split(':')
        if len(parts) > 8:
            return False
        # 检查压缩格式（::）是否只出现一次
        if '::' in ip:
            if ip.count('::') > 1:
                return False
            # 确保压缩后段数合理
            expanded = ip.replace('::', ':' * (9 - len(parts)))
            parts = expanded.split(':')
            if len(parts) != 8:
                return False
        elif len(parts) != 8:
            return False
        # 验证每组是合法的十六进制（0-FFFF）
        for part in parts:
            if part and (len(part) > 4 or not all(c in '0123456789abcdefABCDEF' for c in part)):
                return False
        return True
    except:
        return False

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
            # 验证并添加合法的IPv6地址
            for ip in ipv6_matches:
                if is_valid_ipv6(ip):
                    # 转换为小写并规范化（移除多余前导零）
                    normalized_ip = ':'.join(
                        str(hex(int(part, 16))[2:].zfill(4).lower()) if part else ''
                        for part in ip.replace('::', ':' * (9 - ip.count(':'))).split(':')
                    ) if '::' not in ip else ip.lower()
                    unique_ipv6.add(normalized_ip)
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
