# Bun Utilities

Hashing, glob patterns, HTML rewriting, and other utilities.

---

## Password Hashing (Bun.password)

Secure password hashing with argon2 and bcrypt.

```ts
// Hash (async)
const hash = await Bun.password.hash(password);

// Verify
const match = await Bun.password.verify(password, hash);

// Sync versions
const hash = Bun.password.hashSync(password);
const match = Bun.password.verifySync(password, hash);
```

### Argon2 (default)

```ts
const hash = await Bun.password.hash(password, {
  algorithm: "argon2id", // "argon2id" | "argon2i" | "argon2d"
  memoryCost: 4,         // kibibytes
  timeCost: 3,           // iterations
});
```

### Bcrypt

```ts
const hash = await Bun.password.hash(password, {
  algorithm: "bcrypt",
  cost: 10, // 4-31
});
```

**Note**: Bun auto-hashes passwords >72 bytes with SHA-512 before bcrypt.

---

## Non-Cryptographic Hashing (Bun.hash)

Fast hashing for non-security uses (default: Wyhash).

```ts
Bun.hash("data");                    // bigint
Bun.hash("data", 1234);              // with seed
Bun.hash(new Uint8Array([1, 2, 3])); // TypedArray

// Other algorithms
Bun.hash.crc32("data");
Bun.hash.adler32("data");
Bun.hash.cityHash32("data");
Bun.hash.cityHash64("data");
Bun.hash.xxHash32("data");
Bun.hash.xxHash64("data");
Bun.hash.xxHash3("data");
Bun.hash.murmur32v3("data");
Bun.hash.murmur64v2("data");
Bun.hash.rapidhash("data");
```

---

## Cryptographic Hashing (Bun.CryptoHasher)

Incremental cryptographic hashing.

```ts
const hasher = new Bun.CryptoHasher("sha256");
hasher.update("hello");
hasher.update(" world");

// Output formats
hasher.digest();           // Uint8Array
hasher.digest("hex");      // string
hasher.digest("base64");   // string

// Write to existing buffer
const buffer = new Uint8Array(32);
hasher.digest(buffer);
```

### Supported Algorithms

`blake2b256`, `blake2b512`, `md4`, `md5`, `ripemd160`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512`, `sha512-224`, `sha512-256`, `sha3-224`, `sha3-256`, `sha3-384`, `sha3-512`, `shake128`, `shake256`

### HMAC

```ts
const hasher = new Bun.CryptoHasher("sha256", "secret-key");
hasher.update("data");
console.log(hasher.digest("hex"));
```

---

## Glob (Bun.Glob)

Fast native glob pattern matching.

### Matching Strings

```ts
const glob = new Glob("*.ts");

glob.match("index.ts");     // true
glob.match("index.js");     // false
glob.match("src/index.ts"); // false
```

### Scanning Files

```ts
const glob = new Glob("**/*.ts");

// Async
for await (const file of glob.scan(".")) {
  console.log(file);
}

// Sync
for (const file of glob.scanSync(".")) {
  console.log(file);
}
```

### Scan Options

```ts
glob.scan({
  cwd: "./src",
  dot: true,              // Match dotfiles
  absolute: true,         // Return absolute paths
  followSymlinks: true,
  onlyFiles: true,        // default
});
```

### Pattern Syntax

| Pattern    | Matches                     |
| ---------- | --------------------------- |
| `?`        | Single character            |
| `*`        | Zero+ chars (not `/`)       |
| `**`       | Zero+ chars (including `/`) |
| `[ab]`     | `a` or `b`                  |
| `[a-z]`    | Range                       |
| `[^ab]`    | Not `a` or `b`              |
| `{a,b}`    | `a` or `b`                  |
| `!pattern` | Negation                    |
| `\*`       | Literal `*`                 |

```ts
new Glob("**/*.{ts,tsx}");           // TypeScript files
new Glob("src/**/[A-Z]*.ts");        // PascalCase files
new Glob("!**/*.test.ts");           // Exclude tests
```

---

## HTMLRewriter

Streaming HTML transformation with CSS selectors.

### Basic Usage

```ts
const rewriter = new HTMLRewriter().on("img", {
  element(el) {
    el.setAttribute("loading", "lazy");
  },
});

const result = rewriter.transform(html);
```

### Input Types

```ts
rewriter.transform(new Response(html));
rewriter.transform(html);
rewriter.transform(Bun.file("index.html"));
rewriter.transform(new Blob([html]));
```

### Element Handlers

```ts
rewriter.on("div.content", {
  element(el) {
    // Attributes
    el.setAttribute("class", "new");
    el.getAttribute("id");
    el.hasAttribute("id");
    el.removeAttribute("class");

    // Content
    el.setInnerContent("text");
    el.setInnerContent("<p>HTML</p>", { html: true });

    // Position
    el.before("before");
    el.after("after");
    el.prepend("first child");
    el.append("last child");

    // Removal
    el.remove();
    el.removeAndKeepContent();

    // Properties
    el.tagName;      // lowercase
    el.selfClosing;  // boolean
    el.removed;      // boolean

    // Iterate attributes
    for (const [name, value] of el.attributes) {
      console.log(name, value);
    }

    // End tag
    el.onEndTag(tag => {
      tag.before("before </div>");
      tag.remove();
    });
  },

  text(text) {
    text.text;           // content
    text.lastInTextNode; // boolean
    text.replace("new");
    text.remove();
  },

  comments(comment) {
    comment.text;
    comment.text = "new";
    comment.remove();
  },
});
```

### CSS Selectors

```ts
rewriter.on("p", handler);               // Tag
rewriter.on(".class", handler);          // Class
rewriter.on("#id", handler);             // ID
rewriter.on("[attr]", handler);          // Has attribute
rewriter.on('[attr="value"]', handler);  // Exact match
rewriter.on('[attr^="prefix"]', handler); // Starts with
rewriter.on('[attr$="suffix"]', handler); // Ends with
rewriter.on('[attr*="contains"]', handler);
rewriter.on("div > p", handler);         // Direct child
rewriter.on("div p", handler);           // Descendant
rewriter.on("p:first-child", handler);   // Pseudo-class
rewriter.on("p:nth-child(2)", handler);
rewriter.on("*", handler);               // Universal
```

### Document Handlers

```ts
rewriter.onDocument({
  doctype(doctype) {
    console.log(doctype.name);
  },
  text(text) {},
  comments(comment) {},
  end(end) {
    end.append("<!-- Footer -->");
  },
});
```

---

## Quick Reference

### Semver

```ts
import { semver } from "bun";

semver.satisfies("1.2.3", "^1.0.0"); // true
semver.order("1.2.3", "1.2.4");      // -1
```

### Sleep

```ts
await Bun.sleep(1000); // milliseconds
await Bun.sleepSync(1000);
```

### Random

```ts
Bun.randomUUIDv7();  // UUID v7
crypto.randomUUID(); // UUID v4
```

### Inspect

```ts
Bun.inspect(object);
Bun.inspect(object, { depth: 2, colors: true });
```

### Path Utilities

```ts
Bun.main;           // Entry point path
import.meta.dir;    // Directory of current file
import.meta.file;   // Filename of current file
import.meta.path;   // Full path of current file
```

---

## Markdown Parser (Bun.markdown)

Built-in CommonMark-compliant Markdown parser (v1.3.8+).

### Render to HTML

```ts
const html = Bun.markdown.html("# Hello **world**");
// "<h1>Hello <strong>world</strong></h1>\n"

// With options
Bun.markdown.html("## Hello", { headingIds: true });
// '<h2 id="hello">Hello</h2>\n'
```

### Custom Callbacks

```ts
const ansi = Bun.markdown.render("# Hello\n\n**bold**", {
  heading: (children) => `\x1b[1;4m${children}\x1b[0m\n`,
  paragraph: (children) => children + "\n",
  strong: (children) => `\x1b[1m${children}\x1b[22m`,
});

// Return null to omit elements
Bun.markdown.render("# Title\n\n![logo](img.png)", {
  image: () => null,
  heading: (children) => children,
});
```

### React Elements

```tsx
function Markdown({ text }: { text: string }) {
  return Bun.markdown.react(text);
}

// With custom components
Bun.markdown.react("# Hello", {
  h1: ({ children }) => <h1 className="title">{children}</h1>,
});

// React 18 compatibility
Bun.markdown.react(text, { reactVersion: 18 });
```

### GFM Extensions

Enabled by default: tables, strikethrough (`~~deleted~~`), task lists (`- [x] done`), autolinks.

Additional options: `wikiLinks`, `latexMath`, `headingIds`, `autolinkHeadings`.
