# Bun.WebView

Native headless browser automation built into the Bun runtime.

## Backends

- `webkit` uses the system WebKit stack on macOS and needs no external browser install.
- `chrome` uses Chrome/Chromium through the DevTools Protocol and can auto-detect the browser or accept an explicit executable path.

## Minimal usage

```ts
await using view = new Bun.WebView({ width: 1280, height: 720 });

await view.navigate("https://bun.sh");
await view.click("a[href='/docs']");

const title = await view.evaluate("document.title");
const screenshot = await view.screenshot({ format: "jpeg", quality: 90 });
await Bun.write("page.jpg", screenshot);
```

## What matters operationally

- Input is dispatched as native OS-level events, so click/type actions show up as trusted browser events.
- Selector-based actions wait for actionability (attached, visible, stable, and unobscured) before firing.
- `scrollTo(selector)` walks ancestor scroll containers until the target becomes visible.
- Chrome backend exposes raw `cdp(method, params)` access when the high-level API is not enough.
- One browser subprocess is shared per Bun process; additional `new Bun.WebView()` calls open more tabs, not more browser instances.

## Common API surface

- `navigate(url)`
- `evaluate(expr)`
- `screenshot({ format, quality, encoding })`
- `click(selector)` or `click(x, y)`
- `type(text)`
- `press(key, { modifiers })`
- `scroll(dx, dy)` / `scrollTo(selector)`
- `goBack()` / `goForward()` / `reload()`
- `resize(width, height)`

## Practical rules

- Prefer the default WebKit backend on macOS when you want zero external dependencies.
- Use Chrome backend when you need CDP access, Chromium parity, or non-macOS support.
- Keep long-lived login state in `dataStore` instead of rebuilding sessions on every run.
- Capture page logs via the `console` option when the automation flow doubles as debugging.
- Treat `Bun.WebView` as browser automation inside the app process, not as a general-purpose browser farm.
