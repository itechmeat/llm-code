---
title: Switch
subtitle: A control that indicates whether a setting is on or off.
description: A high-quality, unstyled React switch component that indicates whether a setting is on or off.
---

# Switch

A high-quality, unstyled React switch component that indicates whether a setting is on or off.

## Demo

### Tailwind

This example shows how to implement the component using Tailwind CSS.

```tsx
/* index.tsx */
import { Switch } from "@base-ui/react/switch";

export default function ExampleSwitch() {
  return (
    <label className="flex items-center gap-2 text-base text-gray-900">
      <Switch.Root defaultChecked className="relative flex h-6 w-10 rounded-full bg-gradient-to-r from-gray-700 from-35% to-gray-200 to-65% bg-[length:6.5rem_100%] bg-[100%_0%] bg-no-repeat p-px shadow-[inset_0_1.5px_2px] shadow-gray-200 outline outline-1 -outline-offset-1 outline-gray-200 transition-[background-position,box-shadow] duration-[125ms] ease-[cubic-bezier(0.26,0.75,0.38,0.45)] before:absolute before:rounded-full before:outline-offset-2 before:outline-blue-800 focus-visible:before:inset-0 focus-visible:before:outline focus-visible:before:outline-2 active:bg-gray-100 data-[checked]:bg-[0%_0%] data-[checked]:active:bg-gray-500 dark:from-gray-500 dark:shadow-black/75 dark:outline-white/15 dark:data-[checked]:shadow-none">
        <Switch.Thumb className="aspect-square h-full rounded-full bg-white shadow-[0_0_1px_1px,0_1px_1px,1px_2px_4px_-1px] shadow-gray-100 transition-transform duration-150 data-[checked]:translate-x-4 dark:shadow-black/25" />
      </Switch.Root>
      Notifications
    </label>
  );
}
```

### CSS Modules

This example shows how to implement the component using CSS Modules.

```css
/* index.module.css */
.Label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  line-height: 1.5rem;
  color: var(--color-gray-900);
}

.Switch {
  position: relative;
  display: flex;
  appearance: none;
  border: 0;
  margin: 0;
  padding: 1px;
  width: 2.5rem;
  height: 1.5rem;
  border-radius: 1.5rem;
  outline: 1px solid;
  outline-offset: -1px;
  background-color: transparent;
  background-image: linear-gradient(to right, var(--color-gray-700) 35%, var(--color-gray-200) 65%);
  background-size: 6.5rem 100%;
  background-position-x: 100%;
  background-repeat: no-repeat;
  transition-property: background-position, box-shadow;
  transition-timing-function: cubic-bezier(0.26, 0.75, 0.38, 0.45);
  transition-duration: 125ms;

  &:active {
    background-color: var(--color-gray-100);
  }

  &[data-checked] {
    background-position-x: 0%;
  }

  &[data-checked]:active {
    background-color: var(--color-gray-500);
  }

  @media (prefers-color-scheme: light) {
    box-shadow: var(--color-gray-200) 0 1.5px 2px inset;
    outline-color: var(--color-gray-200);
  }

  @media (prefers-color-scheme: dark) {
    box-shadow: rgb(0 0 0 / 75%) 0 1.5px 2px inset;
    outline-color: rgb(255 255 255 / 15%);
    background-image: linear-gradient(to right, var(--color-gray-500) 35%, var(--color-gray-200) 65%);

    &[data-checked] {
      box-shadow: none;
    }
  }

  &:focus-visible {
    &::before {
      content: "";
      inset: 0;
      position: absolute;
      border-radius: inherit;
      outline: 2px solid var(--color-blue);
      outline-offset: 2px;
    }
  }
}

.Thumb {
  aspect-ratio: 1 / 1;
  height: 100%;
  border-radius: 100%;
  background-color: white;
  transition: translate 150ms ease;

  &[data-checked] {
    translate: 1rem 0;
  }

  @media (prefers-color-scheme: light) {
    box-shadow: 0 0 1px 1px var(--color-gray-100), 0 1px 1px var(--color-gray-100), 1px 2px 4px -1px var(--color-gray-100);
  }

  @media (prefers-color-scheme: dark) {
    box-shadow: 0 0 1px 1px rgb(0 0 0 / 25%), 0 1px 1px rgb(0 0 0 / 25%), 1px 2px 4px -1px rgb(0 0 0 / 25%);
  }
}
```

```tsx
/* index.tsx */
import { Switch } from "@base-ui/react/switch";
import styles from "./index.module.css";

export default function ExampleSwitch() {
  return (
    <label className={styles.Label}>
      <Switch.Root defaultChecked className={styles.Switch}>
        <Switch.Thumb className={styles.Thumb} />
      </Switch.Root>
      Notifications
    </label>
  );
}
```

## Usage guidelines

- **Form controls must have an accessible name**: It can be created using a `<label>` element or the `Field` component. See [Labeling a switch](/react/components/switch.md) and the [forms guide](/react/handbook/forms.md).

## Anatomy

Import the component and assemble its parts:

```jsx title="Anatomy"
import { Switch } from "@base-ui/react/switch";

<Switch.Root>
  <Switch.Thumb />
</Switch.Root>;
```

## Examples

### Labeling a switch

Label a switch using an enclosing `<label>` element that wraps `<Switch.Root>`. An enclosing label is announced to screen readers when focus is on the control, and ensures that clicking on any gaps between the label and switch still toggles the control.

```tsx title="Using an enclosing label to label a switch" {1,4}
<label>
  <Switch.Root />
  Notifications
</label>
```

The [Field](/react/components/field.md) component eliminates the need to track `id` or `aria-label` associations manually. It supports both enclosing and sibling labeling patterns, along with a UX improvement to prevent double clicks from selecting the label text.

```tsx title="Using the Field component to label a switch" {2,5}
<Field.Root>
  <Field.Label>
    <Switch.Root />
    Notifications
  </Field.Label>
</Field.Root>
```

### Form integration

To use a switch in a form, pass the switch's `name` to `<Field.Root>`:

```tsx title="Using Switch in a form" {2}
<Form>
  <Field.Root name="notifications">
    <Field.Label>
      <Switch.Root />
      Notifications
    </Field.Label>
  </Field.Root>
</Form>
```

## API reference

### Root

Represents the switch itself.
Renders a `<span>` element and a hidden `<input>` beside.

**Root Props:**

| Prop            | Type                                                                             | Default | Description                                                                                                                                                                                  |
| :-------------- | :------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| name            | `string`                                                                         | -       | Identifies the field when a form is submitted.                                                                                                                                               |
| defaultChecked  | `boolean`                                                                        | `false` | Whether the switch is initially active. To render a controlled switch, use the `checked` prop instead.                                                                                       |
| checked         | `boolean`                                                                        | -       | Whether the switch is currently active. To render an uncontrolled switch, use the `defaultChecked` prop instead.                                                                             |
| onCheckedChange | `((checked: boolean, eventDetails: Switch.Root.ChangeEventDetails) => void)`     | -       | Event handler called when the switch is activated or deactivated.                                                                                                                            |
| value           | `string`                                                                         | -       | The value submitted with the form when the switch is on.&#xA;By default, switch submits the "on" value, matching native checkbox behavior.                                                   |
| nativeButton    | `boolean`                                                                        | `false` | Whether the component renders a native `<button>` element when replacing it&#xA;via the `render` prop.&#xA;Set to `true` if the rendered element is a native button.                         |
| uncheckedValue  | `string`                                                                         | -       | The value submitted with the form when the switch is off.&#xA;By default, unchecked switches do not submit any value, matching native checkbox behavior.                                     |
| disabled        | `boolean`                                                                        | `false` | Whether the component should ignore user interaction.                                                                                                                                        |
| readOnly        | `boolean`                                                                        | `false` | Whether the user should be unable to activate or deactivate the switch.                                                                                                                      |
| required        | `boolean`                                                                        | `false` | Whether the user must activate the switch before submitting a form.                                                                                                                          |
| inputRef        | `Ref<HTMLInputElement>`                                                          | -       | A ref to access the hidden `<input>` element.                                                                                                                                                |
| id              | `string`                                                                         | -       | The id of the switch element.                                                                                                                                                                |
| className       | `string \| ((state: Switch.Root.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style           | `CSSProperties \| ((state: Switch.Root.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render          | `ReactElement \| ((props: HTMLProps, state: Switch.Root.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Root Data Attributes:**

| Attribute      | Type | Description                                                               |
| :------------- | :--- | :------------------------------------------------------------------------ |
| data-checked   | -    | Present when the switch is checked.                                       |
| data-unchecked | -    | Present when the switch is not checked.                                   |
| data-disabled  | -    | Present when the switch is disabled.                                      |
| data-readonly  | -    | Present when the switch is readonly.                                      |
| data-required  | -    | Present when the switch is required.                                      |
| data-valid     | -    | Present when the switch is in valid state (when wrapped in Field.Root).   |
| data-invalid   | -    | Present when the switch is in invalid state (when wrapped in Field.Root). |
| data-dirty     | -    | Present when the switch's value has changed (when wrapped in Field.Root). |
| data-touched   | -    | Present when the switch has been touched (when wrapped in Field.Root).    |
| data-filled    | -    | Present when the switch is active (when wrapped in Field.Root).           |
| data-focused   | -    | Present when the switch is focused (when wrapped in Field.Root).          |

### Thumb

The movable part of the switch that indicates whether the switch is on or off.
Renders a `<span>`.

**Thumb Props:**

| Prop      | Type                                                                              | Default | Description                                                                                                                                                                                  |
| :-------- | :-------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| className | `string \| ((state: Switch.Thumb.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style     | `CSSProperties \| ((state: Switch.Thumb.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render    | `ReactElement \| ((props: HTMLProps, state: Switch.Thumb.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Thumb Data Attributes:**

| Attribute      | Type | Description                                                               |
| :------------- | :--- | :------------------------------------------------------------------------ |
| data-checked   | -    | Present when the switch is checked.                                       |
| data-unchecked | -    | Present when the switch is not checked.                                   |
| data-disabled  | -    | Present when the switch is disabled.                                      |
| data-readonly  | -    | Present when the switch is readonly.                                      |
| data-required  | -    | Present when the switch is required.                                      |
| data-valid     | -    | Present when the switch is in valid state (when wrapped in Field.Root).   |
| data-invalid   | -    | Present when the switch is in invalid state (when wrapped in Field.Root). |
| data-dirty     | -    | Present when the switch's value has changed (when wrapped in Field.Root). |
| data-touched   | -    | Present when the switch has been touched (when wrapped in Field.Root).    |
| data-filled    | -    | Present when the switch is active (when wrapped in Field.Root).           |
| data-focused   | -    | Present when the switch is focused (when wrapped in Field.Root).          |
