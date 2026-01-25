# Makefile Recipe Execution Reference

> Source: [GNU Make Manual - Writing Recipes in Rules](https://www.gnu.org/software/make/manual/make.html#Recipes)

## Recipe Basics

Recipes are shell commands that update targets.

```makefile
target: prerequisites
        command1
        command2
```

**Critical:** Recipe lines MUST begin with TAB character (not spaces).

Alternative prefix:

```makefile
.RECIPEPREFIX := >

target:
> echo "Using > as prefix"
```

## Recipe Execution Model

Each line runs in a **separate shell**:

```makefile
# Each line is independent shell
target:
        cd subdir
        pwd          # Still in original directory!

# Combine with && or \
target:
        cd subdir && pwd

target:
        cd subdir; \
        pwd; \
        make
```

### .ONESHELL Mode

Run entire recipe in single shell:

```makefile
.ONESHELL:

target:
        cd subdir
        pwd          # Now in subdir!
        for f in *.c; do
                echo $$f
        done
```

## Recipe Echoing

By default, commands are printed before execution.

```makefile
# @ suppresses echo
target:
        @echo "This prints, but command doesn't"

# -s / --silent flag suppresses all echoing
# make -s target

# .SILENT target
.SILENT: quiet-target
quiet-target:
        echo "Command not shown"
```

## Error Handling

### Default: Stop on Error

Make stops if any command returns non-zero:

```makefile
target:
        command1     # If fails, stops here
        command2     # Never runs if command1 fails
```

### Ignore Errors

```makefile
# - prefix ignores error
clean:
        -rm -f *.o   # Continue even if no .o files

# -i flag ignores all errors
# make -i target

# .IGNORE target
.IGNORE: risky-target
```

### Continue on Error

```makefile
# -k / --keep-going: continue other targets
# make -k all
```

## Shell Selection

Default shell is `/bin/sh`:

```makefile
SHELL := /bin/bash

# Enable bash features
target:
        [[ -f file.txt ]] && echo "exists"
```

### Shell Flags

```makefile
.SHELLFLAGS := -ec

# -e: exit on first error
# -c: execute string (required)
```

## Parallel Execution

```makefile
# Run with -j flag
# make -j4          # 4 parallel jobs
# make -j           # Unlimited parallel

# Control parallelism in Makefile
.NOTPARALLEL:       # Disable for entire make
.NOTPARALLEL: target # Disable for target's prereqs

# Force order with .WAIT
all: setup .WAIT build .WAIT test
```

### Parallel Output

```makefile
# Output synchronization (GNU Make 4.0+)
# make -j4 -O       # Group output by target
# make -j4 -Oline   # Group by line
```

## Recursive Make

Call make from make:

```makefile
# Always use $(MAKE), not "make"
subsystem:
        $(MAKE) -C subdir

# Equivalent
subsystem:
        cd subdir && $(MAKE)

# Pass variables
subsystem:
        $(MAKE) -C subdir CFLAGS="$(CFLAGS)"
```

### Export Variables to Sub-make

```makefile
export CFLAGS
export CC

# Or export all
.EXPORT_ALL_VARIABLES:

subsystem:
        $(MAKE) -C subdir
```

### MAKEFLAGS

Flags automatically passed to sub-makes:

```makefile
# -j, -k, -s, etc. are inherited

# Add flags
MAKEFLAGS += --no-print-directory
```

## Canned Recipes

Reusable recipe blocks:

```makefile
define compile-cmd
$(CC) $(CFLAGS) -c $< -o $@
endef

%.o: %.c
        $(compile-cmd)
```

With multiple commands:

```makefile
define run-tests =
echo "Running tests..."
pytest tests/
echo "Done"
endef

test:
        $(run-tests)
```

## Variables in Recipes

Make variables vs shell variables:

```makefile
target:
        echo $(MAKE_VAR)      # Make variable
        echo $$SHELL_VAR      # Shell variable
        echo $$HOME           # Environment variable

# Loop with shell variable
target:
        for i in 1 2 3; do \
                echo $$i; \
        done
```

## Empty Recipes

Explicitly do nothing:

```makefile
target: ;

# Or
target:
        @:    # : is shell no-op
```

Use to:

- Prevent implicit rule search
- Override inherited recipes
- Mark file as always up-to-date

## Common Recipe Patterns

### Check command exists

```makefile
require-docker:
        @command -v docker >/dev/null 2>&1 || \
                (echo "Error: docker not found" && exit 1)
```

### Conditional execution

```makefile
target:
        @if [ -f config.mk ]; then \
                echo "Config found"; \
        else \
                echo "Using defaults"; \
        fi
```

### Loop over files

```makefile
process-all:
        @for f in $(SOURCES); do \
                echo "Processing $$f"; \
                process $$f; \
        done
```

### Create directory if missing

```makefile
$(BUILDDIR)/%.o: %.c | $(BUILDDIR)
        $(CC) -c $< -o $@

$(BUILDDIR):
        mkdir -p $@
```

### Atomic file creation

```makefile
# Write to temp, then move (safe update)
output.txt: input.txt
        process $< > $@.tmp
        mv $@.tmp $@
```

## Recipe Debugging

```makefile
# Dry run - show commands without executing
# make -n target

# Print database
# make -p

# Debug mode
# make -d target
# make --debug=all target
```

## Best Practices

1. **Use `@` for cosmetic echo** - Don't show echo commands
2. **Use `-` sparingly** - Only for truly optional commands
3. **Use `$(MAKE)` for recursion** - Preserves flags
4. **Combine commands with `&&`** - Fail fast
5. **Use `.ONESHELL` for complex scripts** - Or move to external script
6. **Export only needed variables** - Don't pollute environment
7. **Test recipes with `-n`** - Verify before running
