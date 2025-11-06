## MCP Integration

Q•AI targets MCP compatibility for tools/resources interoperability.

### Goals

- Discover MCP servers and list capabilities
- Wrap module commands as MCP tools where applicable
- Allow installing MCP packages via `store/`

### Manifests

Module manifests may include an `mcp` section:

```json
{
  "mcp": {
    "capabilities": ["tools", "resources"],
    "resources": [
      {"name": "example.dataset", "schema": "json"}
    ]
  }
}
```

### Adapter Plan

- Adapter added: see `core/mcp/adapter.py`
- `list_tools()` returns tools derived from manifests; each tool is `module_id:trigger`
- `call_tool(router, tool_name, text)` invokes the command through the router (permissions + audit preserved)
- Next: map permissions to MCP capabilities and add server/client glue


