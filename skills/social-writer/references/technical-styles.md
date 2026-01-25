# Technical Writing Styles

Deep technical blog writing inspired by Karpathy and thought-leader patterns.

---

## Karpathy Style

Andrej Karpathy's approach: patience, clarity, genuine curiosity.

### Philosophy

| Principle         | What It Means                              |
| ----------------- | ------------------------------------------ |
| Start simple      | "Train a tiny model first"                 |
| Look at data      | Become one with actual inputs/outputs      |
| Embrace imperfect | "Don't be a hero" trying perfect solutions |
| Learn by doing    | Fail fast, get hands dirty                 |
| Humility          | "Don't trust authority, trust experiments" |

### Voice Characteristics

- **Conversational:** Like a friend explaining, not a textbook
- **First-person:** "I", "you", direct address
- **Pragmatic:** Tips that worked in practice
- **Honest:** Admits confusion, mistakes, limitations
- **Playful:** Occasional humor, doesn't take self too seriously
- **Technical but accessible:** Deep expertise, simple language

### Common Patterns

**Personal hook:**
"I've spent the last month debugging this and..."

**Intriguing premise:**
"Turns out the entire field had this backwards."

**Leaky abstraction reveal:**
"Under the hood, it's actually just [simple thing]."

**Numbered recipe:**
"Here's the 5-step process that actually works..."

**Progressive disclosure:**
Simple version first → add complexity layer by layer.

### Signature Expressions

- "Don't be a hero"
- "Become one with the data"
- "Train the tiny model first"
- "The most dangerous thing is [X]"
- "It's really just [simple explanation]"

---

## Deep Technical Style

Thought-leadership patterns for technical authority posts.

### Opening Strategies

| Strategy              | Example                                     |
| --------------------- | ------------------------------------------- |
| Contrarian position   | "Everyone uses X. That's the problem."      |
| Practical pain        | "After 6 months, the pattern broke."        |
| Challenge convention  | "The 'best practice' is making you slower." |
| Reframe               | "LLMs aren't AI. They're compression."      |
| Philosophical         | "What does 'understanding' even mean?"      |
| Surprising simplicity | "The fix was 3 lines of code."              |
| Historical hook       | "In 2019, this was impossible. Now..."      |

### Argumentative Structures

**Problem → Evidence → Redefinition:**

1. State the obvious approach
2. Show why it fails (with evidence)
3. Propose new framing

**De-scoping narrative:**

1. What everyone thinks the problem is
2. What the ACTUAL problem is (smaller/different)
3. Simple solution that emerges

**Numbered framework:**

1. Name it (memorable term)
2. Break into 3-5 components
3. Each component = clear action

**Thought experiment:**
"Imagine if [X]. What changes?"

### Rhetorical Techniques

**Authority leverage:**
"After shipping 50 agents..." (credentials prove context)

**Metaphors that demystify:**
"RAG is just ctrl+F with extra steps"

**Direct reader address:**
"You've probably tried this. Here's why it fails."

**Emphatic repetition:**
"Simple. Specific. Short." (rule of three)

---

## Recurring Themes

### Domain > Technical

Domain expertise beats technical understanding.

"You don't need to understand transformers to build great AI products. You need to understand your users."

### Embrace Black Box

Stop trying to explain everything. Use what works.

"The model is a black box. That's fine. Your users are too."

### Simplicity > Complexity

The elegant solution is usually simpler.

"If it needs a 20-page doc to explain, you haven't found the solution yet."

---

## Combining Styles

| Format          | Style Mix                          |
| --------------- | ---------------------------------- |
| X post          | Style guide + hooks                |
| X thread        | Karpathy (progressive disclosure)  |
| LinkedIn        | Deep technical + professional tone |
| Blog intro      | Karpathy (personal hook)           |
| Technical essay | Deep technical throughout          |

### Example: Karpathy-Style X Thread

**Hook (contrarian):**
"Everyone's building AI agents wrong."

**Setup (personal):**
"I've shipped 12 this year. 9 failed."

**Reveal (pattern):**
"The 3 that worked had ONE thing in common:"

**Body (numbered):**
"1/ Tiny scope
2/ Human fallback
3/ No memory"

**Close (simple):**
"That's it. Start there."

### Example: Deep Technical LinkedIn Post

**Hook (reframe):**
"RAG isn't about retrieval. It's about relevance."

**Problem:**
"Most implementations chunk docs and hope for the best."

**Evidence:**
"We tested 8 chunking strategies. Winner wasn't the smartest."

**Insight:**
"Smaller chunks + metadata beats large chunks + embeddings."

**Framework:**
"The 3-R approach: Relevance > Retrieval > Ranking"

**CTA:**
"How are you handling chunk strategy?"

---

## Quality Checklist

Before publishing technical content:

- [ ] Does it open with a hook, not context?
- [ ] Is there ONE clear insight?
- [ ] Did I show evidence, not just claim?
- [ ] Would Karpathy's "don't be a hero" apply?
- [ ] Is the language simple enough?
- [ ] Do I sound like a person, not a paper?
- [ ] Is there a framework or takeaway?

---

## Quick Reference

| Style          | Best For                    | Key Feature                      |
| -------------- | --------------------------- | -------------------------------- |
| Karpathy       | Tutorials, learnings        | Progressive disclosure, humility |
| Deep Technical | Authority posts, frameworks | Contrarian hooks, evidence       |
| Combined       | Threads, essays             | Hook from one, body from other   |

**The essence:** Start simple, show your work, challenge assumptions, stay humble.
