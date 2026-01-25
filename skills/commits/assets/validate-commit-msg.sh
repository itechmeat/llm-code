#!/usr/bin/env bash
# validate-commit-msg.sh - Validate commit message against Conventional Commits
#
# Usage:
#   ./validate-commit-msg.sh "feat(auth): add login"
#   ./validate-commit-msg.sh < .git/COMMIT_EDITMSG
#   echo "fix: bug" | ./validate-commit-msg.sh
#
# Exit codes:
#   0 - Valid commit message
#   1 - Invalid commit message

set -euo pipefail

# Read commit message from argument or stdin
if [[ $# -gt 0 ]]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG=$(cat)
fi

# Get first line (subject)
SUBJECT=$(echo "$COMMIT_MSG" | head -n1)

# Conventional Commits pattern
# type(scope)!: description
# type!: description
# type(scope): description
# type: description
PATTERN='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_-]+\))?(!)?: .+$'

# Check if subject matches pattern
if [[ ! "$SUBJECT" =~ $PATTERN ]]; then
    echo "ERROR: Invalid commit message format" >&2
    echo "" >&2
    echo "Subject: $SUBJECT" >&2
    echo "" >&2
    echo "Expected format: <type>(<scope>): <description>" >&2
    echo "" >&2
    echo "Valid types:" >&2
    echo "  feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  feat: add user authentication" >&2
    echo "  fix(parser): handle empty arrays" >&2
    echo "  feat!: breaking change" >&2
    echo "  feat(api)!: breaking API change" >&2
    echo "" >&2
    echo "See: https://www.conventionalcommits.org/" >&2
    exit 1
fi

# Check subject length (50 chars recommended, 72 max)
SUBJECT_LENGTH=${#SUBJECT}
if [[ $SUBJECT_LENGTH -gt 72 ]]; then
    echo "WARNING: Subject line is $SUBJECT_LENGTH characters (max 72 recommended)" >&2
fi

# Check for period at end of subject
if [[ "$SUBJECT" =~ \\.$ ]]; then
    echo "WARNING: Subject line should not end with a period" >&2
fi

# Check for BREAKING CHANGE in body/footer
if echo "$COMMIT_MSG" | grep -q "^BREAKING CHANGE:"; then
    echo "INFO: Breaking change detected in footer" >&2
fi

echo "OK: Valid commit message" >&2
exit 0
