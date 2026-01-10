# Git Platform Integration

CodeRabbit integrates with major Git platforms for PR-based code reviews.

## Supported Platforms

| Platform     | Variants                                        |
| ------------ | ----------------------------------------------- |
| GitHub       | github.com, Enterprise Cloud, Enterprise Server |
| GitLab       | gitlab.com, Self-Managed                        |
| Azure DevOps | Azure DevOps Services                           |
| Bitbucket    | Cloud, Server                                   |

## Integration Process

1. **Authenticate** — Log in to CodeRabbit with Git platform credentials
2. **Add organizations** — Connect organizations/groups/workspaces
3. **Configure service account** — Create dedicated CodeRabbit account (auto on GitHub.com)
4. **Grant permissions** — Authorize specific repositories

## Platform Terminology

| Concept      | GitHub            | GitLab                    | Bitbucket         |
| ------------ | ----------------- | ------------------------- | ----------------- |
| Organization | organization      | group                     | workspace         |
| Pull Request | pull request      | merge request             | pull request      |
| Permissions  | Repository access | Developer/Maintainer role | Repository access |

## Permission Requirements

### GitHub

- Ownership-level permissions for organizations
- Repository read/write access

### GitLab

- Developer role in primary group to view repositories
- Maintainer role in primary group to enable toggle

### Azure DevOps

- Project-level permissions

### Bitbucket

- Workspace admin for organization setup
- Repository write access

## Enterprise / Self-Hosted

For organizations with 500+ users:

- Self-hosted CodeRabbit deployment available
- Contact CodeRabbit Sales for enterprise options

## Issue Tracker Integration

CodeRabbit connects with issue management for ticket creation:

| Platform      | Status    |
| ------------- | --------- |
| GitHub Issues | Supported |
| GitLab Issues | Supported |
| Jira          | Supported |
| Linear        | Supported |
