# Contributing to Q•AI

Thanks for your interest! This project is open-source and welcomes contributions.

## How to contribute

- Fork the repo and create a feature branch from `main`
- Follow existing code style and linting
- Include tests or a smoke step when possible
- Update docs for any user-visible changes

## Areas and ownership

- Core: router, memory/board, permissions, logging/metrics, popouts, health checks
- Modules (store): integrations and RPA flows using the Core API

## Development setup

- Python 3.10+
- Windows (primary target)
- Create venv and install `requirements.txt`; optional voice deps via `scripts/setup_voice.py`
- Run smoke test: `python scripts/smoke_test.py`

## Commit and PR guidelines

- Use clear, descriptive commit messages
- One logical change per PR
- Link issues and add a concise changelog entry

## Security and privacy

- Never commit secrets (use `.env` and keep it out of VCS)
- Minimize logging of personal data; redact when in doubt
- Follow `SECURITY.md` for reporting vulnerabilities

## Module development

- Provide a `get_manifest()` with permissions and commands
- Optional `ui.json` to render popout UIs
- Document commands, synonyms, and any required environment variables

## Code of Conduct

Be respectful and constructive. We follow a simple “be excellent to each other” policy. Issues or PRs violating this may be closed.
