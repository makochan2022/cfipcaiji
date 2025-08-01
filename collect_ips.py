import requests
from bs4 import BeautifulSoup
import re
import os

# Target URL list
urls = [
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://www.wetest.vip/page/cloudflare/address_v6.html'
]

# Regular expression for matching IPv4 addresses
ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

# Updated IPv6 regular expression to match all valid formats, including compressed ones
ipv6_pattern = r'(?:(?:[0-9a-fA-F]{1,4}:){0,7}(?::[0-9a-fA-F]{1,4}){0,7}|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){0,6}|(?::[0-9a-fA-F]{1,4}){0,7}|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){0,5}:|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){0,4}::|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){0,3}::|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){0,2}::|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4})?::|:(?::[0-9a-fA-F]{1,4}){0,6}::|::)'

# Define files to process
files_to_process = ['ip.txt', 'ipv6.txt', 'ipv4notls.txt', 'ipv6notls.txt']

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
        # Split the address by ':'
        parts = ip.split(':')
        # Count non-empty parts and check for valid :: compression
        non_empty_parts = [p for p in parts if p]
        double_colon = ip.count('::')
        
        # If no ::, must have exactly 8 parts
        if double_colon == 0:
            if len(parts) != 8:
                return False
        # If :: exists, must have at most 7 parts (since :: replaces at least one zero block)
        elif double_colon == 1:
            if len(parts) > 8:
                return False
        else:
            return False  # More than one :: is invalid
        
        # Check each part
        for part in non_empty_parts:
            if len(part) > 4 or not all(c in '0123456789abcdefABCDEF' for c in part):
                return False
        
        # Expand compressed address to verify total length
        if double_colon == 1:
            # Calculate missing zero blocks
            missing_blocks = 8 - (len(parts) - 1)  # Subtract 1 for the :: itself
            if missing_blocks < 1:
                return False
            # Expand :: with zeros
            expanded = ip.replace('::', ':' + '0:' * missing_blocks)
            parts = expanded.split(':')
            if len(parts) != 8:
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

# Save IPv4 addresses to ip.txt (port 443) and ipv4notls.txt (port 80)
with open('ip.txt', 'w') as file:
    if unique_ipv4:
        sorted_ipv4 = sorted(unique_ipv4, key=lambda ip: [int(part) for part in ip.split('.')])
        for index, ip in enumerate(sorted_ipv4, start=1):
            file.write(f"{ip}:2053#CF优选节点{index:02d}\n")
        print(f"Saved {len(sorted_ipv4)} unique IPv4 addresses to ip.txt.")
    else:
        print("No valid IPv4 addresses found, creating empty ip.txt.")

with open('ipv4notls.txt', 'w') as file:
    if unique_ipv4:
        sorted_ipv4 = sorted(unique_ipv4, key=lambda ip: [int(part) for part in ip.split('.')])
        for index, ip in enumerate(sorted_ipv4, start=1):
            file.write(f"{ip}:2052#CF优选节点{index:02d}\n")
        print(f"Saved {len(sorted_ipv4)} unique IPv4 addresses to ipv4notls.txt.")
    else:
        print("No valid IPv4 addresses found, creating empty ipv4notls.txt.")

# Save IPv6 addresses to ipv6.txt (port 443) and ipv6notls.txt (port 80)
with open('ipv6.txt', 'w') as file:
    if unique_ipv6:
        sorted_ipv6 = sorted(unique_ipv6)
        for index, ip in enumerate(sorted_ipv6, start=1):
            file.write(f"[{ip}]:2053#CF优选节点{index:02d}\n")
        print(f"Saved {len(sorted_ipv6)} unique IPv6 addresses to ipv6.txt.")
    else:
        print("No valid IPv6 addresses found, creating empty ipv6.txt.")

with open('ipv6notls.txt', 'w') as file:
    if unique_ipv6:
        sorted_ipv6 = sorted(unique_ipv6)
        for index, ip in enumerate(sorted_ipv6, start=1):
            file.write(f"[{ip}]:2052#CF优选节点{index:02d}\n")
        print(f"Saved {len(sorted_ipv6)} unique IPv6 addresses to ipv6notls.txt.")
    else:
        print("No valid IPv6 addresses found, creating empty ipv6notls.txt.")

# Print file contents for debugging
for file_name in files_to_process:
    if os.path.exists(file_name):
        print(f"{file_name} contents:")
        with open(file_name, 'r') as f:
            print(f.read() or "Empty file")
    else:
        print(f"{file_name} not generated")
