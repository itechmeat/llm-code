# Telegram Mini Apps

Interactive web apps inside Telegram with native features.

## Initialization

```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

```javascript
const tg = window.Telegram.WebApp;
tg.ready();  // Signal app is ready
tg.expand(); // Expand to full height
```

## Core Properties

| Property | Description |
|----------|-------------|
| `initData` | Raw data for server validation |
| `initDataUnsafe` | Parsed data (DO NOT trust server-side) |
| `platform` | ios, android, tdesktop, etc. |
| `colorScheme` | `"light"` or `"dark"` |
| `themeParams` | Current theme colors |
| `viewportHeight` | Visible area height |
| `isFullscreen` | Fullscreen mode (Bot API 8.0+) |

## Theme CSS Variables

```css
.container {
  background: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
}
.button {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
}
```

Available: `--tg-theme-bg-color`, `--tg-theme-text-color`, `--tg-theme-hint-color`, 
`--tg-theme-link-color`, `--tg-theme-button-color`, `--tg-theme-button-text-color`,
`--tg-theme-secondary-bg-color`, `--tg-theme-header-bg-color`.

## Main Button

```javascript
tg.MainButton
  .setText('Submit')
  .show()
  .onClick(() => {
    tg.MainButton.showProgress();
    // Submit logic
    tg.MainButton.hideProgress();
  });
```

## Back Button

```javascript
tg.BackButton.show();
tg.BackButton.onClick(() => tg.BackButton.hide());
```

## Haptic Feedback

```javascript
tg.HapticFeedback.impactOccurred('medium');      // light|medium|heavy|rigid|soft
tg.HapticFeedback.notificationOccurred('success'); // success|error|warning
```

## Cloud Storage

Up to 1024 items per user. Key: 1-128 chars, Value: 0-4096 chars.

```javascript
tg.CloudStorage.setItem('key', 'value');
tg.CloudStorage.getItem('key', (err, val) => { /* ... */ });
tg.CloudStorage.removeItem('key');
```

## Dialogs

```javascript
tg.showAlert('Done!');
tg.showConfirm('Delete?', (ok) => { if (ok) { /* ... */ } });
tg.showPopup({
  title: 'Action',
  message: 'Choose:',
  buttons: [
    { id: 'yes', type: 'default', text: 'Yes' },
    { id: 'no', type: 'cancel' }
  ]
}, (id) => { /* ... */ });
```

## QR Scanner

```javascript
tg.showScanQrPopup({ text: 'Scan code' }, (data) => {
  if (data) { tg.closeScanQrPopup(); return true; }
});
```

## Events

```javascript
tg.onEvent('themeChanged', () => { /* ... */ });
tg.onEvent('viewportChanged', ({ isStateStable }) => { /* ... */ });
tg.onEvent('mainButtonClicked', () => { /* ... */ });
```

## Server-Side Validation

**Always validate initData server-side.**

```python
import hashlib, hmac
from urllib.parse import parse_qsl

def validate_init_data(init_data: str, bot_token: str) -> bool:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop('hash', None)
    if not received_hash:
        return False
    
    data_check_string = '\n'.join(
        f'{k}={v}' for k, v in sorted(parsed.items())
    )
    
    # Note: HMAC key is "WebAppData" + token, different from Login Widget
    secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
    calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(calculated, received_hash)
```

## Mini Apps 2.0 (Bot API 8.0+)

| Feature | Method |
|---------|--------|
| Fullscreen | `requestFullscreen()` / `exitFullscreen()` |
| Lock orientation | `lockOrientation()` / `unlockOrientation()` |
| Home screen | `addToHomeScreen()` |
| Safe area | `safeAreaInset` property |

## Critical Rules

- ❌ Never trust `initDataUnsafe` on server — validate `initData`
- ❌ Never use hardcoded colors — use theme CSS variables
- ✅ Check `auth_date` freshness
- ✅ Handle `viewportChanged` for responsive layout
- ✅ Use `isVersionAtLeast()` for feature detection

## Links

- Official docs: https://core.telegram.org/bots/webapps
- Authentication: [authentication.md](authentication.md)
