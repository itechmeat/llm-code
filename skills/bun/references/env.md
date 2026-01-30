# Bun Environment Variables

Automatic `.env` file support with multiple access methods.

## Automatic Loading

Files loaded in order of precedence:

1. `.env`
2. `.env.production`, `.env.development`, `.env.test` (based on `NODE_ENV`)
3. `.env.local`

## Reading Variables

```ts
// All equivalent
process.env.API_TOKEN;
Bun.env.API_TOKEN;
import.meta.env.API_TOKEN;
```

## Setting Variables

### In .env File

```bash
FOO=hello
BAR=world

# Quotes supported
SINGLE='value'
DOUBLE="value"
BACKTICK=`value`
```

### Command Line

```bash
FOO=hello bun run dev
```

### Cross-Platform (Windows)

```bash
bun exec 'FOO=hello bun run dev'
```

### package.json Scripts

```json
{
  "scripts": {
    "dev": "NODE_ENV=development bun --watch app.ts"
  }
}
```

### Programmatic

```ts
process.env.FOO = "hello";
```

## Variable Expansion

```bash
DB_USER=postgres
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432
DB_URL=postgres://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/mydb
```

Escape to disable expansion:

```bash
BAR=hello\$FOO  # Literal "$FOO"
```

## Manual .env Files

```bash
bun --env-file=.env.custom src/index.ts
bun --env-file=.env.1 --env-file=.env.2 run build
```

## Disable .env Loading

```bash
bun --no-env-file index.ts
```

Or in `bunfig.toml`:

```toml
env = false
```

## TypeScript Typing

Default type: `string | undefined`

For autocompletion:

```ts
declare module "bun" {
  interface Env {
    API_TOKEN: string;
    DATABASE_URL: string;
  }
}
```

## Debug Variables

```bash
bun --print process.env
```

## Bun-Specific Variables

| Variable                                      | Description                           |
| --------------------------------------------- | ------------------------------------- |
| `NODE_ENV`                                    | `development`, `production`, `test`   |
| `NO_COLOR=1`                                  | Disable ANSI colors                   |
| `FORCE_COLOR=1`                               | Force ANSI colors                     |
| `NODE_TLS_REJECT_UNAUTHORIZED=0`              | Disable SSL validation                |
| `BUN_CONFIG_VERBOSE_FETCH=curl`               | Log fetch requests                    |
| `BUN_CONFIG_MAX_HTTP_REQUESTS`                | Max concurrent fetches (default: 256) |
| `BUN_CONFIG_NO_CLEAR_TERMINAL_ON_RELOAD=true` | Don't clear on watch reload           |
| `DO_NOT_TRACK=1`                              | Disable crash reports/telemetry       |
| `BUN_OPTIONS`                                 | Prepend CLI args (e.g., `--hot`)      |
| `TMPDIR`                                      | Temp directory for bundling           |
| `BUN_RUNTIME_TRANSPILER_CACHE_PATH`           | Transpiler cache location             |

## Transpiler Cache

Files >50KB are cached. Disable:

```bash
BUN_RUNTIME_TRANSPILER_CACHE_PATH=0 bun run dev
```

## No dotenv Required

Bun handles `.env` natively — no need for `dotenv` or `dotenv-expand`.

## Practical Patterns

### Environment-Specific Config

```ts
// .env
DATABASE_URL=postgres://localhost/myapp

// .env.production
DATABASE_URL=postgres://prod-server/myapp

// .env.local (gitignored, overrides all)
DATABASE_URL=postgres://my-local/myapp
```

### Type-Safe Config

```ts
// env.ts
declare module "bun" {
  interface Env {
    DATABASE_URL: string;
    API_SECRET: string;
    PORT: string;
  }
}

export const config = {
  databaseUrl: Bun.env.DATABASE_URL,
  apiSecret: Bun.env.API_SECRET,
  port: parseInt(Bun.env.PORT || "3000"),
};
```

### Validation

```ts
const required = ["DATABASE_URL", "API_SECRET"];

for (const key of required) {
  if (!Bun.env[key]) {
    throw new Error(`Missing required env var: ${key}`);
  }
}
```
