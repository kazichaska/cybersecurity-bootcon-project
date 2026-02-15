import subprocess
import time

def verify_container():
    print("[*] Verifying Windows container status...")
    
    # Check if container is running
    cmd = "docker ps --filter name=windows_target --format '{{.Status}}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if "Up" in result.stdout:
        print("[+] Container is running")
        # Test RDP port
        nmap_cmd = "nmap -p3389 -sV windows_target"
        subprocess.run(nmap_cmd, shell=True)
    else:
        print("[-] Container is not running properly")

if __name__ == "__main__":
    verify_container()