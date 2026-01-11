# Vitest Skill

Next generation testing framework powered by Vite.

## What's Covered

- **Test API** - test, describe, beforeEach, afterEach, beforeAll, afterAll
- **Expect API** - 50+ matchers including toBe, toEqual, toContain, toThrow
- **Mocking** - vi.fn, vi.mock, vi.spyOn, fake timers, module mocking
- **Configuration** - vitest.config.ts, environments, coverage, reporters
- **CLI** - Commands, filters, coverage options, watch mode
- **Browser Mode** - Playwright/WebdriverIO, component testing, locators

## References

| File                                | Content                         |
| ----------------------------------- | ------------------------------- |
| [api.md](references/api.md)         | Test functions and hooks        |
| [expect.md](references/expect.md)   | Assertion matchers              |
| [mocking.md](references/mocking.md) | Mock functions, modules, timers |
| [config.md](references/config.md)   | Configuration options           |
| [cli.md](references/cli.md)         | Command line interface          |
| [browser.md](references/browser.md) | Browser mode testing            |

## Quick Example

```ts
import { describe, it, expect, vi } from "vitest";

describe("UserService", () => {
  it("fetches user", async () => {
    const fetchUser = vi.fn().mockResolvedValue({ name: "John" });

    const user = await fetchUser(1);

    expect(fetchUser).toHaveBeenCalledWith(1);
    expect(user.name).toBe("John");
  });
});
```

## Key Features

- **Vite-powered** — instant HMR, ESM native
- **Jest-compatible** — familiar API
- **TypeScript** — out of the box
- **Browser mode** — real browser testing
- **UI mode** — visual test interface

## Resources

- [SKILL.md](./SKILL.md) — main skill file
- [Vitest Docs](https://vitest.dev/)
