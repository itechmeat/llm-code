---
title: Direction Provider
subtitle: Enables RTL behavior for Base UI components.
description: A direction provider component that enables RTL behavior for Base UI components.
---

# Direction Provider

A direction provider component that enables RTL behavior for Base UI components.

## Demo

### Tailwind

This example shows how to implement the component using Tailwind CSS.

```tsx
/* index.tsx */
import { Slider } from '@base-ui/react/slider';
import { DirectionProvider } from '@base-ui/react/direction-provider';

export default function ExampleDirectionProvider() {
  return (
    <div dir="rtl">
      <DirectionProvider direction="rtl">
        <Slider.Root defaultValue={25}>
          <Slider.Control className="flex w-56 items-center py-3">
            <Slider.Track className="relative h-1 w-full rounded bg-gray-200 shadow-[inset_0_0_0_1px] shadow-gray-200">
              <Slider.Indicator className="rounded bg-gray-700" />
              <Slider.Thumb className="size-4 rounded-full bg-white outline outline-1 outline-gray-300 has-[:focus-visible]:outline has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-blue-800" />
            </Slider.Track>
          </Slider.Control>
        </Slider.Root>
      </DirectionProvider>
    </div>
  );
}
```

### CSS Modules

This example shows how to implement the component using CSS Modules.

```css
/* index.module.css */
.Control {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  width: 14rem;
  padding-block: 0.75rem;
}

.Track {
  width: 100%;
  background-color: var(--color-gray-200);
  box-shadow: inset 0 0 0 1px var(--color-gray-200);
  height: 0.25rem;
  border-radius: 0.25rem;
  position: relative;
}

.Indicator {
  border-radius: 0.25rem;
  background-color: var(--color-gray-700);
}

.Thumb {
  width: 1rem;
  height: 1rem;
  border-radius: 100%;
  background-color: white;
  outline: 1px solid var(--color-gray-300);

  &:has(:focus-visible) {
    outline: 2px solid var(--color-blue);
  }
}
```

```tsx
/* index.tsx */
import { DirectionProvider } from '@base-ui/react/direction-provider';
import { Slider } from '@base-ui/react/slider';
import styles from './index.module.css';

export default function ExampleDirectionProvider() {
  return (
    <div dir="rtl">
      <DirectionProvider direction="rtl">
        <Slider.Root defaultValue={25}>
          <Slider.Control className={styles.Control}>
            <Slider.Track className={styles.Track}>
              <Slider.Indicator className={styles.Indicator} />
              <Slider.Thumb className={styles.Thumb} />
            </Slider.Track>
          </Slider.Control>
        </Slider.Root>
      </DirectionProvider>
    </div>
  );
}
```

## Anatomy

Import the component and wrap it around your app:

```jsx title="Anatomy"
import { DirectionProvider } from '@base-ui/react/direction-provider';

// prettier-ignore
<DirectionProvider>
  {/* Your app or a group of components */}
</DirectionProvider>
```

`<DirectionProvider>` enables child Base UI components to adjust behavior based on RTL text direction, but does not affect HTML and CSS. The `dir="rtl"` HTML attribute or `direction: rtl` CSS style must be set additionally by your own application code.

## API reference

Enables RTL behavior for Base UI components.

**DirectionProvider Props:**

| Prop      | Type            | Default | Description                       |
| :-------- | :-------------- | :------ | :-------------------------------- |
| direction | `TextDirection` | `'ltr'` | The reading direction of the text |
| children  | `ReactNode`     | -       | -                                 |

## useDirection

Use this hook to read the current text direction. This is useful for wrapping portaled components that may be rendered outside your application root and are unaffected by the `dir` attribute set within.

### Return value

**Return Value:**

| Property  | Type            | Description                 |
| :-------- | :-------------- | :-------------------------- |
| direction | `TextDirection` | The current text direction. |
