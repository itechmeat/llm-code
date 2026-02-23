# Assets in Skills

## When to Create Assets

Assets make sense when:
- A user needs to **copy a file verbatim** or use it as a starting point (configs, templates)
- A task requires a **fill-in-the-blanks document** the agent fills in per-project (checklists, runbooks)
- There is **static reference data** the agent uses repeatedly — lookup tables, decision matrices
- A piece of prose (prompts, rules) is **reused across multiple interactions** in a predictable shape

Don't create an asset just to hold documentation. If the content is meant to be read and understood, it belongs in `references/`. Assets are things to **copy, fill in, or apply**.

## Asset Types

### Config Templates (YAML / JSON / TOML)
Ready-to-use configuration files the user copies into their project and customizes.

Conventions (from coderabbit pattern):
- Add `# yaml-language-server: $schema=<url>` at the top for IDE validation
- Follow with a one-line comment naming the file and linking to the full reference
- Provide two variants when the surface area is large: `.minimal.yaml` (only required/common options) and `.full.yaml` (all options with inline explanations)
- Inline comments explain non-obvious values; omit comments on self-explanatory keys

```yaml
# yaml-language-server: $schema=https://example.com/schema.json

# MyTool Configuration - Minimal
# See full reference: https://docs.example.com/configuration

setting: value
nested:
  key: default
```

### YAML Manifests (Kubernetes / cloud-native)
Reusable infrastructure manifests parametrized with variables.

Conventions (from k8s-cluster-api pattern):
- First line: `# <Title>` describing the template's purpose
- Second line: short description of use case (dev/prod/minimal)
- Third line: `# Usage: <command to apply>`
- Use `${VAR_NAME:=default_value}` for required parameters with sensible defaults
- Reference variable substitution in comments when it's non-obvious
- Group multi-document YAML files by concern; each resource gets a blank line before `---`

```yaml
# Production Cluster Template
# Suitable for production with AWS provider
# Usage: envsubst < cluster-production.yaml | kubectl apply -f -
---
apiVersion: example.com/v1
kind: Resource
metadata:
  name: ${RESOURCE_NAME:=my-resource}
  namespace: ${NAMESPACE:=default}
```

### Text Templates (git hooks, CI configs, etc.)
Plain-text files where structure matters and users fill in the blanks.

Conventions (from commits pattern):
- Show the expected output format at the very top
- Use `#`-prefixed inline comments to explain each field, option, or constraint
- List all valid values for constrained fields (e.g., commit types)
- End with a link to the authoritative specification

```text
# <type>(<scope>): <subject>

# Explain why this change is being made

# --- TEMPLATE END ---
# Type can be:
#   feat - new feature
#   fix  - bug fix
# For more: https://example.com/spec
```

### Markdown Templates (checklists, runbooks, sign-off forms)
Structured documents the agent fills in or the user follows step-by-step.

Conventions (from k8s-cluster-api upgrade-checklist.md):
- Use `- [ ]` checkboxes for every action item
- Use inline code blocks for commands the user copies: `` `kubectl get pods` ``
- Leave fillable blank fields as `______` or bold-wrapped underscores `**___**`
- Include a sign-off / notes section at the bottom for auditability

```markdown
# Operation Checklist

## Pre-Flight

- [ ] Step one: `command to run`
- [ ] Step two: verify output

## Sign-Off

| Role | Name | Date |
|------|------|------|
| Operator | | |

Notes: _________________________________
```

### Prompt / Prose Templates
Ready-to-paste text blocks for use in prompts, IDE rules, or config files.

Conventions (from coderabbit agent-prompts.md):
- Group variants by use case under `##` headers
- Wrap each block in a fenced code block with appropriate type (`text`, `markdown`)
- Provide 3–5 variants from simplest to most complex
- Keep each variant self-contained — no cross-references between blocks

## Naming Conventions

| Asset type         | Naming pattern                    | Examples                                |
| ------------------ | --------------------------------- | --------------------------------------- |
| Config minimal     | `<tool>.minimal.<ext>`            | `coderabbit.minimal.yaml`               |
| Config full        | `<tool>.full.<ext>`               | `coderabbit.full.yaml`                  |
| Manifest template  | `<purpose>[-<variant>].<ext>`     | `cluster-minimal.yaml`, `cluster-production.yaml` |
| Checklist / runbook | `<operation>-checklist.md`       | `upgrade-checklist.md`                  |
| Runbook / guide    | `<operation>-<type>.md`           | `dr-backup-restore.md`                  |
| Text template      | `<name>.template`                 | `commit-msg.template`                   |
| Prompt collection  | `<topic>-prompts.md`              | `agent-prompts.md`                      |
| Lookup table       | `<topic>-matrix.md`               | `provider-matrix.md`                    |

## How to Reference Assets in SKILL.md

Be explicit: tell the agent to copy the file, what to fill in, and what the result should look like.

```markdown
## Step 2: Create Configuration

Copy `assets/tool.minimal.yaml` to your project root as `.toolrc.yaml`.
Fill in:
- `project_name` — your project identifier
- `token` — from Settings > API Tokens

To enable all options, use `assets/tool.full.yaml` instead (see inline comments).
```

For manifests:
```markdown
Apply the minimal cluster template:
```bash
envsubst < assets/cluster-minimal.yaml | kubectl apply -f -
```
Required variables: `CLUSTER_NAME`, `NAMESPACE`. Optional: `KUBERNETES_VERSION` (default: v1.28.0).
```

For checklists:
```markdown
Before upgrading, work through `assets/upgrade-checklist.md`:
- Complete every checkbox
- Fill in cluster name and version fields
- Get sign-off signatures before proceeding
```

## What Assets Should NOT Do

- No secrets, tokens, or real credentials — use placeholder comments
- No hardcoded environment-specific values — parametrize with variables or comments
- No project-specific paths — keep templates generic
- Do not duplicate content that belongs in `references/` (explanations) or `examples/` (output samples)
