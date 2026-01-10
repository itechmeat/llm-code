# Mantine UI Integration

Refine provides seamless integration with Mantine v5 for building admin interfaces.

## Installation

```bash
npm install @refinedev/mantine @refinedev/react-table \
  @mantine/core@5 @mantine/hooks@5 @mantine/form@5 @mantine/notifications@5 \
  @emotion/react@11 @tabler/icons-react @tanstack/react-table
```

## Basic Setup

```tsx
import { Refine } from "@refinedev/core";
import { useNotificationProvider, RefineThemes } from "@refinedev/mantine";
import { MantineProvider } from "@mantine/core";
import { NotificationsProvider } from "@mantine/notifications";
import routerProvider from "@refinedev/react-router";
import dataProvider from "@refinedev/simple-rest";
import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <MantineProvider
        theme={RefineThemes.Blue}
        withNormalizeCSS
        withGlobalStyles
      >
        <NotificationsProvider position="top-right">
          <Refine
            routerProvider={routerProvider}
            dataProvider={dataProvider("https://api.example.com")}
            notificationProvider={useNotificationProvider}
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
        </NotificationsProvider>
      </MantineProvider>
    </BrowserRouter>
  );
}
```

## Layout Components

### ThemedLayout

```tsx
import { ThemedLayout, ThemedSider, ThemedHeader } from "@refinedev/mantine";

<Routes>
  <Route
    element={
      <ThemedLayout
        Header={ThemedHeader}
        Sider={ThemedSider}
        Title={({ collapsed }) => (
          <div>{collapsed ? "App" : "My Application"}</div>
        )}
      >
        <Outlet />
      </ThemedLayout>
    }
  >
    <Route path="/posts" element={<PostList />} />
    {/* ... */}
  </Route>
</Routes>
```

## View Components

### List View

```tsx
import { List, EditButton, ShowButton, DeleteButton } from "@refinedev/mantine";
import { useTable } from "@refinedev/react-table";
import { ColumnDef, flexRender } from "@tanstack/react-table";
import { Table, Group, Pagination, ScrollArea } from "@mantine/core";

interface Post {
  id: number;
  title: string;
  status: string;
}

export const PostList = () => {
  const columns: ColumnDef<Post>[] = [
    { id: "id", header: "ID", accessorKey: "id" },
    { id: "title", header: "Title", accessorKey: "title" },
    { id: "status", header: "Status", accessorKey: "status" },
    {
      id: "actions",
      header: "Actions",
      accessorKey: "id",
      cell: ({ getValue }) => {
        const id = getValue() as number;
        return (
          <Group spacing="xs" noWrap>
            <ShowButton hideText recordItemId={id} />
            <EditButton hideText recordItemId={id} />
            <DeleteButton hideText recordItemId={id} />
          </Group>
        );
      },
    },
  ];

  const {
    getHeaderGroups,
    getRowModel,
    refineCore: { setCurrent, pageCount, current },
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
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
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
        page={current}
        onChange={setCurrent}
        mt="md"
      />
    </List>
  );
};
```

### Create View

```tsx
import { Create, useForm } from "@refinedev/mantine";
import { TextInput, Select, Textarea } from "@mantine/core";

export const PostCreate = () => {
  const { saveButtonProps, getInputProps, errors } = useForm({
    initialValues: {
      title: "",
      status: "draft",
      content: "",
    },
    validate: {
      title: (value) => (value.length < 2 ? "Title is too short" : null),
    },
  });

  return (
    <Create saveButtonProps={saveButtonProps}>
      <TextInput
        mt="sm"
        label="Title"
        placeholder="Post title"
        {...getInputProps("title")}
      />
      <Select
        mt="sm"
        label="Status"
        data={[
          { value: "draft", label: "Draft" },
          { value: "published", label: "Published" },
        ]}
        {...getInputProps("status")}
      />
      <Textarea
        mt="sm"
        label="Content"
        placeholder="Post content"
        minRows={4}
        {...getInputProps("content")}
      />
    </Create>
  );
};
```

### Edit View

```tsx
import { Edit, useForm } from "@refinedev/mantine";
import { TextInput, Select, Textarea } from "@mantine/core";

export const PostEdit = () => {
  const { saveButtonProps, getInputProps } = useForm({
    initialValues: {
      title: "",
      status: "",
      content: "",
    },
  });

  return (
    <Edit saveButtonProps={saveButtonProps}>
      <TextInput
        mt="sm"
        label="Title"
        {...getInputProps("title")}
      />
      <Select
        mt="sm"
        label="Status"
        data={[
          { value: "draft", label: "Draft" },
          { value: "published", label: "Published" },
        ]}
        {...getInputProps("status")}
      />
      <Textarea
        mt="sm"
        label="Content"
        minRows={4}
        {...getInputProps("content")}
      />
    </Edit>
  );
};
```

### Show View

```tsx
import { Show, TextField, NumberField, DateField, MarkdownField } from "@refinedev/mantine";
import { useShow } from "@refinedev/core";
import { Title, Text } from "@mantine/core";

export const PostShow = () => {
  const { queryResult } = useShow();
  const { data, isLoading } = queryResult;
  const record = data?.data;

  return (
    <Show isLoading={isLoading}>
      <Title order={5}>Title</Title>
      <TextField value={record?.title} />

      <Title mt="sm" order={5}>Status</Title>
      <TextField value={record?.status} />

      <Title mt="sm" order={5}>Created At</Title>
      <DateField value={record?.createdAt} />

      <Title mt="sm" order={5}>Content</Title>
      <MarkdownField value={record?.content} />
    </Show>
  );
};
```

## Buttons

| Component | Purpose |
|-----------|---------|
| `<CreateButton />` | Navigate to create page |
| `<EditButton />` | Navigate to edit page |
| `<ShowButton />` | Navigate to show page |
| `<ListButton />` | Navigate to list page |
| `<CloneButton />` | Navigate to clone page |
| `<DeleteButton />` | Delete with confirmation |
| `<SaveButton />` | Submit form |
| `<RefreshButton />` | Refresh data |
| `<ImportButton />` | Import data |
| `<ExportButton />` | Export data |

```tsx
import {
  CreateButton,
  EditButton,
  DeleteButton,
  ShowButton,
} from "@refinedev/mantine";

// In List view header
<CreateButton />

// In table actions
<EditButton recordItemId={record.id} />
<ShowButton recordItemId={record.id} />
<DeleteButton recordItemId={record.id} />

// Hide text (icon only)
<EditButton hideText recordItemId={record.id} />
```

## Field Components

| Component | Description |
|-----------|-------------|
| `<TextField />` | Text display |
| `<NumberField />` | Formatted numbers |
| `<DateField />` | Formatted dates |
| `<BooleanField />` | Yes/No display |
| `<EmailField />` | Email link |
| `<UrlField />` | URL link |
| `<FileField />` | File download link |
| `<TagField />` | Tag/badge display |
| `<MarkdownField />` | Rendered markdown |

```tsx
import {
  TextField,
  NumberField,
  DateField,
  BooleanField,
  TagField,
} from "@refinedev/mantine";

<TextField value={record.name} />
<NumberField value={record.price} options={{ style: "currency", currency: "USD" }} />
<DateField value={record.createdAt} format="MMMM DD, YYYY" />
<BooleanField value={record.isActive} />
<TagField value={record.status} />
```

## Form Hooks

### useForm

```tsx
import { useForm } from "@refinedev/mantine";

const { 
  saveButtonProps,
  getInputProps,
  values,
  setValues,
  errors,
  refineCore: { formLoading, queryResult },
} = useForm({
  initialValues: { name: "", price: 0 },
  validate: {
    name: (value) => (value ? null : "Name is required"),
    price: (value) => (value > 0 ? null : "Price must be positive"),
  },
  refineCoreProps: {
    resource: "products",
    action: "create", // "create" | "edit" | "clone"
    redirect: "list",
    onMutationSuccess: () => console.log("Success"),
  },
});
```

### useSelect

```tsx
import { useSelect } from "@refinedev/mantine";
import { Select } from "@mantine/core";

const { selectProps } = useSelect({
  resource: "categories",
  optionLabel: "title",
  optionValue: "id",
});

<Select
  label="Category"
  placeholder="Select category"
  {...selectProps}
  {...getInputProps("categoryId")}
/>
```

### useModalForm

```tsx
import { useModalForm } from "@refinedev/mantine";
import { Modal, TextInput, Button } from "@mantine/core";

const {
  modal: { visible, close, title },
  saveButtonProps,
  getInputProps,
} = useModalForm({
  refineCoreProps: { action: "create" },
  initialValues: { name: "" },
});

<>
  <Button onClick={() => modal.show()}>Create</Button>
  <Modal opened={visible} onClose={close} title={title}>
    <TextInput label="Name" {...getInputProps("name")} />
    <Button {...saveButtonProps}>Save</Button>
  </Modal>
</>
```

### useDrawerForm

```tsx
import { useDrawerForm } from "@refinedev/mantine";
import { Drawer, TextInput, Button } from "@mantine/core";

const {
  drawerProps,
  saveButtonProps,
  getInputProps,
} = useDrawerForm({
  refineCoreProps: { action: "edit" },
});

<Drawer {...drawerProps}>
  <TextInput label="Name" {...getInputProps("name")} />
  <Button {...saveButtonProps}>Save</Button>
</Drawer>
```

### useStepsForm

```tsx
import { useStepsForm } from "@refinedev/mantine";
import { Stepper, Button, TextInput } from "@mantine/core";

const {
  saveButtonProps,
  getInputProps,
  steps: { currentStep, gotoStep },
} = useStepsForm({
  initialValues: { name: "", email: "", bio: "" },
  stepsProps: {
    finish: saveButtonProps,
  },
});

<Stepper active={currentStep}>
  <Stepper.Step label="Basic">
    <TextInput label="Name" {...getInputProps("name")} />
  </Stepper.Step>
  <Stepper.Step label="Contact">
    <TextInput label="Email" {...getInputProps("email")} />
  </Stepper.Step>
  <Stepper.Step label="Profile">
    <TextInput label="Bio" {...getInputProps("bio")} />
  </Stepper.Step>
</Stepper>
```

## Theming

### Built-in Themes

```tsx
import { RefineThemes } from "@refinedev/mantine";
import { MantineProvider } from "@mantine/core";

// Available: Blue, Purple, Magenta, Red, Orange, Yellow, Green
<MantineProvider theme={RefineThemes.Blue}>
  {/* ... */}
</MantineProvider>
```

### Dark Mode

```tsx
import { RefineThemes } from "@refinedev/mantine";
import { MantineProvider, ColorSchemeProvider } from "@mantine/core";
import { useState } from "react";

function App() {
  const [colorScheme, setColorScheme] = useState<"light" | "dark">("light");
  
  const toggleColorScheme = () => {
    setColorScheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <ColorSchemeProvider
      colorScheme={colorScheme}
      toggleColorScheme={toggleColorScheme}
    >
      <MantineProvider
        theme={{
          ...RefineThemes.Blue,
          colorScheme,
        }}
        withNormalizeCSS
        withGlobalStyles
      >
        {/* ... */}
      </MantineProvider>
    </ColorSchemeProvider>
  );
}
```

## Auth Pages

```tsx
import { AuthPage } from "@refinedev/mantine";

// Login
<Route path="/login" element={<AuthPage type="login" />} />

// Register
<Route path="/register" element={<AuthPage type="register" />} />

// Forgot Password
<Route path="/forgot-password" element={<AuthPage type="forgotPassword" />} />

// Reset Password
<Route path="/reset-password" element={<AuthPage type="updatePassword" />} />

// Customization
<AuthPage
  type="login"
  title="Welcome Back"
  formProps={{
    initialValues: { email: "", password: "" },
  }}
  rememberMe={true}
  registerLink="/register"
  forgotPasswordLink="/forgot-password"
/>
```

## Error Component

```tsx
import { ErrorComponent } from "@refinedev/mantine";

<Route path="*" element={<ErrorComponent />} />
```
