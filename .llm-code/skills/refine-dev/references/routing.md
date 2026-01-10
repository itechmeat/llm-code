# Routing

Refine integrates with React Router for navigation. The `@refinedev/react-router` package provides the router bindings.

## Installation

```bash
npm install @refinedev/react-router react-router-dom
```

## Basic Setup

```tsx
import { Refine } from "@refinedev/core";
import routerProvider from "@refinedev/react-router";
import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import dataProvider from "@refinedev/simple-rest";

function App() {
  return (
    <BrowserRouter>
      <Refine
        routerProvider={routerProvider}
        dataProvider={dataProvider("https://api.example.com")}
        resources={[
          {
            name: "posts",
            list: "/posts",
            create: "/posts/create",
            edit: "/posts/edit/:id",
            show: "/posts/show/:id",
          },
        ]}
      >
        <Routes>
          <Route element={<Layout><Outlet /></Layout>}>
            <Route path="/posts" element={<PostList />} />
            <Route path="/posts/create" element={<PostCreate />} />
            <Route path="/posts/edit/:id" element={<PostEdit />} />
            <Route path="/posts/show/:id" element={<PostShow />} />
          </Route>
        </Routes>
      </Refine>
    </BrowserRouter>
  );
}
```

## Navigation Hooks

### useNavigation

Navigate to resource actions:

```tsx
import { useNavigation } from "@refinedev/core";

const MyComponent = () => {
  const { list, create, edit, show, clone, goBack } = useNavigation();

  return (
    <>
      <button onClick={() => list("posts")}>Go to Posts</button>
      <button onClick={() => create("posts")}>Create Post</button>
      <button onClick={() => edit("posts", 1)}>Edit Post #1</button>
      <button onClick={() => show("posts", 1)}>Show Post #1</button>
      <button onClick={() => clone("posts", 1)}>Clone Post #1</button>
      <button onClick={() => goBack()}>Go Back</button>
    </>
  );
};
```

### useGo

Lower-level navigation with query params:

```tsx
import { useGo } from "@refinedev/core";

const MyComponent = () => {
  const go = useGo();

  return (
    <>
      {/* Navigate with path */}
      <button
        onClick={() =>
          go({
            to: "/posts",
            query: { status: "published" },
            type: "push", // "push" | "replace" | "path"
          })
        }
      >
        Published Posts
      </button>

      {/* Navigate with resource */}
      <button
        onClick={() =>
          go({
            to: {
              resource: "posts",
              action: "edit",
              id: 1,
            },
            query: { tab: "comments" },
          })
        }
      >
        Edit Post
      </button>

      {/* Keep existing query params */}
      <button
        onClick={() =>
          go({
            to: "/posts",
            query: { page: 2 },
            options: { keepQuery: true },
          })
        }
      >
        Next Page
      </button>
    </>
  );
};
```

### useGo Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `to` | string \| object | Path or resource object |
| `query` | object | Query parameters |
| `type` | "push" \| "replace" \| "path" | Navigation type |
| `hash` | string | URL hash |
| `options.keepQuery` | boolean | Merge with existing query |
| `options.keepHash` | boolean | Keep existing hash |

### useGetToPath

Get path without navigating:

```tsx
import { useGetToPath } from "@refinedev/core";

const MyComponent = () => {
  const getToPath = useGetToPath();

  const editPath = getToPath({
    resource: { name: "posts" },
    action: "edit",
    meta: { id: 1 },
  });

  // editPath = "/posts/edit/1"
};
```

### useParsed

Parse current route:

```tsx
import { useParsed } from "@refinedev/core";

const MyComponent = () => {
  const { resource, action, id, params, pathname } = useParsed();

  // On /posts/edit/1?status=draft
  // resource: { name: "posts", ... }
  // action: "edit"
  // id: "1"
  // params: { status: "draft" }
  // pathname: "/posts/edit/1"
};
```

### useResourceParams

Get resource info from current route:

```tsx
import { useResourceParams } from "@refinedev/core";

const MyComponent = () => {
  const { resource, action, id } = useResourceParams();

  // Useful in page components to know which resource/action is active
};
```

## URL Sync

### Sync Table State

```tsx
<Refine
  options={{
    syncWithLocation: true, // Enable global URL sync
  }}
/>

// Table state syncs to URL:
// /posts?current=2&pageSize=10&sorters[0][field]=title&sorters[0][order]=asc
```

### Manual Sync in useTable

```tsx
const table = useTable({
  refineCoreProps: {
    syncWithLocation: true,
  },
});
```

## Protected Routes

```tsx
import { Authenticated } from "@refinedev/core";
import { Navigate, Outlet } from "react-router-dom";

<Routes>
  {/* Public routes */}
  <Route path="/login" element={<LoginPage />} />
  
  {/* Protected routes */}
  <Route
    element={
      <Authenticated fallback={<Navigate to="/login" />}>
        <Layout>
          <Outlet />
        </Layout>
      </Authenticated>
    }
  >
    <Route path="/posts" element={<PostList />} />
    <Route path="/posts/create" element={<PostCreate />} />
    {/* ... */}
  </Route>
</Routes>
```

## Catch-All / 404 Route

```tsx
import { ErrorComponent } from "@refinedev/mantine";

<Routes>
  {/* ... other routes */}
  <Route path="*" element={<ErrorComponent />} />
</Routes>
```

## Index Redirect

```tsx
import { NavigateToResource } from "@refinedev/react-router";

<Routes>
  <Route index element={<NavigateToResource resource="posts" />} />
  {/* ... */}
</Routes>

// Redirects "/" to the list page of "posts" resource
```

## Custom Route Params

Resources can have custom parameters:

```tsx
// Resource definition
{
  name: "posts",
  list: "/:tenantId/posts",
  edit: "/:tenantId/posts/:id/edit",
}

// Navigation with meta
const { edit } = useNavigation();
edit("posts", 1, undefined, { tenantId: "acme" });
// → /acme/posts/1/edit

// Using useGo
go({
  to: {
    resource: "posts",
    action: "edit",
    id: 1,
    meta: { tenantId: "acme" },
  },
});
```

## Route-Based Action Detection

Refine auto-detects the action based on route:

```tsx
// In PostEdit component (rendered at /posts/edit/:id)
const { action } = useResourceParams();
// action = "edit"

// useForm auto-detects action
const form = useForm(); // Automatically uses "edit" action
```
