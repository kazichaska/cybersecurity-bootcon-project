import subprocess
import time

def verify_windows_container():
    print("[*] Checking Windows container status...")
    
    # Wait for container to initialize
    time.sleep(10)
    
    # Check container status
    status_cmd = "docker ps -f name=windows_target --format '{{.Status}}'"
    status = subprocess.run(status_cmd, shell=True, capture_output=True, text=True)
    
    if "Up" in status.stdout:
        print("[+] Container is running")
        print("[*] Testing RDP port...")
        # Test RDP port
        nmap_cmd = "nmap -p3389 -sV windows_target"
        subprocess.run(nmap_cmd, shell=True)
    else:
        print("[-] Container failed to start properly")
        print(f"Status: {status.stdout}")

if __name__ == "__main__":
    verify_windows_container()