# Why Password Authentication Is Weak

## The fundamental problem

A password is a **shared secret** — the server and the user both know it. This means:

1. The server stores it (even as a hash — hashes can be cracked).
2. It can be guessed systematically (brute-force, dictionary attacks).
3. It can be phished (users can be tricked into entering it on a fake site).
4. It travels over the network as part of the auth exchange (even if encrypted, the protocol exposes the guess attempt to timing attacks).

## Why SSH password auth is especially risky

SSH exposes authentication to the **network**. Unlike a web form that can enforce CAPTCHA, rate-limiting, and lockout in the application layer, raw SSH gives any attacker who can reach port 22 the ability to attempt logins at machine speed.

Hydra with default settings runs ~16 concurrent threads, testing hundreds of passwords per minute. Against a service with no lockout, this is just an endurance game.

## Password auth vs. key-based auth

| Property | Password auth | Key-based (public key) auth |
|---|---|---|
| Attack surface | Any IP that can reach port 22 | Attacker needs the **private key file** |
| Brute-force possible? | Yes — try any password | No — key space is 256+ bits (computationally infeasible) |
| Phishable? | Yes | No (private key never leaves your machine) |
| Stored on server? | As a hash (crackable offline if /etc/shadow leaks) | Only the public key (useless to attacker) |
| Complexity burden on user | Must remember or reuse passwords | One key pair, managed by ssh-agent |

## How key-based auth works

```
Client generates keypair:  private key (stays local)  +  public key (deployed to server)
                                    ↓
On connect: server sends a challenge encrypted with the public key
            only the holder of the private key can decrypt and sign it
            → authentication succeeds without the private key ever being transmitted
```

## Setting it up (reference)

```bash
# Generate a key pair (ed25519 is modern and fast)
ssh-keygen -t ed25519 -C "your-label"

# Copy public key to target
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@target

# Disable password auth on server (/etc/ssh/sshd_config):
PasswordAuthentication no
PermitRootLogin no   # also remove direct root access

# Restart SSH
sudo service ssh restart
```

## The lesson

The lab demonstrates brute-force succeeding because `PasswordAuthentication yes` is set. After `python labctl.py harden`, the playbook flips both settings and restarts SSH. Re-running the attack confirms Hydra can no longer authenticate — the attack surface is gone.

## Further reading

- [OpenSSH public key authentication](https://www.ssh.com/academy/ssh/public-key-authentication)
- [NIST SP 800-63B — Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [MITRE T1110 — Brute Force](https://attack.mitre.org/techniques/T1110/)
