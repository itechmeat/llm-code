# Makefile Syntax Reference

> Source: [GNU Make Manual - Writing Rules](https://www.gnu.org/software/make/manual/make.html#Rules)

## Rule Structure

Basic rule format:

```makefile
target … : prerequisites …
        recipe
        …
```

Alternative with semicolon:

```makefile
target : prerequisites ; recipe
        recipe
        …
```

**Critical:** Recipe lines MUST start with a TAB character, not spaces.

## Targets

- Usually file names to be generated (e.g., `main.o`, `program`)
- Can be action names (e.g., `clean`, `install`)
- First target in makefile becomes default goal
- Targets starting with `.` are not default unless contain `/`

Multiple targets in one rule:

```makefile
# Independent targets (each built separately)
prog1 prog2 : utils.o
        cc -o $@ $^

# Grouped targets (recipe creates all at once)
foo.h foo.c &: foo.y
        bison -d $<
```

## Prerequisites

**Normal prerequisites** - trigger rebuild if newer than target:

```makefile
main.o : main.c defs.h
```

**Order-only prerequisites** - must exist, but don't trigger rebuild:

```makefile
$(OBJDIR)/%.o : %.c | $(OBJDIR)
        $(CC) -c $< -o $@

$(OBJDIR):
        mkdir -p $@
```

Syntax: `target : normal-prereqs | order-only-prereqs`

## Prerequisite Types Summary

| Type              | Triggers Rebuild? | Use Case                 |
| ----------------- | ----------------- | ------------------------ |
| Normal (`:`)      | Yes, if newer     | Source files, headers    |
| Order-only (`\|`) | No                | Directories, setup tasks |

## Wildcards

Wildcard characters: `*`, `?`, `[…]`, `~`

```makefile
# In targets and prerequisites - expanded by Make
clean:
        rm -f *.o

print: *.c
        lpr -p $?
        touch print

# In variables - NOT expanded automatically
objects = *.o           # Literal "*.o"
objects := $(wildcard *.o)  # Expanded list
```

## VPATH - Directory Search

Search directories for prerequisites:

```makefile
# Search all prerequisites in these dirs
VPATH = src:../headers

# Pattern-specific search
vpath %.c src
vpath %.h ../headers
vpath %   foo:bar      # Match anything
vpath %.c              # Clear pattern search
vpath                  # Clear all vpath
```

## Double-Colon Rules

Independent rules for same target:

```makefile
newfile:: file1
        recipe1

newfile:: file2
        recipe2
```

Each rule executed if its prerequisites are newer.

## Static Pattern Rules

Apply pattern to explicit list:

```makefile
objects = foo.o bar.o

$(objects): %.o: %.c
        $(CC) -c $(CFLAGS) $< -o $@
```

Format: `targets : target-pattern: prereq-pattern`

## Multiple Rules for One Target

Prerequisites merge; only one recipe allowed:

```makefile
# OK - prerequisites merge
objects = foo.o bar.o
foo.o : defs.h
bar.o : defs.h test.h
$(objects) : config.h

# ERROR - multiple recipes
foo.o : foo.c
        $(CC) -c foo.c
foo.o : foo.c         # Warning: overriding recipe
        gcc -c foo.c
```

## Automatic Variables

| Variable         | Meaning                             |
| ---------------- | ----------------------------------- |
| `$@`             | Target file name                    |
| `$<`             | First prerequisite                  |
| `$^`             | All prerequisites (deduplicated)    |
| `$+`             | All prerequisites (with duplicates) |
| `$?`             | Prerequisites newer than target     |
| `$*`             | Stem in pattern rules               |
| `$%`             | Archive member name                 |
| `$(@D)`, `$(@F)` | Directory and file parts of `$@`    |

## Line Continuation

```makefile
# Long lines
objects = main.o foo.o bar.o \
          baz.o qux.o

# In recipes (each logical line runs in separate shell)
target:
        cd subdir && \
        $(MAKE)
```

## Comments

```makefile
# This is a comment
target: prereq  # End-of-line comment

# Comments in recipes are passed to shell
recipe:
        # Shell sees this comment
        echo "hello"
```

## Escaping Special Characters

```makefile
# Dollar sign
price = $$100           # Becomes "$100"
shell_var = $$HOME      # Shell variable, not Make variable

# Percent in pattern
files = a%b             # Literal % in file name
%.txt: $$(files)        # Use secondary expansion

# Hash/pound sign in variable value
hash := \#              # Must escape
comment := text$(hash)more
```

## Secondary Expansion

Enable late prerequisite expansion:

```makefile
.SECONDEXPANSION:

main_SRCS := main.c utils.c
lib_SRCS := lib.c api.c

main lib: $$(patsubst %.c,%.o,$$($$@_SRCS))
```

## Best Practices

1. **First target = default goal** - Make it `all` or `help`
2. **Use variables for file lists** - Easier maintenance
3. **Explicit prerequisites** - Don't rely on implicit rules alone
4. **Group related rules** - Organize by feature/component
5. **Document with comments** - Especially non-obvious dependencies
