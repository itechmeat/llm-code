# Makefile Special Targets Reference

> Source: [GNU Make Manual - Special Built-in Target Names](https://www.gnu.org/software/make/manual/make.html#Special-Targets)

## Phony Targets

Targets that don't represent files:

```makefile
.PHONY: clean test install all

clean:
        rm -rf build/

test:
        pytest tests/
```

**Why use .PHONY:**

1. Prevents confusion with actual files named `clean`, `test`, etc.
2. Improves performance (skips file existence check)
3. Recipe always runs when target is requested

```makefile
# Without .PHONY, if file named "clean" exists,
# "make clean" says "clean is up to date"

# With .PHONY: clean, recipe always runs
```

### Phony Target Dependencies

```makefile
.PHONY: all clean test

# Phony with dependencies
all: prog1 prog2 prog3

# Chained phony targets
cleanall: cleanobj cleandiff
        rm program

cleanobj:
        rm *.o

cleandiff:
        rm *.diff
```

**Note:** Phoniness is NOT inherited. Prerequisites of phony targets are not automatically phony.

## Special Built-in Targets

### .PHONY

```makefile
.PHONY: target1 target2 ...
```

Declare targets that are not files.

### .SUFFIXES

```makefile
.SUFFIXES:            # Clear default suffixes
.SUFFIXES: .c .o .h   # Set custom suffix list
```

Controls old-style suffix rules.

### .DEFAULT

```makefile
.DEFAULT:
        @echo "No rule for $@"
```

Recipe for targets with no rules.

### .PRECIOUS

```makefile
.PRECIOUS: %.o intermediate.txt
```

Don't delete these targets on interrupt or as intermediates.

### .INTERMEDIATE

```makefile
.INTERMEDIATE: intermediate.o
```

Mark as intermediate (delete after use).

### .NOTINTERMEDIATE

```makefile
.NOTINTERMEDIATE: important.o
.NOTINTERMEDIATE:    # All targets not intermediate
```

Prevent intermediate file deletion.

### .SECONDARY

```makefile
.SECONDARY: generated.c
.SECONDARY:          # All targets are secondary
```

Like intermediate but never auto-deleted.

### .SECONDEXPANSION

```makefile
.SECONDEXPANSION:

prog: $$(prog_OBJS)
```

Enable secondary expansion of prerequisites.

### .DELETE_ON_ERROR

```makefile
.DELETE_ON_ERROR:
```

Delete target if recipe fails.

### .IGNORE

```makefile
.IGNORE: cleanup      # Ignore errors in cleanup target
.IGNORE:              # Ignore all errors (discouraged)
```

### .LOW_RESOLUTION_TIME

```makefile
.LOW_RESOLUTION_TIME: dst
dst: src
        cp -p src dst
```

For commands that can't preserve sub-second timestamps.

### .SILENT

```makefile
.SILENT: install      # Don't echo install recipe
.SILENT:              # Silent mode for all (discouraged)
```

### .EXPORT_ALL_VARIABLES

```makefile
.EXPORT_ALL_VARIABLES:
```

Export all variables to sub-processes.

### .NOTPARALLEL

```makefile
.NOTPARALLEL:         # Disable parallel for entire make
.NOTPARALLEL: target  # Disable parallel for target's prereqs
```

### .ONESHELL

```makefile
.ONESHELL:

target:
        cd subdir
        pwd           # Still in subdir!
        make
```

Run entire recipe in single shell invocation.

### .POSIX

```makefile
.POSIX:
```

Enable POSIX-conforming behavior.

### .WAIT

```makefile
# Force sequential execution in parallel builds
all: dep1 .WAIT dep2 .WAIT dep3
```

## Pattern Rules

Define how to build file types:

```makefile
# Implicit rule: .c to .o
%.o: %.c
        $(CC) -c $(CFLAGS) $< -o $@

# Multiple targets (grouped)
%.tab.c %.tab.h: %.y
        bison -d $<
```

### Pattern Rule Automatic Variables

| Variable | Meaning             |
| -------- | ------------------- |
| `$@`     | Target              |
| `$<`     | First prerequisite  |
| `$^`     | All prerequisites   |
| `$*`     | Stem (matched by %) |

### Canceling Implicit Rules

```makefile
# Cancel built-in .c.o rule
%.o: %.c
```

Empty recipe with pattern cancels that implicit rule.

## Static Pattern Rules

Apply pattern to explicit target list:

```makefile
objects := foo.o bar.o baz.o

$(objects): %.o: %.c
        $(CC) -c $< -o $@
```

## Double-Colon Rules

Multiple independent rules for same target:

```makefile
# Each rule runs if its prereqs are newer
file.txt:: source1.txt
        cat source1.txt >> file.txt

file.txt:: source2.txt
        cat source2.txt >> file.txt
```

## Empty Targets (Timestamps)

Record when action was last performed:

```makefile
print: *.c
        lpr -p $?
        touch print
```

## Force Targets

Always out-of-date:

```makefile
clean: FORCE
        rm *.o

FORCE:

# Equivalent to:
.PHONY: clean
clean:
        rm *.o
```

## Target-Specific Variables

```makefile
debug: CFLAGS += -g -DDEBUG
debug: all

release: CFLAGS += -O3 -DNDEBUG
release: all

# Pattern-specific
%.debug.o: CFLAGS += -g
```

## Common Target Conventions

| Target      | Purpose                            |
| ----------- | ---------------------------------- |
| `all`       | Build everything (usually default) |
| `clean`     | Remove generated files             |
| `install`   | Install to system                  |
| `uninstall` | Remove from system                 |
| `test`      | Run tests                          |
| `check`     | Alias for test                     |
| `dist`      | Create distribution archive        |
| `distclean` | Clean + remove configure artifacts |
| `help`      | Show available targets             |

## Best Practices

1. **Always use .PHONY** for non-file targets
2. **Make `help` or `all` the default** (first target)
3. **Group .PHONY declarations** at top of file
4. **Use standard target names** for common operations
5. **Document targets** with `## comment` for help generation

```makefile
.PHONY: all clean test install help

help: ## Show this help
        @grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
                awk 'BEGIN {FS = ":.*?## "}; {printf "%-15s %s\n", $$1, $$2}'
```
