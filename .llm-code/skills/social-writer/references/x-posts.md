# X Single Posts

Structure, formats, and best practices for single X posts.

## Anatomy of a Post

### The Hook (Line 1)

**Hook IS the post.** You have ~1 second to stop the scroll.

Hook formulas:

- "How to [solve problem]"
- "Why [X] doesn't work"
- "[X] is [Y]"
- "Shipped [X]"
- "Here's what I learned:"

### The Body

- Short sentences (10-15 words max)
- One idea per line
- Line breaks for emphasis
- Specific > generic (names, numbers, tools)

### The Close (Optional)

- **70%**: Engagement question or teaser
- **30%**: Hard stop, let insight land

## Post Formats

### Project Update (~30% of posts)

**Pattern:** What + insight + why it matters

```
Shipped agents.foo curation v1 today.

Discovery is harder than I thought.

Apps are static, agents are conversations. Totally different UX problem.
```

### Learning Post (~30%)

**Pattern:** What you learned + specifics + context

```
Workflow DevKit handles durability that would take weeks to build manually.

Automatic retries, state persistence, observability built-in.

Ships with Next.js.
```

### Reaction Post (~25%)

**Pattern:** What's happening + your specific angle

```
Everyone's talking about [new release/announcement].

What excites me: [specific feature] makes it better for [your use case].

Changes the [workflow] completely.
```

### Insight Post (~15%)

**Pattern:** Observation + tension/twist

```
The best products are simple.

But getting to simple is incredibly complex.

Most teams stop at complicated.
```

## High-Performing Patterns

### Pattern 1: "Shipped X, Learned Y"

```
Shipped curation v1 for agents.foo today.

Discovery is way harder than app stores.
Agents are conversations, not feature lists.

Rebuilt discovery around context matching instead.
```

### Pattern 2: "Here's What I Learned"

```
Agent discovery is fundamentally different from app discovery.

Apps are static—search features, read descriptions, install.

Agents are conversations. You can't describe all possible conversations.

The UX isn't search. It's contextual matching.
```

### Pattern 3: "How to Do X"

```
How to maintain voice at scale with AI:

- Set up quality gates before shipping
- Use custom style guides, not generic prompts
- Review first 50 outputs manually to tune
- Monitor consistency metrics weekly

Speed means nothing if your voice disappears.
```

### Pattern 4: Problem → Solution

```
Problem: Can't describe agent conversations like app features.

First try: Traditional search. Failed—keywords don't capture conversational capability.

What worked: Context matching based on what the agent does in conversation.

Discovery UX follows the product paradigm.
```

### Pattern 5: Tool Recommendation

```
Workflow DevKit handles agent durability automatically.

Built-in retries, state persistence, observability.
Would take weeks to build.

Using it for all agents.foo workflows. Saved ~3 weeks dev time.
```

## Formatting Rules

| Element    | Rule                                |
| ---------- | ----------------------------------- |
| Length     | 230-280 chars (use available space) |
| Paragraphs | Line breaks for emphasis            |
| Opening    | Hook = first line                   |
| Tone       | Direct, confident, specific         |
| Voice      | First-person, present tense         |
| Language   | Simple, conversational, concrete    |

**Length Rule:** Aim to use most of the 280 character limit. Short tweets (under 180 chars) waste opportunity to add context, details, or specifics. If you have 50+ chars remaining, add more value.

## @Mentions as Names

When mentioning a product/tool/company, use the @mention instead of repeating the name.

**❌ Redundant:**

```
skill: product @product_handle
Working with product @product_official
```

**✅ Clean:**

```
skill: @product_handle
Working with @product_official
```

The @mention IS the name. Don't duplicate.

**Exception:** When the handle differs significantly from the product name, you may need both for clarity.

## What to Include

- **Tools you use:** Name specific tools via @mentions
- **Numbers that prove:** Time saved, metrics, engagement data
- **Real projects:** Specificity builds credibility
- **Genuine surprise:** "Wild." "Pretty cool."

## What to Avoid

### Never Say

- "Game-changer" / "Revolutionary" / "Unlock"
- "Dive in" / "Deep dive"
- "Thoughts?" (too generic)
- "Hot take:" / "Unpopular opinion:" (just state it)
- "Let that sink in"
- Excessive emojis (0-1 max)

### Don't

- Hype your own stuff excessively
- Share without adding your angle
- Apologize for posting
- Post generic motivational quotes

## Pre-Post Checklist

- [ ] Did I get to the point in line 1?
- [ ] Is this specific? (names, numbers, examples)
- [ ] Am I using most of the 280 char limit? (230+ chars)
- [ ] Would I actually say this out loud?
- [ ] Does it sound like a person, not AI?
- [ ] Zero banned phrases?
- [ ] If it's a reaction, did I add MY angle?

## Example Transformations

**✗ Bad:**

```
Just shipped something cool! Really excited about this game-changing feature.
It's going to revolutionize how we think about discovery. Thoughts?
```

**✓ Good:**

```
Shipped agents.foo curation v1 today.

Discovery is the hardest part.
Agents aren't apps—they're conversations.

Traditional app store UX doesn't work here.
```
