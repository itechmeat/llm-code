# Schedule Reference

`@mantine/schedule` is new in Mantine 9.0. It provides calendar scheduling components with multiple view levels, drag-and-drop event management, and extensive customization.

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
