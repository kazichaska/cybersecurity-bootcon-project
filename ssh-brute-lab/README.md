# SSH + RDP + Web Attack Practice Lab

BootCon lab environment for safe, local cybersecurity training with Ansible + Docker + Kali.

## Included scenarios

- SSH brute-force practice target (`target_ssh`)
- RDP brute-force practice target (`rdp_target`)
- bWAPP web application target (`bwapp_web`)

## Prerequisites

- Docker + Colima
- Ansible with `community.docker` collection
- Python 3.11+

Install Ansible collections:

```bash
ansible-galaxy collection install -r ansible/requirements.yml
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Deploy the full lab

```bash
python ../labctl.py setup
```

Optional (HTML report + open in browser):

```bash
python ../labctl.py setup --open
```

## Verify the environment

From the repository root:

```bash
python ../labctl.py verify
```

Check current runtime and container state:

```bash
python ../labctl.py status
```

## Run attack practice scripts

Scripts are mounted into Kali at `/opt/lab`.

```bash
python ../labctl.py attack-ssh -- --help
python ../labctl.py attack-rdp -- --help
python ../labctl.py attack-web
```

Web/XSS practice uses the local bWAPP service exposed on `http://localhost:8080`.

Common examples:

```bash
python ../labctl.py attack-ssh -- --target target_ssh --username root
python ../labctl.py attack-ssh -- --target target_ssh --username root --skip-scan
python ../labctl.py attack-rdp -- --target rdp_target --username admin
python ../labctl.py attack-rdp -- --target rdp_target --username admin --startup-wait 10
python ../labctl.py attack-web
```

Default lab targets:

- `target_ssh` for SSH practice
- `rdp_target` for RDP practice
- `bwapp_web` for web practice

SSH script syntax:

```bash
python ../labctl.py attack-ssh -- --target <hostname> --port <port> --username <user> --wordlist <path> [--skip-scan]
```

RDP script syntax:

```bash
python ../labctl.py attack-rdp -- --target <hostname> --port <port> --username <user> --wordlist <path> [--startup-wait <seconds>]
```

## Web / XSS practice

bWAPP is published on the host at:

```text
http://localhost:8080/bWAPP/
```

Default bWAPP login used by the lab script:

- username: `bee`
- password: `bug`

Useful pages:

- login: `http://localhost:8080/bWAPP/login.php`
- portal: `http://localhost:8080/bWAPP/portal.php`
- security settings: `http://localhost:8080/bWAPP/security.php`
- reflected XSS lab: `http://localhost:8080/bWAPP/xss_get.php`

Automated reflected XSS demo from the host:

```bash
python ../labctl.py attack-web
```

Top-level web/XSS syntax:

```bash
python ../labctl.py attack-web
```

What the XSS script does:

- logs into bWAPP as `bee / bug`
- sets the security level to `low`
- sends the payload `<script>alert('XSS')</script>` to the reflected XSS page
- checks whether the payload is reflected in the response

Manual learner workflow for XSS:

1. Run `python ../labctl.py setup`
2. Open `http://localhost:8080/bWAPP/login.php`
3. Sign in with `bee / bug`
4. Set the security level to `low`
5. Open the reflected XSS page
6. Submit a payload such as `<script>alert('XSS')</script>`
7. Observe that the input is reflected without proper output encoding

Learner note:

- the SSH and RDP scripts run from Kali
- the bWAPP XSS script runs from the host because it targets the host-mapped URL `localhost:8080`

## Cleanup

```bash
python ../labctl.py cleanup
```

Optional (HTML report + open in browser):

```bash
python ../labctl.py cleanup --open
```

## Operator commands

- `python ../labctl.py doctor` checks Colima, Docker context, and container status view
- `python ../labctl.py status` shows Colima, Docker, running containers, and `pentest-net` IPs
- `python ../labctl.py shell` opens a shell in `kali_attacker`
- `python ../labctl.py lesson --track ssh` walks through instructor prompts and expected outputs
- `python ../labctl.py lesson --track ssh --run` executes all lesson steps end-to-end
- `python ../labctl.py lesson --track remediate --run` demonstrates exploit-then-harden-then-retest
- `make -C .. setup verify cleanup` runs lifecycle commands from repo root

## Kali usage

Open a shell in the Kali container:

```bash
python ../labctl.py shell
```

Common Kali commands inside `kali_attacker`:

```bash
ping -c 2 target_ssh
ping -c 2 rdp_target
nmap -p 22 target_ssh
nmap -p 3389 rdp_target
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://target_ssh
hydra -l admin -P /usr/share/wordlists/rockyou.txt rdp://rdp_target
python3 /opt/lab/ssh-bruteforce.py --target target_ssh --username root
python3 /opt/lab/rdp-bruteforce.py --target rdp_target --username admin
```

Useful checks inside Kali:

- `which hydra` confirms Hydra is installed
- `which nmap` confirms Nmap is installed
- `ls /usr/share/wordlists` shows available wordlists
- `head /usr/share/wordlists/rockyou.txt` previews the beginning of the wordlist
- `python3 /opt/lab/ssh-bruteforce.py --help` shows SSH script options
- `python3 /opt/lab/rdp-bruteforce.py --help` shows RDP script options

Useful web/XSS checks from the host:

- `curl -I http://localhost:8080/bWAPP/login.php` confirms the app is reachable
- `python ../labctl.py attack-web` runs the automated reflected XSS demo

## Learner workflow

Recommended sequence for first-time learners:

1. `python ../labctl.py doctor`
2. `python ../labctl.py setup`
3. `python ../labctl.py status`
4. `python ../labctl.py shell`
5. From Kali, test connectivity with `ping` and `nmap`
6. Run `python ../labctl.py attack-ssh -- --target target_ssh --username root`
7. Run `python ../labctl.py attack-rdp -- --target rdp_target --username admin`
8. Run `python ../labctl.py attack-web` for the reflected XSS demo
9. Review results, then run `python ../labctl.py cleanup`

## Demo credentials

Default practice credentials configured by the lab:

- `target_ssh`: `root / toor`
- `rdp_target`: `admin / password123`
- `bwapp_web`: `bee / bug`

## What learners should notice

- `target_ssh` is reachable on port `22` inside the Docker network and on host port `2222`
- `rdp_target` is reachable on port `3389`
- `bwapp_web` is reachable at `http://localhost:8080/bWAPP/`
- the Kali container resolves target names over the `pentest-net` Docker network
- Hydra may print cleanup warnings or resolution noise even after a valid password is found
- a successful brute-force result is the line showing `login:` and `password:` for the target
- a successful reflected XSS demo shows the payload returned unencoded in the response

## Troubleshooting

If something fails, check these first:

- run `python ../labctl.py status` to confirm container names and IPs
- run `python ../labctl.py doctor` to confirm Colima and Docker are healthy
- use the correct target names: `target_ssh`, `rdp_target`, `bwapp_web`
- if SSH succeeds but Hydra exits non-zero, read the output for a valid credential line before assuming failure
- if RDP fails, enter Kali with `python ../labctl.py shell` and test `ping rdp_target` and `nmap -p 3389 rdp_target`
- if the web demo fails, check `http://localhost:8080/bWAPP/login.php` in a browser and confirm `bwapp_web` is running in `python ../labctl.py status`
- if the lab changed, rerun `python ../labctl.py cleanup` followed by `python ../labctl.py setup`

## Command reference

Top-level syntax:

```bash
python ../labctl.py [--dry-run] <command> [options]
```

Available commands:

- `python ../labctl.py setup` deploys the lab with Ansible
- `python ../labctl.py verify` runs the lab verification script
- `python ../labctl.py cleanup` removes lab containers and resources
- `python ../labctl.py doctor` checks local prerequisites
- `python ../labctl.py status` prints live Colima, Docker, and container status
- `python ../labctl.py attack-ssh -- ...` runs the SSH workflow from Kali
- `python ../labctl.py attack-rdp -- ...` runs the RDP workflow from Kali
- `python ../labctl.py attack-web` runs the reflected XSS workflow against bWAPP from the host
- `python ../labctl.py shell` opens a shell inside `kali_attacker`
- `python ../labctl.py lesson --track <ssh|rdp|web|remediate>` runs guided lesson mode
- `python ../labctl.py report --open` writes and opens an HTML status report
- `python ../labctl.py harden` applies the hardening playbook
- `python ../labctl.py scan --type <fs|images>` runs Trivy scans
- `python ../labctl.py detect --container <name> --seconds 60` captures and analyzes traffic signals
- `python ../labctl.py ctf --track <ssh|rdp|web> --setup` plants a flag for CTF mode
- `python ../labctl.py quiz --track <ssh|rdp|web|remediate>` runs the quiz workflow

Useful options:

- `--dry-run` prints commands without executing them
- `setup --open` opens the generated setup report in a browser
- `cleanup --open` opens the generated cleanup report in a browser
- `lesson --run` executes lesson steps instead of only printing guidance

## Safety

Use this lab only for authorized testing and education. Never run these techniques against systems you do not own or have explicit permission to assess.
