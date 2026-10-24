# Schedule Reference

`@mantine/schedule` is new in Mantine 9.0. It provides calendar scheduling components with multiple view levels, drag-and-drop event management, and extensive customization.

## New in v9.7

### Slot label interval

`DayView` and `WeekView` accept `slotLabelInterval` to show time labels more often than once per hour. The value is in minutes and must be a multiple of `intervalMinutes` (values that do not satisfy this are rounded up to the next valid one, invalid values fall back to `60`). Default is `60`:

```tsx
<DayView
  date={new Date()}
  events={events}
  startTime="08:00:00"
  endTime="18:00:00"
  intervalMinutes={15}
  slotLabelInterval={30}
  slotHeight={40}
/>
```

Increase `slotHeight` when the labels are shown more often, otherwise they do not fit.

### Business hours: minutes, per-day ranges and colors

`businessHours` works together with `highlightBusinessHours`. Boundaries do not have to align with the slot grid — when a boundary falls inside a slot, the slot and its time label are painted up to the exact minute.

- The range accepts `HH:mm:ss` or `HH:mm` values, so minutes are supported: `businessHours={['07:42', '19:01']}`.
- `WeekView` also accepts a per-day record keyed by day number (`0` – Sunday, `6` – Saturday). Days that are missing from the record or set to `null` are fully outside business hours:

```tsx
<WeekView
  date={new Date()}
  events={events}
  highlightBusinessHours
  businessHours={{
    1: ['09:00:00', '17:00:00'],
    2: ['09:00:00', '17:00:00'],
    3: ['09:00:00', '17:00:00'],
    4: ['09:00:00', '17:00:00'],
    5: ['09:00:00', '13:00:00'],
  }}
  startTime="07:00:00"
  endTime="20:00:00"
/>
```

Colors are CSS variables, set with the `vars` prop or in CSS. Both variables apply to the time slots and to the time labels:

| View | Business hours background | Outside business hours |
| --- | --- | --- |
| `DayView` | `--day-view-business-hours-bg` | `--day-view-non-business-hours-bg` |
| `WeekView` | `--week-view-business-hours-bg` | `--week-view-non-business-hours-bg` |

```tsx
<DayView
  date={new Date()}
  events={events}
  highlightBusinessHours
  businessHours={['07:42', '19:01']}
  vars={() => ({
    dayView: {
      "--day-view-business-hours-bg": "var(--mantine-color-yellow-light)",
      "--day-view-non-business-hours-bg": "var(--mantine-color-blue-light)",
    },
  })}
/>
```

### MobileMonthView withWeekendDays

`MobileMonthView` accepts `withWeekendDays={false}` to hide weekend days from the mobile grid; default is `true`.

### Event overlap mode

`DayView` and `WeekView` accept `eventOverlapMode` to control how events that overlap in time share the horizontal space:

- `'columns'` (default) splits the width evenly between overlapping events.
- `'cascade'` indents every event over the previous one, so each event keeps a readable width. The indent shrinks as the group grows and the top event always keeps at least 60% of the width. Covered events are raised above the events on top of them when the pointer rests on them, and the same works with `Tab` focus. `eventOverlapRaiseDelay` sets the hover delay in milliseconds (`600` by default).

```tsx
import { ScheduleEventOverlapMode, WeekView } from "@mantine/schedule";

const [mode, setMode] = useState<ScheduleEventOverlapMode>("cascade");

<WeekView date={new Date()} events={events} startTime="08:00:00" endTime="14:00:00" eventOverlapMode={mode} />;
```

### Drop validation

All schedule views can reject a drag or resize before it is committed:

- `preventEventOverlap` rejects placements that would make the event overlap another event. Pass a function to decide per pair of events — return `true` to forbid that particular overlap.
- `canDropEvent` and `canResizeEventTo` are called before a drop or resize is committed — return `false` to reject it.
- `canDropExternalEvent` does the same for items dragged in from outside the schedule.
- `onEventPlacementRejected` reports the rejection with the conflicting events and the reason (`data.action` is `'drop'`, `'resize'` or `'external-drop'`).

The checks compose: a placement is allowed only when the overlap check passes and the matching callback returns a value other than `false`. While the pointer is over an invalid target, the drag ghost and the resizing event get `data-invalid`. In resource views the conflict set is scoped to the target resource row.

### Patch notes (v9.7.x)

- `startScrollTime` now scrolls to the correct position.
- `ResourcesDayView` sticky resource labels no longer cover the time labels row.
- `MobileMonthView` displays multi-day event times correctly on the start, middle and end days.
- `MonthView` no longer assigns rows quadratically for weeks with many events.

## New in v9.6

### ResourcesMonthView event resizing

`ResourcesMonthView` supports `withEventResize` — drag an event's start or end edge to resize. `onEventResize` is called with `{ eventId, newStart, newEnd }`. Resizing snaps to whole days and preserves the event's original time of day; `canResizeEvent` controls which events are resizable:

```tsx
<ResourcesMonthView
  date={date}
  onDateChange={setDate}
  resources={resources}
  events={events}
  withEventResize
  onEventResize={({ eventId, newStart, newEnd }) =>
    setEvents((current) =>
      current.map((event) =>
        event.id === eventId ? { ...event, start: newStart, end: newEnd } : event
      )
    )
  }
/>
```

### Drag and resize snap intervals

Time-grid views (`DayView`, `WeekView`, `ResourcesDayView`, `ResourcesWeekView`) accept `eventDragInterval` and `eventResizeInterval` to snap moves and resizes independently of the grid size — for example, a 30-minute grid can allow 15-minute drag increments. A ghost preview shows where an event will land while dragging.

### Interactive background events

Schedule views (`DayView`, `WeekView`, `MonthView`, `ResourcesDayView`, `ResourcesWeekView`) accept `withInteractiveBackgroundEvents` — background events (`display: "background"`) become clickable and trigger `onEventClick`, which makes it possible to open an edit modal for unavailability blocks and similar events.

### YearView

- `renderDay` replaces a day cell's entire content; it receives the day in `YYYY-MM-DD` format and the day's events (the same list used for the default indicators, without the three-item limit) — useful for counts, badges, or icons.
- `withWeekendDays={false}` hides weekend columns; events that fall only on hidden days are not displayed.

## Patch notes (v9.2.1)

- `MonthView` improves multi-day event overlap rendering when a day is already visually saturated.
- Event positioning with `intervalMinutes={60}` was corrected; if you added manual offsets or custom CSS to compensate, re-test before keeping them.

## Installation

```bash
npm install @mantine/schedule
```

Import styles in your app:

```tsx
import "@mantine/schedule/styles.css";
```

## Core Components

### Schedule

Unified container that combines all views with built-in navigation and view switching:

```tsx
import { useState } from "react";
import { Schedule, ScheduleEventData } from "@mantine/schedule";

function Demo() {
  const [events, setEvents] = useState<ScheduleEventData[]>(initialEvents);

  const handleEventDrop = ({ eventId, newStart, newEnd }) => {
    setEvents((prev) => prev.map((event) => (event.id === eventId ? { ...event, start: newStart, end: newEnd } : event)));
  };

  return <Schedule events={events} withEventsDragAndDrop onEventDrop={handleEventDrop} />;
}
```

### DayView

Single day with configurable time slots, all-day events, current time indicator, and business hours:

```tsx
import { DayView } from "@mantine/schedule";

<DayView date={new Date()} events={events} startTime="08:00:00" endTime="18:00:00" withEventsDragAndDrop onEventDrop={handleEventDrop} />;
```

### WeekView

Weekly calendar grid with time slots, week numbers, weekend toggling, and multi-day spanning.

### MonthView

Monthly calendar with event dots and configurable week start.

### MobileMonthView

Touch-optimized month view for mobile UIs.

### ResourcesDayView / ResourcesWeekView

Day/week grid with a resource column per row (rooms, staff, equipment), each showing its own events:

```tsx
import { ResourcesDayView } from "@mantine/schedule";

<ResourcesDayView
  date={date}
  onDateChange={setDate}
  resources={resources}
  events={events}
  intervalMinutes={120}
  startScrollTime="08:00:00"
/>;
```

New in v9.5: `intervalMinutes` on `ResourcesDayView`/`ResourcesWeekView` now also accepts whole numbers of hours (e.g. `120`, `240`) for multi-hour slot columns, in addition to the values that divide evenly into an hour (`15`, `30`, `60`).

## Event Data Shape

```ts
interface ScheduleEventData {
  id: string | number;
  title: string;
  start: string; // 'YYYY-MM-DD HH:mm:ss'
  end: string; // 'YYYY-MM-DD HH:mm:ss'
  color?: string;
}
```

## Key Props

- `events` — array of `ScheduleEventData`
- `withEventsDragAndDrop` — enable drag to reschedule
- `onEventDrop` — callback with `{ eventId, newStart, newEnd }`
- `startTime` / `endTime` — visible time range (DayView/WeekView)
- `intervalMinutes` — slot length in minutes; `ResourcesDayView`/`ResourcesWeekView` accept whole hours (e.g. `120`, `240`) for multi-hour columns since v9.5
