# Why Vite

Actionable notes from the "Why Vite" page.

## Core problems Vite solves

- Bundler-based dev servers cold-start by eagerly building all modules.
- Large apps slow down incremental rebuilds; HMR can degrade with size.

## Vite dev server approach

- Split code into **dependencies** and **source**.
- Pre-bundle dependencies with esbuild for fast startup.
- Serve source over native ESM; transform on-demand as the browser requests modules.
- HMR invalidates only the minimal boundary chain, keeping updates fast.
- Uses caching headers to avoid unnecessary reloads.

## Why still bundle for production

- Unbundled ESM causes extra network round-trips in production.
- Bundling enables tree-shaking, code splitting, and better caching.
- Vite provides a pre-configured production build for parity and performance.

## Why not bundle with esbuild

- Vite relies on Rollup’s flexible plugin API for ecosystem compatibility.
- esbuild is faster but less flexible for Vite’s plugin model.
- Future direction: Rolldown aims to improve build performance while keeping flexibility.

## Practical takeaways

- Expect different goals in dev (speed) vs build (optimized output).
- Use dependency pre-bundling when you see slow cold starts or CJS interop issues.
- Plugin compatibility is a key reason Vite uses Rollup for builds.
