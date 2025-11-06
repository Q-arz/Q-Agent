## Project Status (Snapshot)

### Completed (Core)
- Health checks, degrade to text, graceful shutdown
- Rotating logs + basic metrics; audit logging
- Permission model: whitelist, allow/deny, path limits; elevated prompts with summary
- Router: timeouts, retries, intent matcher (synonyms + fuzzy)
- Generator: multi-provider with cache and rate limiting
- PopoutService: text/table/form; BeforeUI for setup
- Board: robust schema, archive, dedupe; rule-based suggester; executor with cooldown/backoff

### Completed (Modules)
- system: open_app/open_url/list_dir/move_file; organize_dir/clean_empty_dirs
- system (UIA): focus_window/type_text/notepad_write
- social: post/prepare_tiktok (manifest + UI example)

### In Progress / Next
- RPA abstraction (UI Automation deeper): selectors (UIA/Win32) + OCR fallback [Core + system]
- Windowing and layouts module [Module]
- FileOps advanced rules + preview/dry-run UI [Module]
- Scheduler with UI [Module]
- Clipboard/Snipping/OCR/Notifications [Modules]
- Store/Marketplace v1 (manifest specs, verification, installer) [Core + Store]
- Command palette global + notifications [Core/UX]
- Voice pack (setup, models, wake word) [Module]

### Cross-platform Support
- Core runs on Windows/macOS/Linux. Some capabilities vary by OS.
- System module dispatches per OS; Windows paths and UI automation are most advanced now.
- Voice is optional and off by default; install via `setup voice` and `models ensure vosk <lang>` per OS.
- MCP support is consumer-only for now; no server exposure.

---

## Progress Log

- [x] Rebrand visible strings to Q•Agent (core/UI/docs)
- [x] Multi‑OS detection (`core/platform.py`) + `os_family` in config
- [x] System module: `open_app` cross‑platform; aliases/shortcuts
- [x] UI Automation base (`core/ui_automation.py`) + selector commands (`focus_selector`, `click_selector`, `type_selector`)
- [x] Command palette (`palette`) popout
- [x] Security/OSS docs (SECURITY.md, CONTRIBUTING.md, templates)
- [ ] UI selectors v2: role/name + backend UIA (Windows), stubs mac/Linux
- [ ] Windowing/layouts module (save/restore, move/resize, desktops)
- [ ] FileOps rules UI (preview/dry‑run) + undo
- [ ] Scheduler module UI
- [ ] Clipboard/Snipping/OCR/Notifications
- [ ] Store/Marketplace v1
- [ ] Voice pack (setup/models/wake word)

