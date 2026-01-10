# CodeRabbit CLI usage

## Install

```bash
# Safer install pattern (avoid `curl | sh`):
# 1) Download the installer to a file
curl -fsSL https://cli.coderabbit.ai/install.sh -o coderabbit-install.sh

# 2) Verify integrity (get the expected SHA256 from the official release/artifacts)
shasum -a 256 coderabbit-install.sh

# 3) Run only after verification
sh coderabbit-install.sh
```

## Authenticate

```bash
coderabbit auth login
```

## Review commands

Common review modes:

```bash
# Interactive mode
coderabbit

# Plain text output
coderabbit --plain

# Prompt-only output (optimized for AI agents)
coderabbit --prompt-only

# Only uncommitted changes
coderabbit --prompt-only --type uncommitted

# Compare against a base branch
coderabbit --prompt-only --base develop
```

## Operational notes

- Reviews can take minutes depending on scope.
- If the CLI errors (rate limit/auth/network), stop and resolve the root cause before fixing anything.
