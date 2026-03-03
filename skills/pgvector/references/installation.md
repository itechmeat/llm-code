# Installation (pgvector)

pgvector is a PostgreSQL extension. The upstream README indicates support for Postgres 13+.

## Build from source (Linux/macOS)

```bash
cd /tmp
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install  # may need sudo
```

### Multiple Postgres installs

- Point the build to the correct `pg_config`:

```bash
export PG_CONFIG=/path/to/pg_config
make clean
make
sudo --preserve-env=PG_CONFIG make install
```

## Build on Windows

- Use the x64 Native Tools Command Prompt as Administrator.

```batch
set "PGROOT=C:\Program Files\PostgreSQL\18"
cd %TEMP%
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win
nmake /F Makefile.win install
```

## Common build issues

- Missing `postgres.h`:
  - Linux: install server dev headers (`postgresql-server-dev-<major>`)
  - Windows: verify `PGROOT` points to the correct install
- Portability: `-march=native` can break when moving binaries between CPUs.
  - Build with `make OPTFLAGS=""` for portable binaries.

## Packaging / alternative install methods

- Docker image (based on official Postgres image)
- Homebrew: `brew install pgvector` (for specific Postgres formulas)
- PGXN: `pgxn install vector`
- Debian/Ubuntu: install `postgresql-<major>-pgvector` from PostgreSQL APT repo
- RHEL/Fedora: `dnf install pgvector_<major>` from PostgreSQL Yum repo
- FreeBSD: `pkg install postgresql17-pgvector` (example)
- Alpine: `apk add postgresql-pgvector`
- Conda: `conda install -c conda-forge pgvector`

## Enable

- Per database:
  - `CREATE EXTENSION vector;`
