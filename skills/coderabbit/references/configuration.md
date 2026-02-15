# CodeRabbit Configuration

CodeRabbit can be configured via `.coderabbit.yaml` in repository root.

## Configuration Priority (highest to lowest)

1. **Local .coderabbit.yaml** — Completely overrides all other settings
2. **Central configuration** — From dedicated `coderabbit` repository
3. **Repository settings** — Web UI per-repository
4. **Organization settings** — Web UI organization-wide

Configuration sources don't merge — highest priority replaces all lower.

## Minimal Example

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: en-US
tone_instructions: "Be concise and focus on critical issues only"

reviews:
  profile: chill
  high_level_summary: true
```

## Key Settings

### General

| Setting             | Type    | Default | Description                  |
| ------------------- | ------- | ------- | ---------------------------- |
| `language`          | string  | `en-US` | Review language (ISO code)   |
| `tone_instructions` | string  | `""`    | Custom tone (max 250 chars)  |
| `early_access`      | boolean | `false` | Enable early-access features |

### Reviews

| Setting                                     | Type    | Default | Description                                                      |
| ------------------------------------------- | ------- | ------- | ---------------------------------------------------------------- |
| `reviews.profile`                           | enum    | `chill` | `chill` or `assertive`                                           |
| `reviews.high_level_summary`                | boolean | `true`  | Summary in PR description                                        |
| `reviews.sequence_diagrams`                 | boolean | `true`  | Generate diagrams                                                |
| `reviews.poem`                              | boolean | `true`  | Generate poem in walkthrough                                     |
| `reviews.path_filters`                      | array   | `[]`    | Include/exclude patterns (`!dist/**`)                            |
| `reviews.auto_pause_after_reviewed_commits` | integer | `5`     | Auto-pause reviews after N reviewed commits (set `0` to disable) |

### Auto Review

```yaml
reviews:
  auto_review:
    enabled: true
    auto_incremental_review: true
    drafts: false
    ignore_title_keywords: ["WIP", "DO NOT MERGE"]
    labels: ["!wip"] # Skip PRs with 'wip' label
    base_branches: ["develop", "main"]
```

### Path Instructions

```yaml
reviews:
  path_instructions:
    - path: "**/*.ts"
      instructions: "Focus on type safety and null checks"
    - path: "src/api/**"
      instructions: "Verify authentication and authorization"
```

### Tools Configuration

```yaml
reviews:
  tools:
    eslint:
      enabled: true
    gitleaks:
      enabled: true
    ruff:
      enabled: true
    golangci-lint:
      enabled: true
      config_file: ".golangci.yml"
```

### Pre-merge Checks

```yaml
reviews:
  pre_merge_checks:
    title:
      mode: warning # off, warning, error
    description:
      mode: warning
    docstrings:
      mode: warning
      threshold: 80
```

### Finishing Touches

```yaml
reviews:
  finishing_touches:
    docstrings:
      enabled: true
    unit_tests:
      enabled: true
```

## Labeling Configuration

```yaml
reviews:
  suggested_labels: true
  auto_apply_labels: false
  labeling_instructions:
    - label: "frontend"
      instructions: "Apply when PR contains React component changes"
    - label: "security"
      instructions: "Apply for auth, encryption, or sensitive data handling"
```

## Complete Example

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: en-US
tone_instructions: "Be direct. Focus on bugs and security issues."

reviews:
  profile: chill
  high_level_summary: true
  sequence_diagrams: true
  poem: false

  auto_review:
    enabled: true
    drafts: false
    ignore_title_keywords: ["WIP"]

  path_filters:
    - "!dist/**"
    - "!node_modules/**"
    - "!*.min.js"

  path_instructions:
    - path: "**/*.py"
      instructions: "Check for type hints and proper exception handling"

  tools:
    ruff:
      enabled: true
    gitleaks:
      enabled: true
    eslint:
      enabled: true
```
