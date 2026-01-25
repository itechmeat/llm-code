# Inferencer (Code Generation)

Inferencer automatically generates CRUD pages based on your API response structure.

## Installation

```bash
npm install @refinedev/inferencer
```

## Basic Usage

```tsx
import {
  MantineInferencer,
  MantineListInferencer,
  MantineShowInferencer,
  MantineEditInferencer,
  MantineCreateInferencer,
} from "@refinedev/inferencer/mantine";

// Combined inferencer (auto-detects action from route)
<Route path="/posts" element={<MantineInferencer resource="posts" />} />

// Or specific inferencers
<Route path="/posts" element={<MantineListInferencer resource="posts" />} />
<Route path="/posts/create" element={<MantineCreateInferencer resource="posts" />} />
<Route path="/posts/edit/:id" element={<MantineEditInferencer resource="posts" />} />
<Route path="/posts/show/:id" element={<MantineShowInferencer resource="posts" />} />
```

## Full App Example

```tsx
import { Refine } from "@refinedev/core";
import { ThemedLayout } from "@refinedev/mantine";
import { MantineInferencer } from "@refinedev/inferencer/mantine";
import routerProvider from "@refinedev/react-router";
import dataProvider from "@refinedev/simple-rest";
import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Refine
        routerProvider={routerProvider}
        dataProvider={dataProvider("https://api.fake-rest.refine.dev")}
        resources={[
          {
            name: "posts",
            list: "/posts",
            create: "/posts/create",
            edit: "/posts/edit/:id",
            show: "/posts/show/:id",
          },
          {
            name: "categories",
            list: "/categories",
            show: "/categories/show/:id",
          },
        ]}
      >
        <Routes>
          <Route element={<ThemedLayout><Outlet /></ThemedLayout>}>
            {/* Posts - full CRUD */}
            <Route path="/posts" element={<MantineInferencer />} />
            <Route path="/posts/create" element={<MantineInferencer />} />
            <Route path="/posts/edit/:id" element={<MantineInferencer />} />
            <Route path="/posts/show/:id" element={<MantineInferencer />} />
            
            {/* Categories - list and show only */}
            <Route path="/categories" element={<MantineInferencer />} />
            <Route path="/categories/show/:id" element={<MantineInferencer />} />
          </Route>
        </Routes>
      </Refine>
    </BrowserRouter>
  );
}
```

## How It Works

1. Inferencer fetches data from your API
2. Analyzes the response structure (field types, relations)
3. Generates appropriate components:
   - Text fields → `<TextInput />`
   - Numbers → `<NumberInput />`
   - Booleans → `<Checkbox />`
   - Dates → `<DatePicker />`
   - Relations → `<Select />` with data from related resource
4. Shows the generated code for you to copy

## Viewing Generated Code

The inferencer displays the generated source code in a panel. You can:
- Copy the code
- Customize it for your needs
- Replace the inferencer with the generated component

```tsx
// 1. Start with inferencer
<Route path="/posts" element={<MantineListInferencer />} />

// 2. Copy generated code from the UI panel

// 3. Create your own component with customizations
// posts/list.tsx (based on generated code)
export const PostList = () => {
  // ... generated code with your modifications
};

// 4. Replace inferencer with your component
<Route path="/posts" element={<PostList />} />
```

## Configuration

### Field Transformer

Customize field inference:

```tsx
<MantineListInferencer
  fieldTransformer={(field) => {
    // Skip certain fields
    if (field.key === "internal_id") {
      return false;
    }
    
    // Modify field config
    if (field.key === "status") {
      return {
        ...field,
        type: "select",
        options: [
          { value: "draft", label: "Draft" },
          { value: "published", label: "Published" },
        ],
      };
    }
    
    return field;
  }}
/>
```

### Hide Code Viewer

```tsx
<MantineInferencer hideCodeViewerInProduction />
```

## Supported Field Types

| Type | Generated Component |
|------|---------------------|
| `string` | `<TextInput />` |
| `number` | `<NumberInput />` |
| `boolean` | `<Checkbox />` |
| `date` | `<DatePicker />` |
| `email` | `<TextInput type="email" />` |
| `url` | `<TextInput />` |
| `richtext` | `<Textarea />` |
| `relation` | `<Select />` with `useSelect` |
| `array` | Multiple inputs |
| `object` | Nested fields |

## Workflow

1. **Rapid Prototyping**: Use inferencer to quickly scaffold CRUD pages
2. **Copy Code**: Get the generated code from the UI
3. **Customize**: Modify the code for your specific requirements
4. **Replace**: Swap inferencer with your custom components

## Limitations

- Generated code is a starting point, not production-ready
- Complex validations need manual implementation
- Custom business logic must be added manually
- May not handle all edge cases perfectly

## Best Practice

Use Inferencer for:
- Rapid prototyping
- Learning Refine patterns
- Starting point for new resources

Don't use Inferencer in production:
- Replace with actual components
- Add proper validation
- Implement business logic
- Optimize for your specific needs
