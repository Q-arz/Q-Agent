from typing import List, Dict, Any, Callable
from core.router.dynamic_router import dynamic_manifests


def list_tools() -> List[Dict[str, Any]]:
    tools = []
    for manifest in dynamic_manifests:
        mid = manifest.get("id", "unknown")
        for cmd in manifest.get("commands", []):
            tools.append(
                {
                    "module": mid,
                    "name": f"{mid}:{cmd.get('trigger', '').strip()}",
                    "description": cmd.get("description", ""),
                    "args": cmd.get("args", []),
                    "permissions": manifest.get("permissions", []),
                }
            )
    return tools


def call_tool(router, tool_name: str, text: str) -> str:
    # tool_name format: module_id:trigger
    try:
        module_id, trigger = tool_name.split(":", 1)
    except ValueError:
        return "[Q•AI] Invalid tool name."

    # Reuse router path to enforce permissions and audit
    # Build a command line as if typed
    command = f"{trigger} {text}" if text else trigger
    return router.route(command)


