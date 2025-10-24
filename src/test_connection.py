#!/usr/bin/env python3
"""
Test script to verify connection handling improvements
"""

import requests
import warnings

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def test_connection(url):
    """Test connection to a URL with different methods"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print(f"Testing connection to: {url}")
    
    # Test 1: With SSL verification
    try:
        print("  Trying with SSL verification...")
        resp = requests.get(url, timeout=10, headers=headers)
        print(f"  ✅ Success! Status: {resp.status_code}")
        return True
    except requests.exceptions.SSLError as e:
        print(f"  ❌ SSL Error: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ Connection Error: {e}")
    except Exception as e:
        print(f"  ❌ Other Error: {e}")
    
    # Test 2: Without SSL verification
    try:
        print("  Trying without SSL verification...")
        resp = requests.get(url, timeout=10, verify=False, headers=headers)
        print(f"  ✅ Success! Status: {resp.status_code}")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ Connection Error: {e}")
    except Exception as e:
        print(f"  ❌ Other Error: {e}")
    
    print("  ❌ All connection methods failed")
    return False

if __name__ == "__main__":
    # Test with various sites
    test_sites = [
        "https://httpbin.org/get",  # Test site that should work
        "https://python.org",       # Python.org
        "https://example.com",      # Simple test site
        "https://google.com",       # Google (might have anti-bot measures)
        "https://python.com",       # The problematic site
    ]
    
    print("Testing connection improvements...\n")
    
    for site in test_sites:
        success = test_connection(site)
        print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
        print("-" * 50) 