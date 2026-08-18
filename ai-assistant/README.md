# AI Lab Assistant (GUI)

An optional chat assistant for the lab, backed by a local [Ollama](https://ollama.com) container today, and swappable to OpenAI later with a config change only.

## Included

- **Ollama**: runs the local LLM (`qwen2.5:0.5b` by default — sized for stability in a default 4GB Colima VM shared with the rest of the lab) — no API key, no external calls.
- **ai-backend**: a small Flask app that serves the chat UI and proxies chat requests to whichever provider is configured.

## Modes

- **Freeform** — general cybersecurity Q&A.
- **CLI Copilot** — recommends the right `labctl.py` command for what you're trying to do.
- **Log Analyst** — pick a running lab container; the assistant reads its recent logs (via the Docker socket) and explains what's happening.
- **Lesson Tutor** — pick a track (`ssh`, `rdp`, `web`, `remediate`); the assistant answers grounded in that track's concept cards under [`docs/concepts/`](../docs/concepts/).

## Start

From repo root:

```bash
python3 labctl.py ai --up --open
```

Then open:

- http://localhost:8700

## Stop

```bash
python3 labctl.py ai --down
```

## Switching to OpenAI (production)

1. Copy `.env.example` to `.env` in this directory (or export the same variables in your shell).
2. Set:
   ```bash
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   ```
3. Re-run `python3 labctl.py ai --up --open`.

No code changes are required — both providers speak the same OpenAI-compatible chat schema (see `backend/providers.py`).

## Notes

- First `--up` will take a few minutes while Ollama pulls the model.
- The default model (`qwen2.5:0.5b`) is intentionally tiny. In testing, the 4GB Colima VM shared by this lab got tight enough (`bwapp_web` alone has been observed using ~1.7GB) that even `llama3.2:1b` (~1.3GB) intermittently crashed Ollama's model runner mid-response (chat requests failing with `502 Bad Gateway`). Response quality at 0.5B is limited — expect plausible-sounding but sometimes inaccurate answers (e.g. the CLI Copilot occasionally invents flags). Give Colima more RAM and use a bigger model for better quality (see Troubleshooting below).
- The assistant only sees log data for containers it's explicitly pointed at (Log Analyst mode) — it does not proactively read logs.
- Like the rest of this lab, use only in environments you own or are authorized to test.

## Troubleshooting

**`FileNotFoundError` / `/var/run/docker.sock`**
Colima isn't running. Same fix as the rest of the lab:
```bash
colima start
docker context use colima
python labctl.py doctor
```

**`Bind for 0.0.0.0:11434 failed: port is already allocated`**
Something else on your machine (often another local Ollama install or project) already owns Ollama's standard port. This stack defaults its host-side port to **11435** (not 11434) specifically to avoid this, via `OLLAMA_PORT` in `docker-compose.yml`/`.env.example`. If you still hit a conflict (e.g. 11435 is also taken, or `AI_BACKEND_PORT` 8700 collides), find the owner and set a free port before retrying:
```bash
lsof -nP -iTCP:11435 -sTCP:LISTEN
OLLAMA_PORT=11436 python3 labctl.py ai --up --open   # or set it in ai-assistant/.env
```
This only remaps the host-side port — containers still talk to each other over the internal `ollama:11434` address, so nothing else needs to change.

**Ollama logs show `model requires more system memory (X GiB) than is available`**
The model doesn't fit in Colima's VM alongside the lab's other containers even to load. Same fix as below — drop to a smaller model or give Colima more RAM.

**Chat requests fail with `502 Bad Gateway`, and Ollama logs show `post predict ... EOF` or the model was loaded fine earlier**
The model loaded, but got starved (or killed) mid-response by memory pressure from other containers — `bwapp_web` in particular has been observed spiking to ~1.7GB on its own. Check current usage with `docker stats --no-stream`. Fix, in order of least to most disruptive:
1. Drop to a smaller model (the shipped default, `qwen2.5:0.5b` at ~400MB, is already the smallest commonly-used option — if you've customized `OLLAMA_MODEL` to something bigger, put it back).
2. Give Colima more RAM (this restarts *all* containers on the VM, including any unrelated local projects sharing it — check `docker ps` first if that matters to you):
   ```bash
   colima stop
   colima start --memory 8
   ```
   then a bigger model becomes viable, e.g. `OLLAMA_MODEL=llama3.2:1b` (~1.3GB, still tight on 4GB), `llama3.2:3b` (~2.5GB), or `llama3.1:8b` (~6GB).

Set `OLLAMA_MODEL` in `ai-assistant/.env` (copy from `.env.example`) so it persists across `ai --up` runs, rather than passing it inline each time.
