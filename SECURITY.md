# Security Policy

## Supported use

This repository is for authorized cybersecurity education and testing in controlled environments.

## Reporting a vulnerability

If you discover a security issue in lab code or automation, please report it privately to the maintainers before public disclosure.

Include:

- Affected file(s) and workflow
- Reproduction steps
- Impact assessment
- Suggested fix (if available)

## Safe usage requirements

- Only test systems you own or have explicit written authorization to assess.
- Never target public infrastructure or third-party systems without permission.
- Follow institutional and legal policies for offensive security exercises.

## AI Lab Assistant data handling

The optional AI assistant (`ai-assistant/`, `python labctl.py ai --up`) is local-only by default:

- It runs on a local Ollama container. No lab data, chat messages, container logs, or lesson content leave your machine.
- Its "Log Analyst" mode mounts the Docker socket **read-only** and only reads logs for a container you explicitly select in a chat request — it does not proactively scan or exfiltrate anything.
- If you opt in to `AI_PROVIDER=openai` (see `ai-assistant/README.md`), chat messages and any injected context (command reference, lesson docs, or container log excerpts) are sent to OpenAI's API under your own API key. Don't enable this in an environment where log/lesson content is sensitive.
