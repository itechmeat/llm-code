# Environment API (Introduction)

Actionable notes from the Environment API intro.

## What it is

- Vite 6 formalizes environments beyond `client` and `ssr`.
- Supports multiple runtimes (browser, node, edge) in dev and build.

## Config model

- Default SPA config still maps to `client` environment.
- Use `environments` to define extra environments (e.g., `server`, `edge`).
- Top-level options are defaults for `client` and other envs (unless marked non-inherit).

## Environment options

- `EnvironmentOptions` includes `define`, `resolve`, `optimizeDeps`, `dev`, `build`.
- `client` env is always present; `ssr` env is present in dev and optionally in build.

## Backward compatibility

- Existing Vite 5 APIs still work; module graph is mixed in dev.
- Environment API is RC; avoid full adoption for user apps unless needed.

## Who should use it

- End users: basic awareness.
- Plugin authors: see environment plugins guide.
- Frameworks/runtimes: use framework/runtime guides for integration.
