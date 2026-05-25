# fail2ban — Automated IP Blocking After Auth Failures

## What is it?

**fail2ban** is a daemon that monitors log files (SSH, Apache, FTP, etc.) for repeated authentication failures and automatically creates temporary firewall rules (via iptables/nftables) to block the offending source IP.

## How it works

```
Auth failure → syslog/journal → fail2ban watches log →
  N failures within T seconds → iptables DROP rule for source IP →
    After ban duration expires → rule removed automatically
```

Default SSH jail settings (commonly):
- **maxretry:** 5 failures
- **findtime:** 600 seconds (10 minutes)
- **bantime:** 600 seconds (10 minutes)

## Why it matters

Without fail2ban, an attacker running Hydra with 16 threads can attempt **960+ passwords per minute** against SSH. With fail2ban set to 5 retries in 60 seconds, the attacker's IP gets blocked after ~5 attempts, making full wordlist scans impractical.

## Lab context

The lab does **not** install fail2ban by default so that brute-force succeeds during the lesson. After the lesson, the `harden` command disables password auth — a stronger control. fail2ban is discussed as a **complementary** layer.

## Installing and configuring fail2ban (real system)

```bash
# Install
sudo apt install fail2ban

# Create local override (don't edit /etc/fail2ban/jail.conf directly)
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Edit /etc/fail2ban/jail.local — enable SSH jail:
[sshd]
enabled  = true
port     = ssh
maxretry = 3
bantime  = 3600   # ban for 1 hour
findtime = 300    # within 5 minutes

# Restart
sudo systemctl restart fail2ban

# Check status
sudo fail2ban-client status sshd
```

## Checking if an IP is banned

```bash
sudo fail2ban-client status sshd
# Shows Banned IP list
```

## Limitations

- Does **not** replace strong authentication (key auth is still better)
- Attackers can distribute attempts across many IPs (distributed brute-force)
- Legitimate users can lock themselves out (tune maxretry carefully)
- Does not protect against valid credentials — only slows guessing

## Further reading

- [fail2ban documentation](https://www.fail2ban.org/wiki/index.php/MANUAL_0_8)
- [MITRE T1110 mitigations](https://attack.mitre.org/techniques/T1110/)
