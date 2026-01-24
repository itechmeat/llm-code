# Encryption

Native encryption at rest using AEAD algorithms. Page-level encryption with ~6% read and ~14% write overhead.

## Generate Key

```bash
# 256-bit key (for AEGIS-256, AES-256-GCM)
openssl rand -hex 32

# 128-bit key (for AEGIS-128, AES-128-GCM)
openssl rand -hex 16
```

**Store key securely!** Lost key = lost data.

## Create Encrypted Database

```bash
tursodb --experimental-encryption "file:encrypted.db?cipher=aegis256&hexkey=YOUR_HEX_KEY"
```

```sql
CREATE TABLE secrets (id INT, data TEXT);
INSERT INTO secrets VALUES (1, 'sensitive information');
```

## Open Encrypted Database

```bash
tursodb --experimental-encryption "file:encrypted.db?cipher=aegis256&hexkey=YOUR_HEX_KEY"
```

## Supported Ciphers

### AEGIS (Recommended)

| Cipher     | Key Size | Use Case                |
| ---------- | -------- | ----------------------- |
| aegis256   | 256-bit  | Default recommendation  |
| aegis128l  | 128-bit  | Balanced performance    |
| aegis256x4 | 256-bit  | Max speed (4x parallel) |

### AES-GCM (Compliance)

| Cipher    | Key Size | Use Case           |
| --------- | -------- | ------------------ |
| aes256gcm | 256-bit  | NIST compliance    |
| aes128gcm | 128-bit  | 128-bit compliance |

## URI Format

```text
file:database.db?cipher=CIPHER&hexkey=HEX_KEY
```

Examples:

```text
file:db.db?cipher=aegis256&hexkey=2d7a30108d3eb3e45c90a732...
file:db.db?cipher=aes128gcm&hexkey=5f3e2a8c9b1d4f6e...
```

## What's Encrypted

- ✅ All database pages
- ✅ Database file
- ✅ WAL file
- ❌ Database header (first 100 bytes)
