# Deployment Methods

## Git Integration

Automatic deployments from GitHub or GitLab repositories.

### Setup

1. Go to Workers & Pages > Create application > Pages
2. Connect to Git (GitHub or GitLab)
3. Configure:
   - Project name
   - Production branch
   - Build command
   - Build output directory
   - Root directory (for monorepos)

### Features

- **Preview deployments** — Automatic for non-production branches
- **PR previews** — Preview URLs posted to pull requests
- **Build status checks** — GitHub/GitLab commit status updates
- **Skip builds** — Include `[skip ci]` or `[ci skip]` in commit message

### Branch Controls

| Setting           | Options                      |
| ----------------- | ---------------------------- |
| Production branch | Single branch (e.g., `main`) |
| Preview branches  | All / None / Custom pattern  |

### Custom Branch Pattern

```
# Include
feature/*
release-*

# Exclude
dependabot/*
```

### Key Limitation

> **Cannot switch from Git integration to Direct Upload** — create new project if needed.

---

## Direct Upload

Upload prebuilt assets without Git connection.

### Wrangler CLI

```bash
# Create project
npx wrangler pages project create my-project

# Deploy to production
npx wrangler pages deploy ./dist

# Deploy preview (branch)
npx wrangler pages deploy ./dist --branch=staging

# List projects
npx wrangler pages project list

# List deployments
npx wrangler pages deployment list
```

### Dashboard Upload

- Drag and drop in Cloudflare dashboard
- Limited to 1,000 files, 25 MiB per file

### Wrangler Limits

- 20,000 files per deployment
- 25 MiB per file

---

## C3 CLI (create-cloudflare)

Scaffold new projects with framework support:

```bash
npm create cloudflare@latest -- --platform=pages
```

Options:

- `--framework` — Specify framework (react, vue, svelte, etc.)
- `--ts` — Use TypeScript
- `--git` — Initialize Git repository

---

## Deployment Comparison

| Feature                 | Git Integration | Direct Upload        |
| ----------------------- | --------------- | -------------------- |
| Auto-deploy on push     | ✅              | ❌                   |
| Preview deployments     | ✅ Automatic    | ✅ Manual (--branch) |
| CI/CD integration       | Built-in        | External CI required |
| Monorepo support        | ✅ (V2 build)   | ✅                   |
| Max files               | Unlimited       | 20,000 (Wrangler)    |
| Convert between methods | ❌              | ❌                   |

---

## Preview Deployments

### URL Pattern

```
<branch>.<project>.pages.dev
```

Branch name normalization:

- Lowercase
- Non-alphanumeric → hyphen

Example: `feature/user-auth` → `feature-user-auth.my-project.pages.dev`

### Robots Tag

Preview deployments include `X-Robots-Tag: noindex` by default.

### Access Control

Restrict preview access with Cloudflare Access policies.

---

## Rollbacks

Instantly revert to previous deployment:

1. Go to project > Deployments
2. Find deployment to restore
3. Click "Rollback to this deployment"

> Rollback creates a new deployment, preserving history.
