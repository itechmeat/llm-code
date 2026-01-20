# Environment API for Runtimes

Actionable notes from the runtimes guide.

## Environment factories

- Runtime providers create factory functions returning `EnvironmentOptions`.
- Factories define `dev.createEnvironment` and `build.createEnvironment` defaults.
- Users plug factories into `environments` config.

## Creating a dev environment

- Use `DevEnvironment` plus a `HotChannel` transport.
- Choose a communication level compatible with framework needs.

## Module Runner

- `ModuleRunner` executes transformed modules via `vite/module-runner`.
- Supports custom evaluators when runtime disallows `new AsyncFunction`.
- `import()` is the main API; `clearCache()` and `close()` manage lifecycle.

## Transport

- Implement `ModuleRunnerTransport` with `connect`/`send` (or `invoke`).
- Emit `vite:client:connect` / `vite:client:disconnect` with stable client references.
- For HMR support, transport must provide `send` + `connect`.

## Practical guidance

- Prefer the most flexible communication level for framework compatibility.
- Use `createServerHotChannel` for SSR HMR support.
