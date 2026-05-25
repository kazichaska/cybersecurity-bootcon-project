# SSH Brute-Force Attacks

**MITRE ATT&CK:** T1110.001 — Brute Force: Password Guessing

## What is it?

A brute-force attack against SSH works by systematically trying username and password combinations until valid credentials are found. Tools like **Hydra** and **Medusa** automate this by running hundreds or thousands of attempts per minute.

## Why does it work?

SSH brute-force succeeds when:
- `PasswordAuthentication yes` is set in `sshd_config`
- No account lockout or rate-limiting is enforced
- Weak or default credentials are in use (e.g., `root:toor`, `admin:admin`)

## What happened in this lab

1. **Nmap** scanned the target and found port 22 open.
2. **Hydra** tried credentials from a wordlist until it matched `root:toor`.
3. The tool reported the valid password — full authentication would now be possible.

## Indicators in traffic (from Detection Lab)

- High volume of SYN packets to port 22 in a short window
- Many TCP connections that complete a handshake then immediately close (failed auth)
- Packet rate far above what a human would produce manually (e.g., 16+ attempts/second with Hydra default threads)

## Defenses (mitigations)

| Control | Effectiveness | Notes |
|---|---|---|
| `PasswordAuthentication no` (key-only auth) | Very high | Eliminates the attack surface entirely |
| `PermitRootLogin no` | High | Prevents direct root compromise even if another account is cracked |
| fail2ban / DenyHosts | High | Blocks source IPs after N failures |
| Port knocking or non-standard port | Medium | Obscurity layer, does not replace auth hardening |
| Strong, unique passwords | Medium | Slows brute-force but doesn't stop it |
| MFA (e.g., TOTP via PAM) | High | Requires a second factor even if password is guessed |

## Relevant commands (this lab)

```bash
# Scan for open ports
nmap -sV -p 22 target_ssh

# Brute-force SSH
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://target_ssh

# Apply hardening
python labctl.py harden

# Verify the fix held
python labctl.py attack-ssh -- --target target_ssh --username root --skip-scan
```

## Further reading

- [NIST SP 800-53 AC-7](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final) — Unsuccessful Logon Attempts
- [MITRE T1110.001](https://attack.mitre.org/techniques/T1110/001/)
- [OpenSSH sshd_config manpage](https://man.openbsd.org/sshd_config)
