# Build Configuration

## Build Commands

Specify how your site is built.

### Exit Codes

- `0` — Success, proceed to deployment
- Non-zero — Build failure

### Framework Presets

| Framework               | Build Command                     | Output Directory         |
| ----------------------- | --------------------------------- | ------------------------ |
| React (Vite)            | `npm run build`                   | `dist`                   |
| Next.js                 | `npx @cloudflare/next-on-pages@1` | `.vercel/output/static`  |
| Next.js (Static Export) | `npx next build`                  | `out`                    |
| Nuxt.js                 | `npm run build`                   | `dist`                   |
| SvelteKit               | `npm run build`                   | `.svelte-kit/cloudflare` |
| Astro                   | `npm run build`                   | `dist`                   |
| Vue (Vite)              | `npm run build`                   | `dist`                   |
| Remix                   | `npm run build`                   | `build/client`           |
| Gatsby                  | `npx gatsby build`                | `public`                 |
| Hugo                    | `hugo`                            | `public`                 |
| Jekyll                  | `jekyll build`                    | `_site`                  |
| Eleventy                | `npx @11ty/eleventy`              | `_site`                  |
| Zola                    | `zola build`                      | `public`                 |

### No Build Required

Use `exit 0` if project doesn't need building:

```
Build command: exit 0
```

---

## Environment Variables

### System Variables (auto-injected)

| Variable              | Description         |
| --------------------- | ------------------- |
| `CI`                  | Always `true`       |
| `CF_PAGES`            | Always `1`          |
| `CF_PAGES_BRANCH`     | Current branch name |
| `CF_PAGES_COMMIT_SHA` | Git commit SHA      |
| `CF_PAGES_URL`        | Deployment URL      |

### Setting Variables

**Dashboard:**

Workers & Pages > Project > Settings > Environment variables

**Local Development:**

```bash
# .dev.vars (do not commit)
API_KEY=secret123
DATABASE_URL=postgres://...
```

### Branch-Conditional Builds

```bash
#!/bin/bash
if [ "$CF_PAGES_BRANCH" == "production" ]; then
  npm run build:prod
elif [ "$CF_PAGES_BRANCH" == "staging" ]; then
  npm run build:staging
else
  npm run build:dev
fi
```

---

## Build Caching

Speeds up subsequent builds by caching:

- Package manager caches (npm, yarn, pnpm)
- Framework caches (`.next/cache`, `node_modules/.astro`, `.cache`)

### Requirements

- V2 build system or later
- Enable in project settings

### Limits

- Cache retention: 7 days after last read
- Per-project limit: 10 GB

---

## Node.js Version

### Set via Environment Variable

```
NODE_VERSION = 20
```

or specific:

```
NODE_VERSION = 20.10.0
```

### Set via Version File

Create `.nvmrc` or `.node-version` in project root:

```
20
```

### Default Versions

| Build System | Default Node.js |
| ------------ | --------------- |
| v3           | 22.16.0         |
| v2           | 18.17.1         |
| v1           | 12.18.0         |

---

## Build Watch Paths

Control which file changes trigger builds.

### Configuration

| Field   | Purpose                                |
| ------- | -------------------------------------- |
| Include | Only build if matched files changed    |
| Exclude | Skip build if only these files changed |

### Evaluation Order

1. Check excludes
2. Check includes
3. If any match → trigger build

### Wildcards

```
# Match all in directory
project-a/*

# Match specific extensions
*.md
src/**/*.test.ts
```

### Bypass Conditions

Build watch paths bypassed when:

- Push has 0 file changes
- Push has 3000+ file changes
- Push has 20+ commits

---

## Monorepo Support

Multiple Pages projects from same repository.

### Requirements

- V2 build system or later
- Up to 5 Pages projects per repository

### Configuration

1. Set root directory for each project
2. Use build watch paths to trigger correct project
3. Configure separate environment variables per project

---

## Build System Migration

### V3 (Current)

- Ubuntu 22.04.2
- Node.js 22.16.0 default
- Latest tooling

### V2

- Ubuntu 22.04.2
- Node.js 18.17.1 default
- Monorepo support

### V1 (Deprecated)

- Ubuntu 20.04.5
- Node.js 12.18.0 default

### Skip Dependency Install

```
SKIP_DEPENDENCY_INSTALL = true
```

Then run custom install in build command.
