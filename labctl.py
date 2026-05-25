#!/usr/bin/env python3

import argparse
import datetime as dt
import html
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB_DIR = ROOT / "ssh-brute-lab"
LAB_SETUP_PLAYBOOK = LAB_DIR / "ansible" / "lab" / "lab-setup.yml"
LAB_CLEANUP_PLAYBOOK = LAB_DIR / "ansible" / "lab" / "lab-cleanup.yml"
LAB_HARDEN_PLAYBOOK = LAB_DIR / "ansible" / "lab" / "lab-harden.yml"
VERIFY_SCRIPT = ROOT / "verify-lab.py"
REPORTS_DIR = ROOT / "reports"
DEFENSE_STACK_COMPOSE = ROOT / "defense-stack" / "docker-compose.yml"
BWAPP_ATTACK_SCRIPT = ROOT / "ssh-brute-lab" / "ansible" / "scripts" / "bwapp-attack.py"


class LabCtlError(RuntimeError):
    pass


def require_authorization(confirmed: bool) -> None:
    if confirmed:
        return
    raise LabCtlError(
        "Authorization required. Re-run with --yes to confirm you own or are explicitly authorized to scan the target network."
    )


LESSON_TRACKS: dict[str, list[dict[str, object]]] = {
    "ssh": [
        {
            "title": "Environment preflight",
            "prompt": "Confirm Colima and Docker context are healthy before deployment.",
            "expected": "Colima shows running and Docker lists available containers/table output.",
            "action": "doctor",
        },
        {
            "title": "Deploy lab targets",
            "prompt": "Provision Kali + SSH/RDP/bWAPP targets using Ansible.",
            "expected": "Play recap ends with failed=0 for localhost.",
            "action": "setup",
        },
        {
            "title": "Verify lab state",
            "prompt": "Check required containers are in running state.",
            "expected": "verify-lab output shows running status for kali_attacker, target_ssh, rdp_target, bwapp_web.",
            "action": "verify",
        },
        {
            "title": "Run guided SSH attack",
            "prompt": "Launch Nmap + Hydra workflow from Kali against the SSH target.",
            "expected": "Nmap finds port 22 open; Hydra eventually reports a valid password (demo default: toor).",
            "action": "attack-ssh",
            "args": ["--", "--target", "target_ssh", "--username", "root"],
            "mitre": "T1110.001 (Brute Force: Password Guessing)",
        },
        {
            "title": "Debrief",
            "prompt": "Discuss why brute-force worked and propose hardening controls.",
            "expected": "Recommended controls: key auth, fail2ban, rate limiting, strong passwords, monitoring.",
            "mitre": "T1110.001 mitigations → M1036 (Account Use Policies), M1032 (Multi-factor Auth)",
        },
    ],
    "rdp": [
        {
            "title": "Environment preflight",
            "prompt": "Validate local runtime prerequisites.",
            "expected": "Doctor checks complete without errors.",
            "action": "doctor",
        },
        {
            "title": "Deploy lab targets",
            "prompt": "Run full lab setup to provision RDP target.",
            "expected": "Ansible recap shows successful completion.",
            "action": "setup",
        },
        {
            "title": "Run guided RDP attack",
            "prompt": "Execute RDP workflow from Kali against rdp_target.",
            "expected": "Service probe returns 3389; Hydra tests credentials and may find demo password.",
            "action": "attack-rdp",
            "args": ["--", "--target", "rdp_target", "--username", "admin"],
            "mitre": "T1021.001 (Remote Services: Remote Desktop Protocol) + T1110 (Brute Force)",
        },
        {
            "title": "Debrief",
            "prompt": "Compare SSH vs RDP brute-force behavior and mitigations.",
            "expected": "Account lockout and MFA are emphasized for RDP defense.",
            "mitre": "T1021.001 mitigations → M1035 (Limit Access to Resource), M1032 (MFA)",
        },
    ],
    "web": [
        {
            "title": "Deploy lab targets",
            "prompt": "Provision Kali + bWAPP web target using Ansible.",
            "expected": "Play recap ends with failed=0 for localhost.",
            "action": "setup",
        },
        {
            "title": "Verify lab state",
            "prompt": "Confirm bwapp_web and kali_attacker are running.",
            "expected": "verify-lab shows running status for bwapp_web and kali_attacker.",
            "action": "verify",
        },
        {
            "title": "Reconnaissance: find the web target",
            "prompt": "From the Kali container, identify the bWAPP web service on port 80.",
            "expected": "HTTP service on port 80 of bwapp_web responds with the bWAPP login page.",
            "mitre": "T1046 (Network Service Discovery)",
        },
        {
            "title": "Login to bWAPP and set security level",
            "prompt": "Access bWAPP at http://bwapp_web:80/bWAPP/login.php with credentials bee/bug. Set security level to Low.",
            "expected": "Successful login; portal page loads.",
        },
        {
            "title": "Exploit Reflected XSS",
            "prompt": "Run the bWAPP attack script to inject a reflected XSS payload into the vulnerable GET parameter.",
            "expected": "Script reports XSS payload appears in response — the unencoded script tag is reflected back.",
            "action": "attack-web",
            "args": [],
            "mitre": "T1059.007 (Command and Scripting Interpreter: JavaScript)",
        },
        {
            "title": "Debrief",
            "prompt": "Discuss how XSS can steal session cookies, redirect users, and escalate to stored attacks.",
            "expected": "Key controls: output encoding, Content Security Policy (CSP), input validation, HttpOnly cookies.",
            "mitre": "T1059.007 mitigations → M1021 (Restrict Web-Based Content), output encoding",
        },
    ],
    "remediate": [
        {
            "title": "Deploy lab targets",
            "prompt": "Provision lab targets.",
            "expected": "Ansible recap ends with failed=0.",
            "action": "setup",
        },
        {
            "title": "Verify lab state",
            "prompt": "Confirm required containers are running.",
            "expected": "verify-lab shows running containers.",
            "action": "verify",
        },
        {
            "title": "(Before) Run SSH brute-force",
            "prompt": "Demonstrate the vulnerable configuration.",
            "expected": "Hydra may find the demo password (toor).",
            "action": "attack-ssh",
            "args": ["--", "--target", "target_ssh", "--username", "root"],
            "mitre": "T1110.001 (Brute Force: Password Guessing)",
        },
        {
            "title": "Apply hardening",
            "prompt": "Run hardening playbook to disable weak auth paths.",
            "expected": "Hardening completes without fatal errors.",
            "action": "harden",
        },
        {
            "title": "(After) Re-test SSH",
            "prompt": "Verify brute-force no longer works after hardening.",
            "expected": "Hydra should fail or report no valid password due to password auth disabled.",
            "action": "attack-ssh",
            "args": ["--", "--target", "target_ssh", "--username", "root", "--skip-scan"],
            "mitre": "T1110.001 validation — confirming mitigations hold",
        },
    ],
}

# Per-track metadata for display in lesson mode and documentation.
TRACK_META: dict[str, dict[str, str]] = {
    "ssh": {
        "difficulty": "Beginner",
        "time": "25 min",
        "description": "SSH credential brute-force attack, detection, and defense",
        "concepts": "docs/concepts/ssh-brute-force.md, docs/concepts/fail2ban.md",
    },
    "rdp": {
        "difficulty": "Beginner",
        "time": "20 min",
        "description": "RDP credential brute-force and account lockout defense",
        "concepts": "docs/concepts/rdp-brute-force.md",
    },
    "web": {
        "difficulty": "Beginner",
        "time": "30 min",
        "description": "Web application attacks: XSS and SQL injection via bWAPP",
        "concepts": "docs/concepts/web-attacks.md",
    },
    "remediate": {
        "difficulty": "Intermediate",
        "time": "35 min",
        "description": "Exploit-then-harden-then-retest security lifecycle",
        "concepts": "docs/concepts/ssh-brute-force.md, docs/concepts/fail2ban.md",
    },
}

# CTF flags planted in target containers during `ctf --setup`.
CTF_FLAGS: dict[str, str] = {
    "ssh": "CTF{brute_force_is_easy_when_passwords_are_weak}",
    "rdp": "CTF{rdp_exposed_is_rdp_owned}",
    "web": "CTF{xss_reflected_lab_complete}",
}

QUIZ_BANK: dict[str, list[dict[str, object]]] = {
    "ssh": [
        {
            "q": "What TCP port does SSH use by default?",
            "options": ["A) 21  (FTP)", "B) 22  (SSH)", "C) 23  (Telnet)", "D) 3389 (RDP)"],
            "answer": "B",
            "explanation": "SSH (Secure Shell) listens on TCP port 22 by default (RFC 4251).",
        },
        {
            "q": "Which tool did the lab use to scan for open ports?",
            "options": ["A) Hydra", "B) Wireshark", "C) Nmap", "D) Metasploit"],
            "answer": "C",
            "explanation": "Nmap (Network Mapper) is the industry-standard port scanner used in reconnaissance.",
        },
        {
            "q": "What attack technique did Hydra perform against the SSH service?",
            "options": [
                "A) SQL injection",
                "B) Phishing",
                "C) Buffer overflow",
                "D) Credential brute-force",
            ],
            "answer": "D",
            "explanation": "Hydra performs credential brute-force: systematically testing password combinations until one works.",
        },
        {
            "q": "What MITRE ATT&CK technique ID covers SSH credential brute-force?",
            "options": ["A) T1566", "B) T1059", "C) T1110.001", "D) T1190"],
            "answer": "C",
            "explanation": "T1110.001 (Brute Force: Password Guessing) covers automated credential guessing attacks.",
        },
        {
            "q": "Which control BEST prevents SSH password brute-force attacks?",
            "options": [
                "A) Enabling verbose logging",
                "B) Key-based authentication + disabling PasswordAuthentication",
                "C) Increasing the session timeout",
                "D) Changing the SSH banner",
            ],
            "answer": "B",
            "explanation": (
                "Disabling password authentication forces clients to use cryptographic keys, "
                "eliminating the attack surface for brute-force."
            ),
        },
    ],
    "rdp": [
        {
            "q": "What TCP port does RDP use by default?",
            "options": ["A) 22", "B) 443", "C) 3389", "D) 5900"],
            "answer": "C",
            "explanation": "RDP (Remote Desktop Protocol) listens on TCP 3389 by default.",
        },
        {
            "q": "Which MITRE ATT&CK technique covers adversary use of RDP for remote access?",
            "options": ["A) T1021.001", "B) T1059", "C) T1566.001", "D) T1190"],
            "answer": "A",
            "explanation": "T1021.001 (Remote Services: Remote Desktop Protocol) covers adversary use of RDP for lateral movement.",
        },
        {
            "q": "Which pair of controls MOST reduces RDP brute-force risk?",
            "options": [
                "A) Disabling antivirus + opening more ports",
                "B) Account lockout policy + MFA",
                "C) Enabling HTTP access",
                "D) Removing all user accounts",
            ],
            "answer": "B",
            "explanation": "Account lockout slows automated guessing; MFA adds a second factor that brute-force alone cannot bypass.",
        },
        {
            "q": "Why is exposing RDP directly to the internet dangerous?",
            "options": [
                "A) It causes high bandwidth usage",
                "B) It enables unauthorized remote access and is widely targeted by ransomware actors",
                "C) It encrypts all traffic by default",
                "D) It improves performance",
            ],
            "answer": "B",
            "explanation": "Exposed RDP has been exploited in widespread ransomware campaigns and unauthorized lateral movement.",
        },
        {
            "q": "What does the Hydra flag -t control?",
            "options": [
                "A) Target hostname",
                "B) Timeout duration in minutes",
                "C) Number of parallel threads",
                "D) Type of protocol",
            ],
            "answer": "C",
            "explanation": "The -t flag sets the number of concurrent threads. Higher values speed up attacks but increase noise.",
        },
    ],
    "web": [
        {
            "q": "What does XSS stand for?",
            "options": [
                "A) External Style Sheet",
                "B) Cross-Site Scripting",
                "C) Cross-Server Session",
                "D) Extended Script Syntax",
            ],
            "answer": "B",
            "explanation": "Cross-Site Scripting (XSS) injects malicious client-side scripts into pages viewed by other users.",
        },
        {
            "q": "Which MITRE ATT&CK technique covers JavaScript-based exploitation (XSS)?",
            "options": ["A) T1059.007", "B) T1110.001", "C) T1566", "D) T1190"],
            "answer": "A",
            "explanation": "T1059.007 (Command and Scripting Interpreter: JavaScript) covers JS-based exploitation including XSS.",
        },
        {
            "q": "What is the primary risk of a SQL injection vulnerability?",
            "options": [
                "A) Slow page loads",
                "B) Unauthorized database access and data extraction",
                "C) CSS layout corruption",
                "D) Browser crashes",
            ],
            "answer": "B",
            "explanation": "SQL injection lets attackers read, modify, or delete data, and sometimes execute OS commands.",
        },
        {
            "q": "Which OWASP Top 10 category (2021) includes SQL injection?",
            "options": [
                "A) Broken Access Control",
                "B) Security Misconfiguration",
                "C) Injection (A03:2021)",
                "D) Insecure Design",
            ],
            "answer": "C",
            "explanation": "Injection (A03:2021) covers SQL, OS, LDAP, and other injection flaws caused by untrusted data sent to an interpreter.",
        },
        {
            "q": "What is bWAPP?",
            "options": [
                "A) A network scanner",
                "B) A firewall management tool",
                "C) A deliberately vulnerable web application for security training",
                "D) A container runtime",
            ],
            "answer": "C",
            "explanation": "bWAPP (Buggy Web Application) is intentionally insecure and contains hundreds of web vulnerabilities for safe practice.",
        },
    ],
    "remediate": [
        {
            "q": "What does 'hardening' a system mean in a security context?",
            "options": [
                "A) Making hardware physically stronger",
                "B) Reducing attack surface by removing weak configurations",
                "C) Adding more application features",
                "D) Encrypting all files on disk",
            ],
            "answer": "B",
            "explanation": "Hardening removes unnecessary services, patches vulnerabilities, and enforces least-privilege configurations.",
        },
        {
            "q": "After hardening SSH, which command best validates the fix?",
            "options": [
                "A) labctl.py doctor",
                "B) labctl.py attack-ssh (re-run the exploit)",
                "C) labctl.py scan --type fs",
                "D) labctl.py verify",
            ],
            "answer": "B",
            "explanation": "Re-running the attack is the gold-standard validation: if Hydra cannot find credentials, the control worked.",
        },
        {
            "q": "Which two changes does the lab hardening playbook apply to the SSH target?",
            "options": [
                "A) Enable root login + enable password auth",
                "B) Disable root login + disable password auth",
                "C) Open port 22 + enable Telnet",
                "D) Increase timeout + enable verbose logging",
            ],
            "answer": "B",
            "explanation": "The playbook sets PermitRootLogin no and PasswordAuthentication no in sshd_config, then restarts SSH.",
        },
        {
            "q": "What does fail2ban do?",
            "options": [
                "A) Encrypts SSH traffic",
                "B) Automatically blocks source IPs after repeated authentication failures",
                "C) Scans for vulnerabilities",
                "D) Manages Docker containers",
            ],
            "answer": "B",
            "explanation": "fail2ban monitors log files for repeated failures and uses firewall rules to block offending IPs.",
        },
        {
            "q": "What result should Hydra produce after SSH password auth is disabled?",
            "options": [
                "A) Find credentials faster",
                "B) Connect but report wrong password",
                "C) Fail to authenticate — no valid credentials found",
                "D) Perform no connection attempts at all",
            ],
            "answer": "C",
            "explanation": "With PasswordAuthentication disabled, Hydra's password guessing has no attack surface and attempts are rejected.",
        },
    ],
}


def run(command: list[str], *, cwd: Path | None = None, dry_run: bool = False) -> int:
    printable = " ".join(command)
    print(f"$ {printable}")
    if dry_run:
        return 0

    result = subprocess.run(command, cwd=str(cwd) if cwd else None, check=False)
    return result.returncode


def run_tee(
    command: list[str],
    *,
    cwd: Path | None = None,
    output_path: Path | None = None,
    dry_run: bool = False,
) -> int:
    printable = " ".join(command)
    print(f"$ {printable}")
    if dry_run:
        if output_path:
            print(f"(dry-run) would write log: {output_path}")
        return 0

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = output_path.open("w", encoding="utf-8", errors="replace")
    else:
        log_file = None

    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            if log_file:
                log_file.write(line)
        return int(process.wait())
    finally:
        if log_file:
            log_file.close()


def require_binary(binary: str) -> None:
    if shutil.which(binary) is None:
        raise LabCtlError(f"Required command not found in PATH: {binary}")


def run_ansible_playbook(playbook: Path, dry_run: bool) -> int:
    require_binary("ansible-playbook")
    return run(["ansible-playbook", str(playbook)], cwd=ROOT, dry_run=dry_run)


def run_verify(dry_run: bool) -> int:
    return run([sys.executable, str(VERIFY_SCRIPT)], cwd=ROOT, dry_run=dry_run)


def run_host_python_script(script_path: Path, dry_run: bool) -> int:
    return run([sys.executable, str(script_path)], cwd=ROOT, dry_run=dry_run)


def capture_text(command: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    return output.strip()


def generate_html_report(
    *,
    title: str,
    command_line: str,
    exit_code: int,
    log_path: Path | None,
    extra_sections: list[tuple[str, str]],
    report_id: str | None = None,
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = report_id or dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S%z")
    safe_title = "".join(c for c in title.lower().replace(" ", "-") if c.isalnum() or c in "-_")
    report_path = REPORTS_DIR / f"{timestamp}-{safe_title}.html"

    def section(heading: str, body: str) -> str:
        return (
            f"<section>\n<h2>{html.escape(heading)}</h2>\n"
            f"<pre>{html.escape(body)}</pre>\n</section>\n"
        )

    status = "PASS" if exit_code == 0 else "FAIL"
    log_hint = str(log_path) if log_path else "(no log captured)"

    parts = [
        "<!doctype html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='utf-8' />",
        "  <meta name='viewport' content='width=device-width, initial-scale=1' />",
        f"  <title>{html.escape(title)} - {status}</title>",
        "  <style>",
        "    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;}",
        "    header{display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap;}",
        "    .pill{padding:2px 10px;border-radius:999px;font-weight:700;}",
        "    .pass{background:#e6ffed;color:#055d20;border:1px solid #a9f0bc;}",
        "    .fail{background:#ffeef0;color:#86181d;border:1px solid #fdaeb7;}",
        "    pre{background:#0b1020;color:#e6e6e6;padding:12px 14px;border-radius:10px;overflow:auto;}",
        "    h2{margin-top:22px;}",
        "    .meta{color:#555;font-size:14px;}",
        "  </style>",
        "</head>",
        "<body>",
        "<header>",
        f"  <h1>{html.escape(title)}</h1>",
        f"  <div class='pill {'pass' if exit_code == 0 else 'fail'}'>{status}</div>",
        "</header>",
        f"<div class='meta'>Command: <code>{html.escape(command_line)}</code><br/>Log: <code>{html.escape(log_hint)}</code></div>",
        section("Result", f"Exit code: {exit_code}"),
    ]

    for heading, body in extra_sections:
        parts.append(section(heading, body))

    if log_path and log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            log_text = "(unable to read log file)"
        parts.append(section("Run Log", log_text))

    parts.extend(["</body>", "</html>"])
    report_path.write_text("\n".join(parts), encoding="utf-8")

    latest = REPORTS_DIR / "latest.html"
    try:
        latest.write_text(report_path.name, encoding="utf-8")
    except OSError:
        pass

    write_reports_index()
    return report_path


def write_reports_index() -> None:
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_files = sorted(
            [p for p in REPORTS_DIR.glob("*.html") if p.name not in {"index.html", "latest.html"}],
            key=lambda p: p.name,
            reverse=True,
        )
        items = "\n".join(
            f"<li><a href='{html.escape(p.name)}'>{html.escape(p.name)}</a></li>" for p in report_files
        )
        index_html = "\n".join(
            [
                "<!doctype html>",
                "<html lang='en'>",
                "<head><meta charset='utf-8'/><meta name='viewport' content='width=device-width, initial-scale=1'/>",
                "<title>BootCon Reports</title>",
                "<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;} li{margin:6px 0}</style>",
                "</head>",
                "<body>",
                "<h1>BootCon Lab Reports</h1>",
                "<p>Latest report pointer: <code>latest.html</code> (contains the latest report filename).</p>",
                "<ol>",
                items or "<li>(no reports yet)</li>",
                "</ol>",
                "</body></html>",
            ]
        )
        (REPORTS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    except OSError:
        return


def build_env_sections(*, dry_run: bool) -> list[tuple[str, str]]:
    if dry_run:
        return [("Dry run", "No subprocesses executed. Remove --dry-run to capture live status.")]

    sections: list[tuple[str, str]] = []

    if shutil.which("colima"):
        sections.append(("Colima status", capture_text(["colima", "status"], cwd=ROOT)))
    if shutil.which("docker"):
        sections.append(("Docker context", capture_text(["docker", "context", "show"], cwd=ROOT)))
        sections.append(
            (
                "Docker ps",
                capture_text(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"], cwd=ROOT),
            )
        )
    return sections


def colima_socket_path() -> str:
    return str(Path.home() / ".colima" / "default" / "docker.sock")


def docker_compose_base() -> list[str]:
    require_binary("docker")
    # "docker compose" is the modern default; fall back to docker-compose if needed.
    try:
        code = subprocess.run(["docker", "compose", "version"], capture_output=True).returncode
        if code == 0:
            return ["docker", "compose"]
    except Exception:
        pass
    require_binary("docker-compose")
    return ["docker-compose"]


def gui_stack(up: bool, down: bool, open_browser: bool, dry_run: bool) -> int:
    env = os.environ.copy()
    env.setdefault("DOCKER_SOCKET_PATH", "/var/run/docker.sock")
    env.setdefault("DOZZLE_PORT", "9999")

    compose = docker_compose_base()
    compose_file = str(DEFENSE_STACK_COMPOSE)

    if down:
        printable = " ".join([*compose, "-f", compose_file, "down"])
        print(f"$ {printable}")
        if dry_run:
            return 0
        return subprocess.run([*compose, "-f", compose_file, "down"], cwd=str(ROOT), env=env).returncode

    if up:
        printable = " ".join([*compose, "-f", compose_file, "up", "-d"])
        print(f"$ {printable}")
        if dry_run:
            return 0
        code = subprocess.run(
            [*compose, "-f", compose_file, "up", "-d"],
            cwd=str(ROOT),
            env=env,
        ).returncode
        if code != 0:
            return code

    if open_browser and not dry_run:
        port = env.get("DOZZLE_PORT", "9999")
        webbrowser.open(f"http://localhost:{port}")
    return 0


def harden_with_report(dry_run: bool, open_browser: bool) -> int:
    report_id = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S%z")
    log_path = REPORTS_DIR / f"{report_id}-lab-harden.log"
    exit_code = run_tee(
        ["ansible-playbook", str(LAB_HARDEN_PLAYBOOK)],
        cwd=ROOT,
        output_path=log_path,
        dry_run=dry_run,
    )
    sections = build_env_sections() if not dry_run else [("Dry run", "No commands executed")]
    report_path = generate_html_report(
        title="Lab Hardening Report",
        command_line=f"ansible-playbook {LAB_HARDEN_PLAYBOOK}",
        exit_code=exit_code,
        log_path=None if dry_run else log_path,
        extra_sections=sections,
        report_id=report_id,
    )
    if open_browser and not dry_run:
        open_report(report_path)
    return exit_code


def trivy_scan(
    *,
    scan_type: str,
    open_browser: bool,
    dry_run: bool,
) -> int:
    require_binary("docker")
    report_id = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S%z")
    log_path = REPORTS_DIR / f"{report_id}-trivy-{scan_type}.log"

    socket = colima_socket_path()

    if scan_type == "fs":
        command = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{ROOT}:/work",
            "-w",
            "/work",
            "aquasec/trivy:latest",
            "fs",
            "--scanners",
            "vuln,secret,config",
            "--timeout",
            "5m",
            ".",
        ]
        title = "Supply Chain Scan Report (Trivy FS)"
    elif scan_type == "images":
        images = [
            "kalilinux/kali-rolling",
            "ubuntu",
            "ubuntu:20.04",
            "mysql:5.7",
            "raesene/bwapp",
        ]
        # Use the Docker daemon via the Colima socket.
        command = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{socket}:/var/run/docker.sock",
            "aquasec/trivy:latest",
            "image",
            "--timeout",
            "10m",
            *images,
        ]
        title = "Supply Chain Scan Report (Trivy Images)"
    else:
        raise LabCtlError("scan type must be fs or images")

    exit_code = run_tee(command, cwd=ROOT, output_path=log_path, dry_run=dry_run)
    sections: list[tuple[str, str]] = [("Scan type", scan_type)]
    report_path = generate_html_report(
        title=title,
        command_line=" ".join(command),
        exit_code=exit_code,
        log_path=None if dry_run else log_path,
        extra_sections=sections,
        report_id=report_id,
    )
    if open_browser and not dry_run:
        open_report(report_path)
    return exit_code


def detect_capture_and_analyze(
    *,
    container_name: str,
    seconds: int,
    open_browser: bool,
    dry_run: bool,
) -> int:
    require_binary("docker")

    report_id = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S%z")
    out_dir = REPORTS_DIR / f"{report_id}-detect-{container_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    capture_name = f"bootcon-sensor-{container_name}"
    pcap_name = "capture.pcap"
    pcap_path = out_dir / pcap_name

    capture_cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        capture_name,
        "--network",
        f"container:{container_name}",
        "--cap-add",
        "NET_ADMIN",
        "--cap-add",
        "NET_RAW",
        "-v",
        f"{out_dir}:/out",
        "nicolaka/netshoot:latest",
        "tcpdump",
        "-i",
        "any",
        "-U",
        "-w",
        f"/out/{pcap_name}",
    ]

    print("[*] Detection lab: capturing traffic signals (not a compromise verdict)")
    print(f"[*] Target container: {container_name}")
    print(f"[*] Duration: {seconds}s")

    if dry_run:
        print(f"$ {' '.join(capture_cmd)}")
        print(f"(dry-run) would write pcap: {pcap_path}")
        return 0

    # Ensure any previous sensor for the same target is stopped.
    subprocess.run(["docker", "rm", "-f", capture_name], capture_output=True)

    start = subprocess.run(capture_cmd, cwd=str(ROOT), check=False, capture_output=True, text=True)
    if start.returncode != 0:
        raise LabCtlError(f"Failed to start sensor: {start.stderr.strip() or start.stdout.strip()}")

    try:
        subprocess.run(["sleep", str(max(1, int(seconds)))], check=False)
    finally:
        subprocess.run(["docker", "stop", capture_name], check=False, capture_output=True)
        subprocess.run(["docker", "rm", capture_name], check=False, capture_output=True)

    # Offline analysis (best-effort) using tshark inside netshoot.
    analysis_log = out_dir / "analysis.txt"
    analysis_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{out_dir}:/work",
        "-w",
        "/work",
        "nicolaka/netshoot:latest",
        "sh",
        "-lc",
        "set -e; "
        "echo '=== Protocol hierarchy ==='; "
        "tshark -r capture.pcap -q -z io,phs 2>/dev/null | head -n 220 || true; "
        "echo; echo '=== Top IP endpoints ==='; "
        "tshark -r capture.pcap -q -z endpoints,ip 2>/dev/null | head -n 220 || true; "
        "echo; echo '=== Top IP conversations ==='; "
        "tshark -r capture.pcap -q -z conv,ip 2>/dev/null | head -n 260 || true; "
        "echo; echo '=== SYN-only count (scan signal) ==='; "
        "tshark -r capture.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' 2>/dev/null | wc -l || true; "
        "echo; echo '=== SSH attempts (best-effort) ==='; "
        "tshark -r capture.pcap -Y 'tcp.port==22' 2>/dev/null | wc -l || true; "
        "echo; echo '=== RDP attempts (best-effort) ==='; "
        "tshark -r capture.pcap -Y 'tcp.port==3389' 2>/dev/null | wc -l || true;",
    ]

    analysis_rc = run_tee(analysis_cmd, cwd=ROOT, output_path=analysis_log, dry_run=False)
    narrative = build_attack_narrative(analysis_log, container_name, seconds)

    sections: list[tuple[str, str]] = [
        ("Attack Narrative (What Just Happened?)", narrative),
        (
            "What this report shows",
            "Traffic signals directed at a lab target (scans, connection bursts, protocol activity). "
            "This does NOT prove compromise. For real incident response you need endpoint telemetry "
            "(EDR/agent logs), SIEM correlation, and a full investigation process.",
        ),
        ("Target container", container_name),
        ("Capture duration", f"{seconds} seconds"),
        ("Capture file", str(pcap_path)),
        ("Analysis exit code", str(analysis_rc)),
    ]
    sections.extend(build_env_sections())

    report_path = generate_html_report(
        title="Detection Lab Report (Traffic Signals)",
        command_line=f"labctl detect --container {container_name} --seconds {seconds}",
        exit_code=0 if pcap_path.exists() else 1,
        log_path=analysis_log,
        extra_sections=sections,
        report_id=report_id,
    )

    if open_browser:
        open_report(report_path)
    return 0


def build_attack_narrative(analysis_log: Path, container_name: str, seconds: int) -> str:
    """Build a plain-English narrative from tshark analysis output."""
    if not analysis_log.exists():
        return "Analysis log not available."
    try:
        text = analysis_log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "Could not read analysis log."

    lines = text.splitlines()

    def _next_number(keyword: str) -> int:
        for i, line in enumerate(lines):
            if keyword in line:
                for j in range(i + 1, min(i + 4, len(lines))):
                    stripped = lines[j].strip()
                    if stripped.isdigit():
                        return int(stripped)
        return -1

    syn_count = _next_number("SYN-only count")
    ssh_count = _next_number("SSH attempts")
    rdp_count = _next_number("RDP attempts")

    parts: list[str] = []
    parts.append(f"Capture window: {seconds} seconds targeting container '{container_name}'.")

    if syn_count >= 0:
        rate = round(syn_count / max(seconds, 1), 1)
        if syn_count > 50:
            parts.append(
                f"HIGH SYN SCAN SIGNAL: {syn_count} unanswered SYN packets ({rate}/s). "
                "This volume and pattern is characteristic of automated port scanning (e.g., Nmap -sS half-open scan). "
                "Each SYN without a matching SYN-ACK response indicates a non-responding or filtered port probe."
            )
        elif syn_count > 0:
            parts.append(f"Low SYN activity: {syn_count} unanswered SYN packets ({rate}/s) — minimal scan signal.")
        else:
            parts.append("No SYN scan signal detected during this window.")

    if ssh_count > 0:
        rate = round(ssh_count / max(seconds, 1), 1)
        if ssh_count > 100:
            parts.append(
                f"BRUTE-FORCE SIGNAL on port 22: {ssh_count} SSH-related packets ({rate}/s). "
                "High connection volume per second is typical of Hydra with -t 16+ threads. "
                "Each attempt is a full TCP handshake followed by an SSH auth exchange — "
                "the packet count tracks failed login attempts in near real-time."
            )
        else:
            parts.append(f"Low SSH activity: {ssh_count} packets on port 22 ({rate}/s).")

    if rdp_count > 0:
        rate = round(rdp_count / max(seconds, 1), 1)
        if rdp_count > 50:
            parts.append(
                f"RDP BRUTE-FORCE SIGNAL on port 3389: {rdp_count} packets ({rate}/s). "
                "Repeated RDP connection attempts are a known ransomware delivery vector."
            )
        else:
            parts.append(f"RDP activity on port 3389: {rdp_count} packets ({rate}/s).")

    parts.append(
        "IMPORTANT: Packet counts are indicators, not proof of compromise. "
        "Real incident response requires endpoint telemetry (EDR/agent logs), "
        "log correlation, and a full investigation process — not just packet counts alone."
    )

    return "\n\n".join(parts)


def run_ctf(track: str, setup: bool, check: str | None, dry_run: bool) -> int:
    flag = CTF_FLAGS.get(track)
    if flag is None:
        raise LabCtlError(f"No CTF track available for: {track}. Choices: {sorted(CTF_FLAGS)}")

    if check is not None:
        if check.strip() == flag:
            print("[+] Correct! Flag accepted.")
            print(f"[+] {flag}")
            return 0
        print("[-] Incorrect flag. Keep trying!")
        return 1

    container_map = {"ssh": "target_ssh", "rdp": "rdp_target", "web": "bwapp_web"}
    container = container_map[track]

    flag_locations: dict[str, tuple[str, str]] = {
        "ssh": ("/root/flag.txt", "chmod 600 /root/flag.txt"),
        "rdp": ("/root/flag.txt", "chmod 600 /root/flag.txt"),
        "web": ("/var/www/html/bWAPP/flag.txt", "chmod 644 /var/www/html/bWAPP/flag.txt"),
    }
    flag_path, flag_chmod = flag_locations[track]

    if setup:
        require_binary("docker")
        cmd = [
            "docker",
            "exec",
            container,
            "bash",
            "-c",
            f"echo '{flag}' > {flag_path} && {flag_chmod}",
        ]
        code = run(cmd, cwd=ROOT, dry_run=dry_run)
        if code != 0:
            return code
        print()
        print(f"[+] CTF flag planted in '{container}' at {flag_path}")
        print()

    hints: dict[str, str] = {
        "ssh": "Brute-force into target_ssh as root, then: cat /root/flag.txt",
        "rdp": "Brute-force into rdp_target as admin, then access /root/flag.txt via the shell",
        "web": "Exploit bwapp_web to read the flag from /var/www/html/bWAPP/flag.txt (try command injection or fetch http://bwapp_web/bWAPP/flag.txt)",
    }
    attack_cmds: dict[str, str] = {
        "ssh": "python labctl.py attack-ssh -- --target target_ssh --username root",
        "rdp": "python labctl.py attack-rdp -- --target rdp_target --username admin",
        "web": "python labctl.py attack-web",
    }

    print(f"\n=== CTF Mode: {track.upper()} ===")
    print(f"  Target container : {container}")
    print(f"  Flag location    : {flag_path}")
    print()
    print(f"  Objective        : {hints[track]}")
    print(f"  Attack command   : {attack_cmds[track]}")
    print()
    if not setup:
        print(f"  Plant the flag first: python labctl.py ctf --track {track} --setup")
    print(f"  Submit your flag : python labctl.py ctf --track {track} --check <FLAG>")
    return 0


def run_quiz(track: str, non_interactive: bool, dry_run: bool) -> int:
    questions = QUIZ_BANK.get(track)
    if not questions:
        raise LabCtlError(f"No quiz available for track: {track}. Choices: {sorted(QUIZ_BANK)}")

    print(f"\n=== Quiz: {track.upper()} ({len(questions)} questions) ===")
    meta = TRACK_META.get(track, {})
    if meta.get("description"):
        print(f"    Topic: {meta['description']}")
    print()

    if dry_run:
        for i, q_dict in enumerate(questions, start=1):
            print(f"Q{i}: {q_dict['q']}")
            for opt in q_dict["options"]:
                print(f"  {opt}")
            print()
        return 0

    score = 0
    results: list[tuple[str, str, str, str]] = []

    for i, q_dict in enumerate(questions, start=1):
        question = str(q_dict["q"])
        options: list[str] = list(q_dict["options"])  # type: ignore[arg-type]
        correct = str(q_dict["answer"]).upper()
        explanation = str(q_dict["explanation"])

        print(f"Q{i}/{len(questions)}: {question}")
        for opt in options:
            print(f"  {opt}")

        if non_interactive:
            user_answer = correct
            print(f"  (non-interactive) Auto-answer: {correct}")
        else:
            try:
                raw = input("  Your answer (A/B/C/D): ").strip().upper()
            except EOFError:
                raw = correct
            user_answer = raw if raw in {"A", "B", "C", "D"} else "?"

        is_correct = user_answer == correct
        if is_correct:
            score += 1
            print(f"  [CORRECT] {explanation}")
        else:
            print(f"  [INCORRECT] Correct answer: {correct}. {explanation}")

        results.append((question, user_answer, correct, explanation))
        print()

    pct = int(score / len(questions) * 100)
    print(f"=== Score: {score}/{len(questions)} ({pct}%) ===")
    if pct == 100:
        print("[+] Perfect score! You have mastered this topic.")
    elif pct >= 80:
        print("[+] Great job! Review the questions you missed.")
    else:
        print(f"[*] Keep studying. Re-run the lesson: python labctl.py lesson --track {track}")

    result_lines: list[str] = []
    for idx, (q, ua, ca, exp) in enumerate(results, start=1):
        mark = "CORRECT" if ua == ca else "INCORRECT"
        result_lines.append(f"Q{idx}: {q}")
        result_lines.append(f"  Your answer : {ua}  |  Correct: {ca}  [{mark}]")
        if ua != ca:
            result_lines.append(f"  Explanation : {exp}")
        result_lines.append("")

    report_path = generate_html_report(
        title=f"Quiz Report: {track.upper()}",
        command_line=f"python labctl.py quiz --track {track}",
        exit_code=0 if pct >= 80 else 1,
        log_path=None,
        extra_sections=[
            ("Score", f"{score}/{len(questions)} ({pct}%)"),
            ("Results", "\n".join(result_lines)),
        ],
    )
    print(f"[+] Quiz report: {report_path}")
    return 0 if pct >= 80 else 1


def open_report(report_path: Path) -> None:
    url = report_path.resolve().as_uri()
    print(f"[+] Report written: {report_path}")
    print(f"[+] Open in browser: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        return


def choose_nmap_runner(tool: str) -> list[str]:
    if tool == "host":
        require_binary("nmap")
        return ["nmap"]
    if tool == "docker":
        require_binary("docker")
        # Lightweight container image that includes nmap
        return ["docker", "run", "--rm", "instrumentisto/nmap"]
    raise LabCtlError(f"Unknown tool: {tool}")


def network_audit(
    *,
    targets: str,
    mode: str,
    tool: str,
    yes: bool,
    open_browser: bool,
    dry_run: bool,
) -> int:
    require_authorization(yes)

    report_id = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S%z")
    log_path = REPORTS_DIR / f"{report_id}-network-audit.log"

    runner = choose_nmap_runner(tool)

    # Safe defaults: discovery only. Keep it intentionally limited for learner safety.
    if mode == "discovery":
        nmap_args = ["-sn", "-PE", "-PP", targets]
        title = "Network Audit Report (Discovery)"
    elif mode == "services":
        # Common small-biz/home exposure ports; no exploits, only version detection.
        ports = "21,22,23,25,53,80,110,135,139,143,443,445,465,587,993,995,1433,3306,3389"
        nmap_args = [
            "-sV",
            "--version-light",
            "-Pn",
            "--open",
            "-p",
            ports,
            targets,
        ]
        title = "Network Audit Report (Common Services)"
    else:
        raise LabCtlError("Invalid mode. Use discovery or services.")

    command = [*runner, *nmap_args]
    exit_code = run_tee(command, cwd=ROOT, output_path=log_path, dry_run=dry_run)

    sections: list[tuple[str, str]] = [
        (
            "Safety / authorization",
            "This scan must only be run on networks you own or are explicitly authorized to assess. This tool does not exploit; it performs discovery/service enumeration only.",
        ),
        ("Targets", targets),
        ("Mode", mode),
        ("Runner", tool),
    ]
    if not dry_run:
        sections.extend(build_env_sections(dry_run=False))

    report_path = generate_html_report(
        title=title,
        command_line=" ".join(command),
        exit_code=exit_code,
        log_path=None if dry_run else log_path,
        extra_sections=sections,
        report_id=report_id,
    )

    if open_browser and not dry_run:
        open_report(report_path)

    return exit_code


def setup_with_report(dry_run: bool, open_browser: bool) -> int:
    report_id = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S%z")
    log_path = REPORTS_DIR / f"{report_id}-lab-setup.log"
    exit_code = run_tee(
        ["ansible-playbook", str(LAB_SETUP_PLAYBOOK)],
        cwd=ROOT,
        output_path=log_path,
        dry_run=dry_run,
    )
    sections = build_env_sections(dry_run=dry_run)
    if not dry_run:
        sections.append(("Lab verify", capture_text([sys.executable, str(VERIFY_SCRIPT)], cwd=ROOT)))
    report_path = generate_html_report(
        title="Lab Setup Report",
        command_line=f"ansible-playbook {LAB_SETUP_PLAYBOOK}",
        exit_code=exit_code,
        log_path=None if dry_run else log_path,
        extra_sections=sections,
        report_id=report_id,
    )
    if open_browser and not dry_run:
        open_report(report_path)
    return exit_code


def cleanup_with_report(dry_run: bool, open_browser: bool) -> int:
    report_id = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S%z")
    log_path = REPORTS_DIR / f"{report_id}-lab-cleanup.log"
    exit_code = run_tee(
        ["ansible-playbook", str(LAB_CLEANUP_PLAYBOOK)],
        cwd=ROOT,
        output_path=log_path,
        dry_run=dry_run,
    )
    sections = build_env_sections(dry_run=dry_run)
    report_path = generate_html_report(
        title="Lab Cleanup Report",
        command_line=f"ansible-playbook {LAB_CLEANUP_PLAYBOOK}",
        exit_code=exit_code,
        log_path=None if dry_run else log_path,
        extra_sections=sections,
        report_id=report_id,
    )
    if open_browser and not dry_run:
        open_report(report_path)
    return exit_code


def run_kali_script(script_name: str, extra_args: list[str], dry_run: bool) -> int:
    require_binary("docker")
    passthrough_args = extra_args[1:] if extra_args and extra_args[0] == "--" else extra_args
    command = [
        "docker",
        "exec",
        "-it",
        "kali_attacker",
        "python3",
        f"/opt/lab/{script_name}",
        *passthrough_args,
    ]
    return run(command, cwd=ROOT, dry_run=dry_run)


def prompt_continue(non_interactive: bool) -> bool:
    if non_interactive:
        return True
    try:
        response = input("Press Enter to continue, or type 'q' to stop lesson: ").strip().lower()
    except EOFError:
        return True
    return response != "q"


def action_preview(action: str, args: list[str] | None = None) -> str:
    args = args or []
    return "python labctl.py " + " ".join([action, *args])


def run_action(action: str, dry_run: bool, args: list[str] | None = None) -> int:
    args = args or []
    if action == "doctor":
        return doctor(dry_run)
    if action == "setup":
        return run_ansible_playbook(LAB_SETUP_PLAYBOOK, dry_run)
    if action == "verify":
        return run_verify(dry_run)
    if action == "cleanup":
        return run_ansible_playbook(LAB_CLEANUP_PLAYBOOK, dry_run)
    if action == "attack-ssh":
        return run_kali_script("ssh-bruteforce.py", args, dry_run)
    if action == "attack-rdp":
        return run_kali_script("rdp-bruteforce.py", args, dry_run)
    if action == "attack-web":
        return run_host_python_script(BWAPP_ATTACK_SCRIPT, dry_run)
    if action == "harden":
        return run_ansible_playbook(LAB_HARDEN_PLAYBOOK, dry_run)
    raise LabCtlError(f"Unsupported lesson action: {action}")


def run_lesson(track: str, run_steps: bool, non_interactive: bool, dry_run: bool) -> int:
    steps = LESSON_TRACKS[track]
    meta = TRACK_META.get(track, {})
    total = len(steps)

    difficulty = meta.get("difficulty", "")
    time_est = meta.get("time", "")
    description = meta.get("description", "")
    concepts = meta.get("concepts", "")

    header = f"Guided lesson track: {track.upper()} ({total} steps)"
    if difficulty:
        header += f" | Difficulty: {difficulty}"
    if time_est:
        header += f" | Est. time: {time_est}"
    print(f"\n=== {header} ===")
    if description:
        print(f"    {description}")
    if concepts:
        print(f"    Concepts: {concepts}")
    print()

    for index, step in enumerate(steps, start=1):
        title = str(step["title"])
        prompt = str(step["prompt"])
        expected = str(step["expected"])
        action = step.get("action")
        step_args = step.get("args", [])
        mitre = step.get("mitre")
        print(f"Step {index}/{total}: {title}")
        if mitre:
            print(f"MITRE ATT&CK: {mitre}")
        print(f"Prompt: {prompt}")
        print(f"Expected output: {expected}")

        if isinstance(action, str):
            print(f"Command: {action_preview(action, step_args if isinstance(step_args, list) else [])}")
            if run_steps:
                code = run_action(
                    action,
                    dry_run=dry_run,
                    args=step_args if isinstance(step_args, list) else None,
                )
                if code != 0:
                    print(f"[-] Lesson stopped at step {index} due to exit code {code}")
                    return code

        if index < total and not prompt_continue(non_interactive):
            print("[*] Lesson exited by user")
            return 0

        print("")

    print("[+] Lesson completed")
    return 0


def status(dry_run: bool) -> int:
    """Print a live summary of Colima, Docker context, and lab containers."""
    if dry_run:
        print("$ colima status")
        print("$ docker context show")
        print("$ docker ps --format table")
        print("$ docker network ls --filter name=pentest-net")
        return 0

    print("\n=== Colima ===")
    if shutil.which("colima"):
        run(["colima", "status"], cwd=ROOT)
    else:
        print("[!] colima not found")

    print("\n=== Docker Context ===")
    if shutil.which("docker"):
        run(["docker", "context", "show"], cwd=ROOT)
    else:
        print("[!] docker not found")
        return 1

    print("\n=== Lab Containers ===")
    run(
        ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
        cwd=ROOT,
    )

    print("\n=== All Containers (including stopped) ===")
    run(
        ["docker", "ps", "-a", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
        cwd=ROOT,
    )

    print("\n=== Pentest Network ===")
    run(
        ["docker", "network", "ls", "--filter", "name=pentest-net"],
        cwd=ROOT,
    )

    print("\n=== Network Inspect ===")
    run(
        ["docker", "network", "inspect", "pentest-net",
         "--format", "{{range .Containers}}{{.Name}}: {{.IPv4Address}}\n{{end}}"],
        cwd=ROOT,
    )

    return 0


def doctor(dry_run: bool) -> int:
    checks = [
        ["colima", "status"],
        ["docker", "context", "show"],
        ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
    ]

    # In dry-run mode, the contract is to avoid executing commands.
    # CI environments (Linux runners) often don't have Colima installed.
    if dry_run:
        for command in checks:
            print(f"$ {' '.join(command)}")
        return 0

    for command in checks:
        binary = command[0]
        if shutil.which(binary) is None:
            # Colima is macOS-specific; skip if not present.
            print(f"[!] Skipping missing command: {binary}")
            continue
        code = run(command, cwd=ROOT, dry_run=False)
        if code != 0:
            return code
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BootCon lab control utility")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")

    common = argparse.ArgumentParser(add_help=False)
    # IMPORTANT: many subcommands inherit this via `parents=[common]`.
    # If we set a default here, it can override the top-level --dry-run when
    # users call `labctl.py --dry-run <subcommand>`.
    # Suppressing the default prevents accidental reset to False.
    common.add_argument(
        "--dry-run",
        action="store_true",
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser(
        "setup", parents=[common], help="Run full lab setup playbook"
    )
    setup_parser.add_argument(
        "--no-report",
        action="store_true",
        help="Disable writing an HTML report to reports/",
    )
    setup_parser.add_argument("--report", action="store_true", help=argparse.SUPPRESS)
    setup_parser.add_argument("--open", action="store_true", help="Open the report in a browser")
    subparsers.add_parser("verify", parents=[common], help="Run lab verification script")
    cleanup_parser = subparsers.add_parser(
        "cleanup", parents=[common], help="Run full lab cleanup playbook"
    )
    cleanup_parser.add_argument(
        "--no-report",
        action="store_true",
        help="Disable writing an HTML report to reports/",
    )
    cleanup_parser.add_argument("--report", action="store_true", help=argparse.SUPPRESS)
    cleanup_parser.add_argument("--open", action="store_true", help="Open the report in a browser")
    subparsers.add_parser("doctor", parents=[common], help="Run local environment checks")

    ssh_parser = subparsers.add_parser(
        "attack-ssh", parents=[common], help="Run SSH attack workflow from Kali"
    )
    ssh_parser.add_argument("script_args", nargs=argparse.REMAINDER)

    rdp_parser = subparsers.add_parser(
        "attack-rdp", parents=[common], help="Run RDP attack workflow from Kali"
    )
    rdp_parser.add_argument("script_args", nargs=argparse.REMAINDER)

    subparsers.add_parser(
        "attack-web",
        parents=[common],
        help="Run the bWAPP reflected XSS workflow from the host",
    )

    subparsers.add_parser(
        "shell", parents=[common], help="Open interactive shell in kali_attacker container"
    )

    lesson_parser = subparsers.add_parser(
        "lesson",
        parents=[common],
        help="Guided lesson mode with prompts and expected outputs",
    )
    lesson_parser.add_argument(
        "--track",
        choices=sorted(LESSON_TRACKS.keys()),
        default="ssh",
        help="Lesson track to run",
    )
    lesson_parser.add_argument(
        "--run",
        action="store_true",
        help="Execute each step command in addition to showing guidance",
    )
    lesson_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run lesson without waiting for Enter between steps",
    )

    report_parser = subparsers.add_parser(
        "report", parents=[common], help="Generate a standalone HTML status report"
    )
    report_parser.add_argument("--open", action="store_true", help="Open the report in a browser")

    audit_parser = subparsers.add_parser(
        "audit",
        parents=[common],
        help="Defensive network audit (discovery/service enumeration) with HTML report",
    )
    audit_parser.add_argument(
        "--targets",
        required=True,
        help="Targets to scan (CIDR or range). Example: 192.168.1.0/24",
    )
    audit_parser.add_argument(
        "--mode",
        choices=["discovery", "services"],
        default="discovery",
        help="discovery = host discovery only; services = scan common ports with -sV",
    )
    audit_parser.add_argument(
        "--tool",
        choices=["host", "docker"],
        default="host",
        help="How to run nmap (host requires nmap installed; docker pulls instrumentisto/nmap)",
    )
    audit_parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm you are authorized to scan these targets",
    )
    audit_parser.add_argument("--open", action="store_true", help="Open the report in a browser")

    gui_parser = subparsers.add_parser(
        "gui",
        parents=[common],
        help="Optional GUI helpers (container log viewer stack)",
    )
    gui_parser.add_argument("--up", action="store_true", help="Start the GUI stack")
    gui_parser.add_argument("--down", action="store_true", help="Stop the GUI stack")
    gui_parser.add_argument("--open", action="store_true", help="Open the GUI in a browser")

    harden_parser = subparsers.add_parser(
        "harden",
        parents=[common],
        help="Apply hardening/remediation playbook (post-lesson) and write report",
    )
    harden_parser.add_argument("--open", action="store_true", help="Open the report in a browser")
    harden_parser.add_argument(
        "--no-report",
        action="store_true",
        help="Disable writing an HTML report to reports/",
    )

    scan_parser = subparsers.add_parser(
        "scan",
        parents=[common],
        help="Supply-chain scanning (Trivy) with HTML report",
    )
    scan_parser.add_argument(
        "--type",
        choices=["fs", "images"],
        default="fs",
        help="fs scans repo contents; images scans lab container images",
    )
    scan_parser.add_argument("--open", action="store_true", help="Open the report in a browser")

    detect_parser = subparsers.add_parser(
        "detect",
        parents=[common],
        help="Detection lab: capture + analyze traffic signals for a target container",
    )
    detect_parser.add_argument(
        "--container",
        required=True,
        help="Target container name (e.g., target_ssh, bwapp_web, rdp_target)",
    )
    detect_parser.add_argument(
        "--seconds",
        type=int,
        default=60,
        help="Capture duration in seconds",
    )
    detect_parser.add_argument("--open", action="store_true", help="Open the report in a browser")

    ctf_parser = subparsers.add_parser(
        "ctf",
        parents=[common],
        help="CTF challenge mode: plant a flag in a target container and verify capture",
    )
    ctf_parser.add_argument(
        "--track",
        choices=sorted(CTF_FLAGS.keys()),
        default="ssh",
        help="Target track (ssh, rdp, web)",
    )
    ctf_parser.add_argument(
        "--setup",
        action="store_true",
        help="Plant the CTF flag in the target container and print objectives",
    )
    ctf_parser.add_argument(
        "--check",
        metavar="FLAG",
        default=None,
        help="Submit a captured flag value to verify it",
    )

    quiz_parser = subparsers.add_parser(
        "quiz",
        parents=[common],
        help="Multiple-choice quiz for a lesson track with HTML score report",
    )
    quiz_parser.add_argument(
        "--track",
        choices=sorted(QUIZ_BANK.keys()),
        default="ssh",
        help="Quiz track to run",
    )
    quiz_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Auto-answer correctly (useful for CI/dry-run preview)",
    )

    subparsers.add_parser(
        "status",
        parents=[common],
        help="Show live status of Colima, Docker, and all lab containers",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if args.command == "setup":
            if getattr(args, "no_report", False):
                return run_ansible_playbook(LAB_SETUP_PLAYBOOK, args.dry_run)
            return setup_with_report(args.dry_run, getattr(args, "open", False))
        if args.command == "verify":
            return run_verify(args.dry_run)
        if args.command == "cleanup":
            if getattr(args, "no_report", False):
                return run_ansible_playbook(LAB_CLEANUP_PLAYBOOK, args.dry_run)
            return cleanup_with_report(args.dry_run, getattr(args, "open", False))
        if args.command == "doctor":
            return doctor(args.dry_run)
        if args.command == "attack-ssh":
            return run_kali_script("ssh-bruteforce.py", args.script_args, args.dry_run)
        if args.command == "attack-rdp":
            return run_kali_script("rdp-bruteforce.py", args.script_args, args.dry_run)
        if args.command == "attack-web":
            return run_host_python_script(BWAPP_ATTACK_SCRIPT, args.dry_run)
        if args.command == "shell":
            require_binary("docker")
            return run(["docker", "exec", "-it", "kali_attacker", "bash"], dry_run=args.dry_run)
        if args.command == "lesson":
            return run_lesson(args.track, args.run, args.non_interactive, args.dry_run)
        if args.command == "report":
            sections = build_env_sections(dry_run=args.dry_run)
            if not args.dry_run:
                sections.append(("Lab verify", capture_text([sys.executable, str(VERIFY_SCRIPT)], cwd=ROOT)))
            report_path = generate_html_report(
                title="Lab Status Report",
                command_line="python labctl.py report",
                exit_code=0,
                log_path=None,
                extra_sections=sections,
            )
            if getattr(args, "open", False):
                open_report(report_path)
            return 0
        if args.command == "audit":
            return network_audit(
                targets=args.targets,
                mode=args.mode,
                tool=args.tool,
                yes=args.yes,
                open_browser=getattr(args, "open", False),
                dry_run=args.dry_run,
            )
        if args.command == "gui":
            if not (getattr(args, "up", False) or getattr(args, "down", False) or getattr(args, "open", False)):
                raise LabCtlError("Use --up, --down, and/or --open")
            return gui_stack(
                up=getattr(args, "up", False),
                down=getattr(args, "down", False),
                open_browser=getattr(args, "open", False),
                dry_run=args.dry_run,
            )
        if args.command == "harden":
            if getattr(args, "no_report", False):
                return run_ansible_playbook(LAB_HARDEN_PLAYBOOK, args.dry_run)
            return harden_with_report(args.dry_run, getattr(args, "open", False))
        if args.command == "scan":
            return trivy_scan(
                scan_type=args.type,
                open_browser=getattr(args, "open", False),
                dry_run=args.dry_run,
            )
        if args.command == "detect":
            return detect_capture_and_analyze(
                container_name=args.container,
                seconds=args.seconds,
                open_browser=getattr(args, "open", False),
                dry_run=args.dry_run,
            )
        if args.command == "ctf":
            return run_ctf(
                track=args.track,
                setup=getattr(args, "setup", False),
                check=getattr(args, "check", None),
                dry_run=args.dry_run,
            )
        if args.command == "status":
            return status(args.dry_run)
        if args.command == "quiz":
            return run_quiz(
                track=args.track,
                non_interactive=getattr(args, "non_interactive", False),
                dry_run=args.dry_run,
            )
    except LabCtlError as error:
        print(f"[-] {error}")
        return 2

    print("[-] Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
