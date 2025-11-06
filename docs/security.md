## Security Model

Q•AI aims to control the PC safely. This requires layered defenses:

### Runtime Permissions

- Each module declares required permissions in its manifest
- Router checks permissions via `PermissionManager` before execution
- Sensitive actions (`filesystem.write`, `process.spawn`, `network.request`, `ui.automation`) require explicit confirmation and time-bound elevation (default 5 minutes)
- Config has `permissions_whitelist` to auto-grant selected permissions per module

### Command Safety

- Maintain a denylist for obviously dangerous patterns
- Prefer allowlists per capability
- Log all elevated operations for auditing

### Isolation

- Prefer separate processes for third-party modules (planned)
- Message-passing to avoid importing untrusted code into the core

### Secrets & Config

- No secrets in code; use environment variables or encrypted files
- Validate and sanitize all user inputs before execution


