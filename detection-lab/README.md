# Detection Lab (Signals, Not Guarantees)

This optional module helps learners observe **security signals** from traffic directed at lab targets.

It is intentionally scoped to:

- show **indicators** (scans, brute-force attempts, suspicious request bursts)
- produce an HTML report
- avoid claiming "this device is compromised" (that generally requires endpoint telemetry + investigation)

## How it works

A temporary sensor container runs `tcpdump` inside the **target container’s network namespace** (sidecar model), writes a `.pcap` into `reports/`, then runs a quick offline analysis.

## Quick usage

Capture traffic to the SSH target for 60 seconds and open the report:

```bash
python3 labctl.py detect --container target_ssh --seconds 60 --open
```

Typical workflow:

1. Start capture in one terminal:

   ```bash
   python3 labctl.py detect --container target_ssh --seconds 120 --open
   ```

2. While capture is running, in another terminal run the lab attack workflow:

   ```bash
   python3 labctl.py attack-ssh -- --target target_ssh --username root
   ```

3. Review the HTML report in `reports/`.

## Notes

- This is for the **local lab** (containers). For real networks, use the `audit` command to inventory exposure.
- For real compromise detection, you generally need logs/agents (EDR), IDS/IPS sensors, and an investigation process.
