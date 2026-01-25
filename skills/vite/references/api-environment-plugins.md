# Environment API for Plugins

Actionable notes from the environment plugins guide.

## Current environment access

- Use `this.environment` in hooks instead of `ssr` boolean.
- Use `environment.config` and `environment.moduleGraph` for scoped behavior.

## Configuring environments

- Add environments in `config` hook via `environments`.
- Use `configEnvironment(name, options)` to customize each environment.

## HMR per environment

- Use `hotUpdate` hook; it runs per environment.
- Use `this.environment.hot.send` for custom events.

## Per-environment state

- Use `Map<Environment, State>` keyed by `this.environment`.
- Enable `perEnvironmentStartEndDuringDev` / `perEnvironmentWatchChangeDuringDev` when needed.

## Per-environment plugins

- `applyToEnvironment(environment)` filters or replaces plugin per env.
- Use `perEnvironmentPlugin()` helper to generate per-env plugin instances.

## App-plugin communication

- `environment.hot` supports server↔client messages for that environment.
- `vite:client:connect` / `vite:client:disconnect` signal app instances.

## Shared plugins during build

- `builder.sharedConfigBuild: true` enables shared config/pipeline.
- Plugins can opt-in with `sharedDuringBuild: true`.
