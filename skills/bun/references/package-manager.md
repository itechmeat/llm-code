````markdown
# Package Manager

Bun's npm-compatible package manager (25x faster than npm).

## Core Commands

### Install All

```bash
bun install                    # Install all dependencies
bun install --production       # Skip devDependencies
bun install --frozen-lockfile  # CI mode (fail if lockfile mismatch)
bun ci                         # Same as --frozen-lockfile
```
````

### Add Package

```bash
bun add react                  # Regular dependency
bun add -d typescript          # Dev dependency
bun add --optional lodash      # Optional dependency
bun add --peer @types/react    # Peer dependency
bun add react@^18.0.0          # Specific version range
bun add react --exact          # Pin exact version
bun add -g cowsay              # Global install
```

### Git/URL Dependencies

```bash
bun add github:user/repo
bun add git+https://github.com/user/repo.git
bun add git+ssh://[email protected]:user/repo.git#tag
bun add https://example.com/package.tgz
```

### Remove Package

```bash
bun remove lodash
bun remove -g cowsay           # Global uninstall
```

### Update Packages

```bash
bun update                     # Update all (within semver range)
bun update react               # Update specific package
bun update --latest            # Update to latest (ignore semver)
bun update -i                  # Interactive mode
bun update -i -r               # Interactive across all workspaces
```

### Check Outdated

```bash
bun outdated                   # List outdated packages
bun outdated 'eslint*'         # Filter by pattern
bun outdated '!@types/*'       # Exclude pattern
bun outdated --filter=pkg-a    # Specific workspace
```

---

## Workspaces (Monorepo)

### Setup

```json
// package.json (root)
{
  "workspaces": ["packages/*"],
  "devDependencies": {
    "shared": "workspace:*"
  }
}
```

### Workspace Protocol

```json
{
  "dependencies": {
    "pkg-a": "workspace:*", // Any version
    "pkg-b": "workspace:^", // ^version
    "pkg-c": "workspace:~" // ~version
  }
}
```

### Install Specific Workspaces

```bash
bun install --filter 'pkg-*'         # Match pattern
bun install --filter '!pkg-c'        # Exclude
bun install --filter './packages/a'  # By path
```

### Catalogs (Shared Versions)

```json
{
  "workspaces": {
    "packages": ["packages/*"],
    "catalog": {
      "react": "^18.0.0",
      "typescript": "^5.0.0"
    }
  }
}
```

Usage in workspace:

```json
{
  "dependencies": {
    "react": "catalog:"
  }
}
```

---

## Publishing

### Publish Package

```bash
bun publish                    # Publish to npm
bun publish --tag beta         # With tag
bun publish --access public    # Public scoped package
bun publish --dry-run          # Preview without publishing
bun publish --otp 123456       # With 2FA code
```

### Pack Tarball

```bash
bun pm pack                    # Create .tgz
bun pm pack --dry-run          # Show what would be included
bun pm pack --destination ./dist
```

### publishConfig (package.json)

```json
{
  "publishConfig": {
    "access": "public",
    "tag": "next",
    "registry": "https://registry.npmjs.org"
  }
}
```

---

## Patching Dependencies

```bash
# 1. Prepare for patching
bun patch lodash

# 2. Edit node_modules/lodash/...

# 3. Commit patch
bun patch --commit lodash
# Creates patches/lodash@4.17.21.patch
```

Patches stored in `patches/` directory, tracked in `package.json`:

```json
{
  "patchedDependencies": {
    "[email protected]": "patches/lodash@4.17.21.patch"
  }
}
```

---

## Overrides & Resolutions

Force specific metadependency versions:

```json
{
  "overrides": {
    "bar": "~4.4.0"
  },
  "resolutions": {
    "lodash": "4.17.21"
  }
}
```

---

## Link (Local Development)

```bash
# In package directory
cd ~/my-lib && bun link

# In consuming project
bun link my-lib

# Unlink
bun unlink my-lib
```

Creates `link:` specifier:

```json
{
  "dependencies": {
    "my-lib": "link:my-lib"
  }
}
```

---

## Utility Commands

```bash
bun pm ls                      # List installed packages
bun pm ls --all                # Include transitive deps
bun pm bin                     # Print local bin path
bun pm bin -g                  # Print global bin path
bun pm cache                   # Print cache path
bun pm cache rm                # Clear cache
bun pm hash                    # Hash current lockfile
```

---

## CI/CD Configuration

### GitHub Actions

```yaml
- uses: oven-sh/setup-bun@v2
- run: bun ci # Use frozen lockfile
```

### Trusted Dependencies

```json
{
  "trustedDependencies": ["esbuild", "sharp"]
}
```

```bash
bun add sharp --trust          # Add to trustedDependencies
```

### Supply Chain Protection

```bash
bun add pkg --minimum-release-age 259200  # 3 days
```

```toml
# bunfig.toml
[install]
minimumReleaseAge = 259200
minimumReleaseAgeExcludes = ["typescript"]
```

---

## Installation Strategies

```bash
bun install --linker hoisted   # npm-style (default for single)
bun install --linker isolated  # pnpm-style (default for workspaces)
```

| Strategy   | Description                           |
| ---------- | ------------------------------------- |
| `hoisted`  | Traditional flat node_modules         |
| `isolated` | Strict deps, prevents phantom imports |

---

## Configuration

### bunfig.toml

```toml
[install]
optional = true
dev = true
peer = true
production = false
frozenLockfile = false
linker = "hoisted"
registry = "https://registry.npmjs.org"

[install.scopes]
"@myorg" = { token = "$NPM_TOKEN", url = "https://npm.myorg.com/" }
```

### Environment Variables

| Variable                        | Description               |
| ------------------------------- | ------------------------- |
| `BUN_CONFIG_REGISTRY`           | Default registry URL      |
| `NPM_CONFIG_TOKEN`              | Auth token for publishing |
| `BUN_CONFIG_YARN_LOCKFILE`      | Generate yarn.lock        |
| `BUN_CONFIG_SKIP_SAVE_LOCKFILE` | Don't save lockfile       |

---

## Key Flags Reference

| Flag                  | Description                   |
| --------------------- | ----------------------------- |
| `--production` / `-p` | Skip devDependencies          |
| `--frozen-lockfile`   | Fail if lockfile needs update |
| `--dry-run`           | Preview without changes       |
| `--force` / `-f`      | Re-fetch all from registry    |
| `--exact` / `-E`      | Pin exact version             |
| `--global` / `-g`     | Global install                |
| `--dev` / `-d` / `-D` | Add to devDependencies        |
| `--omit dev`          | Exclude dev deps              |
| `--filter <pattern>`  | Target specific workspaces    |
| `--verbose`           | Debug logging                 |
| `--silent`            | No output                     |

```

```
