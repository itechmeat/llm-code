# Env Variables and Modes

Actionable notes from the env and modes guide.

## Built-in constants

- `import.meta.env.MODE`, `BASE_URL`, `PROD`, `DEV`, `SSR` are always available.

## .env files and loading order

- Loads `.env`, `.env.local`, `.env.[mode]`, `.env.[mode].local`.
- Mode-specific files override generic ones.
- Existing process env values override file values.
- Restart dev server after editing `.env` files.

## Exposure rules

- Only `VITE_*` variables are exposed to client code.
- Values are strings; parse booleans/numbers yourself.
- Use `envPrefix` to change the prefix.
- Do not store secrets in client-exposed vars.

## TypeScript IntelliSense

- Augment `ImportMetaEnv` in `vite-env.d.ts`.
- Do not add `import` statements in the d.ts file, or augmentation breaks.

## HTML replacements

- Use `%CONST_NAME%` in HTML to replace with `import.meta.env` values.
- Missing constants are ignored in HTML (not replaced).

## Modes vs NODE_ENV

- Modes (`--mode`) are distinct from `NODE_ENV`.
- `vite build` defaults to mode `production`.
- You can set `NODE_ENV` via command or `.env.[mode]` to influence behavior.
