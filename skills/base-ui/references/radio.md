---
title: Radio
subtitle: An easily stylable radio button component.
description: A high-quality, unstyled React radio button component that is easy to style.
---

# Radio

A high-quality, unstyled React radio button component that is easy to style.

## Demo

### Tailwind

This example shows how to implement the component using Tailwind CSS.

```tsx
/* index.tsx */
"use client";
import * as React from "react";
import { Radio } from "@base-ui/react/radio";
import { RadioGroup } from "@base-ui/react/radio-group";

export default function ExampleRadioGroup() {
  const id = React.useId();
  return (
    <RadioGroup aria-labelledby={id} defaultValue="fuji-apple" className="flex flex-col items-start gap-1 text-gray-900">
      <div className="font-medium" id={id}>
        Best apple
      </div>

      <label className="flex items-center gap-2">
        <Radio.Root value="fuji-apple" className="flex size-5 items-center justify-center rounded-full focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800 data-[checked]:bg-gray-900 data-[unchecked]:border data-[unchecked]:border-gray-300">
          <Radio.Indicator className="flex before:size-2 before:rounded-full before:bg-gray-50 data-[unchecked]:hidden" />
        </Radio.Root>
        Fuji
      </label>

      <label className="flex items-center gap-2">
        <Radio.Root value="gala-apple" className="flex size-5 items-center justify-center rounded-full focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800 data-[checked]:bg-gray-900 data-[unchecked]:border data-[unchecked]:border-gray-300">
          <Radio.Indicator className="flex before:size-2 before:rounded-full before:bg-gray-50 data-[unchecked]:hidden" />
        </Radio.Root>
        Gala
      </label>

      <label className="flex items-center gap-2">
        <Radio.Root value="granny-smith-apple" className="flex size-5 items-center justify-center rounded-full focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800 data-[checked]:bg-gray-900 data-[unchecked]:border data-[unchecked]:border-gray-300">
          <Radio.Indicator className="flex before:size-2 before:rounded-full before:bg-gray-50 data-[unchecked]:hidden" />
        </Radio.Root>
        Granny Smith
      </label>
    </RadioGroup>
  );
}
```

### CSS Modules

This example shows how to implement the component using CSS Modules.

```css
/* index.module.css */
.RadioGroup {
  display: flex;
  flex-direction: column;
  align-items: start;
  gap: 0.25rem;
  color: var(--color-gray-900);
}

.Caption {
  font-weight: 500;
}

.Item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.Radio {
  box-sizing: border-box;
  display: flex;
  width: 1.25rem;
  height: 1.25rem;
  align-items: center;
  justify-content: center;
  border-radius: 100%;
  outline: 0;
  padding: 0;
  margin: 0;
  border: none;

  &[data-unchecked] {
    border: 1px solid var(--color-gray-300);
    background-color: transparent;
  }

  &[data-checked] {
    background-color: var(--color-gray-900);
  }

  &:focus-visible {
    outline: 2px solid var(--color-blue);
    outline-offset: 2px;
  }
}

.Indicator {
  display: flex;
  align-items: center;
  justify-content: center;

  &[data-unchecked] {
    display: none;
  }

  &::before {
    content: "";
    border-radius: 100%;
    width: 0.5rem;
    height: 0.5rem;
    background-color: var(--color-gray-50);
  }
}
```

```tsx
/* index.tsx */
"use client";
import * as React from "react";
import { Radio } from "@base-ui/react/radio";
import { RadioGroup } from "@base-ui/react/radio-group";
import styles from "./index.module.css";

export default function ExampleRadioGroup() {
  const id = React.useId();
  return (
    <RadioGroup aria-labelledby={id} defaultValue="fuji-apple" className={styles.RadioGroup}>
      <div className={styles.Caption} id={id}>
        Best apple
      </div>

      <label className={styles.Item}>
        <Radio.Root value="fuji-apple" className={styles.Radio}>
          <Radio.Indicator className={styles.Indicator} />
        </Radio.Root>
        Fuji
      </label>

      <label className={styles.Item}>
        <Radio.Root value="gala-apple" className={styles.Radio}>
          <Radio.Indicator className={styles.Indicator} />
        </Radio.Root>
        Gala
      </label>

      <label className={styles.Item}>
        <Radio.Root value="granny-smith-apple" className={styles.Radio}>
          <Radio.Indicator className={styles.Indicator} />
        </Radio.Root>
        Granny Smith
      </label>
    </RadioGroup>
  );
}
```

## Usage guidelines

- **Form controls must have an accessible name**: It can be created using `<label>` elements, or the `Field` and `Fieldset` components. See [Labeling a radio group](#labeling-a-radio-group) and the [forms guide](/react/handbook/forms.md).

## Anatomy

Radio is always placed within Radio Group. Import the components and place them together:

```jsx title="Anatomy"
import { Radio } from "@base-ui/react/radio";
import { RadioGroup } from "@base-ui/react/radio-group";

<RadioGroup>
  <Radio.Root>
    <Radio.Indicator />
  </Radio.Root>
</RadioGroup>;
```

## Examples

### Labeling a radio group

A visible label for the group is created by specifying `aria-labelledby` on `<RadioGroup>` to reference the `id` of a sibling element that contains the group label text.

```tsx title="Using aria-labelledby to label a radio group"
<div id="storage-type-label">Storage type</div>
<RadioGroup aria-labelledby="storage-type-label">{/* ... */}</RadioGroup>
```

For individual radio buttons, use an enclosing `<label>` element that wraps each `<Radio.Root>`. An enclosing label is announced to screen readers when focus is on the control, and ensures that clicking on any gaps between the label and radio still toggles it.

```tsx title="Using an enclosing label to label a radio button" {1,4}
<label>
  <Radio.Root value="ssd" />
  SSD
</label>
```

The [Field](/react/components/field.md) and [Fieldset](/react/components/fieldset.md) components eliminate the need to track `id` or `aria-labelledby` associations manually. They support both enclosing and sibling labeling patterns, along with a UX improvement to prevent double clicks from selecting the label text.

1. **Group label**: Since the group contains multiple controls, it can be labeled as a fieldset. Use [Fieldset](/react/components/fieldset.md) by replacing the `<Fieldset.Root>` element with `<RadioGroup>` via the `render` prop. `<Fieldset.Legend>` provides the visible label for the group.
2. **Individual label**: Label an individual radio using an enclosing `<Field.Label>`. Enclosing labels ensure that clicking on any gaps between the label and radio still toggles it.

```tsx title="Using Field and Fieldset to label a radio group"
<Field.Root>
  <Fieldset.Root render={<RadioGroup />}>
    <Fieldset.Legend>Storage type</Fieldset.Legend>
    <Field.Label>
      <Radio.Root value="ssd" />
      SSD
    </Field.Label>
    <Field.Label>
      <Radio.Root value="hdd" />
      HDD
    </Field.Label>
  </Fieldset.Root>
</Field.Root>
```

### Form integration

To use a radio group in a form, pass the radio group's `name` to `<Field.Root>`:

```tsx title="Using Radio Group in a form" {2}
<Form>
  <Field.Root name="storageType">
    <Fieldset.Root render={<RadioGroup />}>
      <Fieldset.Legend>Storage type</Fieldset.Legend>
      <Field.Label>
        <Radio.Root value="ssd" />
        SSD
      </Field.Label>
      <Field.Label>
        <Radio.Root value="hdd" />
        HDD
      </Field.Label>
    </Fieldset.Root>
  </Field.Root>
</Form>
```

## API reference

### RadioGroup

Provides a shared state to a series of radio buttons. Renders a `<div>` element.

**RadioGroup Props:**

| Prop          | Type                                                                            | Default | Description                                                                                                                                                                                  |
| :------------ | :------------------------------------------------------------------------------ | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| name          | `string`                                                                        | -       | Identifies the field when a form is submitted.                                                                                                                                               |
| defaultValue  | `any`                                                                           | -       | The uncontrolled value of the radio button that should be initially selected. To render a controlled radio group, use the `value` prop instead.                                              |
| value         | `any`                                                                           | -       | The controlled value of the radio item that should be currently selected. To render an uncontrolled radio group, use the `defaultValue` prop instead.                                        |
| onValueChange | `((value: any, eventDetails: Radio.Group.ChangeEventDetails) => void)`          | -       | Callback fired when the value changes.                                                                                                                                                       |
| disabled      | `boolean`                                                                       | `false` | Whether the component should ignore user interaction.                                                                                                                                        |
| readOnly      | `boolean`                                                                       | `false` | Whether the user should be unable to select a different radio button in the group.                                                                                                           |
| required      | `boolean`                                                                       | `false` | Whether the user must choose a value before submitting a form.                                                                                                                               |
| inputRef      | `Ref<HTMLInputElement>`                                                         | -       | A ref to access the hidden input element.                                                                                                                                                    |
| className     | `string \| ((state: RadioGroup.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style         | `CSSProperties \| ((state: RadioGroup.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render        | `ReactElement \| ((props: HTMLProps, state: RadioGroup.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**RadioGroup Data Attributes:**

| Attribute     | Type | Description                               |
| :------------ | :--- | :---------------------------------------- |
| data-disabled | -    | Present when the radio group is disabled. |

### Root

Represents the radio button itself.
Renders a `<span>` element and a hidden `<input>` beside.

**Root Props:**

| Prop         | Type                                                                            | Default | Description                                                                                                                                                                                  |
| :----------- | :------------------------------------------------------------------------------ | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| value        | `any`                                                                           | -       | The unique identifying value of the radio in a group.                                                                                                                                        |
| nativeButton | `boolean`                                                                       | `false` | Whether the component renders a native `<button>` element when replacing it&#xA;via the `render` prop.&#xA;Set to `true` if the rendered element is a native button.                         |
| disabled     | `boolean`                                                                       | -       | Whether the component should ignore user interaction.                                                                                                                                        |
| readOnly     | `boolean`                                                                       | -       | Whether the user should be unable to select the radio button.                                                                                                                                |
| required     | `boolean`                                                                       | -       | Whether the user must choose a value before submitting a form.                                                                                                                               |
| inputRef     | `Ref<HTMLInputElement>`                                                         | -       | A ref to access the hidden input element.                                                                                                                                                    |
| className    | `string \| ((state: Radio.Root.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style        | `CSSProperties \| ((state: Radio.Root.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| render       | `ReactElement \| ((props: HTMLProps, state: Radio.Root.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Root Data Attributes:**

| Attribute      | Type | Description                                                              |
| :------------- | :--- | :----------------------------------------------------------------------- |
| data-checked   | -    | Present when the radio is checked.                                       |
| data-unchecked | -    | Present when the radio is not checked.                                   |
| data-disabled  | -    | Present when the radio is disabled.                                      |
| data-readonly  | -    | Present when the radio is readonly.                                      |
| data-required  | -    | Present when the radio is required.                                      |
| data-valid     | -    | Present when the radio is in valid state (when wrapped in Field.Root).   |
| data-invalid   | -    | Present when the radio is in invalid state (when wrapped in Field.Root). |
| data-dirty     | -    | Present when the radio's value has changed (when wrapped in Field.Root). |
| data-touched   | -    | Present when the radio has been touched (when wrapped in Field.Root).    |
| data-filled    | -    | Present when the radio is checked (when wrapped in Field.Root).          |
| data-focused   | -    | Present when the radio is focused (when wrapped in Field.Root).          |

### Indicator

Indicates whether the radio button is selected.
Renders a `<span>` element.

**Indicator Props:**

| Prop        | Type                                                                                 | Default | Description                                                                                                                                                                                  |
| :---------- | :----------------------------------------------------------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| className   | `string \| ((state: Radio.Indicator.State) => string \| undefined)`                  | -       | CSS class applied to the element, or a function that&#xA;returns a class based on the component’s state.                                                                                     |
| style       | `CSSProperties \| ((state: Radio.Indicator.State) => CSSProperties \| undefined)`    | -       | -                                                                                                                                                                                            |
| keepMounted | `boolean`                                                                            | `false` | Whether to keep the HTML element in the DOM when the radio button is inactive.                                                                                                               |
| render      | `ReactElement \| ((props: HTMLProps, state: Radio.Indicator.State) => ReactElement)` | -       | Allows you to replace the component’s HTML element&#xA;with a different tag, or compose it with another component.Accepts a `ReactElement` or a function that returns the element to render. |

**Indicator Data Attributes:**

| Attribute      | Type | Description                                                              |
| :------------- | :--- | :----------------------------------------------------------------------- |
| data-checked   | -    | Present when the radio is checked.                                       |
| data-unchecked | -    | Present when the radio is not checked.                                   |
| data-disabled  | -    | Present when the radio is disabled.                                      |
| data-readonly  | -    | Present when the radio is readonly.                                      |
| data-required  | -    | Present when the radio is required.                                      |
| data-valid     | -    | Present when the radio is in valid state (when wrapped in Field.Root).   |
| data-invalid   | -    | Present when the radio is in invalid state (when wrapped in Field.Root). |
| data-dirty     | -    | Present when the radio's value has changed (when wrapped in Field.Root). |
| data-touched   | -    | Present when the radio has been touched (when wrapped in Field.Root).    |
| data-filled    | -    | Present when the radio is checked (when wrapped in Field.Root).          |
| data-focused   | -    | Present when the radio is focused (when wrapped in Field.Root).          |
