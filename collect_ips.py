import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://ip.164746.xyz', 
    'https://cf.090227.xyz', 
    'https://stock.hostmonit.com/CloudFlareYesV6',
    'https://www.wetest.vip/page/cloudflare/address_v4.html'
]

# 正则表达式用于匹配IPv4地址
ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

# 更严格的IPv6正则表达式
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
        parts = ip.split(':')
        if len(parts) > 8:
            return False
        if '::' 在 ip:
            if ip.count('::') > 1:
                return False
            expanded = ip.replace('::', ':' * (9 - len(parts)))
            parts = expanded.split(':')
            if len(parts) != 8:
                return False
        elif len(parts) != 8:
            return False
        for part in parts:
            if part and (len(part) > 4 or not all(c in '0123456789abcdefABCDEF' for c in part)):
                return False
        return True
    except:
        return False

for url in urls:
    try:
        # 发送HTTP请求获取网页内容
        print(f"尝试请求: {url}")
        response = requests.get(url, timeout=10)
        
        # 确保请求成功
        if response.status_code == 200:
            html_content = response.text
            print(f"成功获取 {url} 的内容，长度: {len(html_content)} 字节")
            
            # 使用正则表达式查找IPv4地址
            ipv4_matches = re.findall(ipv4_pattern, html_content, re.IGNORECASE)
            print(f"从 {url} 找到 {len(ipv4_matches)} 个IPv4地址: {ipv4_matches}")
            unique_ipv4.update(ipv4_matches)
            
            # 使用正则表达式查找IPv6地址
            ipv6_matches = re.findall(ipv6_pattern, html_content, re.IGNORECASE)
            print(f"从 {url} 找到 {len(ipv6_matches)} 个IPv6地址: {ipv6_matches}")
            # 验证并添加合法的IPv6地址
            for ip in ipv6_matches:
                if is_valid_ipv6(ip):
                    normalized_ip = ip.lower()
                    unique_ipv6.add(normalized_ip)
        else:
            print(f"请求 {url} 返回状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f'请求 {url} 失败: {e}')
        continue

# 始终创建文件，即使为空
with open('ip.txt', 'w') as file:
    if unique_ipv4:
        sorted_ipv4 = sorted(unique_ipv4, key=lambda ip: [int(part) for part in ip.split('.')])
        for ip in sorted_ipv4:
            file.write(ip + '\n')
        print(f'已保存 {len(sorted_ipv4)} 个唯一IPv4地址到ip.txt文件。')
    else:
        print('未找到有效的IPv4地址，创建空ip.txt文件。')

with open('ipv6.txt', 'w') as file:
    if unique_ipv6:
        sorted_ipv6 = sorted(unique_ipv6)
        for ip in sorted_ipv6:
            file.write(ip + '\n')
        print(f'已保存 {len(sorted_ipv6)} 个唯一IPv6地址到ipv6.txt文件。')
    else:
        print('未找到有效的IPv6地址，创建空ipv6.txt文件。')

# 打印文件内容以便调试
for file in ['ip.txt', 'ipv6.txt']:
    if os.path.exists(file):
        print(f"{file} 内容:")
        with open(file, 'r') as f:
            print(f.read() or "空文件")
    else:
        print(f"{file} 未生成")
