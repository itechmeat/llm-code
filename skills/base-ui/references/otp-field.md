# OTP Field

Base UI `OTPField` is a preview primitive for one-time-password and verification-code entry.

## Import and anatomy

```tsx
import { OTPFieldPreview as OTPField } from "@base-ui/react/otp-field";

<OTPField.Root length={6}>
  <OTPField.Input />
  <OTPField.Separator />
</OTPField.Root>;
```

## Core parts

- `OTPField.Root` manages the overall value, validation, and form integration.
- `OTPField.Input` renders each character slot.
- `OTPField.Separator` is a visual grouping element for layouts such as `123-456`.

## Practical guidance

- Treat it as preview API surface until Base UI marks it stable.
- Always provide an accessible name via a native `<label>` or `Field` composition.
- Use `validationType="numeric"` for standard verification codes; switch to `alphanumeric` only when the backend really expects mixed characters.
- Use `onValueComplete` for side effects like verification requests, and `autoSubmit` only when the owning form can safely submit as soon as the value is complete.
- For custom sanitization rules, set `validationType="none"` and provide `sanitizeValue`.

## Operational notes

- `autoComplete="one-time-code"` is the default and should usually be preserved for mobile autofill flows.
- `form`, `required`, `readOnly`, `disabled`, and `name` live on `Root`, so form semantics stay centralized.
- `mask` is useful for short-lived verification secrets, but verify that the UX still supports paste and correction clearly.
