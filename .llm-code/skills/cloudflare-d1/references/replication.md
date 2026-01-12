# D1 Read Replication (Sessions API)

## Overview

Read Replication creates database replicas in different regions to reduce read latency. Cloudflare automatically creates replicas in all supported regions.

**Replica regions**:

- WEUR (Western Europe)
- EEUR (Eastern Europe)
- WNAM (Western North America)
- ENAM (Eastern North America)
- APAC (Asia Pacific)
- OC (Oceania)

---

## Sessions API

To use read replication, you need to use Sessions API.

### Basic usage

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Get bookmark from previous request (if any)
    const bookmark = request.headers.get("x-d1-bookmark") ?? "first-unconstrained";

    // Create session
    const session = env.DB.withSession(bookmark);

    // Execute queries through session
    const { results } = await session.prepare("SELECT * FROM users").run();

    // Return new bookmark for next request
    const response = Response.json(results);
    response.headers.set("x-d1-bookmark", session.getBookmark() ?? "");

    return response;
  },
};
```

---

## Constraints

### first-unconstrained (default)

```typescript
const session = env.DB.withSession("first-unconstrained");
```

- Queries go to **any replica** (closest to user)
- Minimum read latency
- Data may be slightly stale (eventual consistency)

### first-primary

```typescript
const session = env.DB.withSession("first-primary");
```

- All queries go to **primary** instance
- Guarantees freshest data
- Higher latency (primary in one region)

### Bookmark from previous request

```typescript
const previousBookmark = request.headers.get("x-d1-bookmark");
const session = env.DB.withSession(previousBookmark ?? "first-unconstrained");
```

- Guarantees **read-your-writes** consistency
- Replica will show data no older than bookmark

---

## Patterns

### Read-Your-Writes Pattern

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Get bookmark from cookie/header
    const bookmark = getCookie(request, "d1-bookmark") ?? "first-unconstrained";
    const session = env.DB.withSession(bookmark);

    if (request.method === "POST") {
      // Write goes to primary
      const body = await request.json();
      await session.prepare("INSERT INTO posts (title) VALUES (?)").bind(body.title).run();
    }

    // Read can go to replica, but no older than bookmark
    const { results } = await session.prepare("SELECT * FROM posts ORDER BY id DESC LIMIT 10").run();

    const response = Response.json(results);
    // Save bookmark for next request
    response.headers.set("Set-Cookie", `d1-bookmark=${session.getBookmark()}; Path=/`);

    return response;
  },
};
```

### Separate Read/Write Connections

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "GET") {
      // Reads — any replica
      const session = env.DB.withSession("first-unconstrained");
      const { results } = await session.prepare("SELECT * FROM products").run();
      return Response.json(results);
    }

    // Writes — primary
    const session = env.DB.withSession("first-primary");
    await session.prepare("INSERT INTO orders ...").run();

    return new Response("Created", { status: 201 });
  },
};
```

---

## Session Methods

### withSession(constraint)

```typescript
const session = env.DB.withSession(bookmark);
```

Returns `D1DatabaseSession` with methods:

- `prepare(sql)` — create prepared statement
- `batch([...stmts])` — batch operations
- `getBookmark()` — get current bookmark

### getBookmark()

```typescript
const bookmark = session.getBookmark();
// bookmark: string | null
```

Call **after** executing queries to get current bookmark.

---

## Observability

### Meta object

```typescript
const { results, meta } = await session.prepare("SELECT ...").run();

console.log({
  region: meta.served_by_region, // "WEUR"
  isPrimary: meta.served_by_primary, // true/false
});
```

### Dashboard

In Cloudflare Dashboard → D1 → Metrics:

- Breakdown by region
- Primary vs replica traffic

---

## When to Use

| Scenario                  | Constraint                       |
| ------------------------- | -------------------------------- |
| Read-heavy public content | `first-unconstrained`            |
| Dashboard after write     | Save bookmark                    |
| Financial operations      | `first-primary`                  |
| Global users              | `first-unconstrained` + bookmark |

---

## Limitations

- **Writes always go to primary** — replication does not speed up writes
- **Eventual consistency** — replicas may lag by seconds
- **Bookmarks are temporary** — do not store longer than few minutes

---

## Enabling Read Replication

Read replication is enabled automatically when using Sessions API. No separate configuration or payment required.

Check status:

```bash
npx wrangler d1 info my-database
```

Look for `read_replication: enabled` in output.
