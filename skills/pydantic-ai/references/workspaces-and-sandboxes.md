# Workspaces and Sandboxes

`ctx.workspace` (`2.52.0`+) gives tools one API for files and commands, running either locally or inside a sandbox, with durable execution support. `Coder`, `Shell`, and `FileSystem` all run through it, so an agent that edits files and runs commands uses a single surface instead of two unrelated tool sets.

## The workspace interface

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-5',
    tools=[...],  # tools that take ctx.workspace
)

@agent.tool
async def edit_file(ctx: RunContext, path: str, content: str) -> str:
    await ctx.workspace.write_file(path, content)
    return f'wrote {path}'
```

A workspace provider decides where the work runs:

```python
from pydantic_ai import WorkspaceProvider  # provider protocol

agent = Agent('openai:gpt-5', workspace=MyWorkspaceProvider())
```

## Built-in providers

| Provider | Backend | Notes |
| --- | --- | --- |
| `SpritesSandbox` | Fly.io Sprite | `2.52.0` |
| `E2BSandbox` | E2B | `2.52.0` |
| `DaytonaSandbox` | Daytona | `2.59.0` |
| `SSHWorkspace` | any SSH-reachable host | `2.52.0` |
| `BubblewrapSandbox` | local bubblewrap | `2.52.0` |
| `ModalSandboxBackend` | Modal | `2.52.0` |

Notes:

- `ModalSandboxBackend` replaces `ModalSandboxSession`. `ModalSandbox` now runs against a Modal workspace.
- `BubblewrapSandbox` runs a local Linux sandbox with bubblewrap, useful when the host itself is trusted but the workload is not.
- `SSHWorkspace` treats any SSH-reachable machine as the sandbox boundary - point it at a throwaway host.

## Coder tools

`Coder` exposes file and command tools against `ctx.workspace`.

- File tools get a **retry budget of 5**, so transient sandbox errors do not abort a run.
- Scratch files are kept out of the project tree, so a failed agent run does not leave half-written sources behind.

## Durable execution

A workspace can survive a process restart: tool calls are recorded and replayed against the same workspace, so a resumed run sees the files and state it left behind. This is what makes `RunContext.in_durable_context` (`2.50.0`) meaningful - inside a durable run, `ctx.workspace` points at the same filesystem as the previous attempt.

## Choosing a provider

- **Local development:** no provider, or `BubblewrapSandbox` on Linux for a little isolation.
- **Untrusted code execution:** a managed sandbox (`SpritesSandbox`, `E2BSandbox`, `DaytonaSandbox`) - the agent's shell commands run on someone else's machine.
- **Your own infrastructure:** `SSHWorkspace` against a disposable container or VM.
- **Serverless GPU/CPU fleets:** `ModalSandboxBackend`.

## Gotchas

- A sandbox is a boundary for the *agent's* commands, not for the agent's network access - allowlist egress separately if that matters.
- Workspace state is durable by default; a retried agent run continues where it stopped instead of starting clean.
- Sandbox startup latency is part of the first tool call, not of agent construction.
