# Windows / WSL notes (manual)

CodeRabbit CLI may be more practical to run inside WSL on Windows.

## Install WSL + Ubuntu

```powershell
wsl --install -d Ubuntu
```

## Install CodeRabbit CLI in WSL

```powershell
wsl -d Ubuntu -e bash -c "curl -fsSL https://cli.coderabbit.ai/install.sh | sh"
```

## Authenticate

```powershell
wsl -d Ubuntu -e bash -c "~/.local/bin/coderabbit auth login"
```

## Line endings issue (CRLF vs LF)

When accessing Windows files via `/mnt/...`, tools can detect massive line-ending changes.
A common workaround is to copy the repo into a native WSL folder and run CodeRabbit there.

Important: any commands that reset working tree state (e.g., `git checkout .`) must be run intentionally by a human and only on a disposable copy.

## Troubleshooting

- "command not found": use `~/.local/bin/coderabbit` or add `$HOME/.local/bin` to `PATH`.
- Slow performance on `/mnt/...`: prefer working inside WSL home (e.g. `~/projects`).
