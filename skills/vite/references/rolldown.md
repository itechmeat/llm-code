# Rolldown Integration

Actionable notes from the Rolldown integration guide.

## What Rolldown is

- Rust bundler designed as a Rollup drop-in replacement.
- Goals: speed, plugin compatibility, and advanced optimizations.

## Why Vite is migrating

- Unify dependency optimization and build under one bundler.
- Improve performance and capabilities (chunking, HMR, module federation).

## Trying `rolldown-vite`

- Alias `vite` to `rolldown-vite` in `package.json`.
- Pin versions; it’s experimental.
- Use package manager overrides when Vite is a peer dep.

## Known limitations

- Some Rollup options are unsupported; expect validation warnings.
- `manualChunks` is deprecated in favor of `advancedChunks`.

## Performance knobs

- Native plugins enabled by default (`experimental.enableNativePlugin`).
- `@vitejs/plugin-react` uses Oxc refresh transform for speed.
- Use `withFilter` wrapper to reduce hook overhead.

## Plugin author notes

- Detect `rolldown-vite` via `this.meta.rolldownVersion` or `vite.rolldownVersion`.
- If you use `transformWithEsbuild`, add `esbuild` as a dependency or switch to `transformWithOxc`.
- Set `moduleType: 'js'` when transforming non-JS content.
