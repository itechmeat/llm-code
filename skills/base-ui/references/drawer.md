# Drawer

Base UI `Drawer` is a slide-in overlay primitive for mobile navigation, sheets, and bottom panels.

## v1.3.0 status

- `Drawer` is now stable and should be imported from `@base-ui/react/drawer`.
- Treat it as a first-class overlay primitive rather than a preview-only Sheet replacement.
- `Drawer.SwipeArea` is available when you want an explicit edge swipe affordance.

## Recommended anatomy

```tsx
import { Drawer } from "@base-ui/react/drawer";

<Drawer.Root>
  <Drawer.Trigger />
  <Drawer.Portal>
    <Drawer.Backdrop />
    <Drawer.Popup>
      <Drawer.Handle />
      <Drawer.Title />
      <Drawer.Description />
      <Drawer.Close />
    </Drawer.Popup>
  </Drawer.Portal>
</Drawer.Root>;
```

If you need touch-driven opening, add `Drawer.SwipeArea` near the screen edge instead of overloading the visible trigger.

## When to prefer Drawer

- Mobile bottom sheets
- Side panels that should feel modal
- Cases where touch gestures matter more than anchor positioning

Prefer `Popover` when the UI must stay anchored to a trigger and behave like a positioned popup.

## Practical notes

- Keep the interactive surface explicit: `Trigger` for click/tap, `SwipeArea` for gesture affordance.
- Avoid controlled swipe-dismiss flows unless you have a clear state-owner strategy; 1.3.0 specifically hardens controlled-drawer swipe behavior.
- Test nested scrolling and text selection on touch devices, especially for bottom sheets with forms.

## v1.4.0 notes

- Touch scrolling inside portaled popups is more reliable.
- Nested swipe-cancel and interrupted swipe-dismiss cleanup were fixed, so retest any local drawer gesture workarounds before keeping them.
- Base UI now warns when a drawer popup is missing `Viewport`; keep the full anatomy intact for swipe/stack correctness.

## Accessibility checklist

- Provide a visible title or an equivalent accessible label.
- Keep focus management inside the drawer when modal.
- Ensure dismiss controls exist even if swipe is enabled.
- Do not rely on swipe gestures as the only way to close the panel.
