"""Builds the system prompt + message list for each assistant mode."""

from pathlib import Path

import docker

CONTEXT_DIR = Path("/app/context")
DOCS_DIR = CONTEXT_DIR / "docs" / "concepts"

BASE_SYSTEM_PROMPT = (
    "You are the AI assistant embedded in the BootCon Cybersecurity Lab, a "
    "containerized environment for practicing offensive and defensive security "
    "workflows in an authorized, controlled setting. Be concise and practical. "
    "Only ever discuss techniques in the context of this lab or other environments "
    "the user is explicitly authorized to test."
)

# Maps lesson track -> the concept-card files most relevant to it.
TRACK_DOCS: dict[str, list[str]] = {
    "ssh": ["ssh-brute-force.md", "fail2ban.md", "why-password-auth-is-weak.md"],
    "rdp": ["rdp-brute-force.md", "fail2ban.md"],
    "web": ["web-attacks.md"],
    "remediate": ["ssh-brute-force.md", "fail2ban.md", "why-password-auth-is-weak.md"],
}

LABCTL_COMMAND_REFERENCE = """\
Reference: python labctl.py <command> [options]

- doctor                  Preflight checks (Colima/Docker health)
- setup                   Deploy all lab targets (writes an HTML report)
- verify                  Run health checks against deployed containers
- status                  Show live status of Colima, Docker, and lab containers
- attack-ssh -- --target target_ssh --username root   Run SSH brute-force workflow in Kali
- attack-rdp -- --target rdp_target --username admin  Run RDP brute-force workflow in Kali
- attack-web              Run the bWAPP XSS/SQLi workflow
- shell                   Open an interactive shell in kali_attacker
- lesson --track {ssh|rdp|web|remediate}          Guided instructor/student flow
- lesson --track {ssh|rdp|web|remediate} --run     Execute each lesson step automatically
- harden                  Apply remediation/hardening playbook (post-lesson)
- ctf --track {ssh|rdp|web} --setup                Plant a CTF flag + print objective
- ctf --track {ssh|rdp|web} --check CTF{...}        Submit a captured flag
- quiz --track {ssh|rdp|web|remediate}              Scored multiple-choice quiz
- gui --up --open         Open the live container-log GUI (Dozzle) at :9999
- ai --up --open          Open this AI assistant chat UI
- detect --container <name> --seconds <n> --open    Capture + analyze traffic signals
- scan --type {fs|images} --open                    Supply-chain scan with Trivy
- audit --targets <CIDR> --mode {discovery|services} --yes --open   Network audit
- report --open           Generate a standalone lab status report
- cleanup                 Tear down the lab

Every subcommand also accepts --dry-run to preview without executing.
"""


def _read_docs(filenames: list[str]) -> str:
    chunks = []
    for name in filenames:
        path = DOCS_DIR / name
        if path.exists():
            chunks.append(f"### {name}\n\n{path.read_text()}")
    return "\n\n".join(chunks)


def _tail_container_logs(container_name: str, lines: int = 200) -> str:
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound as exc:
        raise ValueError(f"Container not found: {container_name}") from exc
    raw = container.logs(tail=lines, timestamps=True)
    return raw.decode("utf-8", errors="replace")


def build_messages(
    mode: str,
    message: str,
    history: list[dict[str, str]],
    container: str | None,
    track: str | None,
) -> list[dict[str, str]]:
    system = BASE_SYSTEM_PROMPT

    if mode == "copilot":
        system += (
            "\n\nYou are acting as a CLI copilot for labctl.py. Use the command "
            "reference below to recommend the exact command (with flags) the user "
            f"should run.\n\n{LABCTL_COMMAND_REFERENCE}"
        )

    elif mode == "tutor":
        track_key = (track or "ssh").lower()
        docs = _read_docs(TRACK_DOCS.get(track_key, TRACK_DOCS["ssh"]))
        system += (
            f"\n\nYou are tutoring a student on the '{track_key}' lesson track. "
            "Ground your answers in the concept cards below; explain plainly and "
            f"reference MITRE ATT&CK IDs where relevant.\n\n{docs}"
        )

    elif mode == "log_analyst":
        if not container:
            raise ValueError("log_analyst mode requires a 'container' field")
        logs = _tail_container_logs(container)
        system += (
            f"\n\nYou are analyzing recent logs from the '{container}' container in "
            "this lab. Summarize what's happening, flag anything suspicious or "
            f"erroring, and suggest next steps.\n\n--- logs (tail) ---\n{logs}"
        )

    elif mode != "freeform":
        raise ValueError(f"Unknown mode: {mode!r}")

    messages = [{"role": "system", "content": system}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})
    return messages
