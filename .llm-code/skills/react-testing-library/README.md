# React Testing Library Skill

Testing React components the way users interact with them.

## What's Covered

- **Queries** — getBy, findBy, queryBy with all selectors (Role, Text, LabelText, etc.)
- **User Events** — Simulating clicks, typing, pointer, keyboard
- **Async Testing** — waitFor, findBy, handling async operations
- **API** — render, screen, cleanup, act, renderHook
- **Debugging** — screen.debug(), prettyDOM, logRoles
- **Configuration** — testIdAttribute, asyncUtilTimeout

## References

| File                                        | Content                                           | Lines |
| ------------------------------------------- | ------------------------------------------------- | ----- |
| [queries.md](references/queries.md)         | Query types, priority, selectors, ByRole options  | 226   |
| [user-events.md](references/user-events.md) | User event simulation, keyboard, pointer, utility | 302   |
| [api.md](references/api.md)                 | React Testing Library API                         | 306   |
| [async.md](references/async.md)             | Async utilities                                   | 291   |
| [debugging.md](references/debugging.md)     | Debugging utilities                               | 258   |
| [config.md](references/config.md)           | Configuration                                     | 296   |

## Quick Example

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("submits form with user input", async () => {
  const user = userEvent.setup();
  const handleSubmit = jest.fn();
  render(<LoginForm onSubmit={handleSubmit} />);

  // Query by accessible role
  await user.type(screen.getByRole("textbox", { name: /username/i }), "john");
  await user.type(screen.getByLabelText(/password/i), "secret");
  await user.click(screen.getByRole("button", { name: /submit/i }));

  expect(handleSubmit).toHaveBeenCalledWith({ username: "john", password: "secret" });
});
```

## Resources

- [SKILL.md](./SKILL.md) — main skill file
- [Testing Library Docs](https://testing-library.com/)
