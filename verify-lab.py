import docker

# List of expected containers
EXPECTED_CONTAINERS = [
    "kali_attacker",
    "target_ssh",
    "rdp_target",
    "bwapp_web",
    "metasploit_target"
]

# Path to Colima Docker socket (update if needed)
DOCKER_SOCKET = "unix://$HOME/.colima/default/docker.sock"

def main():
    print("🔍 Verifying lab containers...\n")

    try:
        client = docker.DockerClient(base_url=DOCKER_SOCKET)
        running_containers = {container.name for container in client.containers.list()}

        all_ok = True
        for name in EXPECTED_CONTAINERS:
            if name in running_containers:
                print(f"✅ {name} is running")
            else:
                print(f"❌ {name} is NOT running")
                all_ok = False

        if all_ok:
            print("\n🎉 All lab containers are up and running!")
        else:
            print("\n⚠️ Some containers are missing. Please re-run your setup playbook.")

    except docker.errors.DockerException as e:
        print(f"💥 Docker error: {e}")
        print("Make sure Docker and Colima are running and the socket path is correct.")

if __name__ == "__main__":
    main()
