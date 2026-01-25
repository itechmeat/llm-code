# Environment API for Frameworks

Actionable notes from the frameworks guide.

## Dev environment communication levels

- `RunnableDevEnvironment`: runs modules via `runner.import()` in same runtime.
- `FetchableDevEnvironment`: runtime communicates via Fetch API; preferred for portability.
- Raw `DevEnvironment`: requires custom communication (virtual modules or hot messages).

## SSR middleware pattern

- Use middleware mode + `transformIndexHtml`.
- Use `runner.import('/src/entry-server.js')` for SSR rendering in dev.
- Add `import.meta.hot.accept()` in server entry to avoid full invalidation.

## Build across environments

- `vite build` still builds client-only by default for compatibility.
- Use `builder` / `vite build --app` to build all environments.
- Frameworks can override `builder.buildApp` for parallel builds.

## Environment-agnostic code

- Prefer `this.environment` in plugin hooks over `server.environments`.
