---
name: refine-mantine
description: "Bridge skill for Refine + Mantine integration: ThemedLayout, views (List/Show/Edit/Create), forms with @mantine/form, tables with @refinedev/react-table, notifications, auth pages, and RefineThemes. Keywords: @refinedev/mantine, @refinedev/react-table, Refine Mantine, ThemedLayout, useForm, useTable, notificationProvider, AuthPage, RefineThemes."
---

# Refine + Mantine Integration

Bridge skill combining Refine framework with Mantine UI library. For detailed Mantine-specific patterns see [mantine-dev](../mantine-dev/SKILL.md), for Refine core see [refine-dev](../refine-dev/SKILL.md).

## When to use

- Building admin panels with Refine using Mantine UI
- Need ready-made layout, views, and form integration
- Want Refine's data/auth logic with Mantine styling

## Critical Information

:::warning Version
Refine's Mantine integration currently uses **Mantine v5** (not v7/v8).
For v7+ support, see community packages like `refine-mantine-v7`.
:::

## Installation

```bash
npm install @refinedev/mantine @refinedev/react-table \
  @mantine/core@5 @mantine/hooks@5 @mantine/form@5 @mantine/notifications@5 \
  @emotion/react@11 @tabler/icons-react @tanstack/react-table
```

## App Setup

```tsx
import { Refine } from "@refinedev/core";
import { 
  ThemedLayoutV2, 
  useNotificationProvider,
  RefineThemes 
} from "@refinedev/mantine";
import { MantineProvider, Global } from "@mantine/core";
import { NotificationsProvider } from "@mantine/notifications";

function App() {
  return (
    <MantineProvider 
      theme={RefineThemes.Blue} 
      withNormalizeCSS 
      withGlobalStyles
    >
      <Global styles={{ body: { WebkitFontSmoothing: "auto" } }} />
      <NotificationsProvider position="top-right">
        <Refine
          notificationProvider={useNotificationProvider}
          // ... dataProvider, authProvider, resources
        >
          <ThemedLayoutV2>
            {/* Routes */}
          </ThemedLayoutV2>
        </Refine>
      </NotificationsProvider>
    </MantineProvider>
  );
}
```

## Core Components

### Layout

`<ThemedLayoutV2>` provides:
- Header with app name/logo and user info
- Sidebar with resource navigation
- Logout button (if authProvider present)
- Breadcrumbs

```tsx
import { ThemedLayoutV2, ThemedSiderV2, ThemedHeaderV2 } from "@refinedev/mantine";

<ThemedLayoutV2
  Sider={() => <ThemedSiderV2 Title={() => <span>My App</span>} />}
  Header={() => <ThemedHeaderV2 sticky />}
>
  {children}
</ThemedLayoutV2>
```

### Views

Wrap page content with appropriate view component:

```tsx
import { List, Show, Edit, Create } from "@refinedev/mantine";

// List page
<List>
  <Table>{/* ... */}</Table>
</List>

// Show page
<Show isLoading={isLoading}>
  <TextField value={record?.name} />
</Show>

// Edit page
<Edit saveButtonProps={saveButtonProps}>
  <form>{/* ... */}</form>
</Edit>

// Create page
<Create saveButtonProps={saveButtonProps}>
  <form>{/* ... */}</form>
</Create>
```

### Buttons

Pre-built buttons with authorization, loading, navigation:

```tsx
import { 
  CreateButton, EditButton, DeleteButton, 
  ShowButton, ListButton, SaveButton, RefreshButton,
  ExportButton, ImportButton, CloneButton
} from "@refinedev/mantine";

<EditButton recordItemId={id} />
<DeleteButton recordItemId={id} confirmTitle="Delete?" />
<SaveButton {...saveButtonProps} />
```

### Field Components

Formatted display components:

```tsx
import { 
  TextField, NumberField, DateField, 
  BooleanField, EmailField, UrlField,
  MarkdownField, TagField, FileField
} from "@refinedev/mantine";

<NumberField value={price} options={{ style: "currency", currency: "USD" }} />
<DateField value={createdAt} format="LL" />
<BooleanField value={isActive} />
```

## Forms

`@refinedev/mantine` wraps `@mantine/form` with Refine's data hooks:

```tsx
import { Create, useForm } from "@refinedev/mantine";
import { TextInput, NumberInput } from "@mantine/core";

export const ProductCreate = () => {
  const { saveButtonProps, getInputProps, errors } = useForm({
    initialValues: { name: "", price: 0 },
    validate: {
      name: (value) => !value ? "Required" : null,
    },
  });

  return (
    <Create saveButtonProps={saveButtonProps}>
      <form>
        <TextInput label="Name" {...getInputProps("name")} />
        <NumberInput label="Price" {...getInputProps("price")} />
      </form>
    </Create>
  );
};
```

### Advanced Form Hooks

```tsx
import { useModalForm, useDrawerForm, useStepsForm } from "@refinedev/mantine";

// Modal form
const { modal, getInputProps } = useModalForm({ action: "create" });

// Drawer form
const { drawerProps, getInputProps } = useDrawerForm();

// Multi-step form
const { steps, currentStep, gotoStep, getInputProps } = useStepsForm();
```

### Select with Relations

```tsx
import { useSelect } from "@refinedev/mantine";
import { Select } from "@mantine/core";

const { selectProps } = useSelect({
  resource: "categories",
  optionLabel: "title",
});

<Select label="Category" {...selectProps} />
```

## Tables

Use `@refinedev/react-table` for table management:

```tsx
import { useTable } from "@refinedev/react-table";
import { ColumnDef, flexRender } from "@tanstack/react-table";
import { List, EditButton, DeleteButton, ShowButton } from "@refinedev/mantine";
import { Table, Pagination, Group, ScrollArea } from "@mantine/core";

const columns: ColumnDef<IProduct>[] = [
  { id: "id", header: "ID", accessorKey: "id" },
  { id: "name", header: "Name", accessorKey: "name" },
  { id: "price", header: "Price", accessorKey: "price" },
  {
    id: "actions",
    header: "Actions",
    accessorKey: "id",
    cell: ({ getValue }) => (
      <Group spacing="xs" noWrap>
        <ShowButton hideText recordItemId={getValue()} />
        <EditButton hideText recordItemId={getValue()} />
        <DeleteButton hideText recordItemId={getValue()} />
      </Group>
    ),
  },
];

export const ProductList = () => {
  const {
    getHeaderGroups,
    getRowModel,
    refineCore: { setCurrentPage, pageCount, currentPage },
  } = useTable({ columns });

  return (
    <List>
      <ScrollArea>
        <Table highlightOnHover>
          <thead>
            {getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id}>
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </Table>
      </ScrollArea>
      <Pagination 
        position="right" 
        total={pageCount} 
        page={currentPage} 
        onChange={setCurrentPage} 
      />
    </List>
  );
};
```

## Auth Pages

Pre-built authentication pages:

```tsx
import { AuthPage } from "@refinedev/mantine";

// Login
<AuthPage type="login" />

// Register
<AuthPage type="register" />

// Forgot password
<AuthPage type="forgot-password" />

// Reset password
<AuthPage type="reset-password" />
```

## Theming

Use RefineThemes for consistent styling:

```tsx
import { RefineThemes } from "@refinedev/mantine";

// Available themes: Blue, Purple, Magenta, Red, Orange, Yellow, Green
<MantineProvider theme={RefineThemes.Blue}>
```

Custom theme:

```tsx
import { MantineThemeOverride } from "@mantine/core";

const myTheme: MantineThemeOverride = {
  ...RefineThemes.Blue,
  primaryColor: "violet",
  defaultRadius: "md",
};

<MantineProvider theme={myTheme}>
```

## Notifications

```tsx
import { useNotificationProvider } from "@refinedev/mantine";
import { NotificationsProvider } from "@mantine/notifications";

<NotificationsProvider position="top-right">
  <Refine notificationProvider={useNotificationProvider}>
    {/* ... */}
  </Refine>
</NotificationsProvider>
```

## Error Component

```tsx
import { ErrorComponent } from "@refinedev/mantine";

// 404 page
<Route path="*" element={<ErrorComponent />} />
```

## Inferencer (Prototyping)

Auto-generate views from data structure:

```tsx
import { 
  MantineListInferencer, 
  MantineShowInferencer,
  MantineEditInferencer, 
  MantineCreateInferencer 
} from "@refinedev/inferencer/mantine";

// Quick prototyping
<Route path="/products" element={<MantineListInferencer />} />
```

## Critical Prohibitions

- Do NOT use `@mantine/core` v7+ with `@refinedev/mantine` — requires v5
- Do NOT forget `NotificationsProvider` wrapper — notifications won't work
- Do NOT skip `withNormalizeCSS` and `withGlobalStyles` — styling breaks
- Do NOT mix RefineThemes with incompatible Mantine versions

## Definition of Done

- [ ] Mantine v5 packages installed (not v7+)
- [ ] MantineProvider wraps app with RefineThemes
- [ ] NotificationsProvider configured
- [ ] useNotificationProvider passed to Refine
- [ ] ThemedLayoutV2 wrapping routes
- [ ] Views using List/Show/Edit/Create components
- [ ] Tables using @refinedev/react-table
- [ ] Forms using useForm from @refinedev/mantine

## See Also

- [mantine-dev](../mantine-dev/SKILL.md) — Mantine-specific patterns (for standalone use or v7+)
- [refine-dev](../refine-dev/SKILL.md) — Core Refine patterns
- [Community v7 package](https://github.com/bonniss/refine-mantine-v7)
- [Community v8 package](https://github.com/grigoreo-fox/refine-mantine-v8)
