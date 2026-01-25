# Makefile Functions Reference

> Source: [GNU Make Manual - Functions for Transforming Text](https://www.gnu.org/software/make/manual/make.html#Functions)

## Function Call Syntax

```makefile
$(function arguments)
${function arguments}
```

Arguments separated by commas. Spaces after commas are significant.

## String Functions

### subst - Simple Substitution

```makefile
$(subst from,to,text)

# Example
$(subst ee,EE,feet on the street)
# Result: "fEEt on the strEEt"
```

### patsubst - Pattern Substitution

```makefile
$(patsubst pattern,replacement,text)

# Example
$(patsubst %.c,%.o,foo.c bar.c)
# Result: "foo.o bar.o"

# Shorthand for variables
$(var:pattern=replacement)
$(sources:.c=.o)
```

### strip - Remove Whitespace

```makefile
$(strip string)

# Example
$(strip   a  b   c   )
# Result: "a b c"
```

### findstring - Find Substring

```makefile
$(findstring find,in)

# Returns find if found, empty otherwise
$(findstring a,abc)      # "a"
$(findstring x,abc)      # ""
```

### filter - Select Matching Words

```makefile
$(filter pattern...,text)

# Example
sources := foo.c bar.c baz.s qux.h
c_sources := $(filter %.c,$(sources))
# Result: "foo.c bar.c"
```

### filter-out - Remove Matching Words

```makefile
$(filter-out pattern...,text)

# Example
objects := main.o foo.o test.o
prod_objects := $(filter-out test.o,$(objects))
# Result: "main.o foo.o"
```

### sort - Sort and Deduplicate

```makefile
$(sort list)

# Example
$(sort foo bar baz foo bar)
# Result: "bar baz foo"
```

### word - Select Nth Word

```makefile
$(word n,text)

# Example
$(word 2,foo bar baz)
# Result: "bar"
```

### wordlist - Select Word Range

```makefile
$(wordlist start,end,text)

# Example
$(wordlist 2,4,a b c d e f)
# Result: "b c d"
```

### words - Count Words

```makefile
$(words text)

# Example
$(words foo bar baz)
# Result: "3"
```

### firstword / lastword

```makefile
$(firstword text)
$(lastword text)

# Example
$(firstword foo bar baz)  # "foo"
$(lastword foo bar baz)   # "baz"
```

## File Name Functions

### dir - Directory Part

```makefile
$(dir names...)

# Example
$(dir src/foo.c hacks)
# Result: "src/ ./"
```

### notdir - File Name Part

```makefile
$(notdir names...)

# Example
$(notdir src/foo.c hacks)
# Result: "foo.c hacks"
```

### suffix - File Suffix

```makefile
$(suffix names...)

# Example
$(suffix src/foo.c src-1.0/bar.c hacks)
# Result: ".c .c"
```

### basename - Remove Suffix

```makefile
$(basename names...)

# Example
$(basename src/foo.c src-1.0/bar.c hacks)
# Result: "src/foo src-1.0/bar hacks"
```

### addsuffix - Add Suffix

```makefile
$(addsuffix suffix,names...)

# Example
$(addsuffix .c,foo bar)
# Result: "foo.c bar.c"
```

### addprefix - Add Prefix

```makefile
$(addprefix prefix,names...)

# Example
$(addprefix src/,foo bar)
# Result: "src/foo src/bar"
```

### join - Pairwise Join

```makefile
$(join list1,list2)

# Example
$(join a b,1 2 3)
# Result: "a1 b2 3"
```

### wildcard - Glob Expansion

```makefile
$(wildcard pattern)

# Example
$(wildcard *.c)          # All .c files
$(wildcard src/*.c)      # All .c in src/
$(wildcard src/*/*.c)    # .c in src subdirs
```

### realpath / abspath

```makefile
$(realpath names...)     # Canonical path (resolves symlinks)
$(abspath names...)      # Absolute path (no symlink resolution)
```

## Conditional Functions

### if - Conditional

```makefile
$(if condition,then-part)
$(if condition,then-part,else-part)

# Example
$(if $(DEBUG),debug-flags,release-flags)
```

### or - First Non-Empty

```makefile
$(or condition1,condition2,...)

# Example
CC := $(or $(CC),gcc)  # Use CC if set, else gcc
```

### and - All Non-Empty

```makefile
$(and condition1,condition2,...)

# Example
$(and $(CC),$(CFLAGS),ready)
# "ready" only if both CC and CFLAGS set
```

## Loop Functions

### foreach - Iterate Over List

```makefile
$(foreach var,list,text)

# Example
dirs := a b c
files := $(foreach dir,$(dirs),$(wildcard $(dir)/*.c))
```

### call - User-Defined Functions

```makefile
$(call function,arg1,arg2,...)

# Define function
reverse = $(2) $(1)

# Use it
$(call reverse,a,b)
# Result: "b a"
```

Inside function: `$(0)` is function name, `$(1)`, `$(2)` are arguments.

### let - Local Variables (GNU Make 4.4+)

```makefile
$(let var1 var2 ...,value1 value2 ...,text)

# Example
$(let a b,1 2,$(a) and $(b))
# Result: "1 and 2"
```

## Shell and Control Functions

### shell - Execute Command

```makefile
$(shell command)

# Example
git_hash := $(shell git rev-parse --short HEAD)
today := $(shell date +%Y-%m-%d)
```

### eval - Parse as Makefile

```makefile
$(eval text)

# Example - generate rules dynamically
define PROGRAM_template
$(1): $$($(1)_OBJS)
	$$(CC) -o $$@ $$^
endef

$(foreach prog,$(PROGRAMS),$(eval $(call PROGRAM_template,$(prog))))
```

### value - Unexpanded Value

```makefile
$(value variable)

# Example
FOO = $$PATH
# $(FOO) expands $PATH
# $(value FOO) returns "$$PATH"
```

### origin - Variable Origin

```makefile
$(origin variable)

# Returns: undefined, default, environment, environment override,
#          file, command line, override, automatic
```

### flavor - Variable Type

```makefile
$(flavor variable)

# Returns: undefined, recursive, simple
```

## Control Functions

### error - Abort with Message

```makefile
$(error text)

# Example
ifndef JAVA_HOME
$(error JAVA_HOME is not set)
endif
```

### warning - Print Warning

```makefile
$(warning text)

# Example
ifeq ($(DEBUG),1)
$(warning Building in debug mode)
endif
```

### info - Print Message

```makefile
$(info text)

# Example
$(info Building version $(VERSION))
```

## File Function

Read/write files directly:

```makefile
# Read file
$(file <filename)

# Write to file (overwrite)
$(file >filename,text)

# Append to file
$(file >>filename,text)
```

## Common Patterns

### Building file lists

```makefile
sources := $(wildcard src/*.c)
objects := $(patsubst src/%.c,build/%.o,$(sources))
```

### Conditional compilation flags

```makefile
CFLAGS := -Wall
CFLAGS += $(if $(DEBUG),-g -O0,-O2)
```

### Dynamic rule generation

```makefile
PROGRAMS := prog1 prog2

define make-program
$(1): $($(1)_OBJS)
	$$(CC) -o $$@ $$^
endef

$(foreach prog,$(PROGRAMS),$(eval $(call make-program,$(prog))))
```

### Safe file existence check

```makefile
ifneq ($(wildcard config.mk),)
include config.mk
endif
```
