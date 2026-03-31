---
name: vite
description: "Vite next-gen frontend tooling: dev server, HMR, build, config, plugins, Environment API, Rolldown. Use when setting up or running a Vite project, configuring vite.config.*, authoring plugins, working with HMR or JS API, or managing environment variables and modes. Keywords: vite.config, bundler, Vite, HMR, Rolldown."
metadata:
  version: "8.0.3"
  release_date: "2026-03-26"
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

## Prohibitions

- Do not copy large verbatim chunks from vendor docs.
- Do not assume framework-specific behavior without verifying.

## Links

- [Documentation](https://vite.dev/)
- [Releases](https://github.com/vitejs/vite/releases)
- [GitHub](https://github.com/vitejs/vite)
- [npm](https://www.npmjs.com/package/vite)
