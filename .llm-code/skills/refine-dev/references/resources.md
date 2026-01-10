# Resources

Resources are the main building blocks of a Refine app. A resource represents an entity in your API (e.g., `/posts`, `/users`) and connects data from the API to pages in your app.

## Basic Definition

```tsx
import { Refine } from "@refinedev/core";

<Refine
  dataProvider={dataProvider("https://api.example.com")}
  resources={[
    {
      name: "posts",
      list: "/posts",
      create: "/posts/create",
      edit: "/posts/edit/:id",
      show: "/posts/show/:id",
    },
    {
      name: "users",
      list: "/users",
      show: "/users/show/:id",
    },
  ]}
/>
```

## Resource Properties

### name (required)

The API endpoint name. Used for data provider requests:
- `name: "posts"` → `GET /posts`, `POST /posts`, etc.

### identifier

Differentiates resources with the same name but different configurations:

```tsx
resources={[
  {
    name: "posts",
    identifier: "posts",
  },
  {
    name: "posts",
    identifier: "featured-posts",
    meta: {
      dataProviderName: "cms",
      filter: { featured: true },
    },
  },
]}

// Usage
useList({ resource: "featured-posts" });
```

### Action Routes

| Property | Description | Default Path |
|----------|-------------|--------------|
| `list` | List page route | `/${name}` |
| `create` | Create page route | `/${name}/create` |
| `edit` | Edit page route | `/${name}/edit/:id` |
| `show` | Show/detail page route | `/${name}/show/:id` |

Each can be:
- **String**: Route path
- **Component**: Uses default path
- **Object**: `{ component: Component, path: "/custom-path" }`

```tsx
// String paths (recommended)
{
  name: "posts",
  list: "/posts",
  create: "/posts/create",
  edit: "/posts/edit/:id",
  show: "/posts/show/:id",
}

// Custom paths with parameters
{
  name: "posts",
  list: "/:authorId/posts",
  edit: "/:authorId/posts/:id/edit",
}
```

## meta Properties

### label

Custom display name in menus (default: pluralized name):

```tsx
{
  name: "post",
  meta: { label: "Blog Posts" },
}
```

### icon

Icon for menu:

```tsx
import { IconArticle } from "@tabler/icons-react";

{
  name: "posts",
  meta: { icon: <IconArticle /> },
}
```

### canDelete

Show delete button in CRUD views:

```tsx
{
  name: "posts",
  meta: { canDelete: true },
}
```

### parent

Nest resource under another (for hierarchical menus):

```tsx
resources={[
  { name: "cms" },
  {
    name: "posts",
    meta: { parent: "cms" },
  },
  {
    name: "categories",
    meta: { parent: "cms" },
  },
]}
```

### dataProviderName

Specify data provider for multi-provider setups:

```tsx
dataProvider={{
  default: defaultDataProvider,
  cms: cmsDataProvider,
}}
resources={[
  {
    name: "posts",
    meta: { dataProviderName: "cms" },
  },
]}
```

### hide

Hide from menu/sidebar:

```tsx
{
  name: "internal-logs",
  meta: { hide: true },
}
```

## Full Example with All Options

```tsx
import { Refine } from "@refinedev/core";
import { IconArticle, IconUsers, IconSettings } from "@tabler/icons-react";

<Refine
  dataProvider={{
    default: restDataProvider,
    cms: cmsDataProvider,
  }}
  resources={[
    {
      name: "posts",
      identifier: "posts",
      list: "/posts",
      create: "/posts/create",
      edit: "/posts/edit/:id",
      show: "/posts/show/:id",
      meta: {
        label: "Blog Posts",
        icon: <IconArticle />,
        canDelete: true,
        dataProviderName: "cms",
      },
    },
    {
      name: "users",
      list: "/users",
      show: "/users/:id",
      meta: {
        label: "Team Members",
        icon: <IconUsers />,
        canDelete: false,
      },
    },
    {
      name: "settings",
      list: "/settings",
      edit: "/settings",
      meta: {
        icon: <IconSettings />,
        hide: false, // Show in menu
      },
    },
    {
      name: "audit-logs",
      list: "/logs",
      meta: {
        hide: true, // Hidden from menu
      },
    },
  ]}
/>
```

## Accessing Resource Info

### useResource Hook

```tsx
import { useResource } from "@refinedev/core";

const { resource, resources, identifier } = useResource();

// Get specific resource
const { resource: postsResource } = useResource("posts");
```

### useResourceParams Hook

```tsx
import { useResourceParams } from "@refinedev/core";

const { resource, action, id } = useResourceParams();
// resource: current resource object
// action: "list" | "create" | "edit" | "show"
// id: record ID (for edit/show)
```

## Routes Setup (React Router)

```tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Refine } from "@refinedev/core";
import routerProvider from "@refinedev/react-router";

function App() {
  return (
    <BrowserRouter>
      <Refine
        routerProvider={routerProvider}
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
          <Route path="/posts" element={<PostList />} />
          <Route path="/posts/create" element={<PostCreate />} />
          <Route path="/posts/edit/:id" element={<PostEdit />} />
          <Route path="/posts/show/:id" element={<PostShow />} />
        </Routes>
      </Refine>
    </BrowserRouter>
  );
}
```

## Navigation

Use `useNavigation` for programmatic navigation:

```tsx
import { useNavigation } from "@refinedev/core";

const { list, create, edit, show } = useNavigation();

// Navigate to pages
list("posts");           // /posts
create("posts");         // /posts/create
edit("posts", 1);        // /posts/edit/1
show("posts", 1);        // /posts/show/1
```

Or use navigation components (from UI package):

```tsx
import { EditButton, ShowButton, DeleteButton } from "@refinedev/mantine";

<EditButton recordItemId={record.id} />
<ShowButton recordItemId={record.id} />
<DeleteButton recordItemId={record.id} />
```
