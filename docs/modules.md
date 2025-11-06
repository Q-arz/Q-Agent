## Module API (Manifest)

Modules live under `modules/<module_name>/` and must expose a Python API and a manifest function.

### Python API

File: `modules/<module_name>/module.py`

Required function:

```python
def get_manifest():
    return {
        "id": "example.module",
        "name": "Example Module",
        "version": "0.1.0",
        "description": "Sample commands",
        "permissions": ["filesystem.read"],
        "commands": [
            {
                "trigger": "example",
                "description": "Run example command",
                "args": [{"name": "text", "type": "string", "required": False}],
                "handler": example_handler,
            }
        ],
    }
```

Handlers receive `(command_text, router)` and must return a string.

### Permissions

Declare required permissions in the manifest:

- `filesystem.read`, `filesystem.write`, `process.spawn`, `network.request`, `ui.automation`

The router enforces these using `PermissionManager` with time-bound elevation prompts.

### UI Automation (Selectors)

For UI control, the core exposes a minimal selector syntax via `core/ui_automation.py`:

- Selector text: `title="Notepad" app="notepad"`
- Supported fields (MVP): `title` (substring match), `app` (reserved), `role`/`name` (future)

System module commands (examples):

- `focus_selector title="Notepad"`
- `click_selector title="Chrome"`
- `type_selector title="Notepad" Hello world!`

On Windows this uses `pygetwindow` + `pyautogui`. macOS/Linux fallbacks are planned.

### Backwards compatibility

If `get_manifest()` is not found, the loader falls back to `get_commands()` returning a list of `{trigger, function}` entries.

### Permissions (proposed)

- `filesystem.read`, `filesystem.write`, `process.spawn`, `network.request`, `ui.automation`
- Sensitive permissions require explicit user confirmation at runtime.


