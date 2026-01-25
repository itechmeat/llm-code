# Makefile Variables Reference

> Source: [GNU Make Manual - How to Use Variables](https://www.gnu.org/software/make/manual/make.html#Using-Variables)

## Variable Reference Syntax

```makefile
$(variable)     # Standard form
${variable}     # Also valid
$x              # Single-character variable (discouraged)
```

## Assignment Operators

### Recursive (`=`) - Lazy Evaluation

Expanded each time referenced:

```makefile
foo = $(bar)
bar = hello
# $(foo) expands to "hello"

bar = world
# $(foo) now expands to "world"
```

**Use for:** Dynamic values, computed at use time.

**Warning:** Can cause infinite loops:

```makefile
CFLAGS = $(CFLAGS) -Wall  # ERROR: infinite recursion
```

### Simply Expanded (`:=` or `::=`) - Immediate Evaluation

Expanded once at definition:

```makefile
x := foo
y := $(x) bar
# y is "foo bar"

x := later
# y is still "foo bar"
```

**Use for:** Constants, one-time computations, avoiding recursion.

### Immediately Expanded (`:::=`) - GNU Make 4.4+

Like `:=` but in POSIX mode:

```makefile
x :::= $(shell date)
```

### Conditional (`?=`) - Set If Undefined

Only sets if variable has no value:

```makefile
CC ?= gcc        # Use gcc unless CC already set
DEBUG ?= 0       # Default to 0
```

**Use for:** Defaults, allowing command-line overrides.

### Append (`+=`)

Add to existing value:

```makefile
CFLAGS := -Wall
CFLAGS += -O2
# CFLAGS is "-Wall -O2"
```

Behavior depends on original assignment type:

- If originally `=`, append uses `=`
- If originally `:=`, append uses `:=`

### Shell Assignment (`!=`)

Assign command output:

```makefile
hash != git rev-parse --short HEAD
# Same as: hash := $(shell git rev-parse --short HEAD)
```

## Expansion Timing Summary

| Operator | When Expanded         | Typical Use                     |
| -------- | --------------------- | ------------------------------- |
| `=`      | Each use              | Dynamic values, late binding    |
| `:=`     | Definition time       | Constants, one-time shell calls |
| `?=`     | Definition (if unset) | Overridable defaults            |
| `+=`     | Depends on original   | Building up lists               |
| `!=`     | Definition time       | Shell command output            |

## Multi-Line Variables

```makefile
define run-tests =
echo "Running tests..."
pytest tests/
echo "Tests complete"
endef

test:
        $(run-tests)
```

To prevent expansion, use `$$`:

```makefile
define script
for i in 1 2 3; do \
    echo $$i; \
done
endef
```

## Undefining Variables

```makefile
foo := bar
undefine foo
# $(foo) is now empty
```

## Variable Scope

### Global Variables

Default scope - accessible everywhere:

```makefile
CC := gcc
```

### Target-Specific Variables

Set for one target and its prerequisites:

```makefile
debug: CFLAGS += -g -DDEBUG
debug: all

release: CFLAGS += -O3
release: all
```

### Pattern-Specific Variables

Set for targets matching pattern:

```makefile
%.o: CFLAGS += -MMD
```

### Private Variables

Don't inherit to prerequisites:

```makefile
all: private CFLAGS := -Wall
all: prog
# prog does NOT see CFLAGS from all
```

## Environment Variables

Make reads environment variables as defaults:

```makefile
# $HOME from environment if not set in Makefile
homedir := $(HOME)

# Override environment (use -e to reverse)
PATH := /custom/bin:$(PATH)
```

Command-line overrides everything:

```bash
make CFLAGS="-O3"  # Overrides Makefile and environment
```

## Exporting Variables

Pass to sub-makes and shell commands:

```makefile
export PYTHONPATH := $(PWD)/src
export DATABASE_URL

# Export all variables
.EXPORT_ALL_VARIABLES:
```

Unexport:

```makefile
unexport CDPATH
```

## Override Directive

Allow Makefile to override command-line:

```makefile
override CFLAGS += -Wall  # Add even if CFLAGS set on command line
```

## Substitution References

Replace suffix in variable:

```makefile
sources := foo.c bar.c
objects := $(sources:.c=.o)
# objects is "foo.o bar.o"

# Pattern form
$(sources:%.c=%.o)
```

## Computed Variable Names

Variable name from variable:

```makefile
prog_srcs := main.c utils.c
lib_srcs := lib.c api.c

# Single indirection
sources := $($(target)_srcs)

# Example usage
target := prog
# $(sources) expands to main.c utils.c
```

## Special Variables

| Variable        | Meaning                           |
| --------------- | --------------------------------- |
| `MAKEFILE_LIST` | List of makefiles being parsed    |
| `MAKEFLAGS`     | Flags passed to make              |
| `.DEFAULT_GOAL` | Target if none specified          |
| `.RECIPEPREFIX` | Recipe line prefix (default: TAB) |
| `.VARIABLES`    | All defined variable names        |
| `.FEATURES`     | List of make features             |
| `CURDIR`        | Current working directory         |
| `MAKE`          | Path to make executable           |
| `MAKELEVEL`     | Recursion depth                   |
| `MAKECMDGOALS`  | Command line goals                |

## Automatic Variables

See [syntax.md](syntax.md#automatic-variables) for complete list.

## Best Practices

1. **Use `:=` by default** - Predictable, efficient
2. **Use `?=` for overridable settings** - CLI flexibility
3. **Avoid recursive `=` unless needed** - Prevents surprises
4. **Export only what's needed** - Don't pollute subprocess environment
5. **Document non-obvious variables** - Especially computed ones
6. **Use UPPERCASE for configuration** - `DEBUG`, `VERBOSE`
7. **Use lowercase for internal** - `sources`, `objects`
