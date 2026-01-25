# Environment Instances

Actionable notes from the environment instances guide.

## Accessing environments

- Use `server.environments.client` / `server.environments.ssr` in dev.
- Plugins can access the current environment in hooks.

## DevEnvironment capabilities

- Each environment has its own `moduleGraph`, `pluginContainer`, and `hot` channel.
- `transformRequest(url)` resolves, loads, transforms, and updates the module graph.
- `warmupRequest(url)` queues low-priority processing to prevent waterfalls.

## Separate module graphs

- Each environment has an isolated graph with `EnvironmentModuleNode` entries.
- HMR runs independently per environment using its graph.
- Backward compatibility layer exists for the old mixed graph.

## Migration considerations

- Use environment-specific APIs instead of `server.moduleGraph` when possible.
