# Using Plugins

Actionable notes from the plugins usage guide.

## Add plugins

- Install plugin in `devDependencies` and add it to `plugins` in `vite.config.*`.
- `plugins` can include presets (arrays) that are flattened.
- Falsy entries are ignored (useful for conditional toggles).

## Find plugins

- Check the Vite Features guide first; Vite may already cover your need.
- Official plugins: https://vite.dev/plugins/
- Community plugins: https://github.com/vitejs/awesome-vite#plugins
- Recommended conventions: `vite-plugin-*` or `rollup-plugin-*`.

## Order and conditions

- Use `enforce: 'pre' | 'post'` to set order relative to Vite core plugins.
- Use `apply: 'serve' | 'build'` to run only in dev or build.

## Practical takeaways

- Prefer Vite-native plugins for dev server integration.
- Only force ordering when a plugin requires it; avoid overusing `enforce`.
- Keep plugin logic environment-specific with `apply`.
