````markdown
# Refine Hooks Reference

All Refine hooks are built on TanStack Query (React Query) and integrate with your data provider.

## Data Hooks

### useList — Paginated List

```tsx
import { useList } from "@refinedev/core";

const { data, isLoading } = useList({
  resource: "posts",
  pagination: { current: 1, pageSize: 10 },
  sorters: [{ field: "createdAt", order: "desc" }],
  filters: [{ field: "status", operator: "eq", value: "published" }],
});
// data.data — records array, data.total — total count
```

### useOne — Single Record

```tsx
const { data } = useOne({ resource: "posts", id: 1 });
// data.data — the record
```

### useMany — Multiple Records by IDs

```tsx
const { data } = useMany({ resource: "posts", ids: [1, 2, 3] });
```

### useCreate / useUpdate / useDelete — Mutations

```tsx
import { useCreate, useUpdate, useDelete } from "@refinedev/core";

const { mutate: create } = useCreate();
create({ resource: "posts", values: { title: "New Post" } });

const { mutate: update } = useUpdate();
update({ resource: "posts", id: 1, values: { title: "Updated" } });

const { mutate: remove } = useDelete();
remove({ resource: "posts", id: 1 });
```

### Mutation Modes

```tsx
mutate({
  resource: "posts",
  id: 1,
  values: { title: "New" },
  mutationMode: "pessimistic", // Wait for API (default)
  // mutationMode: "optimistic", // Update UI immediately, rollback on error
  // mutationMode: "undoable", // Show undo notification
  undoableTimeout: 5000,
});
```

### Bulk Operations

```tsx
import { useCreateMany, useUpdateMany, useDeleteMany } from "@refinedev/core";

const { mutate: createMany } = useCreateMany();
createMany({ resource: "posts", values: [{ title: "A" }, { title: "B" }] });

const { mutate: updateMany } = useUpdateMany();
updateMany({ resource: "posts", ids: [1, 2], values: { status: "published" } });

const { mutate: deleteMany } = useDeleteMany();
deleteMany({ resource: "posts", ids: [1, 2, 3] });
```

### Filter Operators

| Operator | Description | Operator | Description |
|----------|-------------|----------|-------------|
| `eq` | Equal | `ne` | Not equal |
| `lt` | Less than | `gt` | Greater than |
| `lte` | ≤ | `gte` | ≥ |
| `in` | In array | `nin` | Not in array |
| `contains` | Contains | `null` | Is null |
| `between` | Range | `nnull` | Is not null |

---

## useForm — Create/Edit/Clone

```tsx
import { useForm } from "@refinedev/mantine";
import { Create, Edit } from "@refinedev/mantine";
import { TextInput, Select } from "@mantine/core";

// Action auto-detected from route
const { getInputProps, saveButtonProps } = useForm({
  initialValues: { title: "", status: "draft" },
  validate: {
    title: (v) => (v.length < 2 ? "Too short" : null),
  },
});

// Create page
export const PostCreate = () => (
  <Create saveButtonProps={saveButtonProps}>
    <TextInput label="Title" {...getInputProps("title")} />
    <Select
      label="Status"
      data={[{ value: "draft", label: "Draft" }, { value: "published", label: "Published" }]}
      {...getInputProps("status")}
    />
  </Create>
);
```

### useForm Configuration

| Property | Type | Description |
|----------|------|-------------|
| `action` | "create" \| "edit" \| "clone" | Auto-detected from route |
| `id` | string \| number | Record ID (edit/clone) |
| `redirect` | "list" \| "edit" \| "show" \| false | After success |
| `mutationMode` | "pessimistic" \| "optimistic" \| "undoable" | Behavior |
| `warnWhenUnsavedChanges` | boolean | Browser prompt on leave |

### useForm Return Values

| Property | Description |
|----------|-------------|
| `getInputProps(field)` | Props for Mantine inputs |
| `saveButtonProps` | Props for submit button |
| `values` / `setValues` | Form state |
| `errors` / `setFieldValue` | Validation |
| `refineCore.formLoading` | Loading state |
| `refineCore.queryResult` | Fetched data (edit/clone) |

### Auto-Save

```tsx
const { refineCore: { autoSaveProps } } = useForm({
  refineCoreProps: {
    autoSave: { enabled: true, debounce: 1000 },
  },
});
// autoSaveProps.status: "loading" | "error" | "idle" | "success"
```

---

## useTable — List with TanStack Table

```bash
npm install @refinedev/react-table @tanstack/react-table
```

```tsx
import { useTable } from "@refinedev/react-table";
import { ColumnDef, flexRender } from "@tanstack/react-table";
import { Table, Pagination, Group } from "@mantine/core";

interface Post { id: number; title: string; status: string; }

const columns: ColumnDef<Post>[] = [
  { id: "id", accessorKey: "id", header: "ID" },
  { id: "title", accessorKey: "title", header: "Title" },
  { id: "status", accessorKey: "status", header: "Status" },
];

export const PostList = () => {
  const {
    getHeaderGroups,
    getRowModel,
    getState,
    setPageIndex,
    getPageCount,
    refineCore: { tableQuery, setFilters, setSorters },
  } = useTable({
    columns,
    refineCoreProps: {
      resource: "posts",
      syncWithLocation: true, // URL sync
      pagination: { pageSize: 10 },
      sorters: { initial: [{ field: "createdAt", order: "desc" }] },
    },
  });

  if (tableQuery.isLoading) return <div>Loading...</div>;

  return (
    <>
      <Table striped highlightOnHover>
        <Table.Thead>
          {getHeaderGroups().map((hg) => (
            <Table.Tr key={hg.id}>
              {hg.headers.map((h) => (
                <Table.Th key={h.id}>
                  {flexRender(h.column.columnDef.header, h.getContext())}
                </Table.Th>
              ))}
            </Table.Tr>
          ))}
        </Table.Thead>
        <Table.Tbody>
          {getRowModel().rows.map((row) => (
            <Table.Tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <Table.Td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </Table.Td>
              ))}
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
      <Group justify="flex-end" mt="md">
        <Pagination
          total={getPageCount()}
          value={getState().pagination.pageIndex + 1}
          onChange={(p) => setPageIndex(p - 1)}
        />
      </Group>
    </>
  );
};
```

### Filtering

```tsx
const { refineCore: { setFilters } } = table;

// Set filters
setFilters([{ field: "status", operator: "eq", value: "published" }]);

// Merge filters
setFilters([{ field: "category", operator: "eq", value: "tech" }], "merge");
```

### Sortable Column Header

```tsx
{
  id: "title",
  accessorKey: "title",
  header: ({ column }) => (
    <Group gap={4} style={{ cursor: "pointer" }} onClick={column.getToggleSortingHandler()}>
      <span>Title</span>
      {column.getIsSorted() === "asc" && <IconSortAscending size={16} />}
      {column.getIsSorted() === "desc" && <IconSortDescending size={16} />}
    </Group>
  ),
  enableSorting: true,
}
```

### Actions Column

```tsx
import { useNavigation, useDelete } from "@refinedev/core";
import { ActionIcon, Group } from "@mantine/core";
import { IconEdit, IconEye, IconTrash } from "@tabler/icons-react";

{
  id: "actions",
  header: "Actions",
  cell: ({ row }) => {
    const { show, edit } = useNavigation();
    const { mutate: del } = useDelete();
    const { id } = row.original;
    return (
      <Group gap={4}>
        <ActionIcon onClick={() => show("posts", id)}><IconEye size={16} /></ActionIcon>
        <ActionIcon onClick={() => edit("posts", id)}><IconEdit size={16} /></ActionIcon>
        <ActionIcon color="red" onClick={() => del({ resource: "posts", id })}>
          <IconTrash size={16} />
        </ActionIcon>
      </Group>
    );
  },
}
```

---

## useSelect — Dropdowns & Relations

```tsx
import { useSelect } from "@refinedev/mantine";
import { Select } from "@mantine/core";

const { selectProps } = useSelect({
  resource: "categories",
  optionLabel: "name", // Display field (default: "title")
  optionValue: "id",   // Value field (default: "id")
});

<Select label="Category" {...selectProps} />
```

### Searchable with Filters

```tsx
const { selectProps } = useSelect({
  resource: "users",
  debounce: 500,
  onSearch: (value) => [
    { operator: "or", value: [
      { field: "firstName", operator: "contains", value },
      { field: "email", operator: "contains", value },
    ]},
  ],
});

<Select {...selectProps} searchable clearable />
```

### Dependent Selects

```tsx
const [categoryId, setCategoryId] = useState<string>();

const { selectProps: categoryProps } = useSelect({ resource: "categories" });

const { selectProps: tagProps } = useSelect({
  resource: "tags",
  filters: [{ field: "category_id", operator: "eq", value: categoryId }],
  queryOptions: { enabled: !!categoryId },
});

<Select label="Category" {...categoryProps} onChange={(v) => setCategoryId(v)} />
<Select label="Tag" {...tagProps} disabled={!categoryId} />
```

### Custom Labels

```tsx
const { selectProps, queryResult } = useSelect({ resource: "users" });

const customData = queryResult.data?.data.map((u) => ({
  value: String(u.id),
  label: `${u.firstName} ${u.lastName} (${u.email})`,
})) ?? [];

<Select {...selectProps} data={customData} />
```

### In Forms

```tsx
const { getInputProps, refineCore: { queryResult } } = useForm();

const { selectProps } = useSelect({
  resource: "categories",
  defaultValue: queryResult?.data?.data?.category_id, // Pre-select in edit
});

<Select label="Category" {...selectProps} {...getInputProps("category_id")} />
```

---

## Common Return Values

**Query hooks** (useList, useOne, useMany):
```ts
{ data, isLoading, isFetching, isError, error, refetch }
```

**Mutation hooks** (useCreate, useUpdate, useDelete):
```ts
{ mutate, mutateAsync, isLoading, isSuccess, isError, error, data }
```

**Query invalidation**: Mutations auto-invalidate related queries. Override with `invalidates: ["list", "detail"] | ["all"] | false`.
````
