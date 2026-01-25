---
title: Toast
subtitle: Generates toast notifications.
description: A high-quality, unstyled React toast component to generate notifications.
---

# Toast

A high-quality, unstyled React toast component to generate notifications.

## Demo

### Tailwind

This example shows how to implement the component using Tailwind CSS.

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';

export default function ExampleToast() {
  return (
    <Toast.Provider>
      <ToastButton />
      <Toast.Portal>
        <Toast.Viewport className="fixed z-10 top-auto right-[1rem] bottom-[1rem] mx-auto flex w-[250px] sm:right-[2rem] sm:bottom-[2rem] sm:w-[300px]">
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}

function ToastButton() {
  const toastManager = Toast.useToastManager();
  const [count, setCount] = React.useState(0);

  function createToast() {
    setCount((prev) => prev + 1);
    toastManager.add({
      title: `Toast ${count + 1} created`,
      description: 'This is a toast notification.',
    });
  }

  return (
    <button
      type="button"
      className="box-border flex h-10 items-center justify-center rounded-md border border-gray-200 bg-gray-50 px-3.5 py-0 font-medium text-gray-900 outline-0 select-none hover:bg-gray-100 focus-visible:outline-2 focus-visible:-outline-offset-1 focus-visible:outline-blue active:bg-gray-100"
      onClick={createToast}
    >
      Create toast
    </button>
  );
}

function ToastList() {
  const { toasts } = Toast.useToastManager();
  return toasts.map((toast) => (
    <Toast.Root
      key={toast.id}
      toast={toast}
      className="[--gap:0.75rem] [--peek:0.75rem] [--scale:calc(max(0,1-(var(--toast-index)*0.1)))] [--shrink:calc(1-var(--scale))] [--height:var(--toast-frontmost-height,var(--toast-height))] [--offset-y:calc(var(--toast-offset-y)*-1+calc(var(--toast-index)*var(--gap)*-1)+var(--toast-swipe-movement-y))] absolute right-0 bottom-0 left-auto z-[calc(1000-var(--toast-index))] mr-0 w-full origin-bottom [transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--toast-swipe-movement-y)-(var(--toast-index)*var(--peek))-(var(--shrink)*var(--height))))_scale(var(--scale))] rounded-lg border border-gray-200 bg-gray-50 bg-clip-padding p-4 shadow-lg select-none after:absolute after:top-full after:left-0 after:h-[calc(var(--gap)+1px)] after:w-full after:content-[''] data-[ending-style]:opacity-0 data-[expanded]:[transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--offset-y)))] data-[limited]:opacity-0 data-[starting-style]:[transform:translateY(150%)] [&[data-ending-style]:not([data-limited]):not([data-swipe-direction])]:[transform:translateY(150%)] data-[ending-style]:data-[swipe-direction=down]:[transform:translateY(calc(var(--toast-swipe-movement-y)+150%))] data-[expanded]:data-[ending-style]:data-[swipe-direction=down]:[transform:translateY(calc(var(--toast-swipe-movement-y)+150%))] data-[ending-style]:data-[swipe-direction=left]:[transform:translateX(calc(var(--toast-swipe-movement-x)-150%))_translateY(var(--offset-y))] data-[expanded]:data-[ending-style]:data-[swipe-direction=left]:[transform:translateX(calc(var(--toast-swipe-movement-x)-150%))_translateY(var(--offset-y))] data-[ending-style]:data-[swipe-direction=right]:[transform:translateX(calc(var(--toast-swipe-movement-x)+150%))_translateY(var(--offset-y))] data-[expanded]:data-[ending-style]:data-[swipe-direction=right]:[transform:translateX(calc(var(--toast-swipe-movement-x)+150%))_translateY(var(--offset-y))] data-[ending-style]:data-[swipe-direction=up]:[transform:translateY(calc(var(--toast-swipe-movement-y)-150%))] data-[expanded]:data-[ending-style]:data-[swipe-direction=up]:[transform:translateY(calc(var(--toast-swipe-movement-y)-150%))] h-[var(--height)] data-[expanded]:h-[var(--toast-height)] [transition:transform_0.5s_cubic-bezier(0.22,1,0.36,1),opacity_0.5s,height_0.15s]"
    >
      <Toast.Content className="overflow-hidden transition-opacity [transition-duration:250ms] data-[behind]:pointer-events-none data-[behind]:opacity-0 data-[expanded]:pointer-events-auto data-[expanded]:opacity-100">
        <Toast.Title className="text-[0.975rem] leading-5 font-medium" />
        <Toast.Description className="text-[0.925rem] leading-5 text-gray-700" />
        <Toast.Close
          className="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded border-none bg-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-700"
          aria-label="Close"
        >
          <XIcon className="h-4 w-4" />
        </Toast.Close>
      </Toast.Content>
    </Toast.Root>
  ));
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

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

.Viewport {
  position: fixed;
  z-index: 1;
  width: 250px;
  margin: 0 auto;
  bottom: 1rem;
  right: 1rem;
  left: auto;
  top: auto;

  @media (min-width: 500px) {
    bottom: 2rem;
    right: 2rem;
    width: 300px;
  }
}

.Toast {
  --gap: 0.75rem;
  --peek: 0.75rem;
  --scale: calc(max(0, 1 - (var(--toast-index) * 0.1)));
  --shrink: calc(1 - var(--scale));
  --height: var(--toast-frontmost-height, var(--toast-height));
  --offset-y: calc(
    var(--toast-offset-y) * -1 + (var(--toast-index) * var(--gap) * -1) +
      var(--toast-swipe-movement-y)
  );
  position: absolute;
  right: 0;
  margin: 0 auto;
  box-sizing: border-box;
  background: var(--color-gray-50);
  color: var(--color-gray-900);
  border: 1px solid var(--color-gray-200);
  padding: 1rem;
  width: 100%;
  box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
  background-clip: padding-box;
  border-radius: 0.5rem;
  transform-origin: bottom center;
  bottom: 0;
  left: auto;
  margin-right: 0;
  -webkit-user-select: none;
  user-select: none;
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.5s,
    height 0.15s;
  cursor: default;
  z-index: calc(1000 - var(--toast-index));
  height: var(--height);
  transform: translateX(var(--toast-swipe-movement-x))
    translateY(
      calc(
        var(--toast-swipe-movement-y) - (var(--toast-index) * var(--peek)) -
          (var(--shrink) * var(--height))
      )
    )
    scale(var(--scale));

  &[data-expanded] {
    transform: translateX(var(--toast-swipe-movement-x)) translateY(var(--offset-y));
    height: var(--toast-height);
  }

  &[data-starting-style],
  &[data-ending-style] {
    transform: translateY(150%);
  }

  &[data-limited] {
    opacity: 0;
  }

  &[data-ending-style] {
    opacity: 0;

    &[data-swipe-direction='up'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) - 150%));
    }
    &[data-swipe-direction='left'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) - 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='right'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) + 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='down'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) + 150%));
    }
  }

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    width: 100%;
    left: 0;
    height: calc(var(--gap) + 1px);
  }
}

.Content {
  overflow: hidden;
  transition: opacity 0.25s;

  &[data-behind] {
    opacity: 0;
  }

  &[data-expanded] {
    opacity: 1;
  }
}

.Title {
  font-weight: 500;
  font-size: 0.975rem;
  line-height: 1.25rem;
  margin: 0;
}

.Description {
  font-size: 0.925rem;
  line-height: 1.25rem;
  margin: 0;
}

.Close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0;
  border: none;
  background: transparent;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;

  &:hover {
    background-color: var(--color-gray-100);
  }
}

.Icon {
  width: 1rem;
  height: 1rem;
}
```

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';
import styles from './index.module.css';

export default function ExampleToast() {
  return (
    <Toast.Provider>
      <ToastButton />
      <Toast.Portal>
        <Toast.Viewport className={styles.Viewport}>
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}

function ToastButton() {
  const toastManager = Toast.useToastManager();
  const [count, setCount] = React.useState(0);

  function createToast() {
    setCount((prev) => prev + 1);
    toastManager.add({
      title: `Toast ${count + 1} created`,
      description: 'This is a toast notification.',
    });
  }

  return (
    <button type="button" className={styles.Button} onClick={createToast}>
      Create toast
    </button>
  );
}

function ToastList() {
  const { toasts } = Toast.useToastManager();
  return toasts.map((toast) => (
    <Toast.Root key={toast.id} toast={toast} className={styles.Toast}>
      <Toast.Content className={styles.Content}>
        <Toast.Title className={styles.Title} />
        <Toast.Description className={styles.Description} />
        <Toast.Close className={styles.Close} aria-label="Close">
          <XIcon className={styles.Icon} />
        </Toast.Close>
      </Toast.Content>
    </Toast.Root>
  ));
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

## Anatomy

Import the component and assemble its parts:

```jsx title="Anatomy"
import { Toast } from '@base-ui/react/toast';

<Toast.Provider>
  <Toast.Portal>
    <Toast.Viewport>
      {/* Stacked toasts */}
      <Toast.Root>
        <Toast.Content>
          <Toast.Title />
          <Toast.Description />
          <Toast.Action />
          <Toast.Close />
        </Toast.Content>
      </Toast.Root>

      {/* Anchored toasts */}
      <Toast.Positioner>
        <Toast.Root>
          <Toast.Arrow />
          <Toast.Content>
            <Toast.Title />
            <Toast.Description />
            <Toast.Action />
            <Toast.Close />
          </Toast.Content>
        </Toast.Root>
      </Toast.Positioner>
    </Toast.Viewport>
  </Toast.Portal>
</Toast.Provider>;
```

## General usage

- `<Toast.Provider>` can be wrapped around your entire app, ensuring all toasts are rendered in the same viewport.
- <kbd>F6</kbd> lets users jump into the toast viewport landmark region to navigate toasts with
  keyboard focus.
- The `data-swipe-ignore` attribute can be manually added to elements inside of a toast to prevent swipe-to-dismiss gestures on them. Interactive elements are automatically prevented.

## Global manager

A global toast manager can be created by passing the `toastManager` prop to the `<Toast.Provider>`.
This enables you to queue a toast from anywhere in the app (such as in functions outside the React tree) while still using the same toast renderer.

The created `toastManager` object has the same properties and methods as the `Toast.useToastManager()` hook.

```tsx title="Creating a manager instance"
const toastManager = Toast.createToastManager();
```

```jsx title="Using the instance"
<Toast.Provider toastManager={toastManager}>
```

## Stacking and animations

The `--toast-index` CSS variable can be used to determine the stacking order of the toasts.
The 0th index toast appears at the front.

```css title="z-index stacking"
.Toast {
  z-index: calc(1000 - var(--toast-index));
  transform: scale(1 - calc(0.1 * var(--toast-index)));
}
```

The `--toast-offset-y` CSS variable can be used to determine the vertical offset of the toasts when positioned absolutely with a translation offset — this is usually used with the `data-expanded` attribute, present when the toast viewport is being hovered or has focus.

```css title="Expanded offset"
.Toast[data-expanded] {
  transform: translateY(var(--toast-offset-y));
}
```

`<Toast.Content>` is used to hide overflow from taller toasts while the stack is collapsed.
The `data-behind` attribute marks content that sits behind the frontmost toast and pairs with the `data-expanded` attribute so the content fades back in when the viewport expands:

```css title="Collapsed content" "data-behind" "data-expanded"
.ToastContent {
  overflow: hidden;
  transition: opacity 0.25s;
}

.ToastContent[data-behind] {
  opacity: 0;
}

.ToastContent[data-expanded] {
  opacity: 1;
}
```

The `--toast-swipe-movement-x` and `--toast-swipe-movement-y` CSS variables are used to determine the swipe movement of the toasts in order to add a translation offset.

```css title="Swipe offset"  "--toast-swipe-movement-x" "--toast-swipe-movement-y"
.Toast {
  transform: scale(1 - calc(0.1 * var(--toast-index))) translateX(var(--toast-swipe-movement-x))
    translateY(calc(var(--toast-swipe-movement-y) + (var(--toast-index) * -20%)));
}
```

The `data-swipe-direction` attribute can be used to determine the swipe direction of the toasts to add a translation offset upon dismissal.

```css title="Swipe direction" "data-swipe-direction"
&[data-ending-style] {
  opacity: 0;

  &[data-swipe-direction='up'] {
    transform: translateY(calc(var(--toast-swipe-movement-y) - 150%));
  }
  &[data-swipe-direction='down'] {
    transform: translateY(calc(var(--toast-swipe-movement-y) + 150%));
  }
  /* Note: --offset-y is defined locally in these examples and derives from
   --toast-offset-y, --toast-index, and swipe movement values */
  &[data-swipe-direction='left'] {
    transform: translateX(calc(var(--toast-swipe-movement-x) - 150%)) translateY(var(--offset-y));
  }
  &[data-swipe-direction='right'] {
    transform: translateX(calc(var(--toast-swipe-movement-x) + 150%)) translateY(var(--offset-y));
  }
}
```

The `data-limited` attribute indicates that the toast was removed from the list due to exceeding the `limit` option.
This is useful for animating the toast differently when it is removed from the list.

## Examples

### Anchored toasts

Toasts can be anchored to a specific element using `<Toast.Positioner>` and the `positionerProps` option when adding a toast. This is useful for showing contextual feedback like transient "Copied" toasts that appear near the button that triggered the action.

Anchored toasts should be rendered in a separate `<Toast.Provider>` from stacked toasts. A global toast manager can be created for each to manage them separately throughout your app:

```tsx title="Mixing stacked and anchored toasts"
const anchoredToastManager = Toast.createToastManager();
const stackedToastManager = Toast.createToastManager();

function App() {
  return (
    <React.Fragment>
      <Toast.Provider toastManager={anchoredToastManager}>
        <AnchoredToasts />
      </Toast.Provider>
      <Toast.Provider toastManager={stackedToastManager}>
        <StackedToasts />
      </Toast.Provider>

      {/* App content */}
    </React.Fragment>
  );
}

function AnchoredToasts() {
  const { toasts } = Toast.useToastManager();
  return (
    <Toast.Portal>
      <Toast.Viewport>
        {toasts.map((toast) => (
          <Toast.Positioner key={toast.id} toast={toast}>
            <Toast.Root toast={toast}>{/* ... */}</Toast.Root>
          </Toast.Positioner>
        ))}
      </Toast.Viewport>
    </Toast.Portal>
  );
}

function StackedToasts() {
  const { toasts } = Toast.useToastManager();
  return (
    <Toast.Portal>
      <Toast.Viewport>
        {toasts.map((toast) => (
          <Toast.Root key={toast.id} toast={toast}>
            {/* ... */}
          </Toast.Root>
        ))}
      </Toast.Viewport>
    </Toast.Portal>
  );
}
```

## Demo

### Tailwind

This example shows how to implement the component using Tailwind CSS.

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';
import { Button } from '@base-ui/react/button';
import { Tooltip } from '@base-ui/react/tooltip';

const stackedToastManager = Toast.createToastManager();
const anchoredToastManager = Toast.createToastManager();

export default function ExampleToast() {
  return (
    <Tooltip.Provider>
      <Toast.Provider toastManager={anchoredToastManager}>
        <AnchoredToasts />
      </Toast.Provider>
      <Toast.Provider toastManager={stackedToastManager}>
        <StackedToasts />
      </Toast.Provider>

      <div className="flex items-center gap-2">
        <CopyButton />
        <StackedToastButton />
      </div>
    </Tooltip.Provider>
  );
}

function StackedToastButton() {
  function createToast() {
    stackedToastManager.add({
      description: 'Copied',
    });
  }

  return (
    <button
      type="button"
      className="box-border flex h-10 items-center justify-center rounded-md border border-gray-200 bg-gray-50 px-3.5 py-0 font-medium text-gray-900 outline-0 select-none hover:bg-gray-100 focus-visible:outline-2 focus-visible:-outline-offset-1 focus-visible:outline-blue-800 active:bg-gray-100"
      onClick={createToast}
    >
      Stacked toast
    </button>
  );
}

function CopyButton() {
  const [copied, setCopied] = React.useState(false);
  const buttonRef = React.useRef<HTMLButtonElement | null>(null);

  function handleCopy() {
    setCopied(true);

    anchoredToastManager.add({
      description: 'Copied',
      positionerProps: {
        anchor: buttonRef.current,
        sideOffset: 8,
      },
      timeout: 1500,
      onClose() {
        setCopied(false);
      },
    });
  }

  return (
    <Tooltip.Root
      disabled={copied}
      onOpenChange={(open, eventDetails) => {
        if (eventDetails.reason === 'trigger-press') {
          eventDetails.cancel();
        }
      }}
    >
      <Tooltip.Trigger
        ref={buttonRef}
        className="box-border flex h-10 w-10 items-center justify-center rounded-md border border-gray-200 bg-gray-50 text-gray-900 outline-0 select-none hover:bg-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-1 focus-visible:outline-blue-800 active:bg-gray-100"
        onClick={handleCopy}
        aria-label="Copy to clipboard"
        render={<Button disabled={copied} focusableWhenDisabled />}
      >
        {copied ? <CheckIcon className="h-5 w-5" /> : <ClipboardIcon className="h-5 w-5" />}
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Positioner sideOffset={8}>
          <Tooltip.Popup className="flex origin-(--transform-origin) flex-col rounded-md bg-[canvas] px-2 py-1 text-sm shadow-lg shadow-gray-200 outline-1 outline-gray-200 transition-[transform,scale,opacity] data-ending-style:scale-90 data-ending-style:opacity-0 data-instant:duration-0 data-starting-style:scale-90 data-starting-style:opacity-0 dark:shadow-none dark:-outline-offset-1 dark:outline-gray-300">
            <Tooltip.Arrow className="data-[side=bottom]:-top-2 data-[side=left]:right-[-13px] data-[side=left]:rotate-90 data-[side=right]:left-[-13px] data-[side=right]:-rotate-90 data-[side=top]:-bottom-2 data-[side=top]:rotate-180">
              <ArrowSvg />
            </Tooltip.Arrow>
            Copy
          </Tooltip.Popup>
        </Tooltip.Positioner>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}

function AnchoredToasts() {
  const { toasts } = Toast.useToastManager();
  return (
    <Toast.Portal>
      <Toast.Viewport className="outline-0">
        {toasts.map((toast) => (
          <Toast.Positioner
            key={toast.id}
            toast={toast}
            className="z-[calc(1000-var(--toast-index))]"
          >
            <Toast.Root
              toast={toast}
              className="group flex w-max origin-(--transform-origin) flex-col rounded-md bg-[canvas] px-2 py-1 text-sm shadow-lg shadow-gray-200 outline-1 outline-gray-200 transition-[transform,scale,opacity] data-ending-style:scale-90 data-ending-style:opacity-0 data-starting-style:scale-90 data-starting-style:opacity-0 focus-visible:outline-1 focus-visible:-outline-offset-1 focus-visible:outline-blue-800 dark:shadow-none dark:-outline-offset-1 dark:outline-gray-300 dark:focus-visible:outline-blue-400"
            >
              <Toast.Arrow className="data-[side=bottom]:-top-2 data-[side=left]:right-[-13px] data-[side=left]:rotate-90 data-[side=right]:left-[-13px] data-[side=right]:-rotate-90 data-[side=top]:-bottom-2 data-[side=top]:rotate-180">
                <ArrowSvg />
              </Toast.Arrow>
              <Toast.Content>
                <Toast.Description />
              </Toast.Content>
            </Toast.Root>
          </Toast.Positioner>
        ))}
      </Toast.Viewport>
    </Toast.Portal>
  );
}

function StackedToasts() {
  const { toasts } = Toast.useToastManager();
  return (
    <Toast.Portal>
      <Toast.Viewport className="fixed z-10 top-auto right-[1rem] bottom-[1rem] mx-auto flex w-[250px] sm:right-[2rem] sm:bottom-[2rem] sm:w-[300px]">
        {toasts.map((toast) => (
          <Toast.Root
            key={toast.id}
            toast={toast}
            className="[--gap:0.75rem] [--peek:0.75rem] [--scale:calc(max(0,1-(var(--toast-index)*0.1)))] [--shrink:calc(1-var(--scale))] [--height:var(--toast-frontmost-height,var(--toast-height))] [--offset-y:calc(var(--toast-offset-y)*-1+calc(var(--toast-index)*var(--gap)*-1)+var(--toast-swipe-movement-y))] absolute right-0 bottom-0 left-auto z-[calc(1000-var(--toast-index))] mr-0 w-full origin-bottom [transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--toast-swipe-movement-y)-(var(--toast-index)*var(--peek))-(var(--shrink)*var(--height))))_scale(var(--scale))] rounded-lg border border-gray-200 bg-gray-50 bg-clip-padding p-4 shadow-lg select-none after:absolute after:top-full after:left-0 after:h-[calc(var(--gap)+1px)] after:w-full after:content-[''] data-[ending-style]:opacity-0 data-[expanded]:[transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--offset-y)))] data-[limited]:opacity-0 data-[starting-style]:[transform:translateY(150%)] [&[data-ending-style]:not([data-limited]):not([data-swipe-direction])]:[transform:translateY(150%)] data-[ending-style]:data-[swipe-direction=down]:[transform:translateY(calc(var(--toast-swipe-movement-y)+150%))] data-[expanded]:data-[ending-style]:data-[swipe-direction=down]:[transform:translateY(calc(var(--toast-swipe-movement-y)+150%))] data-[ending-style]:data-[swipe-direction=left]:[transform:translateX(calc(var(--toast-swipe-movement-x)-150%))_translateY(var(--offset-y))] data-[expanded]:data-[ending-style]:data-[swipe-direction=left]:[transform:translateX(calc(var(--toast-swipe-movement-x)-150%))_translateY(var(--offset-y))] data-[ending-style]:data-[swipe-direction=right]:[transform:translateX(calc(var(--toast-swipe-movement-x)+150%))_translateY(var(--offset-y))] data-[expanded]:data-[ending-style]:data-[swipe-direction=right]:[transform:translateX(calc(var(--toast-swipe-movement-x)+150%))_translateY(var(--offset-y))] data-[ending-style]:data-[swipe-direction=up]:[transform:translateY(calc(var(--toast-swipe-movement-y)-150%))] data-[expanded]:data-[ending-style]:data-[swipe-direction=up]:[transform:translateY(calc(var(--toast-swipe-movement-y)-150%))] h-[var(--height)] data-[expanded]:h-[var(--toast-height)] [transition:transform_0.5s_cubic-bezier(0.22,1,0.36,1),opacity_0.5s,height_0.15s]"
          >
            <Toast.Content className="overflow-hidden transition-opacity [transition-duration:250ms] data-[behind]:pointer-events-none data-[behind]:opacity-0 data-[expanded]:pointer-events-auto data-[expanded]:opacity-100">
              <Toast.Title className="text-[0.975rem] leading-5 font-medium" />
              <Toast.Description className="text-[0.925rem] leading-5 text-gray-700" />
              <Toast.Close
                className="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded border-none bg-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-700"
                aria-label="Close"
              >
                <XIcon className="h-4 w-4" />
              </Toast.Close>
            </Toast.Content>
          </Toast.Root>
        ))}
      </Toast.Viewport>
    </Toast.Portal>
  );
}

function ArrowSvg(props: React.ComponentProps<'svg'>) {
  return (
    <svg width="20" height="10" viewBox="0 0 20 10" fill="none" {...props}>
      <path
        d="M9.66437 2.60207L4.80758 6.97318C4.07308 7.63423 3.11989 8 2.13172 8H0V10H20V8H18.5349C17.5468 8 16.5936 7.63423 15.8591 6.97318L11.0023 2.60207C10.622 2.2598 10.0447 2.25979 9.66437 2.60207Z"
        className="fill-[canvas]"
      />
      <path
        d="M8.99542 1.85876C9.75604 1.17425 10.9106 1.17422 11.6713 1.85878L16.5281 6.22989C17.0789 6.72568 17.7938 7.00001 18.5349 7.00001L15.89 7L11.0023 2.60207C10.622 2.2598 10.0447 2.2598 9.66436 2.60207L4.77734 7L2.13171 7.00001C2.87284 7.00001 3.58774 6.72568 4.13861 6.22989L8.99542 1.85876Z"
        className="fill-gray-200 dark:fill-none"
      />
      <path
        d="M10.3333 3.34539L5.47654 7.71648C4.55842 8.54279 3.36693 9 2.13172 9H0V8H2.13172C3.11989 8 4.07308 7.63423 4.80758 6.97318L9.66437 2.60207C10.0447 2.25979 10.622 2.2598 11.0023 2.60207L15.8591 6.97318C16.5936 7.63423 17.5468 8 18.5349 8H20V9H18.5349C17.2998 9 16.1083 8.54278 15.1901 7.71648L10.3333 3.34539Z"
        className="dark:fill-gray-300"
      />
    </svg>
  );
}

function ClipboardIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <rect width="8" height="4" x="8" y="2" rx="1" ry="1" />
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
    </svg>
  );
}

function CheckIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

### CSS Modules

This example shows how to implement the component using CSS Modules.

```css
/* index.module.css */
.ButtonGroup {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

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

.CopyButton {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  margin: 0;
  outline: 0;
  border: 1px solid var(--color-gray-200);
  border-radius: 0.375rem;
  background-color: var(--color-gray-50);
  font-family: inherit;
  color: var(--color-gray-900);
  user-select: none;

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

.AnchoredViewport {
  outline: 0;
}

.AnchoredPositioner {
  z-index: calc(1000 - var(--toast-index));
}

.AnchoredToast {
  box-sizing: border-box;
  font-size: 0.875rem;
  line-height: 1.25rem;
  display: flex;
  flex-direction: column;
  width: max-content;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  background-color: canvas;
  transform-origin: var(--transform-origin);
  transition:
    transform 150ms,
    opacity 150ms;

  &[data-starting-style],
  &[data-ending-style] {
    opacity: 0;
    transform: scale(0.9);
  }

  @media (prefers-color-scheme: light) {
    outline: 1px solid var(--color-gray-200);
    box-shadow:
      0 10px 15px -3px var(--color-gray-200),
      0 4px 6px -4px var(--color-gray-200);

    &:focus-visible {
      outline: 1px solid var(--color-blue-800);
      outline-offset: -1px;
    }
  }

  @media (prefers-color-scheme: dark) {
    outline: 1px solid var(--color-gray-300);
    outline-offset: -1px;

    &:focus-visible {
      outline: 1px solid var(--color-blue-400);
      outline-offset: -1px;
    }
  }
}

.StackedViewport {
  position: fixed;
  z-index: 1;
  width: 250px;
  margin: 0 auto;
  bottom: 1rem;
  right: 1rem;
  left: auto;
  top: auto;

  @media (min-width: 500px) {
    bottom: 2rem;
    right: 2rem;
    width: 300px;
  }
}

.StackedToast {
  --gap: 0.75rem;
  --peek: 0.75rem;
  --scale: calc(max(0, 1 - (var(--toast-index) * 0.1)));
  --shrink: calc(1 - var(--scale));
  --height: var(--toast-frontmost-height, var(--toast-height));
  --offset-y: calc(
    var(--toast-offset-y) * -1 + (var(--toast-index) * var(--gap) * -1) +
      var(--toast-swipe-movement-y)
  );
  position: absolute;
  right: 0;
  margin: 0 auto;
  box-sizing: border-box;
  background: var(--color-gray-50);
  color: var(--color-gray-900);
  border: 1px solid var(--color-gray-200);
  padding: 1rem;
  width: 100%;
  box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
  background-clip: padding-box;
  border-radius: 0.5rem;
  transform-origin: bottom center;
  bottom: 0;
  left: auto;
  margin-right: 0;
  -webkit-user-select: none;
  user-select: none;
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.5s,
    height 0.15s;
  cursor: default;
  z-index: calc(1000 - var(--toast-index));
  height: var(--height);
  transform: translateX(var(--toast-swipe-movement-x))
    translateY(
      calc(
        var(--toast-swipe-movement-y) - (var(--toast-index) * var(--peek)) -
          (var(--shrink) * var(--height))
      )
    )
    scale(var(--scale));

  &[data-expanded] {
    transform: translateX(var(--toast-swipe-movement-x)) translateY(var(--offset-y));
    height: var(--toast-height);
  }

  &[data-starting-style],
  &[data-ending-style] {
    transform: translateY(150%);
  }

  &[data-limited] {
    opacity: 0;
  }

  &[data-ending-style] {
    opacity: 0;

    &[data-swipe-direction='up'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) - 150%));
    }
    &[data-swipe-direction='left'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) - 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='right'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) + 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='down'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) + 150%));
    }
  }

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    width: 100%;
    left: 0;
    height: calc(var(--gap) + 1px);
  }
}

.Content {
  overflow: hidden;
  transition: opacity 0.25s;

  &[data-behind] {
    opacity: 0;
  }

  &[data-expanded] {
    opacity: 1;
  }
}

.Title {
  font-weight: 500;
  font-size: 0.975rem;
  line-height: 1.25rem;
  margin: 0;
}

.Description {
  font-size: 0.925rem;
  line-height: 1.25rem;
  margin: 0;
}

.Close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0;
  border: none;
  background: transparent;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;

  &:hover {
    background-color: var(--color-gray-100);
  }
}

.Icon {
  width: 1rem;
  height: 1rem;
}

.Tooltip {
  box-sizing: border-box;
  font-size: 0.875rem;
  line-height: 1.25rem;
  display: flex;
  flex-direction: column;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  background-color: canvas;
  transform-origin: var(--transform-origin);
  transition:
    transform 150ms,
    opacity 150ms;

  &[data-starting-style],
  &[data-ending-style] {
    opacity: 0;
    transform: scale(0.9);
  }

  &[data-instant] {
    transition-duration: 0ms;
  }

  @media (prefers-color-scheme: light) {
    outline: 1px solid var(--color-gray-200);
    box-shadow:
      0 10px 15px -3px var(--color-gray-200),
      0 4px 6px -4px var(--color-gray-200);
  }

  @media (prefers-color-scheme: dark) {
    outline: 1px solid var(--color-gray-300);
    outline-offset: -1px;
  }
}

.Arrow {
  display: flex;

  &[data-side='top'] {
    bottom: -8px;
    rotate: 180deg;
  }

  &[data-side='bottom'] {
    top: -8px;
    rotate: 0deg;
  }

  &[data-side='left'] {
    right: -13px;
    rotate: 90deg;
  }

  &[data-side='right'] {
    left: -13px;
    rotate: -90deg;
  }
}

.ArrowFill {
  fill: canvas;
}

.ArrowOuterStroke {
  @media (prefers-color-scheme: light) {
    fill: var(--color-gray-200);
  }
}

.ArrowInnerStroke {
  @media (prefers-color-scheme: dark) {
    fill: var(--color-gray-300);
  }
}

.Viewport {
  outline: 0;
}
```

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';
import { Button } from '@base-ui/react/button';
import { Tooltip } from '@base-ui/react/tooltip';
import styles from './index.module.css';

const anchoredToastManager = Toast.createToastManager();
const stackedToastManager = Toast.createToastManager();

export default function ExampleToast() {
  return (
    <Tooltip.Provider>
      <Toast.Provider toastManager={anchoredToastManager}>
        <AnchoredToasts />
      </Toast.Provider>
      <Toast.Provider toastManager={stackedToastManager}>
        <StackedToasts />
      </Toast.Provider>

      <div className={styles.ButtonGroup}>
        <CopyButton />
        <StackedToastButton />
      </div>
    </Tooltip.Provider>
  );
}

function StackedToastButton() {
  function createToast() {
    stackedToastManager.add({
      description: 'Copied',
    });
  }

  return (
    <button type="button" className={styles.Button} onClick={createToast}>
      Stacked toast
    </button>
  );
}

function CopyButton() {
  const [copied, setCopied] = React.useState(false);
  const buttonRef = React.useRef<HTMLButtonElement | null>(null);

  function handleCopy() {
    setCopied(true);

    anchoredToastManager.add({
      description: 'Copied',
      positionerProps: {
        anchor: buttonRef.current,
        sideOffset: 8,
      },
      timeout: 1500,
      onClose() {
        setCopied(false);
      },
    });
  }

  return (
    <Tooltip.Root
      disabled={copied}
      onOpenChange={(open, eventDetails) => {
        if (eventDetails.reason === 'trigger-press') {
          eventDetails.cancel();
        }
      }}
    >
      <Tooltip.Trigger
        ref={buttonRef}
        className={styles.CopyButton}
        onClick={handleCopy}
        aria-label="Copy to clipboard"
        render={<Button disabled={copied} focusableWhenDisabled />}
      >
        {copied ? <CheckIcon className={styles.Icon} /> : <ClipboardIcon className={styles.Icon} />}
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Positioner sideOffset={8}>
          <Tooltip.Popup className={styles.Tooltip}>
            <Tooltip.Arrow className={styles.Arrow}>
              <ArrowSvg />
            </Tooltip.Arrow>
            Copy
          </Tooltip.Popup>
        </Tooltip.Positioner>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}

function AnchoredToasts() {
  const { toasts } = Toast.useToastManager();
  return (
    <Toast.Portal>
      <Toast.Viewport className={styles.AnchoredViewport}>
        {toasts.map((toast) => (
          <Toast.Positioner key={toast.id} toast={toast} className={styles.AnchoredPositioner}>
            <Toast.Root toast={toast} className={styles.AnchoredToast}>
              <Toast.Arrow className={styles.Arrow}>
                <ArrowSvg />
              </Toast.Arrow>
              <Toast.Content>
                <Toast.Description />
              </Toast.Content>
            </Toast.Root>
          </Toast.Positioner>
        ))}
      </Toast.Viewport>
    </Toast.Portal>
  );
}

function StackedToasts() {
  const { toasts } = Toast.useToastManager();
  return (
    <Toast.Portal>
      <Toast.Viewport className={styles.StackedViewport}>
        {toasts.map((toast) => (
          <Toast.Root key={toast.id} toast={toast} className={styles.StackedToast}>
            <Toast.Content className={styles.Content}>
              <Toast.Title className={styles.Title} />
              <Toast.Description className={styles.Description} />
              <Toast.Close className={styles.Close} aria-label="Close">
                <XIcon className={styles.Icon} />
              </Toast.Close>
            </Toast.Content>
          </Toast.Root>
        ))}
      </Toast.Viewport>
    </Toast.Portal>
  );
}

function ArrowSvg(props: React.ComponentProps<'svg'>) {
  return (
    <svg width="20" height="10" viewBox="0 0 20 10" fill="none" {...props}>
      <path
        d="M9.66437 2.60207L4.80758 6.97318C4.07308 7.63423 3.11989 8 2.13172 8H0V10H20V8H18.5349C17.5468 8 16.5936 7.63423 15.8591 6.97318L11.0023 2.60207C10.622 2.2598 10.0447 2.25979 9.66437 2.60207Z"
        className={styles.ArrowFill}
      />
      <path
        d="M8.99542 1.85876C9.75604 1.17425 10.9106 1.17422 11.6713 1.85878L16.5281 6.22989C17.0789 6.72568 17.7938 7.00001 18.5349 7.00001L15.89 7L11.0023 2.60207C10.622 2.2598 10.0447 2.2598 9.66436 2.60207L4.77734 7L2.13171 7.00001C2.87284 7.00001 3.58774 6.72568 4.13861 6.22989L8.99542 1.85876Z"
        className={styles.ArrowOuterStroke}
      />
      <path
        d="M10.3333 3.34539L5.47654 7.71648C4.55842 8.54279 3.36693 9 2.13172 9H0V8H2.13172C3.11989 8 4.07308 7.63423 4.80758 6.97318L9.66437 2.60207C10.0447 2.25979 10.622 2.2598 11.0023 2.60207L15.8591 6.97318C16.5936 7.63423 17.5468 8 18.5349 8H20V9H18.5349C17.2998 9 16.1083 8.54278 15.1901 7.71648L10.3333 3.34539Z"
        className={styles.ArrowInnerStroke}
      />
    </svg>
  );
}

function ClipboardIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <rect width="8" height="4" x="8" y="2" rx="1" ry="1" />
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
    </svg>
  );
}

function CheckIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

### Custom position

The position of the toasts is controlled by your own CSS.
To change the toasts' position, you can modify the `.Viewport` and `.Root` styles.
A more general component could accept a `data-position` attribute, which the CSS handles for each variation.
The following shows a top-center position:

## Demo

### Tailwind

This example shows how to implement the component using Tailwind CSS.

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';

export default function ExampleToast() {
  return (
    <Toast.Provider>
      <ToastButton />
      <Toast.Portal>
        <Toast.Viewport className="fixed z-10 top-[1rem] right-0 bottom-auto left-0 mx-auto flex w-full max-w-[300px]">
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}

function ToastButton() {
  const toastManager = Toast.useToastManager();
  const [count, setCount] = React.useState(0);

  function createToast() {
    setCount((prev) => prev + 1);
    toastManager.add({
      title: `Toast ${count + 1} created`,
      description: 'This is a toast notification.',
    });
  }

  return (
    <button
      type="button"
      className="box-border flex h-10 items-center justify-center rounded-md border border-gray-200 bg-gray-50 px-3.5 py-0 font-medium text-gray-900 outline-0 select-none hover:bg-gray-100 focus-visible:outline-2 focus-visible:-outline-offset-1 focus-visible:outline-blue active:bg-gray-100"
      onClick={createToast}
    >
      Create toast
    </button>
  );
}

function ToastList() {
  const { toasts } = Toast.useToastManager();
  return toasts.map((toast) => (
    <Toast.Root
      key={toast.id}
      toast={toast}
      swipeDirection="up"
      className="[--gap:0.75rem] [--peek:0.75rem] [--scale:calc(max(0,1-(var(--toast-index)*0.1)))] [--shrink:calc(1-var(--scale))] [--height:var(--toast-frontmost-height,var(--toast-height))] [--offset-y:calc(var(--toast-offset-y)+(var(--toast-index)*var(--gap))+var(--toast-swipe-movement-y))] absolute right-0 top-0 left-0 z-[calc(1000-var(--toast-index))] mx-auto w-[300px] origin-top [transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--toast-swipe-movement-y)+(var(--toast-index)*var(--peek))+(var(--shrink)*var(--height))))_scale(var(--scale))] rounded-lg border border-gray-200 bg-gray-50 bg-clip-padding p-4 shadow-lg select-none after:absolute after:bottom-full after:left-0 after:h-[calc(var(--gap)+1px)] after:w-full after:content-[''] data-[ending-style]:opacity-0 data-[expanded]:[transform:translateX(var(--toast-swipe-movement-x))_translateY(calc(var(--offset-y)))] data-[limited]:opacity-0 data-[starting-style]:[transform:translateY(-150%)] [&[data-ending-style]:not([data-limited]):not([data-swipe-direction])]:[transform:translateY(-150%)] data-[ending-style]:data-[swipe-direction=down]:[transform:translateY(calc(var(--toast-swipe-movement-y)+150%))] data-[expanded]:data-[ending-style]:data-[swipe-direction=down]:[transform:translateY(calc(var(--toast-swipe-movement-y)+150%))] data-[ending-style]:data-[swipe-direction=left]:[transform:translateX(calc(var(--toast-swipe-movement-x)-150%))_translateY(var(--offset-y))] data-[expanded]:data-[ending-style]:data-[swipe-direction=left]:[transform:translateX(calc(var(--toast-swipe-movement-x)-150%))_translateY(var(--offset-y))] data-[ending-style]:data-[swipe-direction=right]:[transform:translateX(calc(var(--toast-swipe-movement-x)+150%))_translateY(var(--offset-y))] data-[expanded]:data-[ending-style]:data-[swipe-direction=right]:[transform:translateX(calc(var(--toast-swipe-movement-x)+150%))_translateY(var(--offset-y))] data-[ending-style]:data-[swipe-direction=up]:[transform:translateY(calc(var(--toast-swipe-movement-y)-150%))] data-[expanded]:data-[ending-style]:data-[swipe-direction=up]:[transform:translateY(calc(var(--toast-swipe-movement-y)-150%))] h-[var(--height)] data-[expanded]:h-[var(--toast-height)] [transition:transform_0.5s_cubic-bezier(0.22,1,0.36,1),opacity_0.5s,height_0.15s]"
    >
      <Toast.Content className="overflow-hidden transition-opacity [transition-duration:250ms] data-[behind]:pointer-events-none data-[behind]:opacity-0 data-[expanded]:pointer-events-auto data-[expanded]:opacity-100">
        <Toast.Title className="text-[0.975rem] leading-5 font-medium" />
        <Toast.Description className="text-[0.925rem] leading-5 text-gray-700" />
        <Toast.Close
          className="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded border-none bg-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-700"
          aria-label="Close"
        >
          <XIcon className="h-4 w-4" />
        </Toast.Close>
      </Toast.Content>
    </Toast.Root>
  ));
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

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

.Viewport {
  position: fixed;
  z-index: 1;
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
  top: 1rem;
  right: 0;
  left: 0;
  bottom: auto;
}

.Toast {
  --gap: 0.75rem;
  --peek: 0.75rem;
  --scale: calc(max(0, 1 - (var(--toast-index) * 0.1)));
  --shrink: calc(1 - var(--scale));
  --height: var(--toast-frontmost-height, var(--toast-height));
  --offset-y: calc(
    var(--toast-offset-y) + (var(--toast-index) * var(--gap)) + var(--toast-swipe-movement-y)
  );
  position: absolute;
  margin: 0 auto;
  box-sizing: border-box;
  background: var(--color-gray-50);
  color: var(--color-gray-900);
  border: 1px solid var(--color-gray-200);
  padding: 1rem;
  width: 100%;
  box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
  background-clip: padding-box;
  border-radius: 0.5rem;
  transform-origin: top center;
  top: 0;
  left: 0;
  right: 0;
  margin-right: auto;
  margin-left: auto;
  -webkit-user-select: none;
  user-select: none;
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.5s,
    height 0.15s;
  cursor: default;
  z-index: calc(1000 - var(--toast-index));
  height: var(--height);
  transform: translateX(var(--toast-swipe-movement-x))
    translateY(
      calc(
        var(--toast-swipe-movement-y) + (var(--toast-index) * var(--peek)) +
          (var(--shrink) * var(--height))
      )
    )
    scale(var(--scale));

  &[data-expanded] {
    transform: translateX(var(--toast-swipe-movement-x)) translateY(var(--offset-y));
    height: var(--toast-height);
  }

  &[data-starting-style],
  &[data-ending-style] {
    transform: translateY(-150%);
  }

  &[data-limited] {
    opacity: 0;
  }

  &[data-ending-style] {
    opacity: 0;

    &[data-swipe-direction='up'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) - 150%));
    }
    &[data-swipe-direction='left'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) - 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='right'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) + 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='down'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) + 150%));
    }
  }

  &::after {
    content: '';
    position: absolute;
    width: 100%;
    bottom: 100%;
    left: 0;
    height: calc(var(--gap) + 1px);
  }
}

.Content {
  overflow: hidden;
  transition: opacity 0.25s;

  &[data-behind] {
    opacity: 0;
  }

  &[data-expanded] {
    opacity: 1;
  }
}

.Title {
  font-weight: 500;
  font-size: 0.975rem;
  line-height: 1.25rem;
  margin: 0;
}

.Description {
  font-size: 0.925rem;
  line-height: 1.25rem;
  margin: 0;
}

.Close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0;
  border: none;
  background: transparent;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;

  &:hover {
    background-color: var(--color-gray-100);
  }
}

.Icon {
  width: 1rem;
  height: 1rem;
}
```

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';
import styles from './index.module.css';

export default function ExampleToast() {
  return (
    <Toast.Provider>
      <ToastButton />
      <Toast.Portal>
        <Toast.Viewport className={styles.Viewport}>
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}

function ToastButton() {
  const toastManager = Toast.useToastManager();
  const [count, setCount] = React.useState(0);

  function createToast() {
    setCount((prev) => prev + 1);
    toastManager.add({
      title: `Toast ${count + 1} created`,
      description: 'This is a toast notification.',
    });
  }

  return (
    <button type="button" className={styles.Button} onClick={createToast}>
      Create toast
    </button>
  );
}

function ToastList() {
  const { toasts } = Toast.useToastManager();
  return toasts.map((toast) => (
    <Toast.Root key={toast.id} toast={toast} swipeDirection="up" className={styles.Toast}>
      <Toast.Content className={styles.Content}>
        <Toast.Title className={styles.Title} />
        <Toast.Description className={styles.Description} />
        <Toast.Close className={styles.Close} aria-label="Close">
          <XIcon className={styles.Icon} />
        </Toast.Close>
      </Toast.Content>
    </Toast.Root>
  ));
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

### Undo action

When adding a toast, the `actionProps` option can be used to define props for an action button inside of it—this enables the ability to undo an action associated with the toast.

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

.Viewport {
  position: fixed;
  z-index: 1;
  width: 275px;
  margin: 0 auto;
  bottom: 1rem;
  right: 1rem;
  left: auto;
  top: auto;

  @media (min-width: 500px) {
    bottom: 2rem;
    right: 2rem;
    width: 300px;
  }
}

.Toast {
  --gap: 0.75rem;
  --peek: 0.75rem;
  --scale: calc(max(0, 1 - (var(--toast-index) * 0.1)));
  --shrink: calc(1 - var(--scale));
  --height: var(--toast-frontmost-height, var(--toast-height));
  --offset-y: calc(
    var(--toast-offset-y) * -1 + (var(--toast-index) * var(--gap) * -1) +
      var(--toast-swipe-movement-y)
  );
  position: absolute;
  right: 0;
  margin: 0 auto;
  box-sizing: border-box;
  background: var(--color-gray-50);
  color: var(--color-gray-900);
  border: 1px solid var(--color-gray-200);
  padding: 1rem;
  width: 100%;
  box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
  background-clip: padding-box;
  border-radius: 0.5rem;
  transform-origin: bottom center;
  bottom: 0;
  left: auto;
  margin-right: 0;
  -webkit-user-select: none;
  user-select: none;
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.5s,
    height 0.15s;
  cursor: default;
  z-index: calc(1000 - var(--toast-index));
  height: var(--height);
  transform: translateX(var(--toast-swipe-movement-x))
    translateY(
      calc(
        var(--toast-swipe-movement-y) - (var(--toast-index) * var(--peek)) -
          (var(--shrink) * var(--height))
      )
    )
    scale(var(--scale));

  &[data-expanded] {
    transform: translateX(var(--toast-swipe-movement-x)) translateY(var(--offset-y));
    height: var(--toast-height);
  }

  &[data-starting-style],
  &[data-ending-style] {
    transform: translateY(150%);
  }

  &[data-limited] {
    opacity: 0;
  }

  &[data-ending-style] {
    opacity: 0;

    &[data-swipe-direction='up'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) - 150%));
    }
    &[data-swipe-direction='left'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) - 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='right'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) + 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='down'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) + 150%));
    }
  }

  &::after {
    content: '';
    position: absolute;
    width: 100%;
    top: 100%;
    left: 0;
    height: calc(var(--gap) + 1px);
  }
}

.Content {
  overflow: hidden;
  transition: opacity 0.25s;

  &[data-behind] {
    opacity: 0;
  }

  &[data-expanded] {
    opacity: 1;
  }
}

.Title {
  font-weight: 500;
  font-size: 0.975rem;
  line-height: 1.25rem;
  margin: 0;
}

.Description {
  font-size: 0.925rem;
  line-height: 1.25rem;
  margin: 0;
}

.UndoButton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  padding: 0 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.25rem;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
  background-color: var(--color-gray-900);
  color: var(--color-gray-50);
  border: none;

  &:focus-visible {
    outline: 2px solid var(--color-blue);
    outline-offset: -1px;
  }
}

.Close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0;
  border: none;
  background: transparent;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;

  &:hover {
    background-color: var(--color-gray-100);
  }
}

.Icon {
  width: 1rem;
  height: 1rem;
}
```

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';
import styles from './index.module.css';

export default function UndoToastExample() {
  return (
    <Toast.Provider>
      <Form />
      <Toast.Portal>
        <Toast.Viewport className={styles.Viewport}>
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}

function Form() {
  const toastManager = Toast.useToastManager();

  function action() {
    const id = toastManager.add({
      title: 'Action performed',
      description: 'You can undo this action.',
      type: 'success',
      actionProps: {
        children: 'Undo',
        onClick() {
          toastManager.close(id);
          toastManager.add({
            title: 'Action undone',
          });
        },
      },
    });
  }

  return (
    <button type="button" onClick={action} className={styles.Button}>
      Perform action
    </button>
  );
}

function ToastList() {
  const { toasts } = Toast.useToastManager();
  return toasts.map((toast) => (
    <Toast.Root key={toast.id} toast={toast} className={styles.Toast}>
      <Toast.Content className={styles.Content}>
        <Toast.Title className={styles.Title} />
        <Toast.Description className={styles.Description} />
        <Toast.Action className={styles.UndoButton} />
        <Toast.Close className={styles.Close} aria-label="Close">
          <XIcon className={styles.Icon} />
        </Toast.Close>
      </Toast.Content>
    </Toast.Root>
  ));
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

### Promise

An asynchronous toast can be created with three possible states: `loading`, `success`, and `error`.
The `type` string matches these states to change the styling.
Each of the states also accepts the [method options](/react/components/toast.md) object for more granular control.

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

.Viewport {
  position: fixed;
  z-index: 1;
  width: 250px;
  margin: 0 auto;
  bottom: 1rem;
  right: 1rem;
  left: auto;
  top: auto;

  @media (min-width: 500px) {
    bottom: 2rem;
    right: 2rem;
    width: 300px;
  }
}

.Toast {
  --gap: 0.75rem;
  --peek: 0.75rem;
  --scale: calc(max(0, 1 - (var(--toast-index) * 0.1)));
  --shrink: calc(1 - var(--scale));
  --height: var(--toast-frontmost-height, var(--toast-height));
  --offset-y: calc(
    var(--toast-offset-y) * -1 + (var(--toast-index) * var(--gap) * -1) +
      var(--toast-swipe-movement-y)
  );
  position: absolute;
  right: 0;
  margin: 0 auto;
  box-sizing: border-box;
  background: var(--color-gray-50);
  color: var(--color-gray-900);
  border: 1px solid var(--color-gray-200);
  padding: 1rem;
  width: 100%;
  box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
  background-clip: padding-box;
  border-radius: 0.5rem;
  transform-origin: bottom center;
  bottom: 0;
  left: auto;
  margin-right: 0;
  -webkit-user-select: none;
  user-select: none;
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.5s,
    height 0.15s;
  cursor: default;
  z-index: calc(1000 - var(--toast-index));
  height: var(--height);
  transform: translateX(var(--toast-swipe-movement-x))
    translateY(
      calc(
        var(--toast-swipe-movement-y) - (var(--toast-index) * var(--peek)) -
          (var(--shrink) * var(--height))
      )
    )
    scale(var(--scale));

  &[data-expanded] {
    transform: translateX(var(--toast-swipe-movement-x)) translateY(var(--offset-y));
    height: var(--toast-height);
  }

  &[data-starting-style],
  &[data-ending-style] {
    transform: translateY(150%);
  }

  &[data-limited] {
    opacity: 0;
  }

  &[data-ending-style] {
    opacity: 0;

    &[data-swipe-direction='up'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) - 150%));
    }
    &[data-swipe-direction='left'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) - 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='right'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) + 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='down'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) + 150%));
    }
  }

  &::after {
    content: '';
    position: absolute;
    width: 100%;
    top: 100%;
    left: 0;
    height: calc(var(--gap) + 1px);
  }

  &[data-type='success'] {
    background-color: lightgreen;
    color: black;
  }

  &[data-type='error'] {
    background-color: lightpink;
    color: black;
  }
}

.Content {
  overflow: hidden;
  transition: opacity 0.25s;

  &[data-behind] {
    opacity: 0;
  }

  &[data-expanded] {
    opacity: 1;
  }
}

.Title {
  font-weight: 500;
  font-size: 0.975rem;
  line-height: 1.25rem;
  margin: 0;
}

.Description {
  font-size: 0.925rem;
  line-height: 1.25rem;
  margin: 0;
}

.Close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0;
  border: none;
  background: transparent;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;

  &:hover {
    background-color: var(--color-gray-100);
  }
}

.Icon {
  width: 1rem;
  height: 1rem;
}
```

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';
import styles from './index.module.css';

export default function PromiseToastExample() {
  return (
    <Toast.Provider>
      <PromiseDemo />
      <Toast.Portal>
        <Toast.Viewport className={styles.Viewport}>
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}

function PromiseDemo() {
  const toastManager = Toast.useToastManager();

  function runPromise() {
    toastManager.promise(
      // Simulate an API request with a promise that resolves after 2 seconds
      new Promise<string>((resolve, reject) => {
        const shouldSucceed = Math.random() > 0.3; // 70% success rate
        setTimeout(() => {
          if (shouldSucceed) {
            resolve('operation completed');
          } else {
            reject(new Error('operation failed'));
          }
        }, 2000);
      }),
      {
        loading: 'Loading data…',
        success: (data: string) => `Success: ${data}`,
        error: (err: Error) => `Error: ${err.message}`,
      },
    );
  }

  return (
    <button type="button" onClick={runPromise} className={styles.Button}>
      Run promise
    </button>
  );
}

function ToastList() {
  const { toasts } = Toast.useToastManager();
  return toasts.map((toast) => (
    <Toast.Root key={toast.id} toast={toast} className={styles.Toast}>
      <Toast.Content className={styles.Content}>
        <Toast.Title className={styles.Title} />
        <Toast.Description className={styles.Description} />
        <Toast.Close className={styles.Close} aria-label="Close">
          <XIcon className={styles.Icon} />
        </Toast.Close>
      </Toast.Content>
    </Toast.Root>
  ));
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

### Custom

A toast with custom data can be created by passing any typed object interface to the `data` option.
This enables you to pass any data (including functions) you need to the toast and access it in the toast's rendering logic.

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

.Viewport {
  position: fixed;
  z-index: 1;
  width: 250px;
  margin: 0 auto;
  bottom: 1rem;
  right: 1rem;
  left: auto;
  top: auto;

  @media (min-width: 500px) {
    bottom: 2rem;
    right: 2rem;
    width: 300px;
  }
}

.Toast {
  --gap: 0.75rem;
  --peek: 0.75rem;
  --scale: calc(max(0, 1 - (var(--toast-index) * 0.1)));
  --shrink: calc(1 - var(--scale));
  --height: var(--toast-frontmost-height, var(--toast-height));
  --offset-y: calc(
    var(--toast-offset-y) * -1 + (var(--toast-index) * var(--gap) * -1) +
      var(--toast-swipe-movement-y)
  );
  position: absolute;
  right: 0;
  margin: 0 auto;
  box-sizing: border-box;
  background: var(--color-gray-50);
  color: var(--color-gray-900);
  border: 1px solid var(--color-gray-200);
  padding: 1rem;
  width: 100%;
  box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
  background-clip: padding-box;
  border-radius: 0.5rem;
  transform-origin: bottom center;
  bottom: 0;
  left: auto;
  margin-right: 0;
  -webkit-user-select: none;
  user-select: none;
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.5s,
    height 0.15s;
  cursor: default;
  z-index: calc(1000 - var(--toast-index));
  height: var(--height);
  transform: translateX(var(--toast-swipe-movement-x))
    translateY(
      calc(
        var(--toast-swipe-movement-y) - (var(--toast-index) * var(--peek)) -
          (var(--shrink) * var(--height))
      )
    )
    scale(var(--scale));

  &[data-expanded] {
    transform: translateX(var(--toast-swipe-movement-x)) translateY(var(--offset-y));
    height: var(--toast-height);
  }

  &[data-starting-style],
  &[data-ending-style] {
    transform: translateY(150%);
  }

  &[data-limited] {
    opacity: 0;
  }

  &[data-ending-style] {
    opacity: 0;

    &[data-swipe-direction='up'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) - 150%));
    }
    &[data-swipe-direction='left'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) - 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='right'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) + 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='down'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) + 150%));
    }
  }

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    width: 100%;
    left: 0;
    height: calc(var(--gap) + 1px);
  }
}

.Content {
  overflow: hidden;
  transition: opacity 0.25s cubic-bezier(0.22, 1, 0.36, 1);

  &[data-behind] {
    opacity: 0;
  }

  &[data-expanded] {
    opacity: 1;
  }
}

.Title {
  font-weight: 500;
  font-size: 0.975rem;
  line-height: 1.25rem;
  margin: 0;
}

.Description {
  font-size: 0.925rem;
  line-height: 1.25rem;
  margin: 0;
}

.Close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0;
  border: none;
  background: transparent;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;

  &:hover {
    background-color: var(--color-gray-100);
  }
}

.Icon {
  width: 1rem;
  height: 1rem;
}
```

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';
import styles from './index.module.css';

interface CustomToastData {
  userId: string;
}

function isCustomToast(
  toast: Toast.Root.ToastObject,
): toast is Toast.Root.ToastObject<CustomToastData> {
  return toast.data?.userId !== undefined;
}

export default function CustomToastExample() {
  return (
    <Toast.Provider>
      <CustomToast />
      <Toast.Portal>
        <Toast.Viewport className={styles.Viewport}>
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}

function CustomToast() {
  const toastManager = Toast.useToastManager();

  function action() {
    const data: CustomToastData = {
      userId: '123',
    };

    toastManager.add({
      title: 'Toast with custom data',
      data,
    });
  }

  return (
    <button type="button" onClick={action} className={styles.Button}>
      Create custom toast
    </button>
  );
}

function ToastList() {
  const { toasts } = Toast.useToastManager();
  return toasts.map((toast) => (
    <Toast.Root key={toast.id} toast={toast} className={styles.Toast}>
      <Toast.Content className={styles.Content}>
        <Toast.Title className={styles.Title}>{toast.title}</Toast.Title>
        {isCustomToast(toast) && toast.data ? (
          <Toast.Description className={styles.Description}>
            `data.userId` is {toast.data.userId}
          </Toast.Description>
        ) : (
          <Toast.Description className={styles.Description} />
        )}
        <Toast.Close className={styles.Close} aria-label="Close">
          <XIcon className={styles.Icon} />
        </Toast.Close>
      </Toast.Content>
    </Toast.Root>
  ));
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
```

### Varying heights

Toasts with varying heights are stacked by ensuring that the `<Toast.Content>` element has `overflow: hidden` set, along with all toasts' heights matching the frontmost toast at index 0.
This prevents taller toasts from overflowing the stack when collapsed.

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

.Viewport {
  position: fixed;
  z-index: 1;
  width: 250px;
  margin: 0 auto;
  bottom: 1rem;
  right: 1rem;
  left: auto;
  top: auto;

  @media (min-width: 500px) {
    bottom: 2rem;
    right: 2rem;
    width: 300px;
  }
}

.Toast {
  --gap: 0.75rem;
  --peek: 0.75rem;
  --scale: calc(max(0, 1 - (var(--toast-index) * 0.1)));
  --shrink: calc(1 - var(--scale));
  --height: var(--toast-frontmost-height, var(--toast-height));
  --offset-y: calc(
    var(--toast-offset-y) * -1 + (var(--toast-index) * var(--gap) * -1) +
      var(--toast-swipe-movement-y)
  );
  position: absolute;
  right: 0;
  margin: 0 auto;
  box-sizing: border-box;
  background: var(--color-gray-50);
  color: var(--color-gray-900);
  border: 1px solid var(--color-gray-200);
  padding: 1rem;
  width: 100%;
  box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
  background-clip: padding-box;
  border-radius: 0.5rem;
  bottom: 0;
  left: auto;
  margin-right: 0;
  -webkit-user-select: none;
  user-select: none;
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.5s,
    height 0.15s;
  cursor: default;
  z-index: calc(1000 - var(--toast-index));
  height: var(--height);
  transform-origin: bottom center;
  transform: translateX(var(--toast-swipe-movement-x))
    translateY(
      calc(
        var(--toast-swipe-movement-y) - (var(--toast-index) * var(--peek)) -
          (var(--shrink) * var(--height))
      )
    )
    scale(var(--scale));

  &[data-expanded] {
    transform: translateX(var(--toast-swipe-movement-x)) translateY(var(--offset-y));
    height: var(--toast-height);
  }

  &[data-starting-style],
  &[data-ending-style] {
    transform: translateY(150%);
  }

  &[data-limited] {
    opacity: 0;
  }

  &[data-ending-style] {
    opacity: 0;

    &[data-swipe-direction='up'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) - 150%));
    }
    &[data-swipe-direction='left'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) - 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='right'] {
      transform: translateX(calc(var(--toast-swipe-movement-x) + 150%)) translateY(var(--offset-y));
    }
    &[data-swipe-direction='down'] {
      transform: translateY(calc(var(--toast-swipe-movement-y) + 150%));
    }
  }

  &::after {
    content: '';
    position: absolute;
    width: 100%;
    top: 100%;
    left: 0;
    height: calc(var(--gap) + 1px);
  }
}

.Content {
  overflow: hidden;
  transition: opacity 0.25s;

  &[data-behind] {
    opacity: 0;
  }

  &[data-expanded] {
    opacity: 1;
  }
}

.Title {
  font-weight: 500;
  font-size: 0.975rem;
  line-height: 1.25rem;
  margin: 0;
}

.Description {
  font-size: 0.925rem;
  line-height: 1.25rem;
  margin: 0;
}

.Close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0;
  border: none;
  background: transparent;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;

  &:hover {
    background-color: var(--color-gray-100);
  }
}

.Icon {
  width: 1rem;
  height: 1rem;
}
```

```tsx
/* index.tsx */
'use client';
import * as React from 'react';
import { Toast } from '@base-ui/react/toast';
import styles from './index.module.css';

export default function VaryingHeightsToast() {
  return (
    <Toast.Provider>
      <ToastButton />
      <Toast.Portal>
        <Toast.Viewport className={styles.Viewport}>
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}

function ToastButton() {
  const toastManager = Toast.useToastManager();
  const [count, setCount] = React.useState(0);

  function createToast() {
    setCount((prev) => prev + 1);
    const description = TEXTS[Math.floor(Math.random() * TEXTS.length)];
    toastManager.add({
      title: `Toast ${count + 1} created`,
      description,
    });
  }

  return (
    <button type="button" className={styles.Button} onClick={createToast}>
      Create varying height toast
    </button>
  );
}

function ToastList() {
  const { toasts } = Toast.useToastManager();
  return toasts.map((toast) => (
    <Toast.Root key={toast.id} toast={toast} className={styles.Toast}>
      <Toast.Content className={styles.Content}>
        <Toast.Title className={styles.Title} />
        <Toast.Description className={styles.Description} />
        <Toast.Close className={styles.Close} aria-label="Close">
          <XIcon className={styles.Icon} />
        </Toast.Close>
      </Toast.Content>
    </Toast.Root>
  ));
}

function XIcon(props: React.ComponentProps<'svg'>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}

const TEXTS = [
  'Short message.',
  'A bit longer message that spans two lines.',
  'This is a longer description that intentionally takes more vertical space to demonstrate stacking with varying heights.',
  'An even longer description that should span multiple lines so we can verify the clamped collapsed height and smooth expansion animation when hovering or focusing the viewport.',
];
```

## API reference

### Provider

Provides a context for creating and managing toasts.

**Provider Props:**

| Prop         | Type           | Default | Description                                                                                                                                               |
| :----------- | :------------- | :------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| limit        | `number`       | `3`     | The maximum number of toasts that can be displayed at once.&#xA;When the limit is reached, the oldest toast will be removed to make room for the new one. |
| toastManager | `ToastManager` | -       | A global manager for toasts to use outside of a React component.                                                                                          |
| timeout      | `number`       | `5000`  | The default amount of time (in ms) before a toast is auto dismissed.&#xA;A value of `0` will prevent the toast from being dismissed automatically.        |
| children     | `ReactNode`    | -       | -                                                                                                                                                         |

### Viewport

A container viewport for toasts.
Renders a `<div>` element.

**Viewport Props:**

| Prop      | Type                                                                                | Default | Description                                                                                                                                                                                  |
| :-------- | :---------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| className | `string \| ((state: Toast.Viewport.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style     | `CSSProperties \| ((state: Toast.Viewport.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render    | `ReactElement \| ((props: HTMLProps, state: Toast.Viewport.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Viewport Data Attributes:**

| Attribute     | Type      | Description                                    |
| :------------ | :-------- | :--------------------------------------------- |
| data-expanded | `boolean` | Indicates toasts are expanded in the viewport. |

**Viewport CSS Variables:**

| Variable                 | Type     | Default | Description                                  |
| :----------------------- | :------- | :------ | :------------------------------------------- |
| --toast-frontmost-height | `number` | -       | Indicates the height of the frontmost toast. |

### Portal

A portal element that moves the viewport to a different part of the DOM.
By default, the portal element is appended to `<body>`.
Renders a `<div>` element.

**Portal Props:**

| Prop      | Type                                                                                | Default | Description                                                                                                                                                                                  |
| :-------- | :---------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| container | `HTMLElement \| ShadowRoot \| RefObject<HTMLElement \| ShadowRoot \| null> \| null` | -       | A parent element to render the portal element into.                                                                                                                                          |
| className | `string \| ((state: any) => string \| undefined)`                                   | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style     | `CSSProperties \| ((state: any) => CSSProperties \| undefined)`                     | -       | -                                                                                                                                                                                            |
| render    | `ReactElement \| ((props: HTMLProps, state: any) => ReactElement)`                  | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

### Root

Groups all parts of an individual toast.
Renders a `<div>` element.

**Root Props:**

| Prop           | Type                                                                             | Default             | Description                                                                                                                                                                                  |
| :------------- | :------------------------------------------------------------------------------- | :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| swipeDirection | `'left' \| 'right' \| 'up' \| 'down' \| ('left' \| 'right' \| 'up' \| 'down')[]` | `['down', 'right']` | Direction(s) in which the toast can be swiped to dismiss.                                                                                                                                    |
| toast          | `Toast.Root.ToastObject<any>`                                                    | -                   | The toast to render.                                                                                                                                                                         |
| className      | `string \| ((state: Toast.Root.State) => string \| undefined)`                   | -                   | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style          | `CSSProperties \| ((state: Toast.Root.State) => CSSProperties \| undefined)`     | -                   | -                                                                                                                                                                                            |
| render         | `ReactElement \| ((props: HTMLProps, state: Toast.Root.State) => ReactElement)`  | -                   | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Root Data Attributes:**

| Attribute            | Type                                  | Description                                                    |
| :------------------- | :------------------------------------ | :------------------------------------------------------------- |
| data-expanded        | `boolean`                             | Present when the toast is expanded in the viewport.            |
| data-limited         | `boolean`                             | Present when the toast was removed due to exceeding the limit. |
| data-swipe-direction | `'up' \| 'down' \| 'left' \| 'right'` | The direction the toast was swiped.                            |
| data-swiping         | `boolean`                             | Present when the toast is being swiped.                        |
| data-type            | `string`                              | The type of the toast.                                         |
| data-starting-style  | -                                     | Present when the toast is animating in.                        |
| data-ending-style    | -                                     | Present when the toast is animating out.                       |

**Root CSS Variables:**

| Variable                 | Type     | Default | Description                                                                  |
| :----------------------- | :------- | :------ | :--------------------------------------------------------------------------- |
| --toast-height           | `number` | -       | Indicates the measured natural height of the toast in pixels.                |
| --toast-index            | `number` | -       | Indicates the index of the toast in the list.                                |
| --toast-offset-y         | `number` | -       | Indicates the vertical pixels offset of the toast in the list when expanded. |
| --toast-swipe-movement-x | `number` | -       | Indicates the horizontal swipe movement of the toast.                        |
| --toast-swipe-movement-y | `number` | -       | Indicates the vertical swipe movement of the toast.                          |

### Content

A container for the contents of a toast.
Renders a `<div>` element.

**Content Props:**

| Prop      | Type                                                                               | Default | Description                                                                                                                                                                                  |
| :-------- | :--------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| className | `string \| ((state: Toast.Content.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style     | `CSSProperties \| ((state: Toast.Content.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render    | `ReactElement \| ((props: HTMLProps, state: Toast.Content.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Content Data Attributes:**

| Attribute     | Type      | Description                                                        |
| :------------ | :-------- | :----------------------------------------------------------------- |
| data-behind   | `boolean` | Present when the toast is behind the frontmost toast in the stack. |
| data-expanded | `boolean` | Present when the toast viewport is expanded.                       |

### Title

A title that labels the toast.
Renders an `<h2>` element.

**Title Props:**

| Prop      | Type                                                                             | Default | Description                                                                                                                                                                                  |
| :-------- | :------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| className | `string \| ((state: Toast.Title.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style     | `CSSProperties \| ((state: Toast.Title.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render    | `ReactElement \| ((props: HTMLProps, state: Toast.Title.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Title Data Attributes:**

| Attribute | Type     | Description            |
| :-------- | :------- | :--------------------- |
| data-type | `string` | The type of the toast. |

### Description

A description that describes the toast.
Can be used as the default message for the toast when no title is provided.
Renders a `<p>` element.

**Description Props:**

| Prop      | Type                                                                                   | Default | Description                                                                                                                                                                                  |
| :-------- | :------------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| className | `string \| ((state: Toast.Description.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style     | `CSSProperties \| ((state: Toast.Description.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render    | `ReactElement \| ((props: HTMLProps, state: Toast.Description.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Description Data Attributes:**

| Attribute | Type     | Description            |
| :-------- | :------- | :--------------------- |
| data-type | `string` | The type of the toast. |

### Action

Performs an action when clicked.
Renders a `<button>` element.

**Action Props:**

| Prop         | Type                                                                              | Default | Description                                                                                                                                                                                  |
| :----------- | :-------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| nativeButton | `boolean`                                                                         | `true`  | Whether the component renders a native `<button>` element when replacing it&#xA;via the `render` prop.&#xA;Set to `false` if the rendered element is not a button (e.g. `<div>`).            |
| className    | `string \| ((state: Toast.Action.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style        | `CSSProperties \| ((state: Toast.Action.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render       | `ReactElement \| ((props: HTMLProps, state: Toast.Action.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Action Data Attributes:**

| Attribute | Type     | Description            |
| :-------- | :------- | :--------------------- |
| data-type | `string` | The type of the toast. |

### Close

Closes the toast when clicked.
Renders a `<button>` element.

**Close Props:**

| Prop         | Type                                                                             | Default | Description                                                                                                                                                                                  |
| :----------- | :------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| nativeButton | `boolean`                                                                        | `true`  | Whether the component renders a native `<button>` element when replacing it&#xA;via the `render` prop.&#xA;Set to `false` if the rendered element is not a button (e.g. `<div>`).            |
| className    | `string \| ((state: Toast.Close.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style        | `CSSProperties \| ((state: Toast.Close.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render       | `ReactElement \| ((props: HTMLProps, state: Toast.Close.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Close Data Attributes:**

| Attribute | Type     | Description            |
| :-------- | :------- | :--------------------- |
| data-type | `string` | The type of the toast. |

### Positioner

Positions the toast against the anchor.
Renders a `<div>` element.

**Positioner Props:**

| Prop                  | Type                       | Default    | Description                                                                                                                                                                                                                                                                                                                                                                           |
| :-------------------- | :------------------------- | :--------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| disableAnchorTracking | `boolean`                  | `false`    | Whether to disable the popup from tracking any layout shift of its positioning anchor.                                                                                                                                                                                                                                                                                                |
| toast                 | `ToastObject<any>`         | -          | The toast object associated with the positioner.                                                                                                                                                                                                                                                                                                                                      |
| align                 | `Align`                    | `'center'` | How to align the popup relative to the specified side.                                                                                                                                                                                                                                                                                                                                |
| alignOffset           | `number \| OffsetFunction` | `0`        | Additional offset along the alignment axis in pixels.&#xA;Also accepts a function that returns the offset to read the dimensions of the anchor&#xA;and positioner elements, along with its side and alignment.The function takes a `data` object parameter with the following properties:\* `data.anchor`: the dimensions of the anchor element with properties `width` and `height`. |

- `data.positioner`: the dimensions of the positioner element with properties `width` and `height`.
- `data.side`: which side of the anchor element the positioner is aligned against.
- `data.align`: how the positioner is aligned relative to the specified side. |
  | side | `Side` | `'top'` | Which side of the anchor element to align the toast against.&#xA;May automatically change to avoid collisions. |
  | sideOffset | `number \| OffsetFunction` | `0` | Distance between the anchor and the popup in pixels.&#xA;Also accepts a function that returns the distance to read the dimensions of the anchor&#xA;and positioner elements, along with its side and alignment.The function takes a `data` object parameter with the following properties:\* `data.anchor`: the dimensions of the anchor element with properties `width` and `height`.
- `data.positioner`: the dimensions of the positioner element with properties `width` and `height`.
- `data.side`: which side of the anchor element the positioner is aligned against.
- `data.align`: how the positioner is aligned relative to the specified side. |
  | arrowPadding | `number` | `5` | Minimum distance to maintain between the arrow and the edges of the popup.Use it to prevent the arrow element from hanging out of the rounded corners of a popup. |
  | anchor | `Element \| null` | - | An element to position the toast against. |
  | collisionAvoidance | `CollisionAvoidance` | - | Determines how to handle collisions when positioning the popup. |
  | collisionBoundary | `Boundary` | `'clipping-ancestors'` | An element or a rectangle that delimits the area that the popup is confined to. |
  | collisionPadding | `Padding` | `5` | Additional space to maintain from the edge of the collision boundary. |
  | sticky | `boolean` | `false` | Whether to maintain the popup in the viewport after&#xA;the anchor element was scrolled out of view. |
  | positionMethod | `'fixed' \| 'absolute'` | `'absolute'` | Determines which CSS `position` property to use. |
  | className | `string \| ((state: Toast.Positioner.State) => string \| undefined)` | - | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state. |
  | style | `CSSProperties \| ((state: Toast.Positioner.State) => CSSProperties \| undefined)` | - | - |
  | render | `ReactElement \| ((props: HTMLProps, state: Toast.Positioner.State) => ReactElement)` | - | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Positioner Data Attributes:**

| Attribute          | Type                                                                       | Description                                                           |
| :----------------- | :------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| data-anchor-hidden | -                                                                          | Present when the anchor is hidden.                                    |
| data-align         | `'start' \| 'center' \| 'end'`                                             | Indicates how the toast is aligned relative to specified side.        |
| data-side          | `'top' \| 'bottom' \| 'left' \| 'right' \| 'inline-end' \| 'inline-start'` | Indicates which side the toast is positioned relative to the trigger. |

**Positioner CSS Variables:**

| Variable           | Type     | Default | Description                                                                            |
| :----------------- | :------- | :------ | :------------------------------------------------------------------------------------- |
| --anchor-height    | `number` | -       | The anchor's height.                                                                   |
| --anchor-width     | `number` | -       | The anchor's width.                                                                    |
| --available-height | `number` | -       | The available height between the anchor and the edge of the viewport.                  |
| --available-width  | `number` | -       | The available width between the anchor and the edge of the viewport.                   |
| --transform-origin | `string` | -       | The coordinates that this element is anchored to. Used for animations and transitions. |

### Arrow

Displays an element positioned against the toast anchor.
Renders a `<div>` element.

**Arrow Props:**

| Prop      | Type                                                                             | Default | Description                                                                                                                                                                                  |
| :-------- | :------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| className | `string \| ((state: Toast.Arrow.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style     | `CSSProperties \| ((state: Toast.Arrow.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render    | `ReactElement \| ((props: HTMLProps, state: Toast.Arrow.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Arrow Data Attributes:**

| Attribute       | Type                                                                       | Description                                                          |
| :-------------- | :------------------------------------------------------------------------- | :------------------------------------------------------------------- |
| data-uncentered | -                                                                          | Present when the toast arrow is uncentered.                          |
| data-align      | `'start' \| 'center' \| 'end'`                                             | Indicates how the toast is aligned relative to specified side.       |
| data-side       | `'top' \| 'bottom' \| 'left' \| 'right' \| 'inline-end' \| 'inline-start'` | Indicates which side the toast is positioned relative to the anchor. |

## useToastManager

Manages toasts, called inside of a `<Toast.Provider>`.

```tsx title="Usage"
const toastManager = Toast.useToastManager();
```

### Return value

**Return Value:**

| Property | Type                                                                                      | Description                                                                                                             |
| :------- | :---------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| toasts   | `Toast.Root.ToastObject[]`                                                                | The array of toast objects.                                                                                             |
| add      | `(options: ToastManagerAddOptions) => string`                                             | Add a toast to the toast list.                                                                                          |
| close    | `(toastId: string) => void`                                                               | Closes and removes a toast from the toast list.                                                                         |
| update   | `(toastId: string, options: ToastManagerUpdateOptions) => void`                           | Update a toast in the toast list.                                                                                       |
| promise  | `<Value>(promise: Promise<Value>, options: ToastManagerPromiseOptions) => Promise<Value>` | Create a toast that resolves with a value, with three possible states for the toast: `loading`, `success`, and `error`. |

### Method options

**Props:**

| Prop        | Type              | Default | Description                                                                                |
| :---------- | :---------------- | :------ | :----------------------------------------------------------------------------------------- |
| title       | `React.ReactNode` | -       | The title of the toast.                                                                    |
| description | `React.ReactNode` | -       | The description of the toast.                                                              |
| type        | `string`          | -       | The type of the toast. Used to conditionally style the toast or render different elements. |
| timeout     | `number`          | -       | The amount of time (in ms) before the toast is auto dismissed.                             |
| priority    | `'low' \| 'high'` | `'low'` | ```                                                                                        |

The priority of the toast.

- \`low\` - The toast will be announced politely.
- \`high\` - The toast will be announced urgently.

````|
| onClose     | `() => void`                            | -       | A callback invoked when the toast is closed.                                                                                                  |
| onRemove    | `() => void`                            | -       | A callback invoked when the toast is removed from the list after animations complete when closed.                                             |
| actionProps | `React.ComponentPropsWithRef<'button'>` | -       | The props of the action button.                                                                                                               |
| data        | `Record<string, unknown>`               | -       | The data of the toast.                                                                                                                        |

### `add` method

Creates a toast by adding it to the toast list.

Returns a `toastId` that can be used to update or close the toast later.

```jsx title="Usage"
const toastId = toastManager.add({
  description: 'Hello, world!',
});
````

```jsx title="Example" {2,7-9}
function App() {
  const toastManager = Toast.useToastManager();
  return (
    <button
      type="button"
      onClick={() => {
        toastManager.add({
          description: 'Hello, world!',
        });
      }}
    >
      Add toast
    </button>
  );
}
```

For high priority toasts, the `title` and `description` strings are what are used to announce the toast to screen readers.
Screen readers do not announce any extra content rendered inside `<Toast.Root>`, including the `<Toast.Title>` or `<Toast.Description>` components, unless they intentionally navigate to the toast viewport.

### `update` method

Updates the toast with new options.

```jsx title="Usage"
toastManager.update(toastId, {
  description: 'New description',
});
```

### `close` method

Closes the toast, removing it from the toast list after any animations complete.

```jsx title="Usage"
toastManager.close(toastId);
```

### `promise` method

Creates an asynchronous toast with three possible states: `loading`, `success`, and `error`.

```tsx title="Description configuration"
const promise = toastManager.promise(
  new Promise((resolve) => {
    setTimeout(() => resolve('world!'), 1000);
  }),
  {
    // Each are a shortcut for the `description` option
    loading: 'Loading…',
    success: (data) => `Hello ${data}`,
    error: (err) => `Error: ${err}`,
  },
);
```

Each state also accepts the [method options](/react/components/toast.md) object to granularly control the toast for each state:

```tsx title="Method options configuration"
const promise = toastManager.promise(
  new Promise((resolve) => {
    setTimeout(() => resolve('world!'), 1000);
  }),
  {
    loading: {
      title: 'Loading…',
      description: 'The promise is loading.',
    },
    success: {
      title: 'Success',
      description: 'The promise resolved successfully.',
    },
    error: {
      title: 'Error',
      description: 'The promise rejected.',
      actionProps: {
        children: 'Contact support',
        onClick() {
          // Redirect to support page
        },
      },
    },
  },
);
```
