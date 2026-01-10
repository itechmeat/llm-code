# CodeRabbit configuration (.coderabbit.yaml)

CodeRabbit can be configured via a `.coderabbit.yaml` file in the repository root.

## Typical configuration knobs

- Review style/tone (to reduce nits and focus on correctness).
- Auto-review settings for pull requests.
- Knowledge base / guidelines sources (team standards).

## Minimal example

```yaml
# yaml-language-server: $schema=https://coderabbit.ai/integrations/schema.v2.json
language: en-US

tone_instructions: "Be concise and focus on critical issues only"

reviews:
  profile: chill
  high_level_summary: true
```

## Notes for portable usage

- Keep configuration focused on outcomes (security, correctness, reliability).
- Avoid project-specific secrets or internal URLs.
