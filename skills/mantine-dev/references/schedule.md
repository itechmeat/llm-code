# Schedule Reference

`@mantine/schedule` is new in Mantine 9.0. It provides calendar scheduling components with multiple view levels, drag-and-drop event management, and extensive customization.

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
