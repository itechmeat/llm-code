# File I/O

Optimized APIs for reading and writing files.

## Reading Files

### Bun.file()

Creates lazy file reference (doesn't read immediately):

```typescript
const file = Bun.file("data.txt");

// Metadata
file.size; // Bytes
file.type; // MIME type
await file.exists(); // Boolean
```

### Read Content

```typescript
const file = Bun.file("data.txt");

await file.text(); // String
await file.json(); // Parsed JSON
await file.bytes(); // Uint8Array
await file.arrayBuffer(); // ArrayBuffer
await file.stream(); // ReadableStream
```

### File References

```typescript
// Relative path
Bun.file("./data.txt");

// Absolute path
Bun.file("/tmp/data.txt");

// File descriptor
Bun.file(1234);

// URL
Bun.file(new URL("file:///path/to/file.txt"));
Bun.file(new URL(import.meta.url)); // Current file

// Custom MIME type
Bun.file("data.bin", { type: "application/octet-stream" });
```

### Standard Streams

```typescript
Bun.stdin; // Read-only
Bun.stdout; // Write
Bun.stderr; // Write
```

## Writing Files

### Bun.write()

```typescript
// String to file
await Bun.write("output.txt", "Hello World");

// Copy file
await Bun.write("output.txt", Bun.file("input.txt"));

// ArrayBuffer/TypedArray
await Bun.write("data.bin", new Uint8Array([1, 2, 3]));

// HTTP Response body
const res = await fetch("https://example.com");
await Bun.write("page.html", res);

// To stdout
await Bun.write(Bun.stdout, Bun.file("input.txt"));
```

Returns: `Promise<number>` — bytes written.

## Images (`Bun.Image`, v1.3.14)

Bun now has a built-in image pipeline for decode → transform → encode workflows with no extra npm package.

```typescript
const out = await Bun.file("photo.jpg").image().resize(400, 400, { fit: "inside" }).webp({ quality: 80 }).write("thumb.webp");
```

Key rules:

- `Bun.Image` is lazy and chainable; work begins only when you await a terminal such as `.bytes()`, `.blob()`, or `.write()`.
- Supported core formats include JPEG, PNG, and WebP everywhere; HEIC/AVIF support depends on platform backends.
- The input format is detected from bytes, not file extension or `Content-Type`.
- Do not pass unvalidated user-controlled path strings directly into the constructor; convert untrusted input to bytes first.

Useful operations include:

- `.metadata()` for width/height/format without full decode
- `.resize()`, `.rotate()`, `.flip()`, `.flop()`, `.modulate()` for transforms
- `.jpeg()`, `.png()`, `.webp()`, `.heic()`, `.avif()` for output selection
- `.placeholder()` for low-quality image placeholders

`Bun.Image` pipelines also work well with `Bun.serve()` handlers, but prefer awaiting a terminal result before constructing the `Response` if you want the encode to stay off the JS thread.

## Incremental Writing (FileSink)

```typescript
const file = Bun.file("log.txt");
const writer = file.writer({ highWaterMark: 1024 * 1024 }); // 1MB buffer

writer.write("Line 1\n");
writer.write("Line 2\n");

writer.flush(); // Force write to disk
writer.end(); // Flush and close

// Process lifecycle
writer.unref(); // Allow process to exit
writer.ref(); // Keep process alive
```

## Delete Files

```typescript
await Bun.file("old.txt").delete();
```

## Directories (node:fs)

```typescript
import { readdir, mkdir, rm } from "node:fs/promises";

// List files
const files = await readdir("./src");

// List recursively
const all = await readdir("./src", { recursive: true });

// Create directory
await mkdir("./logs", { recursive: true });

// Delete directory
await rm("./temp", { recursive: true, force: true });
```

## Performance Tips

- `Bun.write()` uses optimal syscalls (`copy_file_range`, `sendfile`, etc.)
- `BunFile` is lazy — reading happens only when content methods called
- Use `FileSink` for incremental writes (streaming logs, etc.)

## Example: cat Command

```typescript
const path = process.argv.at(-1)!;
await Bun.write(Bun.stdout, Bun.file(path));
```

2x faster than GNU `cat` on Linux.

## API Reference

```typescript
interface BunFile extends Blob {
  size: number;
  type: string;
  text(): Promise<string>;
  json(): Promise<any>;
  bytes(): Promise<Uint8Array>;
  arrayBuffer(): Promise<ArrayBuffer>;
  stream(): ReadableStream;
  exists(): Promise<boolean>;
  delete(): Promise<void>;
  writer(opts?: { highWaterMark?: number }): FileSink;
}

interface FileSink {
  write(chunk: string | ArrayBufferView): number;
  flush(): number | Promise<number>;
  end(): number | Promise<number>;
  ref(): void;
  unref(): void;
}
```
