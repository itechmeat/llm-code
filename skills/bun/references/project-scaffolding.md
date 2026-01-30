````markdown
# Project Scaffolding

Quick project setup with `bun init` and `bun create`.

## bun init

Create empty project:

```bash
bun init                    # Interactive
bun init -y                 # Accept defaults
```
````

**Creates:**

- `package.json`
- `tsconfig.json`
- `index.ts` (entry point)
- `.gitignore`
- `README.md`

**Common options:**

```bash
bun init my-app             # Create in ./my-app
bun init --open             # Open in editor
bun init --no-git           # Skip git init
```

---

## bun create

Create from template:

```bash
# From npm package
bun create <package> [destination]

# From GitHub
bun create <user>/<repo>
bun create github.com/<user>/<repo>

# Framework starters
bun create vite my-app
bun create next-app my-app
bun create elysia my-api
```

### Popular Templates

```bash
# Frontend
bun create vite my-app           # Vite
bun create next-app my-app       # Next.js
bun create react-app my-app      # React
bun create svelte my-app         # Svelte

# Backend
bun create elysia my-api         # Elysia
bun create hono my-api           # Hono
```

### GitHub Templates

```bash
bun create vercel/next.js my-next
bun create sveltejs/template my-svelte
```

### Custom npm Template

Package must export:

```javascript
// package.json
{
  "name": "create-my-template",
  "module": "index.ts"
}

// index.ts
export default {
  name: "my-template",
  // files to copy from package
};
```

---

## Post-Create

```bash
cd my-app
bun install                 # Install dependencies
bun run dev                 # Start dev server
```

---

## React Component (File-Based)

```bash
bunx --bun react my-component
```

Creates `MyComponent.tsx` with boilerplate.

---

## Key Points

- `bun init` — blank project, minimal setup
- `bun create` — from templates (npm, GitHub)
- Auto-detects and configures TypeScript
- All templates run `bun install` automatically
- Use `-y` to skip prompts

```

```
