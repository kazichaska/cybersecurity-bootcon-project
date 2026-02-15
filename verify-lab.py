#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys

try:
    import docker  # type: ignore
except Exception:  # pragma: no cover
    docker = None

EXPECTED_CONTAINERS = [
    "kali_attacker",
    "target_ssh",
    "rdp_target",
    "bwapp_web",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify BootCon cyber lab health")
    parser.add_argument(
        "--docker-socket",
        default="unix://{home}/.colima/default/docker.sock".format(
            home=os.path.expanduser("~")
        ),
        help="Docker socket URL (default: Colima socket)",
    )
    parser.add_argument(
        "--expect",
        nargs="+",
        default=EXPECTED_CONTAINERS,
        help="Container names expected to be running",
    )
    return parser.parse_args()


def status_icon(state: str) -> str:
    return "✅" if state == "running" else "⚠️"


def main() -> None:
    args = parse_args()
    print("🔍 Verifying lab containers...\n")

    if docker is not None:
        try:
            client = docker.DockerClient(base_url=args.docker_socket)
            containers = {
                container.name: container for container in client.containers.list(all=True)
            }
        except Exception as error:
            print(f"💥 Docker SDK error: {error}")
            print("Tip: If you don't have the docker Python package, install it or use the CLI fallback.")
            containers = {}
    else:
        containers = {}

    # CLI fallback (works even when python 'docker' isn't installed)
    cli_status: dict[str, str] = {}
    if not containers:
        if shutil.which("docker") is None:
            print("💥 Docker is not installed or not available in PATH")
            print("Install Docker Desktop/Colima and ensure `docker` works.")
            sys.exit(2)

        try:
            result = subprocess.run(
                [
                    "docker",
                    "--host",
                    args.docker_socket,
                    "ps",
                    "-a",
                    "--format",
                    "{{.Names}}\t{{.Status}}",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as error:
            print(f"💥 Docker CLI error: {error}")
            print("Check Docker/Colima status and verify the socket path.")
            sys.exit(2)

        if result.returncode != 0:
            print("💥 Docker CLI error:")
            print(result.stderr.strip() or result.stdout.strip() or "(no output)")
            sys.exit(2)

        for line in (result.stdout or "").splitlines():
            if not line.strip() or "\t" not in line:
                continue
            name, status = line.split("\t", 1)
            cli_status[name.strip()] = status.strip()

    all_healthy = True
    for expected_name in args.expect:
        if containers:
            container = containers.get(expected_name)
            if container is None:
                print(f"❌ {expected_name}: missing")
                all_healthy = False
                continue

            container_state = container.status
            print(f"{status_icon(container_state)} {expected_name}: {container_state}")
            if container_state != "running":
                all_healthy = False
        else:
            status = cli_status.get(expected_name)
            if status is None:
                print(f"❌ {expected_name}: missing")
                all_healthy = False
                continue
            running = status.startswith("Up")
            print(f"{'✅' if running else '⚠️'} {expected_name}: {status}")
            if not running:
                all_healthy = False

    if all_healthy:
        print("\n🎉 Lab health check passed")
        sys.exit(0)

    print("\n⚠️ Lab health check failed. Re-run the setup playbook or inspect failed containers.")
    sys.exit(1)


if __name__ == "__main__":
    main()
