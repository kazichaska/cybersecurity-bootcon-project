# Defense Stack (GUI)

This optional stack gives learners a simple web UI to observe what’s happening in the lab.

## Included

- Dozzle: real-time Docker log viewer (web UI)

## Start

From repo root:

```bash
python3 labctl.py gui --up --open
```

Then open:

- http://localhost:9999

## Stop

```bash
python3 labctl.py gui --down
```

## Notes

- This stack is for visibility/learning (logs + container activity), not for “guaranteed compromise detection”.
- Default socket: `/var/run/docker.sock`.
- Override if needed: set `DOCKER_SOCKET_PATH` (the compose file maps it into `/var/run/docker.sock`).
