PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

.PHONY: setup verify cleanup doctor attack-ssh attack-rdp shell lesson lesson-run lesson-rdp lesson-web quality
.PHONY: audit-discovery audit-services
.PHONY: gui-up gui-down gui-open ai-up ai-down ai-open harden harden-open scan-fs scan-images
.PHONY: detect-ssh detect-bwapp detect-rdp
.PHONY: report setup-report cleanup-report
.PHONY: ctf-ssh ctf-rdp ctf-web quiz-ssh quiz-rdp quiz-web quiz-remediate

setup:
	$(PYTHON) labctl.py setup

setup-report:
	$(PYTHON) labctl.py setup --open

verify:
	$(PYTHON) labctl.py verify

cleanup:
	$(PYTHON) labctl.py cleanup

cleanup-report:
	$(PYTHON) labctl.py cleanup --open

doctor:
	$(PYTHON) labctl.py doctor

report:
	$(PYTHON) labctl.py report --open

audit-discovery:
	@echo "Example: make audit-discovery TARGETS=192.168.1.0/24"
	$(PYTHON) labctl.py audit --targets "$(TARGETS)" --mode discovery --yes --open

audit-services:
	@echo "Example: make audit-services TARGETS=192.168.1.0/24"
	$(PYTHON) labctl.py audit --targets "$(TARGETS)" --mode services --yes --open

gui-up:
	$(PYTHON) labctl.py gui --up

gui-open:
	$(PYTHON) labctl.py gui --up --open

gui-down:
	$(PYTHON) labctl.py gui --down

ai-up:
	$(PYTHON) labctl.py ai --up

ai-open:
	$(PYTHON) labctl.py ai --up --open

ai-down:
	$(PYTHON) labctl.py ai --down

harden:
	$(PYTHON) labctl.py harden

harden-open:
	$(PYTHON) labctl.py harden --open

scan-fs:
	$(PYTHON) labctl.py scan --type fs --open

scan-images:
	$(PYTHON) labctl.py scan --type images --open

detect-ssh:
	$(PYTHON) labctl.py detect --container target_ssh --seconds 90 --open

detect-rdp:
	$(PYTHON) labctl.py detect --container rdp_target --seconds 90 --open

detect-bwapp:
	$(PYTHON) labctl.py detect --container bwapp_web --seconds 90 --open

attack-ssh:
	$(PYTHON) labctl.py attack-ssh

attack-rdp:
	$(PYTHON) labctl.py attack-rdp

shell:
	$(PYTHON) labctl.py shell

lesson:
	$(PYTHON) labctl.py lesson --track ssh

lesson-run:
	$(PYTHON) labctl.py lesson --track ssh --run

lesson-rdp:
	$(PYTHON) labctl.py lesson --track rdp

lesson-web:
	$(PYTHON) labctl.py lesson --track web --run

ctf-ssh:
	$(PYTHON) labctl.py ctf --track ssh --setup

ctf-rdp:
	$(PYTHON) labctl.py ctf --track rdp --setup

ctf-web:
	$(PYTHON) labctl.py ctf --track web --setup

quiz-ssh:
	$(PYTHON) labctl.py quiz --track ssh --non-interactive

quiz-rdp:
	$(PYTHON) labctl.py quiz --track rdp --non-interactive

quiz-web:
	$(PYTHON) labctl.py quiz --track web --non-interactive

quiz-remediate:
	$(PYTHON) labctl.py quiz --track remediate --non-interactive

quality:
	$(PYTHON) -m compileall -q verify-lab.py ssh-brute-lab/ansible/scripts labctl.py
	$(PYTHON) -m ruff check .
	ansible-playbook --syntax-check ssh-brute-lab/ansible/lab/lab-setup.yml
