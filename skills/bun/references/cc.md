# Bun C Compiler

Compile and run C code directly from JavaScript using TinyCC.

## Basic Usage

```ts
import { cc } from "bun:ffi";
import source from "./hello.c" with { type: "file" };

const {
  symbols: { hello },
} = cc({
  source,
  symbols: {
    hello: {
      args: [],
      returns: "int",
    },
  },
});

console.log(hello()); // 42
```

**hello.c:**

```c
int hello() {
  return 42;
}
```

## Supported Types

Same FFI types as `dlopen`:

| Type         | C Type     | Aliases      |
| ------------ | ---------- | ------------ |
| `i8`         | int8_t     | int8_t       |
| `i16`        | int16_t    | int16_t      |
| `i32`        | int32_t    | int32_t, int |
| `i64`        | int64_t    | int64_t      |
| `u8`         | uint8_t    | uint8_t      |
| `u16`        | uint16_t   | uint16_t     |
| `u32`        | uint32_t   | uint32_t     |
| `u64`        | uint64_t   | uint64_t     |
| `f32`        | float      | float        |
| `f64`        | double     | double       |
| `bool`       | bool       | —            |
| `ptr`        | void\*     | pointer      |
| `cstring`    | char\*     | —            |
| `function`   | fn ptr     | fn, callback |
| `napi_env`   | napi_env   | —            |
| `napi_value` | napi_value | —            |

## N-API Integration

Use `napi_value` for complex JavaScript types:

```ts
import { cc } from "bun:ffi";
import source from "./hello.c" with { type: "file" };

const {
  symbols: { hello },
} = cc({
  source,
  symbols: {
    hello: {
      args: ["napi_env"],
      returns: "napi_value",
    },
  },
});

const result = hello(); // JavaScript string
```

**hello.c:**

```c
#include <node/node_api.h>

napi_value hello(napi_env env) {
  napi_value result;
  napi_create_string_utf8(env, "Hello from C!", NAPI_AUTO_LENGTH, &result);
  return result;
}
```

### Returning Objects

```c
#include <node/node_api.h>

napi_value create_object(napi_env env) {
  napi_value result;
  napi_create_object(env, &result);

  napi_value name;
  napi_create_string_utf8(env, "John", NAPI_AUTO_LENGTH, &name);
  napi_set_named_property(env, result, "name", name);

  return result;
}
```

## cc() Options

### source

File path to C code:

```ts
cc({
  source: "hello.c",
  // or
  source: new URL("./hello.c", import.meta.url),
  // or
  source: Bun.file("hello.c"),
});
```

### symbols

Functions to expose:

```ts
cc({
  source: "math.c",
  symbols: {
    add: {
      args: ["i32", "i32"],
      returns: "i32",
    },
    multiply: {
      args: ["f64", "f64"],
      returns: "f64",
    },
  },
});
```

### library

Link external libraries:

```ts
cc({
  source: "db.c",
  library: ["sqlite3"],
  symbols: {
    query: {
      args: ["cstring"],
      returns: "ptr",
    },
  },
});
```

### flags

Compiler flags:

```ts
cc({
  source: "app.c",
  flags: ["-I/usr/local/include", "-O2"],
});
```

### define

Preprocessor definitions:

```ts
cc({
  source: "app.c",
  define: {
    NDEBUG: "1",
    VERSION: '"1.0.0"',
  },
});
```

## Practical Examples

### Simple Math

```ts
import { cc } from "bun:ffi";

const { symbols: { add, multiply } } = cc({
  source: `
    int add(int a, int b) { return a + b; }
    double multiply(double a, double b) { return a * b; }
  `,
  symbols: {
    add: { args: ["i32", "i32"], returns: "i32" },
    multiply: { args: ["f64", "f64"], returns: "f64" },
  },
});

console.log(add(1, 2));        // 3
console.log(multiply(2.5, 4)); // 10.0
```

### Using SQLite

```ts
import { cc } from "bun:ffi";
import source from "./db.c" with { type: "file" };

const { symbols: { get_version } } = cc({
  source,
  library: ["sqlite3"],
  symbols: {
    get_version: {
      args: [],
      returns: "cstring",
    },
  },
});

console.log(get_version());
```

**db.c:**

```c
#include <sqlite3.h>

const char* get_version() {
  return sqlite3_libversion();
}
```

### Processing Arrays

```ts
import { cc, ptr } from "bun:ffi";

const { symbols: { sum_array } } = cc({
  source: `
    int sum_array(int* arr, int len) {
      int sum = 0;
      for (int i = 0; i < len; i++) {
        sum += arr[i];
      }
      return sum;
    }
  `,
  symbols: {
    sum_array: {
      args: ["ptr", "i32"],
      returns: "i32",
    },
  },
});

const numbers = new Int32Array([1, 2, 3, 4, 5]);
console.log(sum_array(ptr(numbers), numbers.length)); // 15
```

## Notes

- Uses TinyCC (embedded compiler)
- Low overhead for type conversion
- Supports N-API for complex types
- Source can be inline string or file
