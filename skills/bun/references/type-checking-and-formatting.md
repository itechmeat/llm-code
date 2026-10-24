# Type Checking & Formatting

Bun ships a TypeScript type checker (`bun check`, since 1.4.3) and a Prettier-compatible formatter (`bun fmt`, since 1.4.4). Neither needs an extra dependency.

## bun check

### Usage

```bash
bun check                    # Check the project of the nearest tsconfig.json
bun check src/index.ts       # Check specific files and everything they import
bun check -p packages/server # Check another project (a tsconfig.json or its directory)
bun check -b                 # Follow "references" like tsc -b
bun check --no-pretty        # One line per error (tsc --pretty false)
bun check --pretty           # Show source around each error (default in a terminal)
bun check --all              # Show every error instead of grouping repeats
bun check --threads 4        # Limit threads (default: one per CPU core)
bun check --timing           # Print how long loading and checking took
bun check --no-script        # Force the type checker even if package.json has a "check" script
bun check --strict           # Any compiler option works as a flag and overrides tsconfig.json
bun check --target es2022
```

### Exit behavior

- Exit code `1` when a type error is found, `0` when there is none. It never writes files.
- Errors go to stdout, the summary line to stderr.
- When stdout is not a terminal, output is one line per error in `tsc --pretty false` format, so existing problem matchers keep working.
- If there is nothing to check, the run exits `1` — an empty run fails instead of silently passing.
- No `.tsbuildinfo` is written. Every run checks the whole project.

```txt
src/index.ts(3,25): error TS2322: Type 'string' is not assignable to type 'number'.
Found 1 error in 1 file, checked 2 files [14.00ms]
```

### Replace tsc

| Instead of                           | Run                            |
| ------------------------------------ | ------------------------------ |
| `tsc --noEmit`                       | `bun check`                    |
| `tsc --noEmit -p packages/server`    | `bun check -p packages/server` |
| `tsc -b`                             | `bun check -b`                 |
| `tsc --noEmit && bun src/index.ts`   | `bun --check src/index.ts`     |
| `tsc --noEmit && bun test`           | `bun test --check`             |
| `tsc --noEmit && bun build ./app.ts` | `bun build --check ./app.ts`   |

Keep `tsc` when you need to emit `.d.ts` files or JavaScript — `bun check` only checks.

### Check before you run, build, or test

`--check` type checks first. On a type error Bun prints the error, exits `1`, and does nothing else.

```bash
bun --check src/index.ts             # Check, then run
bun run --check dev                  # Check, then run a package.json script
bun test --check                     # Check the test files and everything they import
bun build --check ./src/index.ts --outdir out
```

`bun build --check` checks after the bundler has read every file and before anything is written, so each file is read from disk once. A type error fails the build like any other build error and no output is produced.

The JavaScript API equivalent is `Bun.build({ check: true })`. Each type error arrives as a `BuildMessage` whose message starts with the TypeScript error code.

```ts
const result = await Bun.build({
  entrypoints: ["./src/index.ts"],
  outdir: "./out",
  check: true,
  throw: false,
});

for (const log of result.logs) {
  console.error(`${log.position?.file}:${log.position?.line}: ${log.message}`);
}
```

`--check` follows static imports only. A worker (`new Worker("./worker.ts")`), a computed `import(name)`, a `require()` inside a TypeScript file, a spawned process, and `--preload` files are not covered by `--check`; `bun check` covers them when `tsconfig.json` includes them.

With `--watch`, Bun checks again before every restart. With `--hot --check`, the same happens on reload.

### Errors match tsc

- Same file, line, column, and error code as `tsc` from TypeScript 7.0.2.
- Passes 100% of the TypeScript 7.0.2 conformance test suite.
- Verified against 72 deliberately misconfigured popular open-source repositories.
- 3x–6.4x faster than `tsc` 7.0.2 and 2.2x–4.9x less memory on VS Code, mikro-orm, Next.js, Storybook, Nuxt, Playwright, and lit.

### When to keep tsc

- You need to emit `.d.ts` files or JavaScript.
- You rely on language-service plugins — the `plugins` compiler option is ignored by `bun check`.
- You use Yarn Plug'n'Play. Bun finds packages in `node_modules`; set `nodeLinker: node-modules` in `.yarnrc.yml`.
- Your editor and CI must agree. `bun check` matches one exact TypeScript version, reported by `process.versions.typescript`:

```bash
bun add -d typescript@$(bun -p process.versions.typescript)
```

Then point the editor at the workspace copy of TypeScript.

### TypeScript 5 to 7 defaults

`bun check` behaves like TypeScript 7, whichever version of `typescript` is installed.

| Default                         | Effect                                                          |
| ------------------------------- | --------------------------------------------------------------- |
| `strict` is on                  | New errors such as `TS7006: Parameter 'x' implicitly has an 'any' type` |
| `types` is empty                | `Cannot find name 'process'`, `'describe'`, `'Bun'`             |
| Side-effect imports are checked | `TS2882` on `import "./index.css"`                              |

Removed options stop the check with an error before any file is checked: `baseUrl`, `moduleResolution: node|node10|classic`, `target: es5`, `module: amd|umd|system`, `downlevelIteration`, `outFile`, `esModuleInterop: false`, `alwaysStrict: false`. Use `moduleResolution: "bundler"` (or `"nodenext"`), `target: "es2015"` or later, and start every `paths` entry with `./` instead of `baseUrl`.

### Project selection and monorepos

- Without arguments, Bun looks for `tsconfig.json` in the current directory, then in each parent directory, and checks the files that `files`, `include`, and `exclude` select.
- `-p <path>` takes a `tsconfig.json` or the directory containing one.
- `-b` follows `references` like `tsc -b`, checking each project with its own options, in build order.
- A `tsconfig.json` with nothing but `references` (the shape `create vite` writes) is followed, and Bun says so in a note.
- If no `tsconfig.json` exists in the current directory or above it, but some exist below it, Bun lists them and stops instead of guessing.
- Without a `tsconfig.json`, Bun uses the defaults that `bun init` writes, and includes `@types/bun` when it is installed.

```bash
bun check -p packages/web      # One package
bun check -b                   # Every referenced project
bun check .                    # Every TypeScript file below the current directory
bun --filter '*' typecheck     # The typecheck script of every workspace package
```

### package.json "check" script

A `check` script in `package.json` wins: `bun check` runs it like `bun run check` and passes it your flags.

```bash
bun check             # Runs "biome check" if package.json defines that script
bun check --no-script # Always the type checker
bun check --no-script -b
bun --check           # The type checker too
```

Inside a `check` script, `bun check` is the type checker, so `"check": "bun check"` works. Use `bun check --no-script` in tools that run in projects you do not control.

### CI

```yaml .github/workflows/typecheck.yml
name: Type check
on: [push, pull_request]
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install --frozen-lockfile
      - run: bun check
```

In GitHub Actions, `bun check` also prints a workflow command per error, so GitHub shows them as annotations on the pull request diff. No problem matcher is needed.

For a pre-commit hook, run `bun check` from `.git/hooks/pre-commit`. Checking only staged files misses errors in files that import them, so still run the full check in CI.

## bun fmt

### Usage

```bash
bun fmt                     # Format the current directory
bun fmt src "test/**/*.ts"  # Format specific paths and globs
bun fmt --check             # List files that need formatting, write nothing
bun fmt --staged            # Format staged files and stage them again
bun fmt --changed           # Format files that differ from the default branch
bun fmt --changed=origin/dev
bun fmt --init              # Create the [fmt] section in bunfig.toml
bun fmt --doctor            # Show how Bun reads your config and what you can uninstall
bun fmt --stdin-filepath src/index.ts < src/index.ts
bun fmt --parser typescript < in.ts
```

Exit codes: `1` if a file needs formatting, `0` if none does, `2` if something went wrong, such as a syntax error or an unsupported Prettier plugin. `--check` is therefore the CI command.

```yaml .github/workflows/format.yml
steps:
  - uses: actions/checkout@v4
  - uses: oven-sh/setup-bun@v2
  - run: bun fmt --check
```

### Supported languages

JavaScript, TypeScript, JSX, Flow, CSS, SCSS, Less, HTML, Vue, Svelte, Angular, Lightning Web Components, MJML, JSON, JSONC, JSON5, YAML, TOML, Markdown, MDX, GraphQL, and Handlebars.

Embedded code is formatted too: `<script>` and `<style>` blocks in HTML, Vue, and Svelte, code blocks in Markdown, and `css\`...\``, `html\`...\``, and `graphql\`...\`` templates in JavaScript. A syntax error inside a `<script>` or `<style>` of a Svelte component is a warning: that block is left as written and the rest of the file is formatted.

Output matches Prettier. The JavaScript/TypeScript printer is a port of `oxc_formatter`, itself a port of Biome's formatter.

### Flags

| Flag                        | Effect                                                       |
| --------------------------- | ------------------------------------------------------------ |
| `-c`, `--check`             | Write nothing; exit `1` if a file needs formatting           |
| `-l`, `--list-different`    | Like `--check`, but print only file names                     |
| `--stdin-filepath <path>`   | Format standard input as that file and print the result      |
| `--parser <name>`           | Format standard input with that parser                       |
| `--init`                    | Add a `[fmt]` section to `bunfig.toml`                        |
| `--doctor`                  | Show how Bun interprets the config and which packages to remove |
| `--no-script`               | Run the formatter even if the project has an `fmt` script    |
| `--staged`                  | Format staged files and stage them again                     |
| `--changed[=<ref>]`         | Format files that differ from a Git ref (default: default branch) |
| `--ignore-pattern <glob>`   | Skip files matching a glob; repeatable                        |
| `--print-width <n>`         | Wrap lines at this column (default `80`)                     |
| `--tab-width <n>`           | Spaces per indentation level (default `2`)                    |
| `--use-tabs`                | Indent with tabs                                              |
| `--no-semi`                 | Only print semicolons where needed                            |
| `--single-quote`            | Use single quotes                                             |
| `--trailing-comma <mode>`   | `all`, `es5`, or `none`                                       |
| `--sort-imports`            | Sort and group imports                                        |
| `--sort-tailwindcss`        | Sort Tailwind CSS classes                                     |
| `--sort-package-json`       | Sort the keys of `package.json`                               |
| `--jsdoc`                   | Format JSDoc comments                                         |
| `--svelte` / `--no-svelte`  | Format Svelte components (on by default without a Prettier or oxfmt config) |
| `--no-editorconfig`         | Do not read `.editorconfig`                                   |
| `--threads <n>`             | Number of threads (default: one per CPU core)                 |
| `--log-level <level>`       | `silent`, `error`, `warn`, `log`, or `debug`                  |

`bun fmt` also accepts the flags of Prettier and oxfmt. Run `bun fmt --help --all` to see them.

### Config discovery

Bun resolves configuration in this order:

1. Prettier config: `.prettierrc*`, `prettier.config.*`, or a `prettier` key in `package.json`, including its `overrides`.
2. oxfmt config: `.oxfmtrc.json`, `.oxfmtrc.jsonc`, `oxfmt.config.ts`, or `oxfmt.config.mts`.
3. `.editorconfig` (`indent_style`, `indent_size`, `tab_width`, `max_line_length`, `end_of_line`) and `.prettierignore`.
4. The `[fmt]` section of `bunfig.toml`, which overrides the above.

`bunfig.toml` wins over `.editorconfig`. All Prettier options work under the same names, and each is also a flag.

`// prettier-ignore` comments keep working, in the syntax of the file type: `// prettier-ignore` in JS/TS, `{/* prettier-ignore */}` in JSX, `/* prettier-ignore */` in CSS, `<!-- prettier-ignore -->` in HTML and Markdown, `# prettier-ignore` in YAML and GraphQL.

In a monorepo, `bun fmt` walks up from the working directory to the nearest `bunfig.toml` that has a `[fmt]` section. Without a Prettier config it also formats TOML.

### bunfig.toml [fmt]

```toml
[fmt]
printWidth = 100
semi = false
singleQuote = true
sortImports = true
sortTailwindcss = true
sortPackageJson = true
jsdoc = true
svelte = true
ignorePatterns = ["vendor/", "**/*.gen.ts"]

[[fmt.overrides]]
files = ["*.test.ts", "scripts/**"]
options = { printWidth = 120 }
```

| Option            | Default | What it does                          |
| ----------------- | ------- | ------------------------------------- |
| `printWidth`      | `80`    | Wrap lines at this column             |
| `tabWidth`        | `2`     | Spaces per indentation level          |
| `useTabs`         | `false` | Indent with tabs                      |
| `semi`            | `true`  | Print semicolons                      |
| `singleQuote`     | `false` | Use single quotes                     |
| `trailingComma`   | `"all"` | `"all"`, `"es5"`, or `"none"`         |

`sortImports`, `sortTailwindcss`, `sortPackageJson`, and `jsdoc` are off by default and do not need a Prettier or oxfmt config.

### Built-in import sorting

```toml
[fmt]
sortImports = true
```

- Imports are grouped: built-in modules, packages, aliases such as `@/`, relative paths, styles.
- Each group is sorted by path, and the names inside `{ }` are sorted too.
- Two imports from the same module become one.
- Side-effect imports such as `import "./setup"` never move, and nothing moves past one.
- A comment directly above an import moves with it; file-level comments such as `// @ts-nocheck` stay at the top.

Custom groups:

```toml
[fmt.sortImports]
groups = ["react", "builtin", "external", "internal", ["parent", "sibling", "index"]]
customGroups = [{ groupName = "react", elementNamePattern = ["react", "react-dom/**"] }]
```

This makes `@trivago/prettier-plugin-sort-imports`, `@ianvs/prettier-plugin-sort-imports`, and `prettier-plugin-organize-imports` unnecessary.

### Built-in plugin equivalents

`prettier-plugin-tailwindcss`, `prettier-plugin-packagejson`, and `prettier-plugin-svelte` are built in, and their options are supported.

- **Tailwind**: classes are sorted in Tailwind's recommended order, in `class` and `className` and in calls to `clsx`, `cn`, `cva`, `twMerge`. Sorting uses the project's `tailwindcss` (version 3 or 4); without it, classes are left as they are.

```toml
[fmt.sortTailwindcss]
stylesheet = "./src/app.css"
functions = ["clsx", "tw"]
```

- **package.json**: keys go in the conventional order (`name`, `version`, `description`, …).

```toml
[fmt]
sortPackageJson = true
```

- **Svelte**: `.svelte` files are formatted like `prettier-plugin-svelte` formats them.

```toml
[fmt.svelte]
sortOrder = "options-scripts-markup-styles"
allowShorthand = true
indentScriptAndStyle = true
```

Turn it off with `svelte = false` in `[fmt]`.

### What is skipped

`bun fmt` skips `node_modules`, anything in `.gitignore` or `.git/info/exclude`, minified files (`*.min.js`, `*.min.css`), and lockfiles such as `package-lock.json` — unless you pass those paths explicitly.

Every `.gitignore` in the repository counts, whichever directory you run `bun fmt` from. With a Prettier config, only the `.gitignore` in the current directory counts, because that is the only one Prettier reads. To skip more, list patterns in `bunfig.toml` (`ignorePatterns = [...]`) or in `.prettierignore`.

### Git hooks

`--staged` formats only the files you are about to commit and stages them again, so it replaces `lint-staged`:

```sh .git/hooks/pre-commit
#!/bin/sh
bun fmt --staged
```

If a file has both staged and unstaged changes, Bun looks at the staged version, which is what the commit gets, and does not write that file. If the staged version needs formatting, Bun names the file and exits with code `2`.

`--changed` formats the files that differ from the default branch. Pass a ref to compare against something else: `bun fmt --changed=origin/dev`.

### Standard input

`bun fmt` reads standard input, prints the result, and writes nothing. The path picks the language and the options, and the file does not have to exist.

```bash
bun fmt --stdin-filepath src/index.ts < src/index.ts
bun run generate-types | bun fmt --parser typescript > types.ts
```

Without a path, name the parser. Your config still applies, except for the parts that go by file name: `overrides`, `.editorconfig`, and ignore files.

### Script conflicts

- `bun format` still runs your `format` script.
- `bun fmt` is the new command, like `cargo fmt`, `go fmt`, `deno fmt`, and `zig fmt`.
- If `package.json` has an `fmt` script, `bun fmt` runs that script, and inside the script `bun fmt` is the formatter.
- If `package.json` has an `fmt` key that cannot be parsed, `bun fmt` formats nothing and exits with code `2`.
- `bun fmt --no-script` is always the formatter. Use it in tools that run in projects you do not control.

### Migrating from Prettier or oxfmt

`bun fmt` reads an existing `.prettierrc` or `.oxfmtrc.json` and prints what that tool prints. Change the script and you are done:

```json package.json
{
  "scripts": {
    "format": "prettier --write ."
  }
}
```

Languages that need a Prettier plugin, such as Astro, fall back to the Prettier installed in the project. `bun fmt --doctor` shows which files go to Prettier and which packages you can now uninstall.

`bun fmt` is 60 ms on Prettier's own repository (2,616 files), where Prettier takes 17 seconds — about 286x faster with 48 MB peak memory instead of 459 MB. On vitest, date-fns, monkeytype, and h3 it is 234x–425x faster; on projects already using oxfmt, 3x–6x faster.
