# Browser API (Remote Sessions)

Perplexity's Python SDK exposes a minimal Browser API for creating and cleaning up **remote browser sessions** for CDP-based automation.

## Endpoints / Methods

- `client.browser.sessions.create()` → `POST /v1/browser/sessions`
- `client.browser.sessions.delete(session_id)` → `DELETE /v1/browser/sessions/{session_id}`

## Basic Workflow

```python
from perplexity import Perplexity

client = Perplexity()

session = client.browser.sessions.create()
if not session.session_id:
    raise RuntimeError('Browser session did not return a session_id')

try:
    # Use `session.session_id` with your CDP client to automate the remote browser.
    # The Perplexity SDK manages session lifecycle; CDP automation is outside this SDK.
    pass
finally:
    client.browser.sessions.delete(session.session_id)
```

## Notes

- The create response includes `session_id` and `status`.
- Always delete sessions to avoid leaking remote resources.
