# Getting Started (Guide)

Actionable notes from the Vite guide start page.

## What Vite is

- Vite provides a fast dev server with enhanced native ES module support and a production build that uses Rollup.
- The dev server focuses on fast iteration (HMR and native ESM). The build targets optimized static assets.

## First run / scaffolding

- Recommended scaffolding command: `npm create vite@latest`.
- Online playground: `https://vite.new/` supports framework templates (vanilla, vue, react, preact, lit, svelte, solid, qwik and TS variants).

## Project structure basics

- `index.html` is the application entry and is treated as source.
- Absolute URLs resolve from the project root (`<root>`).
- You can set a different root with `vite serve <path>`; config is resolved inside the root.
- Multi-page apps are supported with multiple HTML entry points.

## CLI basics

- Common scripts: `vite` (dev), `vite build`, `vite preview`.
- Extra flags like `--port` and `--open` are available; `npx vite --help` lists all options.

## Browser targets

- Dev uses modern browser assumptions and `esnext` transform target.
- Production targets a baseline of widely-available browsers; can be lowered in config.

## Using unreleased Vite

- You can install a specific commit via `https://pkg.pr.new/vite@<SHA>`.
- To use a local checkout, link `packages/vite` after building.

## Cross-links (next steps)

- Features, Plugins, Config, Build, and HMR are covered in their dedicated pages.
