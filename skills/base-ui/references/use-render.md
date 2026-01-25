---
title: useRender
subtitle: Hook for enabling a render prop in custom components.
description: Hook for enabling a render prop in custom components.
---

# useRender

Hook for enabling a render prop in custom components.

The `useRender` hook lets you build custom components that provide a `render` prop to override the default rendered element.

## Examples

A `render` prop for a custom Text component lets consumers use it to replace the default rendered `p` element with a different tag or component.

## Demo

### CSS Modules

This example shows how to implement the component using CSS Modules.

```css
/* index.module.css */
.Text {
  font-size: 0.875rem;
  line-height: 1rem;
  color: var(--color-gray-900);

  strong& {
    font-weight: 500;
  }
}
```

```tsx
/* index.tsx */
'use client';
import { useRender } from '@base-ui/react/use-render';
import { mergeProps } from '@base-ui/react/merge-props';
import styles from './index.module.css';

interface TextProps extends useRender.ComponentProps<'p'> {}

function Text(props: TextProps) {
  const { render, ...otherProps } = props;

  const element = useRender({
    defaultTagName: 'p',
    render,
    props: mergeProps<'p'>({ className: styles.Text }, otherProps),
  });

  return element;
}

export default function ExampleText() {
  return (
    <div>
      <Text>Text component rendered as a paragraph tag</Text>
      <Text render={<strong />}>Text component rendered as a strong tag</Text>
    </div>
  );
}
```

The callback version of the `render` prop enables more control of how props are spread, and also passes the internal `state` of a component.

## Demo

### CSS Modules

This example shows how to implement the component using CSS Modules.

```css
/* index.module.css */
.Button {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 2.5rem;
  padding: 0 0.875rem;
  margin: 0;
  outline: 0;
  border: 1px solid var(--color-gray-200);
  border-radius: 0.375rem;
  background-color: var(--color-gray-50);
  font-family: inherit;
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5rem;
  color: var(--color-gray-900);
  user-select: none;

  & span {
    font-variant-numeric: tabular-nums;
    display: inline-block;
    text-align: end;
    min-width: 2.5ch;
  }

  @media (hover: hover) {
    &:hover {
      background-color: var(--color-gray-100);
    }
  }

  &:active {
    background-color: var(--color-gray-100);
  }

  &:focus-visible {
    outline: 2px solid var(--color-blue);
    outline-offset: -1px;
  }
}

.suffix {
  margin-left: 0.125rem;
}
```

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { useRender } from '@base-ui/react/use-render';
import { mergeProps } from '@base-ui/react/merge-props';
import styles from './index.module.css';

interface CounterState {
  odd: boolean;
}

interface CounterProps extends useRender.ComponentProps<'button', CounterState> {}

function Counter(props: CounterProps) {
  const { render, ...otherProps } = props;

  const [count, setCount] = React.useState(0);
  const odd = count % 2 === 1;
  const state = React.useMemo(() => ({ odd }), [odd]);

  const defaultProps: useRender.ElementProps<'button'> = {
    className: styles.Button,
    type: 'button',
    children: (
      <React.Fragment>
        Counter: <span>{count}</span>
      </React.Fragment>
    ),
    onClick() {
      setCount((prev) => prev + 1);
    },
    'aria-label': `Count is ${count}, click to increase.`,
  };

  const element = useRender({
    defaultTagName: 'button',
    render,
    state,
    props: mergeProps<'button'>(defaultProps, otherProps),
  });

  return element;
}

export default function ExampleCounter() {
  return (
    <Counter
      render={(props, state) => (
        <button {...props}>
          {props.children}
          <span className={styles.suffix}>{state.odd ? '👎' : '👍'}</span>
        </button>
      )}
    />
  );
}
```

## Merging props

The `mergeProps` function merges two or more sets of React props together. It safely merges three types of props:

1. Event handlers, so that all are invoked
2. `className` strings
3. `style` properties

`mergeProps` merges objects from left to right, so that subsequent objects' properties in the arguments overwrite previous ones. Merging props is useful when creating custom components, as well as inside the callback version of the `render` prop for any Base UI component.

```tsx title="Using mergeProps in the render callback"
import { mergeProps } from '@base-ui/react/merge-props';
import styles from './index.module.css';

function Button() {
  return (
    <Component
      render={(props, state) => (
        <button
          {...mergeProps<'button'>(props, {
            className: styles.Button,
          })}
        />
      )}
    />
  );
}
```

## Merging refs

When building custom components, you often need to control a ref internally while still letting external consumers pass their own—merging refs lets both parties have access to the underlying DOM element. The `ref` option in `useRender` enables this, which holds an array of refs to be merged together.

In React 19, `React.forwardRef()` is not needed when building primitive components, as the external ref prop is already contained inside `props`. Your internal ref can be passed to `ref` to be merged with `props.ref`:

```tsx title="React 19" {6} "internalRef"
function Text({ render, ...props }: TextProps) {
  const internalRef = React.useRef<HTMLElement | null>(null);

  const element = useRender({
    defaultTagName: 'p',
    ref: internalRef,
    props,
    render,
  });

  return element;
}
```

In older versions of React, you need to use `React.forwardRef()` and add the forwarded ref to the `ref` array along with your own internal ref.

The [examples](/react/utils/use-render.md) above assume React 19, and should be modified to use `React.forwardRef()` to support React 18 and 17.

```tsx title="React 18 and 17" {9} "forwardedRef" "internalRef"
const Text = React.forwardRef(function Text(
  { render, ...props }: TextProps,
  forwardedRef: React.ForwardedRef<HTMLElement>,
) {
  const internalRef = React.useRef<HTMLElement | null>(null);

  const element = useRender({
    defaultTagName: 'p',
    ref: [forwardedRef, internalRef],
    props,
    render,
  });

  return element;
});
```

## TypeScript

To type props, there are two interfaces:

- `useRender.ComponentProps` for a component's external (public) props. It types the `render` prop and HTML attributes.
- `useRender.ElementProps` for the element's internal (private) props. It types HTML attributes alone.

```tsx title="Typing props" {1,4}
interface ButtonProps extends useRender.ComponentProps<'button'> {}

function Button({ render, ...props }: ButtonProps) {
  const defaultProps: useRender.ElementProps<'button'> = {
    className: styles.Button,
    type: 'button',
    children: 'Click me',
  };

  const element = useRender({
    defaultTagName: 'button',
    render,
    props: mergeProps<'button'>(defaultProps, props),
  });

  return element;
}
```

## Migrating from Radix UI

Radix UI uses an `asChild` prop, while Base UI uses a `render` prop. Learn more about how composition works in Base UI in the [composition guide](/react/handbook/composition.md).

In Radix UI, the `Slot` component lets you implement an `asChild` prop.

```jsx title="Radix UI Slot component"
import { Slot } from 'radix-ui';

function Button({ asChild, ...props }) {
  const Comp = asChild ? Slot.Root : 'button';
  return <Comp {...props} />;
}

// Usage
<Button asChild>
  <a href="/contact">Contact</a>
</Button>;
```

In Base UI, `useRender` lets you implement a `render` prop. The example below is the equivalent implementation to the Radix example above.

```jsx title="Base UI render prop"
import { useRender } from '@base-ui/react/use-render';

function Button({ render, ...props }) {
  return useRender({
    defaultTagName: 'button',
    render,
    props,
  });
}

// Usage
<Button render={<a href="/contact" />}>Contact</Button>;
```

## API reference

### Input parameters

**Props:**

| Prop                   | Type                                                                 | Default | Description                                                                                                                                                                                                                                                  |
| :--------------------- | :------------------------------------------------------------------- | :------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| defaultTagName         | `keyof React.JSX.IntrinsicElements`                                  | -       | The default tag name to use for the rendered element when `render` is not provided.                                                                                                                                                                          |
| render                 | `RenderProp<State>`                                                  | -       | The React element or a function that returns one to override the default element.                                                                                                                                                                            |
| props                  | `Record<string, unknown>`                                            | -       | Props to be spread on the rendered element.They are merged with the internal props&#xA;of the component, so that event handlers are merged,&#xA;`className` strings and `style` properties are joined, and other external props overwrite the internal ones. |
| ref                    | `React.Ref<RenderedElementType> \| React.Ref<RenderedElementType>[]` | -       | The refs to apply to the rendered element.                                                                                                                                                                                                                   |
| state                  | `State`                                                              | -       | The state of the component. It will be used as a parameter for the render callback.                                                                                                                                                                          |
| stateAttributesMapping | `StateAttributesMapping<State>`                                      | -       | Custom mapping for converting state properties to data-\* attributes.                                                                                                                                                                                        |

### Return value

**Return Value:**

| Property | Type                 | Description                |
| :------- | :------------------- | :------------------------- |
| element  | `React.ReactElement` | The rendered React element |

```tsx title="Usage"
const element = useRender({
  // Input parameters
});
```
