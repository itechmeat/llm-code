# Installation

## npm (Recommended)

```bash
npm install -g agent-browser
agent-browser install  # Download Chromium
```

## Linux Dependencies

```bash
agent-browser install --with-deps
# Or: npx playwright install-deps chromium
```

## Custom Browser

Use existing browser instead of bundled Chromium:

```bash
# Via flag
agent-browser --executable-path /path/to/chromium open example.com

# Via environment variable
AGENT_BROWSER_EXECUTABLE_PATH=/path/to/chromium agent-browser open example.com
```

## From Source

```bash
git clone https://github.com/vercel-labs/agent-browser
cd agent-browser
pnpm install && pnpm build && pnpm build:native
./bin/agent-browser install
pnpm link --global
```

## Platforms

Native Rust binaries: macOS (ARM64, x64), Linux (ARM64, x64), Windows (x64)
