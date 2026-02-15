# Contributing

Thanks for improving the BootCon cybersecurity lab.

## Development setup

1. Install runtime dependencies:

   ```bash
   pip install -r ssh-brute-lab/requirements.txt
   ```

2. Install quality tooling:

   ```bash
   pip install -r requirements-dev.txt
   ```

## Local quality checks

Run before opening a PR:

```bash
ruff check .
python -m compileall -q verify-lab.py ssh-brute-lab/ansible/scripts labctl.py
ansible-playbook --syntax-check ssh-brute-lab/ansible/lab/lab-setup.yml
ansible-playbook --syntax-check ssh-brute-lab/ansible/lab/lab-cleanup.yml
```

## Contribution scope

- Keep changes focused and minimal.
- Prefer improving reproducibility, learner UX, and safety.
- Do not add attack automation for unauthorized targets.
- Update documentation when behavior or commands change.

## Pull requests

- Describe what changed and why.
- Include test/validation output.
- Note any backward-incompatible changes.
