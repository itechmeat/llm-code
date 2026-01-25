# Refs & Snapshots

Refs are deterministic element identifiers from the accessibility tree.

## Snapshots

The `snapshot` command returns the accessibility tree with refs.

### Options

| Option            | Description                                        |
| ----------------- | -------------------------------------------------- |
| -i, --interactive | Only interactive elements (buttons, links, inputs) |
| -c, --compact     | Remove empty structural elements                   |
| -d, --depth       | Limit tree depth                                   |
| -s, --selector    | Scope to CSS selector                              |

```bash
agent-browser snapshot                    # Full tree
agent-browser snapshot -i                 # Interactive only
agent-browser snapshot -c                 # Compact
agent-browser snapshot -d 3               # Depth limit
agent-browser snapshot -s "#main"         # Scoped
agent-browser snapshot -i -c -d 5         # Combined
```

### Output

```text
- heading "Example Domain" [ref=e1] [level=1]
- button "Submit" [ref=e2]
- textbox "Email" [ref=e3]
- link "Learn more" [ref=e4]
```

### JSON Output

```bash
agent-browser snapshot --json
```

## Selectors

### Priority for AI Agents

1. **@refs** - always prefer (from `snapshot`)
2. **Semantic locators** - when refs unavailable
3. **CSS/XPath** - fallback

### Refs

From snapshot output, use refs directly:

```bash
agent-browser click @e2
agent-browser fill @e3 "test@example.com"
agent-browser get text @e1
```

### CSS Selectors

```bash
agent-browser click "#id"
agent-browser click ".class"
agent-browser click "[data-testid='submit']"
```

### Text & XPath

```bash
agent-browser click "text=Submit"
agent-browser click "xpath=//button[@type='submit']"
```

### Semantic Locators (find)

```bash
agent-browser find role button click --name "Submit"
agent-browser find label "Email" fill "test@test.com"
agent-browser find placeholder "Search..." fill "query"
agent-browser find testid "submit-btn" click
agent-browser find first ".item" click
agent-browser find nth 2 ".item" click
```

## Best Practices

- Use `snapshot -i` to reduce output to actionable elements
- Use `--json` for structured parsing
- Re-snapshot after page changes to get updated refs
