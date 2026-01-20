# Project Philosophy

Actionable notes from the Vite philosophy page.

## Design goals

- Keep core lean and extensible; push features into plugins whenever possible.
- Maintain a small API surface to improve long-term maintainability.
- Align plugin behavior with Rollup to share ecosystem value.

## Modern web stance

- Source is ESM-first; non-ESM deps must be pre-bundled.
- Encourage modern patterns (e.g., new Worker syntax).
- Node.js built-ins are not assumed to be available in the browser.

## Performance approach

- Dev server architecture prioritizes fast HMR at scale.
- Use native tools (esbuild, SWC) for heavy transforms; keep core in JS for flexibility.
- Builds rely on Rollup for bundle size and plugin ecosystem.

## Frameworks and integrations

- Vite is framework-agnostic but designed to enable framework tooling.
- JS API and SSR primitives support framework authors.
- Backend integrations exist (e.g., Ruby, Laravel) via dedicated plugins.

## Ecosystem health

- Releases are coordinated with framework/plugin maintainers.
- Ecosystem CI is used to spot regressions early.

## Practical takeaways

- Prefer a plugin when extending behavior instead of forking core.
- Plan for ESM-only source and pre-bundling constraints.
- For framework tooling, lean on JS API + plugin hooks rather than re-implementing pipeline pieces.
