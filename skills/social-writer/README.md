# Social Writer

Agent skill for creating high-engagement social media content across platforms.

## Overview

This skill helps AI agents write effective social media posts for X (primary), LinkedIn, Threads, Instagram, and Facebook. It emphasizes human-sounding writing, avoiding AI patterns, and platform-specific optimization.

## Quick Start

```
# For X (priority platform)
→ references/x-posts.md      # Single post structure
→ references/x-threads.md    # Thread frameworks
→ references/hooks.md        # Hook patterns

# For other platforms
→ references/linkedin.md     # Professional content
→ references/threads-instagram.md  # Meta platforms
→ references/facebook.md     # Facebook guidelines

# Quality essentials
→ references/ai-avoidance.md # Critical - avoid AI patterns
→ references/style-guide.md  # Voice and tone
```

## Files

### Main

- `SKILL.md` - Entry point and router

### References

| File                   | Purpose                            |
| ---------------------- | ---------------------------------- |
| `x-posts.md`           | X single post guidelines   |
| `x-threads.md`         | Thread frameworks and structure    |
| `x-strategy.md`        | Content selection strategy         |
| `hooks.md`             | Hook patterns catalog              |
| `linkedin.md`          | LinkedIn professional content      |
| `threads-instagram.md` | Threads and Instagram              |
| `facebook.md`          | Facebook best practices            |
| `ai-avoidance.md`      | AI patterns to avoid               |
| `style-guide.md`       | Voice, tone, formatting            |
| `technical-styles.md`  | Karpathy and deep technical styles |

### Assets

| File                    | Purpose              |
| ----------------------- | -------------------- |
| `platform-templates.md` | Quick-copy templates |

### Scripts

| File                 | Purpose                              |
| -------------------- | ------------------------------------ |
| `tweet_validator.py` | Validate tweet length (280 char max) |

## Script Usage

### tweet_validator.py

Validates markdown files with tweets against X's 280 character limit.

```bash
python scripts/tweet_validator.py path/to/tweets.md
```

Expected markdown format:

```markdown
## Main Tweet

Your tweet content here.

---

## Reply 1: Name

Reply content here.

---
```

Output:

```
✅ Main Tweet: 233 chars (47 remaining)
✅ Reply 1: Name: 227 chars (53 remaining)
❌ Reply 2: Name: 295 chars (+15 over limit)
```

## Usage

### Basic Workflow

1. **Determine platform** → Route to platform reference
2. **Check hooks** → Strong opening (hooks.md)
3. **Write content** → Follow platform guide
4. **Verify quality** → ai-avoidance.md checklist
5. **Final check** → style-guide.md voice checklist

### Platform Priority

1. **X** - Primary focus, most detailed guides
2. **LinkedIn** - Professional audience
3. **Threads** - Casual, conversational
4. **Instagram** - Visual-first
5. **Facebook** - Community engagement

## Key Principles

1. **Hook first** - First line IS the post
2. **Specific > generic** - Numbers, names, examples
3. **Human voice** - Sounds like a person talking
4. **No AI patterns** - Avoid banned words/phrases
5. **Platform-native** - Adapt to each platform's culture

## Related Skills

- `content-writer` - Long-form content
- `x-writing` - X-specific (merged into this skill)

## Source

Consolidated from 7 source skills:

- content-writer
- social-media
- social-media-generator
- social-media-post
- x-thread
- writing-x-posts
- x-writing
