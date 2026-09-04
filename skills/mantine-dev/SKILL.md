---
name: mantine-dev
description: "Mantine UI library for React: 100+ components, hooks, forms, theming, dark mode, CSS modules, and Vite/TypeScript setup. Use when building React applications with Mantine components, configuring theming/dark mode, or working with Mantine hooks and forms. Keywords: Mantine, React, UI components, CSS modules, theming."
metadata:
  version: "9.6.0"
  release_date: "2026-08-31"
---

# Mantine UI Library

Mantine is a fully-featured React components library with TypeScript support. It provides 100+ hooks and components with native dark mode, CSS-in-JS via CSS modules, and excellent accessibility.

## v9.6 Highlights

- New `@mantine/lightbox` package: full-screen media lightbox with carousel navigation, zoom, thumbnails, video and custom slides, and a store-based API (mount once, open from anywhere, same pattern as Spotlight and Notifications).
- New `ActionBar` component: a floating selection-action bar that hosts bulk actions for selected items (for example, selected table rows).
- `@mantine/charts` adds `GaugeChart`, `WaffleChart`, `MatrixChart`, and `CandlestickChart`; area/bar/line/composite/scatter charts gain `referenceAreas` and `referenceDots`; `AreaChart` gains `type="stream"`; `ScatterChart` gains a right Y axis.
- `@mantine/tiptap` `RichTextEditor` gains table controls, a collapsible `Details` control, and an `InvisibleCharacters` formatting-marks control (register the matching Tiptap extensions); `Typography` now styles `details`/`summary` elements.
- `Notifications` gains `renderNotification` to replace the default notification with fully custom content while keeping enter/exit/drag-dismiss animations.
- `@mantine/schedule`: `ResourcesMonthView` supports event resizing, time-grid views support configurable drag/resize snap intervals, background events can be interactive, and `YearView` gains `renderDay` and `withWeekendDays`.
- `Dropzone` upgrades to `react-dropzone` 20 (partial-accept `maxFiles` behavior, stricter `FileWithPath`). **Node.js 22 or later is now required** (Node 20 reached end of life in April 2026).

## v9.5 Highlights

- New `Cascader` component: select a value from hierarchical data by drilling down through cascading columns, with `changeOnSelect`, hover-to-expand, search, and a flat-list layout for mobile.
- `@mantine/charts` gains `SunburstChart` (hierarchical data as concentric rings) and `BulletChart` (a value against a target and qualitative ranges); the area/bar/line/composite charts add `withBrush` for a draggable range-selector, and every chart component now ships `accessibilityLayer` (arrow-key navigation, Enter for tooltips) enabled by default.
- Calendar-based date components gain `withNativeLevelSelect`, replacing the calendar header's level button with native `<select>` elements, paired with `yearsSelectRange`.
- `Timeline.Item` gains `opposite` (content on the other side of the line, switching to a centered two-sided layout) and `alternate` (flips sides per item); `FloatingWindow` gains a `ResizeHandle` compound component with a `dimensions` prop and keyboard resizing; `Modal`/`Drawer` gain `keepMountedMode` (`'activity'` or `'display-none'`); `Accordion` gains `disableCollapse` to keep one item always open.
- `@mantine/schedule` `ResourcesDayView`/`ResourcesWeekView` accept `intervalMinutes` greater than 60 for multi-hour slot columns.
- `9.5.0` fixes an `autoClose` timer leak in the notifications container.
- The official Vite template replaced ESLint/Prettier/`eslint-config-mantine` with `oxlint`/`oxfmt` via the new `oxc-config-mantine` package (internal tooling migration); `eslint-config-mantine` remains available for projects that keep ESLint.

## v9.4 Highlights

- New components: `ComboboxPopover` (low-level popover built on the Combobox engine), `DataList` (key/value description lists), `EmptyState` (empty/placeholder screens), and `Menubar` (desktop-style application menu bar).
- `@mantine/schedule` gains `ResourcesDayView` and `ResourcesWeekView` for resource-grouped scheduling layouts.
- `9.4.1` patch fixes: `@mantine/form` compatibility with the React compiler, Heatmap rendering, and assorted component fixes.

## v9.3 Highlights

- New `Splitter` component (with `use-splitter` hook): declarative resizable split-pane layout with horizontal/vertical orientation, collapsible panes, and keyboard navigation. `Splitter.Pane` must be a direct child of `Splitter`.
- New component props: `Pagination` gains `layout="responsive"` (CSS container queries), `Text`/`Blockquote` gain `textWrap`, `CodeHighlight` gains `withLineNumbers`, `OverflowList` gains `collapseFrom` ("start"/"end"), `Textarea` gains `bottomSection` (character counters), and the Combobox family (`Select`, `MultiSelect`, `Autocomplete`, `TagsInput`) supports `floatingHeight="viewport"`.
- `DateInput` gains `presets` for quick value selection; `Menu.Sub` supports controlled open state.
- `9.3.1` patch fixes: notification DOM cleanup on close, `Collapse` `keepMounted`, `SegmentedControl` indicator radius, `PinInput` placeholder centering, `Tree` arrow-key navigation skipping hidden nodes, `MaskInput` with uncontrolled `use-form`, and stable `use-id` under an `Activity` wrapper.

## v9.2.2 Highlights

- Accessibility fixes landed across selection controls and sliders: `Checkbox`, `Radio`, and `Switch` now wire error ids into `aria-describedby`, while `Slider` and `RangeSlider` support `aria-valuetext`.
- Overlay/input behavior was refined with submenu safe polygon support, duplicate modal-id fixes, PinInput keyboard fixes, and ScrollArea/TreeSelect interaction fixes.
- Patch fixes in `9.2.2` cover `Pill` overflow, `Input` sections under local `dir` overrides, `Select` clear buttons for falsy primitive values, Modal/Drawer/Spotlight attribute types, and safer `Menu.Sub` safe-area polygon option forwarding.
- `@mantine/hooks` `use-mask` now preserves undo and cursor position across paste/cut flows, and `@mantine/tiptap` controls avoid errors after the editor is destroyed or not initialized.
- Forms and theming were hardened: `@mantine/form` handlers are more stable, default validators no longer force async results unexpectedly, and `mergeMantineTheme` no longer mutates `DEFAULT_THEME.headings`.
- `@mantine/schedule` continues to mature with better multi-day overlap rendering and corrected positioning for `intervalMinutes={60}`.

## v9.0 Breaking Changes

- **React 19.2+** required for all `@mantine/*` packages
- **Tiptap 3+** required for `@mantine/tiptap`
- **Recharts 3+** required for `@mantine/charts` (no migration needed)
- Follow the official [8.x → 9.x migration guide](https://mantine.dev/changelog/9-0-0/) for full details

## Focus

This skill focuses on:

- **Vite** + **TypeScript** setup (not Next.js or CRA)
- CSS modules with PostCSS preset
- Vitest for testing
- Oxlint/Oxfmt (`oxc-config-mantine`) for linting and formatting, matching the current official Vite template; ESLint (`eslint-config-mantine`) remains a supported alternative

## Installation

See `references/getting-started.md` for Vite template setup, manual installation, and optional packages.

## PostCSS Configuration

Create `postcss.config.cjs`:

```js
module.exports = {
  plugins: {
    "postcss-preset-mantine": {},
    "postcss-simple-vars": {
      variables: {
        "mantine-breakpoint-xs": "36em",
        "mantine-breakpoint-sm": "48em",
        "mantine-breakpoint-md": "62em",
        "mantine-breakpoint-lg": "75em",
        "mantine-breakpoint-xl": "88em",
      },
    },
  },
};
```

## App Setup

```tsx
// src/App.tsx
import "@mantine/core/styles.css";
// Other style imports as needed:
// import '@mantine/dates/styles.css';
// import '@mantine/notifications/styles.css';

import { MantineProvider, createTheme } from "@mantine/core";

const theme = createTheme({
  // Theme customization here
});

function App() {
  return <MantineProvider theme={theme}>{/* Your app */}</MantineProvider>;
}
```

## Critical Prohibitions

- Do NOT skip MantineProvider wrapper — all components require it
- Do NOT forget to import `@mantine/core/styles.css` — components won't style without it
- Do NOT mix Mantine with other UI libraries (e.g., Chakra, MUI) in same project
- Do NOT use inline styles for theme values — use CSS variables or theme object
- Do NOT skip PostCSS setup — responsive mixins won't work
- Do NOT forget `key={form.key('path')}` when using uncontrolled forms

## Core Concepts

### 1. MantineProvider

Wraps your app, provides theme context and color scheme management.

### 2. Theme Object

Customize colors, typography, spacing, component default props.

### 3. Style Props

All components accept style props like `mt`, `p`, `c`, `bg`, etc.

### 4. CSS Variables

All theme values exposed as CSS variables (e.g., `--mantine-color-blue-6`).

### 5. Polymorphic Components

Many components support `component` prop to render as different elements.

## Definition of Done

- [ ] MantineProvider wraps the app
- [ ] Styles imported (`@mantine/core/styles.css`)
- [ ] PostCSS configured with mantine-preset
- [ ] Theme customization in createTheme
- [ ] Color scheme (light/dark) handled
- [ ] TypeScript types working
- [ ] Tests pass with Vitest + custom render

## References (Detailed Guides)

### Setup & Configuration

- [getting-started.md](references/getting-started.md) — Installation, Vite setup, project structure
- [styling.md](references/styling.md) — MantineProvider, theme, CSS modules, style props, dark mode

### Core Features

- [components.md](references/components.md) — Core UI components patterns
- [hooks.md](references/hooks.md) — @mantine/hooks utility hooks
- [forms.md](references/forms.md) — @mantine/form, useForm, validation
- [schedule.md](references/schedule.md) — @mantine/schedule calendar scheduling

### Development

- [testing.md](references/testing.md) — Vitest setup, custom render, mocking
- [eslint.md](references/eslint.md) — Oxlint/Oxfmt (oxc-config-mantine) setup, plus legacy eslint-config-mantine option

## Links

- [Documentation](https://mantine.dev)
- [Releases](https://github.com/mantinedev/mantine/releases)
- [GitHub](https://github.com/mantinedev/mantine)
- [npm](https://www.npmjs.com/package/@mantine/core)
- [Vite template](https://github.com/mantinedev/vite-template)
- [LLM docs](https://mantine.dev/llms.txt)
