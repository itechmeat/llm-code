# Supported Tools Reference

CodeRabbit integrates with 40+ static analysis tools, linters, and security scanners.

## Configuration

Enable/disable tools in `.coderabbit.yaml`:

```yaml
reviews:
  tools:
    eslint:
      enabled: true
    gitleaks:
      enabled: true
```

## Tools by Category

### JavaScript/TypeScript

| Tool   | Version | Description                            |
| ------ | ------- | -------------------------------------- |
| ESLint | latest  | Static analysis for JavaScript         |
| Biome  | v2.1.2  | Fast formatter/linter for web projects |
| Oxlint | v1.28.0 | Rust-based JS/TS linter                |

### Stylesheets

| Tool      | Version | Description                          |
| --------- | ------- | ------------------------------------ |
| Stylelint | v17.2.0 | Linter for CSS, SCSS, Sass, and Less |

### Python

| Tool   | Version | Description                      |
| ------ | ------- | -------------------------------- |
| Ruff   | v0.14.5 | Fast Python linter and formatter |
| Flake8 | v7.3.0  | PyFlakes + pycodestyle + McCabe  |
| Pylint | v4.0.3  | Static code analysis             |

### Go

| Tool          | Version | Description                |
| ------------- | ------- | -------------------------- |
| golangci-lint | v2.5.0  | Fast linters runner for Go |

### Ruby

| Tool     | Version | Description                   |
| -------- | ------- | ----------------------------- |
| RuboCop  | v1.81.7 | Static analyzer and formatter |
| Brakeman | v7.1.1  | Security scanner for Rails    |

### PHP

| Tool            | Version | Description                       |
| --------------- | ------- | --------------------------------- |
| PHPStan         | v2.1.32 | Static analysis (requires config) |
| PHPMD           | v2.15.0 | Mess detector                     |
| PHP CodeSniffer | v3.7.2  | Coding standard checker           |

### Rust

| Tool   | Version | Description              |
| ------ | ------- | ------------------------ |
| Clippy | latest  | Lint collection for Rust |

### Kotlin/Java

| Tool   | Version | Description                         |
| ------ | ------- | ----------------------------------- |
| detekt | v1.23.8 | Static analysis for Kotlin          |
| PMD    | v7.18.0 | Multilanguage analyzer (Java focus) |

### C/C++

| Tool     | Version | Description     |
| -------- | ------- | --------------- |
| Clang    | v14.0.6 | Static analysis |
| Cppcheck | v2.18.0 | Static analysis |

### Swift

| Tool      | Version | Description  |
| --------- | ------- | ------------ |
| SwiftLint | v0.57.0 | Swift linter |

### Shell

| Tool       | Version | Description           |
| ---------- | ------- | --------------------- |
| ShellCheck | v0.11.0 | Shell script analyzer |

### SQL

| Tool     | Version | Description                 |
| -------- | ------- | --------------------------- |
| SQLFluff | v3.5.0  | Dialect-flexible SQL linter |

### Infrastructure

| Tool       | Version    | Description                        |
| ---------- | ---------- | ---------------------------------- |
| Checkov    | v3.2.334   | IaC security scanner               |
| Hadolint   | v2.14.0    | Dockerfile linter                  |
| Trivy      | latest     | IaC security scanner (config mode) |
| TFLint     | latest     | Terraform linter                   |
| actionlint | v1.7.8     | GitHub Actions checker             |
| CircleCI   | v0.1.33494 | CircleCI config checker            |
| YAMLlint   | v1.37.1    | YAML linter                        |

### Security

| Tool        | Version  | Description                      |
| ----------- | -------- | -------------------------------- |
| Gitleaks    | v8.29.0  | Secret scanner                   |
| TruffleHog  | v3.92.0  | Secret scanner with verification |
| OpenGrep    | v1.16.0  | Semgrep-compatible code scanning |
| Semgrep     | v1.143.0 | Security vulnerability scanner   |
| OSV Scanner | v2.2.4   | Package vulnerability scanner    |

### Documentation

| Tool         | Version | Description                           |
| ------------ | ------- | ------------------------------------- |
| LanguageTool | latest  | Grammar/style checker (30+ languages) |
| markdownlint | v0.18.1 | Markdown standards                    |

### Other

| Tool                | Version | Description           |
| ------------------- | ------- | --------------------- |
| ast-grep            | v0.40.0 | AST pattern matching  |
| HTMLHint            | v1.7.1  | HTML analyzer         |
| Prisma Lint         | v0.11.0 | Prisma schema linter  |
| checkmake           | v0.2.2  | Makefile linter       |
| dotenv-linter       | v4.0.0  | .env file checker     |
| Buf                 | v1.60.0 | Protobuf linter       |
| Regal               | v0.37.0 | Rego linter           |
| Luacheck            | v1.2.0  | Lua linter            |
| Shopify Theme Check | v3.58.2 | Liquid best practices |
| Fortitude           | v0.7.5  | Fortran linter        |
| Blinter             | latest  | Windows batch linter  |

## Tools with Config File Support

Some tools accept custom configuration paths:

```yaml
reviews:
  tools:
    golangci-lint:
      enabled: true
      config_file: ".golangci.yml"
    detekt:
      enabled: true
      config_file: "detekt.yml"
    semgrep:
      enabled: true
      config_file: ".semgrep.yml"
    swiftlint:
      enabled: true
      config_file: ".swiftlint.yml"
    pmd:
      enabled: true
      config_file: "ruleset.xml"
```

## PHPStan Level Configuration

```yaml
reviews:
  tools:
    phpstan:
      enabled: true
      level: "max" # 0-9 or "max"
```

## LanguageTool Configuration

```yaml
reviews:
  tools:
    languagetool:
      enabled: true
      level: "picky" # default or picky
      enabled_rules: []
      disabled_rules: []
```

## GitHub Checks Integration

```yaml
reviews:
  tools:
    github-checks:
      enabled: true
      timeout_ms: 90000 # Max 900000 (15 min)
```
