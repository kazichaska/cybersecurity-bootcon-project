# Changelog

All notable changes to the BootCon Cybersecurity Lab are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **AI Lab Assistant** (`ai --up --open`): optional chat UI backed by a local Ollama container (`qwen2.5:0.5b` by default, host port 11435) or OpenAI (via `AI_PROVIDER=openai` config, no code change). Four modes: freeform Q&A, CLI copilot for `labctl.py` commands, log analyst for running containers, and lesson tutor grounded in `docs/concepts/`. Default model/port chosen to avoid colliding with an existing local Ollama and to stay stable in a default 4GB Colima VM shared with the rest of the lab (larger models observed intermittently crashing the model runner under memory pressure from `bwapp_web`) — see `ai-assistant/README.md` (Troubleshooting section) for sizing up if you give Colima more RAM.
- **Web attack lesson track** (`lesson --track web`): guided XSS and SQL injection lesson via bWAPP, including Nmap recon, bWAPP login, reflected XSS exploit, and debrief. MITRE ATT&CK T1059.007.
- **CTF mode** (`ctf --track <ssh|rdp|web>`): plants a flag in a target container and guides learners through an exploit-to-capture exercise. `--setup` plants the flag; `--check <FLAG>` validates it.
- **Knowledge quizzes** (`quiz --track <track>`): 5 multiple-choice questions per lesson track (ssh, rdp, web, remediate) with scored HTML report output.
- **MITRE ATT&CK tags** on all lesson steps (displayed during `lesson` mode and used for curriculum alignment).
- **Difficulty and estimated time** labels on all lesson tracks (shown in lesson mode header and README).
- **Concept cards** in `docs/concepts/` for self-study and handouts:
  - `ssh-brute-force.md`
  - `fail2ban.md`
  - `why-password-auth-is-weak.md`
  - `rdp-brute-force.md`
  - `web-attacks.md`
- **Instructor guide** (`docs/instructor-guide.md`): session timing guide, class management, CTF setup, common issues.
- **Dev Container config** (`.devcontainer/devcontainer.json`): enables one-click GitHub Codespaces / VS Code Dev Container setup with Python 3.11, Docker-in-Docker, Ansible, and recommended extensions.
- **Architecture diagram** (Mermaid) in README showing container topology and network relationships.
- **README badges**: CI status, Python version, license, Open in Dev Container.
- **CTF flag seeded in setup playbook** (`setup-target.yml`): `target_ssh` now receives a flag file at `/root/flag.txt` during `labctl.py setup`.
- **Enhanced detection narrative** in `detect` HTML reports: plain-English "Attack Narrative (What Just Happened?)" section with per-signal analysis (SYN scan rate, brute-force packet volume, RDP activity).
- **Makefile targets**: `lesson-web`, `ctf-ssh`, `ctf-rdp`, `ctf-web`, `quiz-ssh`, `quiz-rdp`, `quiz-web`, `quiz-remediate`.

### Changed
- `lesson --track ssh/rdp/remediate` now shows difficulty, estimated time, and concept doc links in the header.
- `lesson` steps with MITRE ATT&CK mappings now display the technique ID inline.
- Detection lab report title updated to "Attack Narrative (What Just Happened?)" to improve learner comprehension.

---

## [2026.02] — 2026-02-15

### Added
- Supply-chain scanning with Trivy (`scan --type fs`, `scan --type images`).
- Detection lab module (`detect --container <name> --seconds <n> --open`) with sidecar tcpdump + tshark analysis.
- Defensive network audit (`audit --targets <CIDR> --mode discovery|services --yes --open`).
- Live container log GUI via Dozzle (`gui --up --open`).
- Lab hardening playbook and `harden` command with HTML report.
- HTML report generation for all major commands (setup, cleanup, harden, scan, detect, audit).
- Reports index at `reports/index.html`.

### Changed
- Python automation modernized with safer `subprocess` handling (no `shell=True`) and explicit CLI arguments.
- Lab verification workflow replaced with explicit per-container health checks.
- CI workflow adds ruff lint, Python compile check, Ansible syntax check, and lesson dry-run sanity check.

---

## [2026.01] — 2026-01-10

### Added
- Initial BootCon lab: SSH and RDP brute-force practice with Hydra + Nmap.
- bWAPP vulnerable web target deployment.
- Ansible-based lab setup, cleanup, and hardening playbooks.
- `labctl.py` control script with `setup`, `verify`, `cleanup`, `doctor`, `attack-ssh`, `attack-rdp`, `shell`, `lesson` commands.
- Guided lesson mode with `--run` and `--non-interactive` flags.
