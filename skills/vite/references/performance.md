# Performance

Actionable notes from the performance guide.

## Browser and cache

- Disable extensions for dev profile; use incognito for faster reloads.
- Ensure “Disable Cache” is off in DevTools for Vite dev server.

## Plugin audit

- Avoid heavy work in `buildStart`, `config`, `configResolved`.
- Gate expensive transforms by extension/keyword checks.
- Use `vite --debug plugin-transform` or `vite-plugin-inspect` to spot slow hooks.

## Resolve costs

- Prefer explicit import extensions to reduce filesystem checks.
- Consider narrowing `resolve.extensions` if safe.
- In TS: `moduleResolution: "bundler"` and `allowImportingTsExtensions: true`.

## Avoid barrels

- Import specific files instead of `index` re-exports to reduce waterfall.

## Warmup

- Use `server.warmup.clientFiles` for frequently hit heavy files.
- `--open` or `server.open` will warm the entry automatically.

## Tooling tradeoffs

- Prefer native CSS and avoid unnecessary transforms.
- Use `@vitejs/plugin-react-swc` for faster React builds.
- Consider Rolldown/LightningCSS if aligned with your stack.
