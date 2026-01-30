# Bun Native Interop

Node-API and FFI for native code integration.

## Node-API

Bun implements 95% of Node-API. Use `.node` files directly:

```ts
const napi = require("./my-module.node");
```

Or with `process.dlopen`:

```ts
let mod = { exports: {} };
process.dlopen(mod, "./my-module.node");
```

---

## FFI (bun:ffi)

**Experimental** — call native libraries from JavaScript.

Works with any language supporting C ABI (C, C++, Rust, Zig, etc.).

### Basic Example

```ts
import { dlopen, FFIType, suffix } from "bun:ffi";

// suffix = "dylib" | "so" | "dll"
const lib = dlopen(`libsqlite3.${suffix}`, {
  sqlite3_libversion: {
    args: [],
    returns: FFIType.cstring,
  },
});

console.log(lib.symbols.sqlite3_libversion());
```

### FFI Types

| FFIType    | C Type     | Aliases      |
| ---------- | ---------- | ------------ |
| `i8`       | int8_t     | int8_t       |
| `i16`      | int16_t    | int16_t      |
| `i32`      | int32_t    | int32_t, int |
| `i64`      | int64_t    | int64_t      |
| `u8`       | uint8_t    | uint8_t      |
| `u16`      | uint16_t   | uint16_t     |
| `u32`      | uint32_t   | uint32_t     |
| `u64`      | uint64_t   | uint64_t     |
| `f32`      | float      | float        |
| `f64`      | double     | double       |
| `bool`     | bool       | —            |
| `char`     | char       | —            |
| `ptr`      | void\*     | pointer      |
| `cstring`  | char\*     | —            |
| `buffer`   | char\*     | —            |
| `function` | fn pointer | fn, callback |

### Compiling Native Code

**Zig:**

```zig
// add.zig
pub export fn add(a: i32, b: i32) i32 {
    return a + b;
}
```

```bash
zig build-lib add.zig -dynamic -OReleaseFast
```

**Rust:**

```rust
// add.rs
#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

```bash
rustc --crate-type cdylib add.rs
```

**C++:**

```cpp
extern "C" int32_t add(int32_t a, int32_t b) {
    return a + b;
}
```

```bash
zig build-lib add.cpp -dynamic -lc -lc++
```

### Loading & Calling

```ts
import { dlopen, FFIType, suffix } from "bun:ffi";

const lib = dlopen(`libadd.${suffix}`, {
  add: {
    args: [FFIType.i32, FFIType.i32],
    returns: FFIType.i32,
  },
});

console.log(lib.symbols.add(1, 2)); // 3
```

## Strings

### CString

```ts
import { CString } from "bun:ffi";

// From null-terminated pointer
const str = new CString(ptr);

// With known length
const str = new CString(ptr, 0, byteLength);

// Safe to use after ptr is freed (cloned)
lib.free(str.ptr);
console.log(str); // Still works
```

## Pointers

### TypedArray to Pointer

```ts
import { ptr } from "bun:ffi";

const myArray = new Uint8Array(32);
const myPtr = ptr(myArray);
```

### Pointer to ArrayBuffer

```ts
import { toArrayBuffer } from "bun:ffi";

const buffer = toArrayBuffer(myPtr, 0, 32);
const array = new Uint8Array(buffer);
```

### Reading from Pointer

```ts
import { read } from "bun:ffi";

// Fast reading (no ArrayBuffer creation)
const value = read.u8(myPtr, 0);  // byte at offset 0
const value2 = read.i32(myPtr, 4); // int32 at offset 4
```

Read functions: `read.ptr`, `read.i8`, `read.i16`, `read.i32`, `read.i64`, `read.u8`, `read.u16`, `read.u32`, `read.u64`, `read.f32`, `read.f64`

## Function Pointers

```ts
import { CFunction, linkSymbols } from "bun:ffi";

// Single function pointer
const getVersion = new CFunction({
  returns: "cstring",
  args: [],
  ptr: myFunctionPointer,
});
getVersion();

// Multiple function pointers
const lib = linkSymbols({
  getMajor: {
    returns: "cstring",
    args: [],
    ptr: majorPtr,
  },
  getMinor: {
    returns: "cstring",
    args: [],
    ptr: minorPtr,
  },
});
```

## Callbacks (JSCallback)

```ts
import { JSCallback, CString } from "bun:ffi";

const callback = new JSCallback(
  (ptr, length) => {
    const str = new CString(ptr, 0, length);
    return /pattern/.test(str);
  },
  {
    returns: "bool",
    args: ["ptr", "usize"],
    threadsafe: false, // Set true for cross-thread calls
  }
);

// Pass to native function
nativeSearch(data, callback);

// Performance: use .ptr directly
nativeSearch(data, callback.ptr);

// Clean up when done
callback.close();
```

## Memory Management

**FFI does not manage memory.** You must free it yourself.

### JavaScript FinalizationRegistry

```ts
const registry = new FinalizationRegistry((ptr) => {
  lib.free(ptr);
});

const buffer = new Uint8Array(toArrayBuffer(allocatedPtr, 0, size));
registry.register(buffer, allocatedPtr);
```

### Native Deallocator

```ts
import { toArrayBuffer } from "bun:ffi";

toArrayBuffer(
  bytes,
  0,
  byteLength,
  deallocatorContext,    // Optional context pointer
  deallocatorFunction,   // Called when GC frees buffer
);
```

## Practical Patterns

### SQLite Version

```ts
import { dlopen, FFIType, suffix } from "bun:ffi";

const sqlite = dlopen(`libsqlite3.${suffix}`, {
  sqlite3_libversion: {
    args: [],
    returns: FFIType.cstring,
  },
});

console.log(sqlite.symbols.sqlite3_libversion());
```

### Image Encoding

```ts
import { dlopen, ptr } from "bun:ffi";

const lib = dlopen("libpng.dylib", {
  encode_png: {
    args: ["ptr", "u32", "u32"],
    returns: "ptr",
  },
});

const pixels = new Uint8ClampedArray(128 * 128 * 4);
pixels.fill(254);

const outPtr = lib.symbols.encode_png(pixels, 128, 128);
const png = new Uint8Array(toArrayBuffer(outPtr));
await Bun.write("out.png", png);
```

### Calling System Libraries

```ts
import { dlopen, FFIType, suffix } from "bun:ffi";

const libc = dlopen(`libc.${suffix}`, {
  getpid: {
    args: [],
    returns: FFIType.i32,
  },
  getenv: {
    args: [FFIType.cstring],
    returns: FFIType.cstring,
  },
});

console.log("PID:", libc.symbols.getpid());
console.log("HOME:", libc.symbols.getenv("HOME"));
```

## Performance

- `bun:ffi` is 2-6x faster than Node.js FFI via Node-API
- Bun JIT-compiles C bindings using embedded TinyCC
- Use `callback.ptr` directly for slight performance boost

## Limitations

- Async functions not supported in callbacks
- Memory not managed automatically
- Windows HANDLE should use `u64`, not `ptr`
- Thread-safe callbacks experimental
