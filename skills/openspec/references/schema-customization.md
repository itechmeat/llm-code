# Schema Customization (Current Process and Gaps)

## Current Manual Flow

1. Determine the user data path (XDG):
   - macOS/Linux: ~/.local/share/openspec/schemas/
   - Windows: %LOCALAPPDATA%\openspec\schemas\
   - If set: $XDG_DATA_HOME/openspec/schemas/
2. Create a schema directory with templates:
   - <schema>/schema.yaml
   - <schema>/templates/\*.md
3. Copy built-in schema and template files from the installed package.
4. Edit schema.yaml and templates to customize.

## Friction Points

- Path discovery depends on XDG knowledge.
- Locating the package varies by install method.
- No built-in scaffolding or verification.
- No diffing against built-in defaults.

## Recommended CLI Capabilities

Priority commands:

- `schema list`: show available schemas and sources.
- `schema which <name>`: display resolved location.
- `schema copy <name>`: scaffold a customizable copy.
- `schema diff <name>`: compare override to built-in.
- `schema reset <name>`: revert to built-in.

## Guidance for User Requests

- Provide explicit paths and emphasize where overrides are read from.
- Clarify that overrides are all-or-nothing at the schema level.
- Suggest a CLI for users to avoid manual path discovery.
