# Components Reference

`@mantine/core` provides 120+ components. This reference covers key patterns.

## New in v9.5

### Cascader

Hierarchical selection component: pick a value by drilling down through cascading columns instead of a single flat list. Each `data` entry is a `CascaderOption` with a unique `value`, optional `label`, and optional `children`.

```tsx
import { Cascader } from "@mantine/core";

const data = [
  {
    value: "asia",
    label: "Asia",
    children: [{ value: "jp", label: "Japan", children: [{ value: "tokyo", label: "Tokyo" }] }],
  },
];

<Cascader data={data} placeholder="Pick location" searchable />;
```

Key props: `changeOnSelect` (allow selecting a non-leaf level), `searchable` (filters options and renders matches as a flat list), `withColumns={false}` (flat list layout instead of cascading columns — useful for mobile, often paired with `useMatches`), `expandTrigger="hover"`, `allowDeselect`. Full keyboard navigation ships by default: arrows move between options, Enter expands a parent or picks a leaf, Escape closes the dropdown.

### Charts: SunburstChart and BulletChart

`SunburstChart` (`@mantine/charts`) renders hierarchical data as concentric rings — a treemap plotted in polar coordinates. Each node needs `name` and `color`, plus either a `value` (leaf) or `children`.

`BulletChart` compares one measured `value` against a `target` and a set of qualitative `ranges` (`{ value, color, label? }`) — useful for KPI-vs-threshold displays.

```tsx
import { BulletChart } from "@mantine/charts";

<BulletChart
  value={230000}
  target={150000}
  ranges={[
    { value: 150000, color: "red.8" },
    { value: 225000, color: "yellow.8" },
    { value: 300000, color: "teal.8" },
  ]}
  valueFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
/>;
```

`AreaChart`, `BarChart`, `LineChart`, and `CompositeChart` gain `withBrush`, which renders a draggable range-selector (a recharts Brush) below the chart, tunable via `brushProps`. Every chart component — those four plus `ScatterChart`, `BubbleChart`, `PieChart`, `DonutChart`, `RadarChart`, `RadialBarChart`, and `FunnelChart` — now ships `accessibilityLayer` (`true` by default), enabling arrow-key navigation between data points and Enter to toggle tooltips; set it to `false` when the chart sits inside a widget that already owns keyboard handling.

### Timeline

Vertical list of connected events with an active step index:

```tsx
import { Timeline, Text } from "@mantine/core";

<Timeline active={1}>
  <Timeline.Item title="New branch" opposite={<Text size="sm">2 hours ago</Text>}>
    <Text>You created branch fix-notifications</Text>
  </Timeline.Item>
  <Timeline.Item title="Commits" opposite={<Text size="sm">52 minutes ago</Text>} alternate>
    <Text>You pushed 23 commits</Text>
  </Timeline.Item>
</Timeline>;
```

New in v9.5: `Timeline.Item` accepts `opposite` to render content on the other side of the line — once any item sets it, the whole timeline switches to a centered, two-sided layout — and `alternate` to flip the content/opposite sides on an individual item.

### New props on existing components

- `FloatingWindow` gains a `ResizeHandle` compound component (`<FloatingWindow.ResizeHandle />`) for drag-resizing; pair it with a `dimensions` prop (`initialWidth`/`initialHeight`, `minWidth`/`minHeight`, `maxWidth`/`maxHeight`). It is keyboard-accessible: arrow keys resize in 10px steps, Home/End jump to the min/max size.
- `Modal` and `Drawer` gain `keepMountedMode` (`'activity'` default or `'display-none'`), which controls how a `keepMounted` modal/drawer is hidden instead of unmounted — `'activity'` wraps it in React 19's `Activity` component, `'display-none'` applies `display: none` styles.
- `Accordion` gains `disableCollapse` — in single (non-`multiple`) mode, clicking the open item's control again becomes a no-op, so one item always stays open; pair with `defaultValue` to guarantee an initial open item. It has no effect when `multiple` is set.
- Calendar-based date components (`DatePicker`, `DatePickerInput`, `DateInput`, and similar) gain `withNativeLevelSelect`, which swaps the calendar header's level button for native `<select>` elements (month + year at the month level, year at the year level); pair it with `yearsSelectRange` to bound the year options.

## Patch notes (9.4.1 -> 9.5.0)

- Fixed an `autoClose` timer leak in the notifications container; if you added a workaround for notifications not clearing their close timers, it can be removed.

## New in v9.3

### Splitter

Resizable split-pane layout built on the `use-splitter` hook. `Splitter.Pane` must be a direct child of `Splitter`; nest `Splitter` for complex layouts.

```tsx
import { Splitter } from "@mantine/core";

<Splitter h={200}>
  <Splitter.Pane defaultSize={50} min={20}>First pane</Splitter.Pane>
  <Splitter.Pane defaultSize={50} min={20}>Second pane</Splitter.Pane>
</Splitter>;
```

`Splitter` props: `orientation` ("horizontal" default / "vertical"), `sizes` + `onSizeChange` (controlled), `splitterRef` (imperative API), `lineSize`, `withHandle`, `redistribute`. `Splitter.Pane` props: `defaultSize`, `min`, `collapsible`, plus standard style props.

### New props on existing components

- `Pagination` `layout="responsive"` uses CSS container queries to adapt to available width.
- `Text` and `Blockquote` gain `textWrap` to control line length.
- `CodeHighlight` gains `withLineNumbers`.
- `OverflowList` gains `collapseFrom` ("start" / "end") to control collapse direction.
- `Textarea` gains `bottomSection` for character counters and supplementary info.
- Combobox family (`Select`, `MultiSelect`, `Autocomplete`, `TagsInput`) supports `floatingHeight="viewport"`.
- `DateInput` gains `presets` for quick value selection; `Menu.Sub` supports controlled open state.

## Patch notes (v9.2.1 -> v9.2.2)

- `Checkbox`, `Radio`, and `Switch` now pass the generated error id into `aria-describedby`, which matters if you depend on Mantine's built-in error text for screen-reader context.
- `Slider` and `RangeSlider` support `aria-valuetext`; use it when the numeric value needs a spoken label different from the raw number.
- `Menu` adds safe polygon support for submenus, reducing accidental submenu closure on diagonal pointer movement.
- `Menu.Sub` can receive safe-area polygon options; use this when submenu pointer corridors need custom tuning.
- `Table` fixes sticky-header border rendering, `PinInput` stops blocking common numeric-input keyboard shortcuts, and `Highlight` supports accent-insensitive matching.
- `Pill` overflow handling, `Input` section placement under local `dir` overrides, and `Select` clear-button visibility for falsy primitive values were fixed in `9.2.2`; remove local layout/clear-button workarounds after upgrade.
- Modal, Drawer, and Spotlight attribute typings were corrected; re-run TypeScript on wrappers that pass custom attributes through those components.
- `@mantine/tiptap` controls no longer throw when the editor is destroyed or not initialized, but still guard custom controls against null editor instances in app code.
- `Dropzone` now defaults `useFsAccessApi` to `false` for broader browser compatibility; enable it explicitly only when you need the File System Access API behavior and your target browsers support it.

## New in v9.0

### FloatingWindow

Draggable floating element with viewport constraint support:

```tsx
import { FloatingWindow } from "@mantine/core";

<FloatingWindow w={280} p="md" withBorder radius="md" excludeDragHandleSelector="button" initialPosition={{ top: 300, left: 20 }} style={{ cursor: "move" }}>
  Drag me around
</FloatingWindow>;
```

### OverflowList

Displays items and collapses overflowing ones into a single element.

### Typography

Generalized text component.

### Collapse (horizontal)

`Collapse` now supports `orientation="horizontal"` for animating width.

## Layout Components

### Container, Stack, Group, Flex

```tsx
import { Container, Stack, Group, Flex } from '@mantine/core';

<Container size="md">{/* Centers content, max-width */}</Container>

<Stack gap="md">{/* Vertical flex */}</Stack>

<Group gap="sm" justify="space-between">{/* Horizontal flex */}</Group>

<Flex direction="column" gap="md" align="center">{/* Generic flex */}</Flex>
```

### Grid & SimpleGrid

```tsx
import { Grid, SimpleGrid } from '@mantine/core';

// CSS Grid with responsive spans
<Grid>
  <Grid.Col span={{ base: 12, sm: 6, lg: 4 }}>Responsive</Grid.Col>
</Grid>

// Equal-width columns
<SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }}>{/* Items */}</SimpleGrid>
```

## Button Variants

```tsx
import { Button, ActionIcon } from '@mantine/core';

<Button variant="filled">Default</Button>
<Button variant="outline">Outline</Button>
<Button variant="light">Light</Button>
<Button variant="subtle">Subtle</Button>
<Button variant="white">White</Button>

<Button loading>Loading state</Button>
<Button leftSection={<IconPlus />}>With Icon</Button>

// Icon button
<ActionIcon variant="filled" color="blue"><IconSettings /></ActionIcon>
```

## Inputs Pattern

All inputs follow consistent API:

```tsx
import { TextInput, PasswordInput, Textarea, NumberInput, Select } from '@mantine/core';

// Common props: label, description, error, required, placeholder
<TextInput
  label="Email"
  description="We won't share it"
  error="Invalid email"
  required
  withAsterisk
/>

<Select
  label="Country"
  data={['USA', 'Canada']}
  searchable
  clearable
/>

// Objects with value/label
<Select data={[{ value: 'us', label: 'United States' }]} />
```

## Overlays Pattern

Modals, Drawers, Menus, Popovers all use similar pattern:

```tsx
import { Modal, Drawer, Menu, Popover } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';

// Common pattern with useDisclosure
const [opened, { open, close }] = useDisclosure(false);

// Modal
<Modal opened={opened} onClose={close} title="Title">Content</Modal>

// Drawer
<Drawer opened={opened} onClose={close} position="left">Navigation</Drawer>

// Menu (dropdown)
<Menu>
  <Menu.Target><Button>Toggle</Button></Menu.Target>
  <Menu.Dropdown>
    <Menu.Item leftSection={<IconSettings />}>Settings</Menu.Item>
    <Menu.Divider />
    <Menu.Item color="red">Delete</Menu.Item>
  </Menu.Dropdown>
</Menu>

// Popover
<Popover width={200} withArrow>
  <Popover.Target><Button>Info</Button></Popover.Target>
  <Popover.Dropdown>Details here</Popover.Dropdown>
</Popover>
```

## Feedback Components

```tsx
import { Loader, Alert, Notification, Progress, Skeleton } from '@mantine/core';

<Loader type="bars" />  // oval, bars, dots

<Alert variant="light" color="blue" title="Info">Message</Alert>

<Notification title="Success" color="green" icon={<IconCheck />}>
  Saved!
</Notification>

<Progress value={65} />
<Progress.Root size="xl">
  <Progress.Section value={35} color="cyan"><Progress.Label>Docs</Progress.Label></Progress.Section>
</Progress.Root>

// Loading placeholders
<Skeleton height={50} circle />
<Skeleton height={8} radius="xl" />
```

## Typography

```tsx
import { Title, Text, Anchor, Highlight, Code } from '@mantine/core';

<Title order={1}>h1 heading</Title>
<Title order={2} c="dimmed">h2 dimmed</Title>

<Text size="sm" c="dimmed" fw={700}>Small bold dimmed</Text>
<Text truncate>Long text...</Text>
<Text lineClamp={2}>Multi-line truncate...</Text>

<Highlight highlight={['react', 'mantine']}>
  Learn React with Mantine
</Highlight>

<Code>inline</Code>
<Code block>{`const x = 1;`}</Code>
```

## Data Display

```tsx
import { Badge, Card, Table, Avatar, Image, Tabs, Accordion } from '@mantine/core';

// Badge variants
<Badge>Default</Badge>
<Badge variant="dot" color="red">Dot</Badge>

// Card with sections
<Card shadow="sm" padding="lg" withBorder>
  <Card.Section><Image src="/img.jpg" height={160} /></Card.Section>
  <Text>Content</Text>
</Card>

// Table
<Table striped highlightOnHover withTableBorder>
  <Table.Thead><Table.Tr><Table.Th>Name</Table.Th></Table.Tr></Table.Thead>
  <Table.Tbody><Table.Tr><Table.Td>John</Table.Td></Table.Tr></Table.Tbody>
</Table>

// Tabs
<Tabs defaultValue="tab1">
  <Tabs.List>
    <Tabs.Tab value="tab1">First</Tabs.Tab>
    <Tabs.Tab value="tab2">Second</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="tab1">Content 1</Tabs.Panel>
</Tabs>

// Accordion
<Accordion defaultValue="item-1">
  <Accordion.Item value="item-1">
    <Accordion.Control>Section 1</Accordion.Control>
    <Accordion.Panel>Content</Accordion.Panel>
  </Accordion.Item>
</Accordion>
```

## Navigation

```tsx
import { NavLink, Pagination, Stepper, Breadcrumbs } from '@mantine/core';

<NavLink href="#" label="Dashboard" leftSection={<IconHome />} active />
<NavLink label="Settings">
  <NavLink label="General" />
  <NavLink label="Security" />
</NavLink>

<Pagination total={10} value={page} onChange={setPage} />

<Stepper active={active}>
  <Stepper.Step label="Step 1">Content 1</Stepper.Step>
  <Stepper.Step label="Step 2">Content 2</Stepper.Step>
  <Stepper.Completed>Done!</Stepper.Completed>
</Stepper>
```

## Common Style Props

All components accept these props:

```tsx
<Component
  // Margin & Padding
  m="md"
  mt="xs"
  p="sm"
  px="md"
  // Colors
  c="dimmed"
  bg="blue.1"
  // Typography
  fw={500}
  fz="sm"
  // Dimensions
  w={200}
  h="100%"
  maw={500}
  // Responsive
  p={{ base: "xs", sm: "md", lg: "xl" }}
/>
```

## Polymorphic Components

Render as different elements:

```tsx
import { Button } from '@mantine/core';
import { Link } from 'react-router-dom';

<Button component={Link} to="/about">Link Button</Button>
<Button component="a" href="https://example.com">Anchor Button</Button>
```

## Visibility Props

```tsx
<Text hiddenFrom="sm">Hidden on sm+</Text>
<Text visibleFrom="md">Visible on md+</Text>
<Text lightHidden>Only in dark mode</Text>
<Text darkHidden>Only in light mode</Text>
```
