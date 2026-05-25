# RDP Brute-Force Attacks

**MITRE ATT&CK:** T1021.001 — Remote Services: Remote Desktop Protocol  
**Related technique:** T1110 — Brute Force

## What is RDP?

Remote Desktop Protocol (RDP) is a Microsoft protocol that provides a graphical remote desktop session over TCP port 3389. It is widely used for remote administration of Windows systems — and widely targeted by attackers.

## Why RDP is a high-value target

- Provides **full graphical desktop access** — an attacker who gets in can do anything a local user can
- Widely exposed on the internet (tens of millions of exposed hosts scanned via Shodan)
- Default Windows installs often enable it with weak credentials
- No built-in rate limiting or lockout on older configurations
- Historically linked to ransomware delivery (RDP was the #1 ransomware entry vector in many years)

## How the brute-force works

1. Attacker scans for port 3389 open hosts (Nmap, Shodan, etc.)
2. Tool (Hydra, Crowbar, RDPForce) connects and tests username/password pairs via the RDP auth exchange
3. On success, attacker has a live remote desktop session

## Indicators in traffic

- High volume of TCP SYN packets to port 3389 from a single source
- Many short-lived connections (failed auth = connection closed quickly)
- Unusual hours or geographic origin for auth attempts

## Defenses

| Control | Effectiveness | Notes |
|---|---|---|
| **Account lockout policy** | High | Locks account after N failures; forces attacker to slow down or change usernames |
| **Multi-Factor Authentication (MFA)** | Very high | A guessed password alone is not enough to log in |
| **Network-level Authentication (NLA)** | High | Requires auth before the desktop session is established |
| **VPN-only access (no direct RDP to internet)** | Very high | Removes the attack surface from public internet |
| **Non-standard port** | Low | Obscurity only — scanners find it within hours |
| **Allowlist by IP** | Very high | Only allow known-good IPs to reach port 3389 |
| **Windows Firewall rules** | Medium | Restrict RDP to specific subnets |

## Lab commands

```bash
# Start the RDP lesson
python labctl.py lesson --track rdp --run

# Run the RDP attack directly
python labctl.py attack-rdp -- --target rdp_target --username admin

# CTF mode
python labctl.py ctf --track rdp --setup
python labctl.py ctf --track rdp --check <FLAG>
```

## Real-world context

The 2017–2020 ransomware waves (Ryuk, REvil, Conti) heavily leveraged exposed RDP for initial access. Credentials were often purchased from dark-web marketplaces where actors sold previously brute-forced RDP access.

## Further reading

- [MITRE T1021.001](https://attack.mitre.org/techniques/T1021/001/)
- [CISA Advisory AA21-131A — DarkSide Ransomware](https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-131a)
- [CIS Benchmark for Windows](https://www.cisecurity.org/benchmark/microsoft_windows_desktop)
