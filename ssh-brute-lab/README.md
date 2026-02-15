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

## Run attack practice scripts

Scripts are mounted into Kali at `/opt/lab`.

```bash
python ../labctl.py attack-ssh -- --help
python ../labctl.py attack-rdp -- --help
```

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
- `python ../labctl.py shell` opens a shell in `kali_attacker`
- `python ../labctl.py lesson --track ssh` walks through instructor prompts and expected outputs
- `python ../labctl.py lesson --track ssh --run` executes all lesson steps end-to-end
- `python ../labctl.py lesson --track remediate --run` demonstrates exploit-then-harden-then-retest
- `make -C .. setup verify cleanup` runs lifecycle commands from repo root

## Safety

Use this lab only for authorized testing and education. Never run these techniques against systems you do not own or have explicit permission to assess.
