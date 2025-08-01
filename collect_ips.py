import requests
from bs4 import BeautifulSoup
import re
import os

# Target URL list
urls = [
    'https://api.uouin.com/cloudflare.html',
    'https://www.wetest.vip/page/cloudflare/address_v4.html'
]

# Regular expression for matching IPv4 addresses
ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

# Strict IPv6 regular expression
ipv6_pattern = r'(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}|:(?::[0-9a-fA-F]{1,4}){1,7}|::)'

# Define files to process
files_to_process = ['ip.txt', 'ipv6.txt']

# Check if files exist and delete them
for file_name in files_to_process:
    if os.path.exists(file_name):
        os.remove(file_name)

# Use sets to store IP addresses for automatic deduplication
unique_ipv4 = set()
unique_ipv6 = set()

def is_valid_ipv6(ip):
    """Validate if an IPv6 address is legal"""
    try:
        parts = ip.split(':')
        if len(parts) > 8:
            return False
        if '::' in ip:
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
        # Send HTTP request to fetch web content
        print(f"Attempting to request: {url}")
        response = requests.get(url, timeout=10)
        
        # Ensure the request is successful
        if response.status_code == 200:
            html_content = response.text
            print(f"Successfully fetched {url}, content length: {len(html_content)} bytes")
            
            # Find IPv4 addresses using regex
            ipv4_matches = re.findall(ipv4_pattern, html_content, re.IGNORECASE)
            print(f"Found {len(ipv4_matches)} IPv4 addresses from {url}: {ipv4_matches}")
            unique_ipv4.update(ipv4_matches)
            
            # Find IPv6 addresses using regex
            ipv6_matches = re.findall(ipv6_pattern, html_content, re.IGNORECASE)
            print(f"Found {len(ipv6_matches)} IPv6 addresses from {url}: {ipv6_matches}")
            # Validate and add legal IPv6 addresses
            for ip in ipv6_matches:
                if is_valid_ipv6(ip):
                    normalized_ip = ip.lower()
                    unique_ipv6.add(normalized_ip)
        else:
            print(f"Request to {url} returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed: {e}")
        continue

# Always create files, even if empty
with open('ip.txt', 'w') as file:
    if unique_ipv4:
        sorted_ipv4 = sorted(unique_ipv4, key=lambda ip: [int(part) for part in ip.split('.')])
        for ip in sorted_ipv4:
            file.write(ip + '\n')
        print(f"Saved {len(sorted_ipv4)} unique IPv4 addresses to ip.txt.")
    else:
        print("No valid IPv4 addresses found, creating empty ip.txt.")

with open('ipv6.txt', 'w') as file:
    if unique_ipv6:
        sorted_ipv6 = sorted(unique_ipv6)
        for ip in sorted_ipv6:
            file.write(ip + '\n')
        print(f"Saved {len(sorted_ipv6)} unique IPv6 addresses to ipv6.txt.")
    else:
        print("No valid IPv6 addresses found, creating empty ipv6.txt.")

# Print file contents for debugging
for file_name in files_to_process:
    if os.path.exists(file_name):
        print(f"{file_name} contents:")
        with open(file_name, 'r') as f:
            print(f.read() or "Empty file")
    else:
        print(f"{file_name} not generated")
