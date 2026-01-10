````markdown
# Authentication & Access Control

## Auth Provider Interface

```tsx
import type { AuthProvider } from "@refinedev/core";

const authProvider: AuthProvider = {
  // Required
  login: async ({ email, password }) => AuthActionResponse,
  logout: async () => AuthActionResponse,
  check: async () => CheckResponse,
  onError: async (error) => OnErrorResponse,
  
  // Optional
  register: async (params) => AuthActionResponse,
  forgotPassword: async (params) => AuthActionResponse,
  updatePassword: async (params) => AuthActionResponse,
  getPermissions: async () => unknown,
  getIdentity: async () => unknown,
};
```

## JWT Auth Implementation

```tsx
import { AuthProvider } from "@refinedev/core";
import axios from "axios";

const API_URL = "https://api.example.com";

// Add token to all requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authProvider: AuthProvider = {
  login: async ({ email, password }) => {
    try {
      const { data } = await axios.post(`${API_URL}/auth/login`, { email, password });
      localStorage.setItem("access_token", data.accessToken);
      localStorage.setItem("refresh_token", data.refreshToken);
      return { success: true, redirectTo: "/" };
    } catch (error: any) {
      return {
        success: false,
        error: { name: "LoginError", message: error.response?.data?.message || "Login failed" },
      };
    }
  },

  logout: async () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    return { success: true, redirectTo: "/login" };
  },

  check: async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return { authenticated: false, redirectTo: "/login" };
    
    try {
      await axios.get(`${API_URL}/auth/me`);
      return { authenticated: true };
    } catch {
      return { authenticated: false, logout: true, redirectTo: "/login" };
    }
  },

  onError: async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, { refreshToken });
          localStorage.setItem("access_token", data.accessToken);
          return {};
        } catch {
          return { logout: true, redirectTo: "/login" };
        }
      }
      return { logout: true, redirectTo: "/login" };
    }
    return { error };
  },

  getIdentity: async () => {
    try {
      const { data } = await axios.get(`${API_URL}/auth/me`);
      return data;
    } catch { return null; }
  },

  getPermissions: async () => {
    try {
      const { data } = await axios.get(`${API_URL}/auth/me`);
      return data.roles;
    } catch { return null; }
  },
};
```

## Auth Hooks

```tsx
import { useLogin, useLogout, useIsAuthenticated, useGetIdentity, usePermissions } from "@refinedev/core";

// Login
const { mutate: login, isLoading } = useLogin();
login({ email, password }, { onSuccess: () => {}, onError: (e) => {} });

// Logout
const { mutate: logout } = useLogout();

// Check auth
const { data: { authenticated } } = useIsAuthenticated();

// Get user info
const { data: user } = useGetIdentity<{ id: number; name: string }>();

// Get permissions
const { data: permissions } = usePermissions();
```

## Protected Routes

```tsx
import { Authenticated } from "@refinedev/core";
import { Navigate, Outlet, Routes, Route } from "react-router-dom";

<Routes>
  {/* Public */}
  <Route path="/login" element={<AuthPage type="login" />} />
  <Route path="/register" element={<AuthPage type="register" />} />
  
  {/* Protected */}
  <Route element={
    <Authenticated key="protected" fallback={<Navigate to="/login" />}>
      <Layout><Outlet /></Layout>
    </Authenticated>
  }>
    <Route path="/" element={<Dashboard />} />
    <Route path="/posts" element={<PostList />} />
  </Route>
</Routes>
```

## Auth Pages (Mantine)

```tsx
import { AuthPage } from "@refinedev/mantine";

<AuthPage
  type="login"        // "login" | "register" | "forgotPassword" | "updatePassword"
  title="Welcome"
  rememberMe={true}
  forgotPasswordLink="/forgot-password"
  registerLink="/register"
/>
```

---

## Access Control Provider

```tsx
import type { AccessControlProvider } from "@refinedev/core";

const accessControlProvider: AccessControlProvider = {
  can: async ({ resource, action, params }) => {
    // Return { can: true } or { can: false, reason: "..." }
    return { can: true };
  },
  options: {
    buttons: {
      enableAccessControl: true,
      hideIfUnauthorized: false, // Hide vs disable unauthorized buttons
    },
  },
};
```

## Role-Based Access Control (RBAC)

```tsx
const roles: Record<string, string[]> = {
  admin: ["*"],
  editor: ["posts.list", "posts.show", "posts.create", "posts.edit"],
  viewer: ["posts.list", "posts.show"],
};

const accessControlProvider: AccessControlProvider = {
  can: async ({ resource, action }) => {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    const permissions = roles[user.role || "viewer"] || [];
    
    if (permissions.includes("*")) return { can: true };
    
    const key = `${resource}.${action}`;
    return {
      can: permissions.includes(key),
      reason: permissions.includes(key) ? undefined : `Cannot ${action} ${resource}`,
    };
  },
};
```

## Attribute-Based Access (ABAC)

```tsx
const accessControlProvider: AccessControlProvider = {
  can: async ({ resource, action, params }) => {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    
    // Users can only edit their own posts
    if (resource === "posts" && action === "edit") {
      const postAuthorId = params?.id ? await getPostAuthor(params.id) : null;
      if (postAuthorId !== user.id && user.role !== "admin") {
        return { can: false, reason: "You can only edit your own posts" };
      }
    }
    
    // Premium content check
    if (params?.resource?.meta?.premium && !user.isPremium) {
      return { can: false, reason: "Premium subscription required" };
    }
    
    return { can: true };
  },
};
```

## useCan Hook

```tsx
import { useCan } from "@refinedev/core";

const { data: canEdit } = useCan({ resource: "posts", action: "edit", params: { id: 1 } });
const { data: canDelete } = useCan({ resource: "posts", action: "delete", params: { id: 1 } });

{canEdit?.can && <EditButton />}
{!canEdit?.can && <span>{canEdit?.reason}</span>}
```

## CanAccess Component

```tsx
import { CanAccess } from "@refinedev/core";

<CanAccess resource="posts" action="create" fallback={<div>No access</div>}>
  <CreateButton />
</CanAccess>
```

## Button Auto-Checks

Refine buttons automatically check access control:

| Button | Check |
|--------|-------|
| `<ListButton />` | `{ resource, action: "list" }` |
| `<CreateButton />` | `{ resource, action: "create" }` |
| `<EditButton recordItemId={id} />` | `{ resource, action: "edit", params: { id } }` |
| `<DeleteButton recordItemId={id} />` | `{ resource, action: "delete", params: { id } }` |
| `<ShowButton recordItemId={id} />` | `{ resource, action: "show", params: { id } }` |

```tsx
// Hide instead of disable
<EditButton recordItemId={1} accessControl={{ hideIfUnauthorized: true }} />
```

## Casbin Integration

```tsx
import { newEnforcer } from "casbin";

let enforcer: Awaited<ReturnType<typeof newEnforcer>>;

const accessControlProvider: AccessControlProvider = {
  can: async ({ resource, action }) => {
    if (!enforcer) enforcer = await newEnforcer("model.conf", "policy.csv");
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    const can = await enforcer.enforce(user.role, resource, action);
    return { can, reason: can ? undefined : "Forbidden by policy" };
  },
};
```

## CASL Integration

```tsx
import { createMongoAbility, AbilityBuilder } from "@casl/ability";

const defineAbilityFor = (user: { role: string }) => {
  const { can, cannot, build } = new AbilityBuilder(createMongoAbility);
  
  if (user.role === "admin") can("manage", "all");
  else if (user.role === "editor") {
    can("read", "all");
    can(["create", "update"], "Post");
    cannot("delete", "Post");
  } else {
    can("read", "all");
  }
  return build();
};

const accessControlProvider: AccessControlProvider = {
  can: async ({ resource, action }) => {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    const ability = defineAbilityFor(user);
    const caslAction = { list: "read", show: "read", create: "create", edit: "update", delete: "delete" }[action] || action;
    const can = ability.can(caslAction, resource);
    return { can, reason: can ? undefined : `Cannot ${action} ${resource}` };
  },
};
```

## Performance

```tsx
const accessControlProvider: AccessControlProvider = {
  can: async ({ resource, action }) => { /* ... */ },
  options: {
    queryOptions: {
      staleTime: 5 * 60 * 1000,  // Cache 5 min
      cacheTime: 10 * 60 * 1000,
    },
  },
};
```
````
