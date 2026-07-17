---
name: vite
description: "Vite next-gen frontend tooling: dev server, HMR, build, config, plugins, Environment API, Rolldown. Use when setting up or running a Vite project, configuring vite.config.*, authoring plugins, working with HMR or JS API, or managing environment variables and modes. Keywords: vite.config, bundler, Vite, HMR, Rolldown."
metadata:
  version: "8.1.5"
  release_date: "2026-07-16"
---

# Vite

## Quick navigation

- Getting started: references/getting-started.md
- Philosophy and rationale: references/philosophy.md, references/why-vite.md
- Features: references/features.md
- CLI: references/cli.md
- Plugins (usage): references/using-plugins.md
- Plugin API: references/api-plugin.md
- HMR API: references/api-hmr.md
- JavaScript API: references/api-javascript.md
- Config reference: references/config.md
- Dependency optimization: references/dep-pre-bundling.md
- Assets: references/assets.md
- Build: references/build.md
- Static deploy: references/static-deploy.md
- Env & modes: references/env-and-mode.md
- SSR: references/ssr.md
- Backend integration: references/backend-integration.md
- Troubleshooting: references/troubleshooting.md
- Performance: references/performance.md
- Rolldown: references/rolldown.md
- Migration: references/migration.md
- Breaking changes: references/breaking-changes.md
- Environment API: references/api-environment.md
- Environment instances: references/api-environment-instances.md
- Env plugins: references/api-environment-plugins.md
- Env frameworks: references/api-environment-frameworks.md
- Env runtimes: references/api-environment-runtimes.md

## Core rules

- Prefer minimal configuration; extend only as needed.
- Keep `index.html` as a first-class entry point when using Vite defaults.
- Treat dev server settings and build settings separately.
- Document mode-dependent behavior for env variables and `define`.
- Use `future` config to opt-in to deprecation warnings before migration.

## Recipes

- Scaffold a project with `npm create vite@latest`.
- Configure aliases, server options, and build outputs in `vite.config.*`.
- Load `.env` values into config with `loadEnv` when config needs them.
- Add plugins with `plugins: []` and define `apply` or `enforce` when needed.
- Use HMR APIs for fine-grained updates when plugin or framework needs it.
- Use `optimizeDeps.include/exclude` when deps aren't discovered on startup.
- Use `build.rollupOptions.input` for multi-page apps.
- Enable deprecation warnings: `future: { removeSsrLoadModule: 'warn' }`.
- Use `hotUpdate` hook instead of `handleHotUpdate` for environment-aware HMR.
- Use `this.environment` instead of `options.ssr` in plugin hooks.

## Release Highlights (8.0.0)

- Default browser target is raised again under `baseline-widely-available`.
- CommonJS default-import interop becomes more consistent and may expose packages that relied on older ambiguous behavior.
- Vite stops resolving `browser` vs `module` via format sniffing and follows configured `resolve.mainFields` more strictly.
- JS API `build()` now throws `BundleError` with nested `.errors` when multiple Rolldown-level errors are present.
- Rolldown transition becomes more explicit: `build.rollupOptions` / `worker.rollupOptions` are deprecated in favor of `*.rolldownOptions`.

## Release Highlights (8.1.0 -> 8.1.5)

- **WASM ESM integration**: direct `.wasm` imports work as ES modules natively.
- **Zero-config build caching**: integration with Vite Task enables build caching without manual setup.
- **`server.hmr` renamed to `server.ws`**: WebSocket options move under `server.ws`; update configs that set HMR transport options.
- **New options**: `html.additionalAssetSources` for custom asset sources during HTML transform, `import.meta.glob` `caseSensitive`, multiple hosts via `__VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS`, and an extended default `server.fs.deny` list.
- **8.1.1 -> 8.1.5**: stability only (stack-trace handling, dependency bumps, module-resolution edge cases).

## Patch Notes (8.0.14 -> 8.0.16)

- Rolldown moves to `1.0.3` (was `1.0.2` in `8.0.14`); if you maintain plugin or build guidance, validate it against the current Rolldown behavior instead of assuming early `8.0.x` patch semantics.
- Dev server now sends HTTP `408` on request timeout instead of hanging the connection (`8.0.15`).
- `launch-editor-middleware` rejects UNC paths and Windows alternate paths, closing a local path-traversal vector (`8.0.16`); relevant if you expose the dev server beyond localhost.
- `8.0.15` fixes: `/@fs/` HTML-proxy cache-key mismatch, relative-glob-in-virtual-module errors when no files match, closing the Rolldown bundle when `write()` rejects, and `onWarn` for `viteResolvePlugin` in JS plugin containers.
- `transformIndexHtml` handles trailing-slash paths more reliably, which matters for plugins and static deploy setups that rewrite or inject HTML on directory-style URLs.
- Dependency scanning now passes Oxc JSX options through the optimizer path, so JSX-heavy linked dependencies should behave closer to the main transform pipeline.

## Prohibitions

- Do not copy large verbatim chunks from vendor docs.
- Do not assume framework-specific behavior without verifying.

## Links

- [Documentation](https://vite.dev/)
- [Releases](https://github.com/vitejs/vite/releases)
- [GitHub](https://github.com/vitejs/vite)
- [npm](https://www.npmjs.com/package/vite)
