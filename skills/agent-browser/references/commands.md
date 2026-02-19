# Commands Reference

## Core Commands

```bash
agent-browser open <url>              # Navigate (aliases: goto, navigate)
agent-browser click <sel>             # Click element
agent-browser dblclick <sel>          # Double-click
agent-browser fill <sel> <text>       # Clear and fill
agent-browser type <sel> <text>       # Type into element
agent-browser press <key>             # Press key (Enter, Tab, Control+a)
agent-browser hover <sel>             # Hover element
agent-browser select <sel> <val>      # Select dropdown option
agent-browser check <sel>             # Check checkbox
agent-browser uncheck <sel>           # Uncheck checkbox
agent-browser scroll <dir> [px]       # Scroll (up/down/left/right)
agent-browser screenshot [path]       # Screenshot (--full for full page)
agent-browser snapshot                # Accessibility tree with refs
agent-browser eval <js>               # Run JavaScript
agent-browser close                   # Close browser
agent-browser tap <x> <y>             # Tap screen (mobile)
agent-browser swipe <x1> <y1> <x2> <y2> [ms] # Swipe gesture (mobile)
```

## Flags (v0.9.1+)

```bash
agent-browser open <url> --allow-file-access  # Enable file:// access (local PDFs/HTML)
agent-browser snapshot -C|--cursor            # Include cursor-interactive elements
agent-browser click <sel> --new-tab           # Open link in a new tab (v0.10.0)
agent-browser snapshot --annotate             # Numbered visual labels + legend (v0.12.0)
```

`--annotate` can also be enabled via `AGENT_BROWSER_ANNOTATE=1` for multimodal element mapping.

## Get Info

```bash
agent-browser get text <sel>          # Get text content
agent-browser get html <sel>          # Get innerHTML
agent-browser get value <sel>         # Get input value
agent-browser get attr <sel> <attr>   # Get attribute
agent-browser get title               # Get page title
agent-browser get url                 # Get current URL
agent-browser get count <sel>         # Count matching elements
agent-browser get box <sel>           # Get bounding box
```

## Check State

```bash
agent-browser is visible <sel>        # Check if visible
agent-browser is enabled <sel>        # Check if enabled
agent-browser is checked <sel>        # Check if checked
```

## Find Elements (Semantic Locators)

Actions: `click`, `fill`, `check`, `hover`, `text`

```bash
agent-browser find role <role> <action> [value]
agent-browser find text <text> <action>
agent-browser find label <label> <action> [value]
agent-browser find placeholder <ph> <action> [value]
agent-browser find testid <id> <action> [value]
agent-browser find first <sel> <action> [value]
agent-browser find nth <n> <sel> <action> [value]
```

`find` actions/filters were expanded in v0.11.x; prefer semantic locators before falling back to raw selectors.

Examples:

```bash
agent-browser find role button click --name "Submit"
agent-browser find label "Email" fill "test@test.com"
agent-browser find first ".item" click
```

## Wait Commands

```bash
agent-browser wait <selector>         # Wait for element
agent-browser wait <ms>               # Wait for time
agent-browser wait --text "Welcome"   # Wait for text
agent-browser wait --url "**/dash"    # Wait for URL pattern
agent-browser wait --load networkidle # Wait for load state
agent-browser wait --fn "condition"   # Wait for JS condition
```

## Mouse Commands

```bash
agent-browser mouse move <x> <y>      # Move mouse
agent-browser mouse down [button]     # Press button
agent-browser mouse up [button]       # Release button
agent-browser mouse wheel <dy> [dx]   # Scroll wheel
```

## Settings

```bash
agent-browser set viewport <w> <h>    # Set viewport size
agent-browser set device <name>       # Emulate device ("iPhone 14")
agent-browser set geo <lat> <lng>     # Set geolocation
agent-browser set offline [on|off]    # Toggle offline mode
agent-browser set headers <json>      # Extra HTTP headers
agent-browser set credentials <u> <p> # HTTP basic auth
agent-browser set media [dark|light]  # Emulate color scheme
agent-browser --device <name>         # Select iOS simulator/device (v0.9+)
```

## Devices (iOS)

```bash
agent-browser device list             # List available iOS simulators/devices
```

````

## Cookies & Storage

```bash
agent-browser cookies                 # Get all cookies
agent-browser cookies set <name> <val> # Set cookie (supports domain/path/httpOnly/secure/sameSite/expires)
agent-browser cookies clear           # Clear cookies

agent-browser storage local           # Get all localStorage
agent-browser storage local <key>     # Get specific key
agent-browser storage local set <k> <v>  # Set value
agent-browser storage local clear     # Clear all

agent-browser storage session         # Same for sessionStorage
````

## Network Interception

```bash
agent-browser network route <url>              # Intercept requests
agent-browser network route <url> --abort      # Block requests
agent-browser network route <url> --body <json>  # Mock response
agent-browser network unroute [url]            # Remove routes
agent-browser network requests                 # View tracked requests
```

## Tabs & Frames

```bash
agent-browser tab                     # List tabs
agent-browser tab new [url]           # New tab
agent-browser tab <n>                 # Switch to tab
agent-browser tab close [n]           # Close tab
agent-browser frame <sel>             # Switch to iframe
agent-browser frame main              # Back to main frame
```

## Debug Commands

```bash
agent-browser trace start [path]      # Start trace
agent-browser trace stop [path]       # Stop and save trace
agent-browser console                 # View console messages
agent-browser errors                  # View page errors
agent-browser highlight <sel>         # Highlight element
agent-browser state save <path>       # Save auth state
agent-browser state load <path>       # Load auth state
```

## State Management (v0.10.0)

```bash
agent-browser state list              # List saved sessions
agent-browser state show <name>       # Show stored session metadata
agent-browser state rename <old> <new> # Rename session state
agent-browser state clear <name>      # Remove a saved session state
agent-browser state cleanup           # Remove old/unused session files
```

## Navigation

```bash
agent-browser back                    # Go back
agent-browser forward                 # Go forward
agent-browser reload                  # Reload page
```
