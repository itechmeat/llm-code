# Security Advisories and Hardening

Pydantic AI ships security fixes in patch releases. Three advisories landed between `2.48.0` and `2.59.0`. Upgrade to `2.59.0` (or the matching `v1.107.9` line) and check the notes below before deploying an agent that fetches web content, uses MCP servers, or exposes a UI adapter.

## Advisories in the 2.49.0 -> 2.59.0 window

### GHSA-4whf-38hw-pxxh - local `web_fetch` HTML conversion (High, fixed in 2.59.0 / v1.107.9)

Converting attacker-controlled HTML with the local `web_fetch` tool could delay unrelated work running in the same process when the document contains many elements. The cost was paid by every other task in that process, not only the fetch that triggered it.

- **Affected:** any deployment that lets a model or a user fetch arbitrary URLs with the local `web_fetch` tool.
- **Fixed in:** `2.59.0`, `v1.107.9`.
- **Action:** upgrade. On older versions, isolate `web_fetch` in a separate process or apply an allowlist of fetchable hosts.

### GHSA-xv4x-g8mx-ch56 - MCP credentials in OpenTelemetry traces (Medium, fixed in 2.58.0 / v1.107.8)

With provider-native MCP configuration, server URLs, authorization tokens, and custom header values could appear in OpenTelemetry request traces even when `include_content=False`. URL-based MCP capabilities could additionally leak a credential embedded in a URL-derived identifier.

- **Affected:** agents configured with provider-native MCP servers and an OTel exporter.
- **Fixed in:** `2.58.0`, `v1.107.8`.
- **Action:** upgrade, and re-check any previously exported spans - traces already collected may contain tokens, so treat them as compromised and rotate the affected credentials.

### GHSA-5pfm-2g3g-gh85 - client-triggered tool execution through UI adapters (Medium, fixed in 2.58.0)

With a non-empty server-side `message_history` and `manage_system_prompt='server'` (the default), the Vercel AI and AG-UI adapters could execute an available tool with client-chosen arguments without a model request. Tools that require approval were not executed through that path, but tools without approval were.

- **Affected:** apps exposing a Vercel AI or AG-UI endpoint while keeping server-side message history.
- **Fixed in:** `2.58.0`.
- **Action:** upgrade. Until then, disable server-side `message_history` or mark every side-effecting tool as requiring approval.

### Moderate: deeply nested HTML in `web_fetch` (2.52.0)

Converting attacker-controlled, deeply nested HTML with the local `web_fetch` tool could consume excessive CPU and memory.

- **Fixed in:** `2.52.0` (the `2.59.0` fix covers the related many-elements case).
- **Action:** upgrade.

## Hardening checklist

- Keep `include_content=False` on OTel exporters, and treat `2.58.0`+ as the minimum for any agent with native MCP servers.
- Rotate MCP authorization tokens and any credential embedded in a URL once you upgrade from a version below `2.58.0`.
- Do not rely on server-side `message_history` as a security boundary in front of a Vercel AI or AG-UI endpoint.
- Require approval for every tool that writes, sends, or spends; approval-required tools are the only ones the adapters refuse to run client-triggered.
- Restrict `web_fetch` to known hosts, or run it in a separate process.
- Review `manage_system_prompt`: `'server'` keeps the system prompt server-side (safer for client-driven adapters), `'all'` sends it to the client.

## Upgrading

```bash
pip install -U "pydantic-ai>=2.59.0"   # or the v1.107.9+ line
```

After upgrading, re-run the agent's tool-permission tests: the fixes change which calls the adapters are allowed to make, so a tool list that was previously safe may now behave differently in the opposite direction (fewer implicit calls, not more).
