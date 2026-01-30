# bunfig.toml

Configuration file for Bun. Place in project root or globally at `~/.bunfig.toml`.

## Location Priority

1. `./bunfig.toml` (project)
2. `$HOME/.bunfig.toml` (global)
3. `$XDG_CONFIG_HOME/.bunfig.toml` (global)

Local overrides global; CLI flags override both.

## Runtime Settings

```toml
# Preload scripts (plugins, setup)
preload = ["./setup.ts"]

# JSX configuration
jsx = "react"
jsxFactory = "h"
jsxFragment = "Fragment"
jsxImportSource = "react"

# Reduce memory (slower)
smol = true

# Log level
logLevel = "debug"  # "debug" | "warn" | "error"

# Disable telemetry
telemetry = false

# Disable .env loading
env = false

# Console depth for object inspection
[console]
depth = 3
```

## Define (Replace Globals)

```toml
[define]
"process.env.API_URL" = "'https://api.example.com'"
```

## Custom Loaders

```toml
[loader]
".txt" = "text"
".csv" = "text"
".wasm" = "wasm"
```

Available: `jsx`, `js`, `ts`, `tsx`, `css`, `file`, `json`, `toml`, `wasm`, `napi`, `base64`, `dataurl`, `text`

## Test Runner

```toml
[test]
root = "./__tests__"
preload = ["./test-setup.ts"]
coverage = true
coverageThreshold = 0.9
coverageReporter = ["text", "lcov"]
coverageDir = "coverage"
randomize = true
rerunEach = 3
onlyFailures = true

[test.reporter]
dots = true
junit = "test-results.xml"
```

## Package Manager (bun install)

```toml
[install]
optional = true
dev = true
peer = true
production = false
exact = false
frozenLockfile = false
saveTextLockfile = true  # bun.lock vs bun.lockb
auto = "auto"  # "auto" | "force" | "disable" | "fallback"
linker = "isolated"  # "isolated" | "hoisted"

# Directories
globalDir = "~/.bun/install/global"
globalBinDir = "~/.bun/bin"

# Registry
registry = "https://registry.npmjs.org"
# Or with auth:
registry = { url = "https://registry.npmjs.org", token = "xxx" }

# Scoped registries
[install.scopes]
myorg = { url = "https://registry.myorg.com/", token = "$NPM_TOKEN" }

# Cache
[install.cache]
dir = "~/.bun/install/cache"
disable = false

# Lockfile
[install.lockfile]
save = true
print = "yarn"  # Generate yarn.lock alongside bun.lock
```

## bun run Settings

```toml
[run]
shell = "bun"   # "bun" | "system"
bun = true      # Auto-alias node to bun
silent = true   # Suppress command output
```

## Debug

```toml
[debug]
editor = "code"  # "code" | "subl" | "nvim" | "vim" | "emacs" | "idea"
```

## HTTP Server (Bun.serve)

```toml
[serve.static]
plugins = ["bun-plugin-tailwind"]
```
