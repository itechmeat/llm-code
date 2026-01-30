# Bun Shell

Cross-platform bash-like shell with JavaScript interop.

## Basic Usage

```ts
import { $ } from "bun";

await $`echo "Hello World!"`;
```

## Features

- Cross-platform (Windows, Linux, macOS)
- Native glob support (`**`, `*`, `{expansion}`)
- Auto-escaping prevents shell injection
- JavaScript object interop (Response, Buffer, Bun.file)
- Concurrent execution

## Output Handling

```ts
// Print to stdout (default)
await $`echo "Hello"`;

// Quiet mode (no output)
await $`echo "Hello"`.quiet();

// Get as text
const text = await $`echo "Hello"`.text();

// Get as JSON
const json = await $`echo '{"a":1}'`.json();

// Get as Blob
const blob = await $`echo "Hello"`.blob();

// Get stdout/stderr buffers
const { stdout, stderr } = await $`echo "Hello"`.quiet();

// Line-by-line
for await (const line of $`cat file.txt`.lines()) {
  console.log(line);
}
```

## Error Handling

```ts
// Default: throws on non-zero exit
try {
  await $`command-that-fails`.text();
} catch (err) {
  console.log(err.exitCode);
  console.log(err.stdout.toString());
  console.log(err.stderr.toString());
}

// Disable throwing
const { exitCode, stdout, stderr } = await $`command`.nothrow().quiet();

// Global default
$.nothrow();  // Disable throws globally
$.throws(true);  // Re-enable
```

## Environment Variables

```ts
// Inline
await $`FOO=bar bun -e 'console.log(process.env.FOO)'`;

// Interpolated
const value = "bar123";
await $`FOO=${value} bun -e 'console.log(process.env.FOO)'`;

// Set for single command
await $`echo $FOO`.env({ ...process.env, FOO: "bar" });

// Set globally
$.env({ FOO: "bar" });
await $`echo $FOO`;  // bar
```

## Working Directory

```ts
// Single command
await $`pwd`.cwd("/tmp");  // /tmp

// Global default
$.cwd("/tmp");
await $`pwd`;  // /tmp
```

## Redirection

### Output Redirection

```ts
// To file
await $`echo "Hello" > file.txt`;
await $`echo "More" >> file.txt`;  // Append

// To JavaScript objects
const buffer = Buffer.alloc(100);
await $`echo "Hello" > ${buffer}`;

// Stderr
await $`command 2> errors.txt`;
await $`command &> all.txt`;  // Both stdout+stderr
```

### Input Redirection

```ts
// From file
await $`cat < input.txt`;

// From Response
const response = await fetch("https://example.com");
await $`cat < ${response} | wc -c`;

// From Buffer
const data = Buffer.from("hello");
await $`cat < ${data}`;

// From Bun.file
await $`cat < ${Bun.file("input.txt")}`;
```

### Stream Redirection

```ts
await $`command 2>&1`;  // stderr to stdout
await $`command 1>&2`;  // stdout to stderr
```

## Piping

```ts
const result = await $`echo "Hello World" | wc -w`.text();
// "2\n"

// With JavaScript objects
const response = new Response("hello world");
await $`cat < ${response} | wc -w`.text();
// "2\n"
```

## Command Substitution

```ts
await $`echo "Current commit: $(git rev-parse HEAD)"`;

// With shell variables
await $`
  REV=$(git rev-parse HEAD)
  docker build -t myapp:$REV .
`;
```

## String Interpolation

All interpolated values are **automatically escaped**:

```ts
const userInput = "file.txt; rm -rf /";
await $`ls ${userInput}`;  // Safe: treated as literal string
```

### Raw (Unescaped) Strings

```ts
await $`echo ${{ raw: "$(date)" }}`;  // Executes date command
```

## Builtin Commands

Cross-platform without PATH:

| Command    | Description                 |
| ---------- | --------------------------- |
| `cd`       | Change directory            |
| `ls`       | List files (`-l` supported) |
| `rm`       | Remove files/dirs           |
| `mkdir`    | Create directory            |
| `mv`       | Move files                  |
| `cat`      | Print file contents         |
| `echo`     | Print text                  |
| `pwd`      | Print working directory     |
| `touch`    | Create/update file          |
| `which`    | Locate command              |
| `exit`     | Exit shell                  |
| `true`     | Exit 0                      |
| `false`    | Exit 1                      |
| `yes`      | Output "y" repeatedly       |
| `seq`      | Print number sequence       |
| `dirname`  | Directory part of path      |
| `basename` | Filename part of path       |

## Utilities

### Brace Expansion

```ts
const expanded = await $.braces(`echo {1,2,3}`);
// ["echo 1", "echo 2", "echo 3"]
```

### Escape Strings

```ts
const escaped = $.escape('$(foo) `bar` "baz"');
// \$(foo) \`bar\` \"baz\"
```

## Shell Scripts

Run `.sh` files cross-platform:

```bash
# script.sh
echo "Hello from $(pwd)"
```

```bash
bun ./script.sh  # Works on Linux/macOS/Windows
```

## Practical Patterns

### Build Script

```ts
import { $ } from "bun";

await $`rm -rf dist`;
await $`mkdir -p dist`;

const version = await $`git describe --tags`.text();
await $`echo "Building ${version.trim()}"`;

await $`bun build src/index.ts --outdir dist`;
```

### Parallel Commands

```ts
await Promise.all([
  $`bun run lint`,
  $`bun run typecheck`,
  $`bun run test`,
]);
```

### Git Operations

```ts
const branch = await $`git branch --show-current`.text();
const status = await $`git status --porcelain`.text();

if (status.trim()) {
  await $`git add -A`;
  await $`git commit -m "Auto commit"`;
}
```

### File Processing

```ts
for await (const line of $`cat data.csv | tail -n +2`.lines()) {
  const [id, name] = line.split(",");
  await $`curl -X POST http://api/items -d '{"id":"${id}","name":"${name}"}'`;
}
```

### Docker Workflow

```ts
const tag = `myapp:${Date.now()}`;

await $`docker build -t ${tag} .`;
await $`docker push ${tag}`;
await $`kubectl set image deployment/myapp myapp=${tag}`;
```

## Security

**Safe by default**: Interpolated values are escaped.

**⚠️ Unsafe patterns**:

```ts
// Spawning new shell loses protection
await $`bash -c "echo ${userInput}"`;  // UNSAFE

// Argument injection still possible
await $`git ls-remote origin ${branch}`;  // Git interprets flags
```

**Always sanitize** user input before passing to commands.
