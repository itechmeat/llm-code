# PostgreSQL Character Sets, Encoding & Collation

Character encoding, locale settings, and collation rules for text storage and comparison.

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Encoding** | How characters are stored (UTF8, LATIN1, etc.) |
| **Locale** | Regional settings (LC_COLLATE, LC_CTYPE) |
| **Collation** | Rules for sorting and comparing strings |
| **Provider** | Collation implementation (libc, ICU, builtin) |

## Database Encoding

### Set at Cluster Creation

```bash
# Set default encoding for cluster
initdb -E UTF8
initdb -E EUC_JP
initdb --locale=en_US.UTF-8
```

### Set at Database Creation

```bash
# Command line
createdb -E EUC_KR -T template0 --lc-collate=ko_KR.euckr --lc-ctype=ko_KR.euckr korean
```

```sql
-- SQL
CREATE DATABASE music
    LOCALE 'sv_SE.utf8'
    TEMPLATE template0;

CREATE DATABASE music2
    LOCALE 'sv_SE.iso885915'
    ENCODING LATIN9
    TEMPLATE template0;

CREATE DATABASE korean
    ENCODING 'EUC_KR'
    LC_COLLATE='ko_KR.euckr'
    LC_CTYPE='ko_KR.euckr'
    TEMPLATE template0;
```

**Important**: Always use `TEMPLATE template0` when specifying custom encoding/locale.

### Common Encodings

| Encoding | Description | Language | Server? | Bytes/Char |
|----------|-------------|----------|---------|------------|
| `UTF8` | Unicode, 8-bit | all | Yes | 1-4 |
| `SQL_ASCII` | unspecified | any | Yes | 1 |
| `EUC_JP` | Extended UNIX Code-JP | Japanese | Yes | 1-3 |
| `EUC_CN` | Extended UNIX Code-CN | Simplified Chinese | Yes | 1-3 |
| `EUC_KR` | Extended UNIX Code-KR | Korean | Yes | 1-3 |
| `LATIN1` | ISO 8859-1 | Western European | Yes | 1 |
| `LATIN2` | ISO 8859-2 | Central European | Yes | 1 |
| `LATIN9` | ISO 8859-15 | Western European | Yes | 1 |
| `WIN1251` | Windows CP1251 | Cyrillic | Yes | 1 |
| `WIN1252` | Windows CP1252 | Western European | Yes | 1 |
| `SJIS` | Shift JIS | Japanese | No (client only) | 1-2 |
| `BIG5` | Big Five | Traditional Chinese | No (client only) | 1-2 |
| `GBK` | Extended National Standard | Simplified Chinese | No (client only) | 1-2 |

**Warning**: `SQL_ASCII` performs no encoding validation. Data with invalid encoding may be stored, causing issues later. Avoid for new databases.

### Available Client Conversions

| Server Encoding | Available Client Encodings |
|-----------------|---------------------------|
| `UTF8` | All supported encodings |
| `LATIN1` | LATIN1, MULE_INTERNAL, UTF8 |
| `LATIN2` | LATIN2, MULE_INTERNAL, UTF8, WIN1250 |
| `EUC_JP` | EUC_JP, MULE_INTERNAL, SJIS, UTF8 |
| `EUC_KR` | EUC_KR, MULE_INTERNAL, UTF8 |
| `WIN1251` | WIN1251, ISO_8859_5, KOI8R, MULE_INTERNAL, UTF8, WIN866 |

### Query Encoding

```sql
SHOW server_encoding;
SHOW client_encoding;
```

## Client Encoding

### Set Client Encoding

```sql
SET CLIENT_ENCODING TO 'UTF8';
SET NAMES 'UTF8';  -- Standard SQL equivalent

SHOW client_encoding;
RESET client_encoding;
```

```bash
# psql
\encoding UTF8
\encoding  -- Show current
```

```c
// libpq
int PQsetClientEncoding(PGconn *conn, const char *encoding);
int enc = PQclientEncoding(conn);
```

### Encoding Conversion

```sql
-- Convert bytea between encodings
SELECT convert('\x746578745f696e5f75746638', 'UTF8', 'LATIN1');

-- Decode bytea to text
SELECT convert_from('\x746578745f696e5f75746638', 'UTF8');

-- Encode text to bytea
SELECT convert_to('some_text', 'UTF8');
```

### Encoding Functions

```sql
-- Encoding name to internal ID
SELECT pg_char_to_encoding('UTF8');  -- Returns 6

-- Internal ID to name
SELECT pg_encoding_to_char(6);  -- Returns 'UTF8'

-- Current client encoding
SELECT pg_client_encoding();
```

## Locale Settings

### Cluster-Level (initdb)

```bash
initdb --locale=en_US.UTF-8
initdb --locale-provider=icu --icu-locale=en

# Mix locale categories
initdb --locale=fr_CA --lc-monetary=en_US
```

### Database-Level

```sql
CREATE DATABASE mydb
    LOCALE 'en_US.UTF-8'
    LOCALE_PROVIDER = icu
    ICU_LOCALE = 'en-US'
    TEMPLATE template0;
```

### Locale Categories

| Category | Purpose | Fixed at DB creation? |
|----------|---------|----------------------|
| `LC_COLLATE` | String sort order | **Yes** |
| `LC_CTYPE` | Character classification | **Yes** |
| `LC_MESSAGES` | Message language | No (runtime) |
| `LC_MONETARY` | Currency formatting | No (runtime) |
| `LC_NUMERIC` | Number formatting | No (runtime) |
| `LC_TIME` | Date/time formatting | No (runtime) |

**Important**: `LC_COLLATE` and `LC_CTYPE` affect index sort order and **cannot be changed** after database creation.

### Locale Behavior Impact

Locale settings affect:
- Sort order in `ORDER BY` on text
- `upper()`, `lower()`, `initcap()` functions  
- Pattern matching (`LIKE`, `SIMILAR TO`, regex)
- `to_char()` family functions
- Index usage with `LIKE` clauses

**Performance**: Using locales other than `C` or `POSIX` slows character handling and may prevent index usage with `LIKE`. Use locales only when needed.

### Special Locales

| Locale | Behavior |
|--------|----------|
| `C` | Byte-order sorting, ASCII-only character classes |
| `POSIX` | Same as `C` |
| `C.UTF-8` | UTF-8 aware, Unicode character classes (builtin provider) |

## Collation Providers

### Comparison

| Provider | Source | Advantages | Limitations |
|----------|--------|------------|-------------|
| `builtin` | PostgreSQL | No dependencies, consistent | Only C, C.UTF-8, PG_UNICODE_FAST |
| `icu` | ICU library | Consistent across platforms, feature-rich | Requires ICU library |
| `libc` | OS locales | No extra dependencies | Platform-dependent behavior |

### builtin Provider

Available only for specific locales:

| Locale | Database Encoding | Behavior |
|--------|-------------------|----------|
| `C` | Any | Byte-order sorting, basic ASCII |
| `C.UTF-8` | UTF8 only | Unicode-aware, "POSIX Compatible" semantics |
| `PG_UNICODE_FAST` | UTF8 only | Unicode-aware, "Standard" semantics, full case mapping |

```sql
-- Using builtin provider
CREATE DATABASE mydb
    LOCALE_PROVIDER = builtin
    BUILTIN_LOCALE = 'C.UTF-8'
    TEMPLATE template0;
```

### icu Provider

ICU provides consistent behavior across platforms. Results may vary between ICU library versions.

```sql
-- ICU locale with database
CREATE DATABASE mydb
    LOCALE_PROVIDER = icu
    ICU_LOCALE = 'en-US'
    TEMPLATE template0;
```

### libc Provider

Uses operating system locales. **Same locale name may behave differently on different platforms.**

```bash
# List available libc locales
locale -a
```

### Creating Collations

#### libc Collations

```sql
CREATE COLLATION german (provider = libc, locale = 'de_DE');
CREATE COLLATION french (locale = 'fr_FR.utf8');  -- libc default
```

#### ICU Collations

```sql
CREATE COLLATION german (provider = icu, locale = 'de-DE');
CREATE COLLATION mycollation1 (provider = icu, locale = 'ja-JP');
CREATE COLLATION mycollation2 (provider = icu, locale = 'fr');
```

ICU accepts BCP 47 language tags (e.g., `de-DE`) or libc-style names (converted automatically):

```sql
CREATE COLLATION mycollation4 (provider = icu, locale = 'de_DE.utf8');
-- NOTICE: using standard form "de-DE" for locale "de_DE.utf8"
```

### Copy Existing Collations

```sql
CREATE COLLATION german FROM "de_DE";
CREATE COLLATION french FROM "fr-x-icu";
```

## ICU Collation Features

### Case Sensitivity

```sql
-- Case-insensitive (level 2 = ignore case)
CREATE COLLATION case_insensitive (
    provider = icu,
    deterministic = false,
    locale = 'und-u-ks-level2'
);
SELECT 'aB' = 'Ab' COLLATE case_insensitive;  -- true
```

### Accent Insensitivity

```sql
-- Ignore accents and case (level 1)
CREATE COLLATION ignore_accent_case (
    provider = icu,
    deterministic = false,
    locale = 'und-u-ks-level1'
);
SELECT 'Å' = 'A' COLLATE ignore_accent_case;  -- true
```

### Numeric Sorting

```sql
-- Treat digits numerically
CREATE COLLATION num_ignore_punct (
    provider = icu,
    deterministic = false,
    locale = 'und-u-ka-shifted-kn'
);
SELECT 'id-45' < 'id-123' COLLATE num_ignore_punct;  -- true
```

### Phone Book Order

```sql
CREATE COLLATION "de-u-co-phonebk-x-icu" (provider = icu, locale = 'de-u-co-phonebk');
```

### Case Order

```sql
-- Uppercase first
CREATE COLLATION upper_first (provider = icu, locale = 'und-u-kf-upper');
SELECT 'B' < 'b' COLLATE upper_first;  -- true
```

### Custom Tailoring Rules

```sql
CREATE COLLATION custom (provider = icu, locale = 'und', rules = '&V << w <<< W');
```

### ICU Collation Keys

| Key | Description | Example |
|-----|-------------|---------|
| `co` | Collation type | `de-u-co-phonebk` |
| `ks` | Comparison strength | `und-u-ks-level2` |
| `kn` | Numeric ordering | `en-u-kn` |
| `kf` | Case first | `und-u-kf-upper` |
| `ka` | Alternate handling | `und-u-ka-shifted` |
| `kr` | Reorder scripts | `en-u-kr-grek-latn` |

### Strength Levels

| Level | Ignores | Example |
|-------|---------|---------|
| `level1` (primary) | Case, accents | `e = E = é` |
| `level2` (secondary) | Case | `e = E ≠ é` |
| `level3` (tertiary) | Nothing | `e ≠ E ≠ é` |
| `level4` (quaternary) | Punctuation | Fine distinctions |
| `identic` | Nothing | Byte-level |

```sql
CREATE COLLATION level3 (provider = icu, deterministic = false, locale = 'und-u-ka-shifted-ks-level3');
CREATE COLLATION level4 (provider = icu, deterministic = false, locale = 'und-u-ka-shifted-ks-level4');

SELECT 'x-y' = 'x_y' COLLATE level3;  -- true (punctuation ignored)
SELECT 'x-y' = 'x_y' COLLATE level4;  -- false
```

## Nondeterministic Collations

Required for case/accent insensitive comparisons:

```sql
CREATE COLLATION ndcoll (provider = icu, locale = 'und', deterministic = false);
```

### Deterministic vs Nondeterministic

| Type | Comparison | Use Case |
|------|------------|----------|
| **Deterministic** | Byte-by-byte, 'x' ≠ 'X' | Default, indexes work normally |
| **Nondeterministic** | Semantic, 'x' = 'X' possible | Case/accent insensitive |

### Limitations of Nondeterministic Collations

- ❌ `LIKE` / `SIMILAR TO` pattern matching not supported
- ❌ Hash indexes may not work correctly
- ❌ Hash joins may produce incorrect results
- ❌ `DISTINCT` may behave unexpectedly
- ⚠️ B-tree indexes work but with semantic equality

```sql
-- This will ERROR with nondeterministic collation
SELECT * FROM t WHERE name LIKE 'foo%' COLLATE case_insensitive;
-- ERROR: nondeterministic collations are not supported for LIKE
```

## Using Collations

### In Column Definitions

```sql
CREATE TABLE test1 (
    a text COLLATE "de_DE",
    b text COLLATE "es_ES"
);
```

### In Queries

```sql
SELECT * FROM test1 ORDER BY a COLLATE "C";
SELECT a < 'foo' COLLATE "de_DE" FROM test1;
```

### In Indexes

```sql
-- Default collation index
CREATE INDEX test1c_content_index ON test1c (content);

-- Specific collation index
CREATE INDEX test1c_content_y_index ON test1c (content COLLATE "y");
```

### Conflicting Collations

```sql
-- ERROR: conflicting collations
SELECT a < b FROM test1;  -- a has de_DE, b has es_ES

-- Fix: explicit collation
SELECT a COLLATE "de_DE" < b COLLATE "de_DE" FROM test1;
```

## Managing Collations

### List Collations

```sql
SELECT * FROM pg_collation;

-- psql
\dO
```

### Alter Collation

```sql
ALTER COLLATION german RENAME TO german_de;
ALTER COLLATION german OWNER TO admin;
ALTER COLLATION german SET SCHEMA myschema;

-- Refresh after OS upgrade
ALTER COLLATION "de_DE" REFRESH VERSION;
```

### Drop Collation

```sql
DROP COLLATION german;
DROP COLLATION IF EXISTS german CASCADE;
```

### Collation Version Warnings

After OS/ICU upgrades, collation versions may mismatch:

```sql
WARNING: collation "xx-x-icu" has version mismatch
DETAIL: The collation in the database was created using version 1.2.3.4, 
        but the operating system provides version 2.3.4.5.
```

Fix by rebuilding indexes and refreshing:

```sql
REINDEX DATABASE mydb;
ALTER DATABASE mydb REFRESH COLLATION VERSION;
```

## Character Encoding Conversion

### Create Conversion

```sql
CREATE CONVERSION myconv FOR 'UTF8' TO 'LATIN1' FROM myfunc;
CREATE DEFAULT CONVERSION myconv FOR 'UTF8' TO 'LATIN1' FROM myfunc;
```

### Drop Conversion

```sql
DROP CONVERSION myconv;
```

## Unicode Functions

### Normalize Unicode

```sql
-- Normalize to NFC form
SELECT normalize(U&'\0061\0308bc', NFC);  -- ä + bc

-- Check normalization
SELECT U&'\0061\0308bc' IS NFD NORMALIZED;  -- true
```

### Unicode Escapes

```sql
-- Evaluate Unicode escapes
SELECT unistr('d\0061t\+000061');  -- 'data'
SELECT unistr('d\u0061t\U00000061');  -- 'data'
```

### ASCII Conversion

```sql
SELECT to_ascii('Karél');  -- 'Karel' (removes accents)
```

## Text Search Locale Integration

### Create Language-Specific Config

```sql
CREATE TEXT SEARCH CONFIGURATION fr (COPY = french);

-- Add unaccent for accent-insensitive search
ALTER TEXT SEARCH CONFIGURATION fr
    ALTER MAPPING FOR hword, hword_part, word
    WITH unaccent, french_stem;

SELECT to_tsvector('fr', 'Hôtels de la Mer');
-- 'hotel':1 'mer':4
```

### Dictionary for Specific Language

```sql
CREATE TEXT SEARCH DICTIONARY my_russian (
    template = snowball,
    language = russian,
    stopwords = myrussian
);
```

## Quick Reference

### Locale Selection Scope

From broadest to narrowest (each overrides the previous):

1. **OS environment** → defaults for `initdb`
2. **initdb options** → cluster-wide defaults
3. **CREATE DATABASE** → per-database settings
4. **Column COLLATE** → per-column collation
5. **Query COLLATE** → per-expression collation

### Encoding Best Practices

- Use UTF8 for new databases (universal support)
- Match client and server encoding when possible
- Use `TEMPLATE template0` for custom encoding
- Avoid SQL_ASCII (no validation)
- For maximum performance with ASCII data, use `C` locale

### Collation Best Practices

- Use ICU for cross-platform consistency
- Use `builtin` provider for minimal dependencies
- Create explicit collations rather than relying on OS locales
- Use deterministic collations for indexed columns with LIKE
- Test collation behavior after OS/ICU upgrades
- Avoid mixing stripped and non-stripped locale names

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Encoding mismatch | Client/server encoding differ | Set client_encoding |
| Collation not found | OS locale not installed | Install locale or use ICU |
| Version mismatch | OS/ICU upgraded | REINDEX + REFRESH VERSION |
| Conflicting collations | Mixed column collations | Explicit COLLATE clause |

## See Also

- [PostgreSQL Character Set Support](https://www.postgresql.org/docs/current/multibyte.html)
- [PostgreSQL Collation Support](https://www.postgresql.org/docs/current/collation.html)
- [PostgreSQL Locale Support](https://www.postgresql.org/docs/current/locale.html)
- [ICU Collation Specification](https://unicode.org/reports/tr35/tr35-collation.html)
