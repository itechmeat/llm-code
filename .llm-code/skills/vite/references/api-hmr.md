# HMR API

Actionable notes from the HMR API guide.

## Required guard

- Always wrap usage with `if (import.meta.hot) { ... }`.

## Accept updates

- `hot.accept(cb)` to self-accept; callback receives updated module.
- `hot.accept(deps, cb)` to accept updates from specific dependencies.
- Keep exports mutable (`let`) if re-exporting from HMR boundaries.

## Lifecycle helpers

- `hot.dispose(cb)` for cleanup before replacing module.
- `hot.prune(cb)` when module is removed entirely.
- `hot.data` persists between updates; mutate properties only.
- `hot.invalidate()` to force upstream reload; call `accept` first.

## Events

- `hot.on` / `hot.off` for Vite events and custom plugin events.
- `hot.send` sends payloads to the dev server.

## TypeScript

- Add `vite/client` types for IntelliSense.
