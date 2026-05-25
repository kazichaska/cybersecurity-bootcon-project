# Instructor Guide — BootCon Cybersecurity Lab

This guide is for instructors, teaching assistants, and workshop facilitators running the BootCon lab with a group of students.

---

## Before the session

### 1. Preflight your machine

```bash
colima start
docker context use colima
python labctl.py doctor
```

All three checks should pass. If Colima shows "stopped", run `colima start` again.

### 2. Pre-deploy the lab (recommended)

Pre-deploying before students arrive avoids image-pull delays during the session.

```bash
python labctl.py setup
python labctl.py verify
```

Verify should show all four containers (`kali_attacker`, `target_ssh`, `rdp_target`, `bwapp_web`) in `running` state.

### 3. Open the live GUI (projector)

The Dozzle GUI lets you display live container logs on a projector so the class can watch what's happening in real time.

```bash
python labctl.py gui --up --open
```

Leave this running on your projector browser tab throughout the session.

---

## Running a lesson (guided mode)

### Show steps to the class without executing them

```bash
python labctl.py lesson --track ssh
```

This prints each step with the prompt, expected output, and MITRE ATT&CK tag. Use this to narrate while a volunteer runs commands.

### Execute all steps automatically (demo / instructor machine)

```bash
python labctl.py lesson --track ssh --run
```

Pauses at each step for `Enter`. Type `q` to stop early.

### Fully automated run (no pauses — for screen recording or CI demo)

```bash
python labctl.py lesson --track ssh --run --non-interactive
```

---

## Lesson tracks at a glance

| Track | Difficulty | Est. Time | Key Concept |
|---|---|---|---|
| `ssh` | Beginner | 25 min | SSH brute-force + hardening |
| `rdp` | Beginner | 20 min | RDP brute-force + account lockout |
| `web` | Beginner | 30 min | XSS + SQL injection via bWAPP |
| `remediate` | Intermediate | 35 min | Full exploit → harden → re-test cycle |

Run any track with:
```bash
python labctl.py lesson --track <track> --run
```

---

## CTF exercises (graded / self-paced)

CTF mode plants a flag inside a target container. Students must exploit the target to read the flag and submit it.

### Setup for students (run once, or let students run `--setup` themselves)

```bash
python labctl.py ctf --track ssh --setup
python labctl.py ctf --track rdp --setup
python labctl.py ctf --track web --setup
```

### What students do

```bash
# 1. Read the objective
python labctl.py ctf --track ssh

# 2. Exploit the target (brute-force SSH, find the flag)
python labctl.py attack-ssh -- --target target_ssh --username root
# → SSH in manually, cat /root/flag.txt

# 3. Submit
python labctl.py ctf --track ssh --check CTF{...}
```

A correct flag prints `[+] Correct! Flag accepted.` — students can screenshot this as proof.

---

## Quizzes (assessment)

Each track has a 5-question multiple-choice quiz covering key concepts. Generates an HTML report with score.

```bash
# Interactive quiz
python labctl.py quiz --track ssh

# Non-interactive / demo preview
python labctl.py quiz --track ssh --non-interactive
```

Report is saved to `reports/`. Students can submit their quiz report HTML as evidence of completion.

---

## Resetting the lab between students / groups

```bash
python labctl.py cleanup
python labctl.py setup
python labctl.py verify
```

This tears down all containers and redeploys a clean state. Takes ~2–3 minutes.

---

## Timing guide for common session formats

### 50-minute introductory class

| Time | Activity |
|---|---|
| 0–5 min | Instructor setup, Dozzle GUI on projector |
| 5–15 min | Lecture: what is brute-force? MITRE ATT&CK T1110 |
| 15–35 min | Live demo: `lesson --track ssh --run` |
| 35–45 min | Students run the quiz independently: `quiz --track ssh` |
| 45–50 min | Debrief, controls discussion |

### 90-minute hands-on lab

| Time | Activity |
|---|---|
| 0–10 min | Instructor setup + preflight |
| 10–20 min | Lecture: attack landscape overview |
| 20–50 min | `lesson --track ssh --run` with class participation |
| 50–70 min | CTF challenge: `ctf --track ssh --setup`, students exploit independently |
| 70–80 min | Detection lab: `detect --container target_ssh --seconds 60 --open` while attack runs |
| 80–90 min | Debrief, quiz, review HTML reports |

### Full-day workshop (6 hours)

Suggested flow:
1. SSH track (25 min lesson + 15 min CTF)
2. RDP track (20 min lesson + 15 min CTF)
3. Detection lab (30 min)
4. Web track (30 min lesson + 20 min CTF)
5. Remediation track (35 min)
6. Supply chain scan: `python labctl.py scan --type fs --open` (15 min)
7. Network audit on lab network (optional, 20 min)
8. Final quiz all tracks + debrief (30 min)

---

## Common issues

### Docker socket not found

```bash
colima start
docker context use colima
python labctl.py doctor
```

### A container is stuck in "created" state

```bash
python labctl.py cleanup
python labctl.py setup
```

### Students can't reach bwapp_web

bWAPP runs on port 80 **inside the Docker network** (Docker maps host port 8080 to container port 80). Students access it from inside the Kali container:

```bash
python labctl.py shell
# Inside Kali:
curl http://bwapp_web/bWAPP/
```

If accessing from the host machine, the container maps to `http://localhost:8080`.

### Hydra doesn't find the password

Ensure the target is using the default `root:toor` credential (lab default). Check the wordlist path inside Kali at `/opt/lab/`. Re-run setup if the container was customized.

---

## Concept cards (for handouts or pre-reading)

Point students to `docs/concepts/` for short reference cards:

- [SSH Brute-Force](concepts/ssh-brute-force.md)
- [fail2ban](concepts/fail2ban.md)
- [Why Password Auth Is Weak](concepts/why-password-auth-is-weak.md)
- [RDP Brute-Force](concepts/rdp-brute-force.md)
- [Web Attacks: XSS and SQL Injection](concepts/web-attacks.md)

---

## Ethical and legal reminder

Remind students at the start of every session:

> All attack commands in this lab only work against containers running **on your own machine**. Never run these tools against any system you do not own or have **explicit written authorization** to test. Unauthorized access to computer systems is a federal crime (CFAA) and a violation of state law.
