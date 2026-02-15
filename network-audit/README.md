# Defensive Network Audit (Learner Tool)

This module adds a safe-by-default way to inventory devices and exposed services on a network you are **authorized** to assess.

## What it does (and does not do)

- ✅ Host discovery (who is on the network)
- ✅ Limited service enumeration on common ports (version detection)
- ❌ No exploitation, no password attacks, no destructive actions

## Usage

From repo root:

```bash
python3 labctl.py audit --targets 192.168.1.0/24 --mode discovery --yes --open
```

Common services scan (limited ports + `-sV`):

```bash
python3 labctl.py audit --targets 192.168.1.0/24 --mode services --yes --open
```

Reports are written to `reports/` and an index is maintained at `reports/index.html`.

## Notes

- Only scan networks you own or have explicit permission to assess.
- If you don’t have `nmap` installed locally, use Docker mode:

  ```bash
  python3 labctl.py audit --targets 192.168.1.0/24 --mode discovery --tool docker --yes --open
  ```
