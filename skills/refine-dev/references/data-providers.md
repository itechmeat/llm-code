# Data Providers

Data providers are the core abstraction layer in Refine for backend communication. They handle all CRUD operations through a unified interface.

## Interface Methods

| Method | Purpose | Key Parameters |
|--------|---------|----------------|
| `getList` | Fetch paginated list | resource, pagination, filters, sorters |
| `getOne` | Fetch single record | resource, id |
| `getMany` | Fetch multiple by IDs | resource, ids |
| `create` | Create new record | resource, variables |
| `update` | Update existing | resource, id, variables |
| `deleteOne` | Delete single | resource, id |
| `deleteMany` | Delete multiple | resource, ids |
| `createMany` | Bulk create | resource, variables[] |
| `updateMany` | Bulk update | resource, ids, variables |

## Available Providers

### REST API
- `@refinedev/simple-rest` — Generic REST API (recommended for custom APIs)
- `@refinedev/nestjsx-crud` — NestJS with @nestjsx/crud

### GraphQL
- `@refinedev/graphql` — Generic GraphQL with URQL
- `@refinedev/hasura` — Hasura GraphQL Engine

### Backend-as-a-Service
- `@refinedev/supabase` — Supabase (PostgreSQL + Auth + Storage)
- `@refinedev/appwrite` — Appwrite backend
- `@refinedev/firebase` — Firebase/Firestore

### CMS
- `@refinedev/strapi-v4` — Strapi v4
- `@refinedev/airtable` — Airtable

## Basic Usage

```tsx
import { Refine } from "@refinedev/core";
import dataProvider from "@refinedev/simple-rest";

const API_URL = "https://api.example.com";

function App() {
  return (
    <Refine
      dataProvider={dataProvider(API_URL)}
      // ...
    />
  );
}
```

## Multiple Data Providers

```tsx
<Refine
  dataProvider={{
    default: simpleRestDataProvider("https://api.example.com"),
    cms: strapiDataProvider("https://cms.example.com"),
  }}
  resources={[
    { name: "posts", meta: { dataProviderName: "cms" } },
    { name: "users" }, // uses "default"
  ]}
/>
```

## Custom Data Provider

```tsx
import { DataProvider } from "@refinedev/core";

const customDataProvider: DataProvider = {
  getList: async ({ resource, pagination, filters, sorters }) => {
    const { current = 1, pageSize = 10 } = pagination ?? {};
    
    const response = await fetch(
      `${API_URL}/${resource}?_page=${current}&_limit=${pageSize}`
    );
    const data = await response.json();
    const total = Number(response.headers.get("x-total-count"));
    
    return { data, total };
  },
  
  getOne: async ({ resource, id }) => {
    const response = await fetch(`${API_URL}/${resource}/${id}`);
    const data = await response.json();
    return { data };
  },
  
  create: async ({ resource, variables }) => {
    const response = await fetch(`${API_URL}/${resource}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(variables),
    });
    const data = await response.json();
    return { data };
  },
  
  update: async ({ resource, id, variables }) => {
    const response = await fetch(`${API_URL}/${resource}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(variables),
    });
    const data = await response.json();
    return { data };
  },
  
  deleteOne: async ({ resource, id }) => {
    const response = await fetch(`${API_URL}/${resource}/${id}`, {
      method: "DELETE",
    });
    const data = await response.json();
    return { data };
  },
  
  getMany: async ({ resource, ids }) => {
    const data = await Promise.all(
      ids.map(async (id) => {
        const response = await fetch(`${API_URL}/${resource}/${id}`);
        return response.json();
      })
    );
    return { data };
  },
  
  deleteMany: async ({ resource, ids }) => {
    const data = await Promise.all(
      ids.map(async (id) => {
        const response = await fetch(`${API_URL}/${resource}/${id}`, {
          method: "DELETE",
        });
        return response.json();
      })
    );
    return { data };
  },
  
  createMany: async ({ resource, variables }) => {
    const data = await Promise.all(
      variables.map(async (vars) => {
        const response = await fetch(`${API_URL}/${resource}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(vars),
        });
        return response.json();
      })
    );
    return { data };
  },
  
  updateMany: async ({ resource, ids, variables }) => {
    const data = await Promise.all(
      ids.map(async (id) => {
        const response = await fetch(`${API_URL}/${resource}/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(variables),
        });
        return response.json();
      })
    );
    return { data };
  },
  
  getApiUrl: () => API_URL,
};
```

## Response Formats

### getList Response
```ts
{
  data: TData[];
  total: number;
}
```

### getOne Response
```ts
{
  data: TData;
}
```

### create/update/delete Response
```ts
{
  data: TData;
}
```

## Meta Parameter

All methods accept a `meta` parameter for custom options:

```tsx
const { data } = useList({
  resource: "posts",
  meta: {
    headers: { "X-Custom-Header": "value" },
    // Provider-specific options
  },
});
```

## React Query Integration

Data providers integrate with React Query (TanStack Query):
- Automatic caching
- Background refetching
- Optimistic updates
- Query invalidation on mutations
