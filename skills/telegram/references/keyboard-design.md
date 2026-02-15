# Keyboard Design

## Principles

- Progressive disclosure: show 3–5 relevant actions, not 20.
- Mobile-first: max 2 buttons per row; avoid long labels.
- Navigation consistency: always provide "Back"/"Main menu" for multi-step flows.
- Responsiveness: always `answer_callback_query` quickly to clear the loading spinner.
- Emphasis: use button colors/emoji to highlight primary actions when available.

## Callback data design

Use short, parseable callback data strings:

- Prefix by feature: `evt:` / `place:` / `page:`
- Include only identifiers you can validate (never trust arbitrary client data)

### Example conventions

- `place:details:<place_id>`
- `place:save:<place_id>`
- `page:<page_number>`

### Callback data limits

Telegram limits callback_data to 64 bytes. Keep it short and parseable.

## Common patterns

### Action keyboard (inline)

- Primary action(s) on the first row
- Secondary action(s) below
- Always include a navigation row (Back/Main)

### Pagination

- Show `Prev` / `Next` with a page indicator
- Use a no-op callback for the page indicator

### Edit vs reply

- Prefer editing the existing message during navigation flows to avoid chat spam.
- Prefer replying with a new message when:
  - the content is important for history (receipts, confirmations)
  - the edited message is too old or already removed

## Safety checklist

- Always `answer_callback_query`.
- Validate identifiers from callback data (types, ownership/tenant).
- Never include secrets or tokens in callback data.
- Keep callback data within Telegram limits (64 bytes).
