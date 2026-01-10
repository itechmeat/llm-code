# Makefile Implicit Rules Reference

> Source: [GNU Make Manual - Using Implicit Rules](https://www.gnu.org/software/make/manual/make.html#Implicit-Rules)

## What Are Implicit Rules?

Built-in rules that make knows how to build common file types:

```makefile
# You write:
prog: main.o utils.o
        $(CC) -o $@ $^

# Make automatically knows:
# main.o comes from main.c using cc -c
# utils.o comes from utils.c using cc -c
```

## Common Built-in Rules

### C Compilation

```makefile
# .c → .o
%.o: %.c
        $(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# .c → executable (single file)
%: %.c
        $(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) $< $(LDLIBS) -o $@
```

### C++ Compilation

```makefile
# .cc/.cpp/.C → .o
%.o: %.cc
        $(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@
```

### Other Languages

```makefile
# Fortran: .f → .o
# Pascal: .p → .o
# Assembly: .s → .o
# Yacc: .y → .c
# Lex: .l → .c
```

## Variables Used by Implicit Rules

### Program Names

| Variable | Default | Purpose      |
| -------- | ------- | ------------ |
| `CC`     | `cc`    | C compiler   |
| `CXX`    | `g++`   | C++ compiler |
| `AS`     | `as`    | Assembler    |
| `AR`     | `ar`    | Archiver     |
| `LEX`    | `lex`   | Lex          |
| `YACC`   | `yacc`  | Yacc         |
| `RM`     | `rm -f` | File removal |

### Flags

| Variable   | Purpose                       |
| ---------- | ----------------------------- |
| `CFLAGS`   | C compiler flags              |
| `CXXFLAGS` | C++ compiler flags            |
| `CPPFLAGS` | C preprocessor flags (-I, -D) |
| `LDFLAGS`  | Linker flags (-L)             |
| `LDLIBS`   | Libraries (-l)                |
| `ARFLAGS`  | Archiver flags                |

### Customize Built-in Rules

```makefile
CC := gcc
CFLAGS := -Wall -O2
CPPFLAGS := -I./include -DDEBUG
LDFLAGS := -L./lib
LDLIBS := -lm -lpthread
```

## Pattern Rules

Define custom implicit rules:

```makefile
# Pattern rule syntax
%.o: %.c
        $(CC) -c $(CFLAGS) $< -o $@

# Multiple prerequisites
%.o: %.c %.h
        $(CC) -c $(CFLAGS) $< -o $@

# Multiple targets (grouped)
%.tab.c %.tab.h: %.y
        bison -d $<
```

### Pattern Rule Variables

| Variable | Meaning                  |
| -------- | ------------------------ |
| `$@`     | Target file              |
| `$<`     | First prerequisite       |
| `$^`     | All prerequisites        |
| `$*`     | Stem (part matched by %) |
| `$(@D)`  | Directory of target      |
| `$(@F)`  | File part of target      |

### Stem Matching

```makefile
# Rule: %.o: %.c
# Target: src/foo.o
# $* = src/foo (the stem)
# Looking for: src/foo.c
```

## Static Pattern Rules

Apply pattern to explicit list of targets:

```makefile
objects := foo.o bar.o baz.o

$(objects): %.o: %.c
        $(CC) -c $(CFLAGS) $< -o $@
```

Advantage: More control, faster matching, no accidental matches.

### With Filter

```makefile
files := foo.c bar.c baz.s qux.h

$(filter %.o,$(files:.c=.o)): %.o: %.c
        $(CC) -c $< -o $@
```

## Suffix Rules (Old Style)

Legacy syntax, prefer pattern rules:

```makefile
# Double-suffix: .c → .o
.c.o:
        $(CC) -c $<

# Single-suffix: anything → .c
.c:
        $(CC) $< -o $@

# Define suffixes
.SUFFIXES: .c .o .h
```

## Implicit Rule Search

How Make finds applicable rules:

1. Look for explicit rule with recipe
2. Look for pattern rule matching target
3. Check if prerequisites exist or can be made
4. First applicable rule wins

### Rule Ordering

Rules are tried in order:

1. Pattern rules defined in makefile
2. Built-in rules
3. Match-anything rules (%)

### Canceling Rules

```makefile
# Cancel specific implicit rule
%.o: %.c

# Cancel all built-in rules
.SUFFIXES:
MAKEFLAGS += -r
```

## Chains of Implicit Rules

Make can chain rules:

```makefile
# Given: foo.y
# Make can: foo.y → foo.c → foo.o → foo

# Intermediate files are auto-deleted
# Mark as precious to keep:
.PRECIOUS: %.c
```

### .INTERMEDIATE and .SECONDARY

```makefile
# Explicitly mark as intermediate
.INTERMEDIATE: generated.c

# Keep intermediate (don't delete)
.SECONDARY: generated.c
.SECONDARY:              # Keep all
```

## Match-Anything Rules

Pattern with just `%`:

```makefile
# Last-resort rule
%:
        @echo "Don't know how to make $@"

# Terminal rule (can't chain further)
%:: default-recipe
```

## Automatic Prerequisites

Generate dependencies automatically:

```makefile
# Generate .d files with gcc
%.d: %.c
        $(CC) -MM $(CPPFLAGS) $< > $@

# Include generated dependencies
-include $(sources:.c=.d)
```

Modern approach:

```makefile
CFLAGS += -MMD -MP
-include $(objects:.o=.d)
```

## Common Custom Rules

### Documentation

```makefile
%.html: %.md
        pandoc -o $@ $<

%.pdf: %.tex
        pdflatex $<
```

### Archive Files

```makefile
%.tar.gz: %
        tar czf $@ $<

%.zip: %
        zip -r $@ $<
```

### Code Generation

```makefile
%.pb.go: %.proto
        protoc --go_out=. $<

%_generated.py: %.yaml
        python generate.py $< > $@
```

## Best Practices

1. **Prefer pattern rules over suffix rules** - More readable
2. **Use static patterns for explicit lists** - Faster, clearer
3. **Set implicit variables** - `CC`, `CFLAGS`, etc.
4. **Generate dependencies automatically** - `-MMD -MP`
5. **Cancel unused implicit rules** - Performance
6. **Mark precious intermediates** - If you need them

```makefile
# Optimized implicit rule setup
MAKEFLAGS += -rR          # Disable built-in rules
.SUFFIXES:                # Clear suffix list

CC := gcc
CFLAGS := -Wall -O2 -MMD -MP

%.o: %.c
        $(CC) $(CFLAGS) -c $< -o $@

-include $(objects:.o=.d)
```
