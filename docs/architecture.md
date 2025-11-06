## Q•AI Architecture Overview

This document describes the high-level architecture of Q•AI after flattening the repository structure.

### Components

- core/
  - memory/: Symbolic memory management and boot context
  - interfaces/: IO layer (text/voice, TTS), listeners
  - router/: Command routing (built-in and dynamic modules)
  - auto/: Reflection/suggestion routines
  - generators/: External info generators
  - config/: JSON configuration files

- modules/: First-party modules, each offering commands via a manifest
- store/: Tools to download/import external modules (marketplace plumbing)
- main.py: Entrypoint (loads config, builds memory context, starts IO)

### Runtime Flow

1) main.py loads config and opens a SymbolicContext
2) IOHandler initializes TTS and a voice/text listener
3) CommandRouter loads built-in handlers and dynamic module commands
4) User input is confirmed (for voice) and then routed
5) If no trigger/synonym matches, a Generator fallback suggests an action
6) Responses are spoken/printed and persisted to memory (audit included)

### Design Goals

- Extensibility: modules add commands without changing the core
- Safety: sensitive commands require explicit permissions and confirmations
- Portability: Windows-first, cross-platform aware
- Observability: clear logs and recoverable failures


