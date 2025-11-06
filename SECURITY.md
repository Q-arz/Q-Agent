# Security Policy

## Supported versions

This is an active project. Security fixes are applied to `main` and backported as needed.

## Reporting a vulnerability

- Please open a private report via email or a confidential issue (do not post details publicly).
- Include: steps to reproduce, impact, affected area (core or module), and suggested remediation if any.

## Threat model

- Local assistant with system control (Windows-first). Primary risks:
  - Privilege misuse: filesystem/process/network/UI automation
  - Supply chain: third-party modules
  - Data leakage: logs, memory, secrets

## Protections in core

- Capabilities and permissions per module: `filesystem.read|write`, `process.spawn`, `network.request`, `ui.automation`
- Permission prompts with time-bound elevation; whitelist in `core/config/qai_config.json`
- Security policy: `security.allow/deny` per command, `path_limits` to restrict filesystem operations
- Audit trail: command executions stored in memory; rotating logs under `logs/`
- Timeouts/retries and isolation of dynamic commands execution via thread pool
- Health checks and safe degradation to text mode if voice deps are missing

## Modules and marketplace

- Manifest v1 (id, version, permissions, commands, optional ui.json)
- Dynamic loader: loads only declared commands/handlers, records manifest metadata
- Recommended: run third-party modules with restricted permissions and review code before enabling

## Secrets and logs

- Store secrets in environment variables (`.env` ignored by VCS)
- Do not include tokens in code or UI schemas
- Logs redact sensitive fields where possible; rotate regularly

## UI automation

- `ui.automation` is sensitive: requires explicit opt-in (whitelist) and is time-bound when prompted
- Prefer path-limited operations and confirmation for high-impact actions

## Responsible disclosure

We appreciate responsible disclosure. You will receive acknowledgment in the changelog after the fix is released.
