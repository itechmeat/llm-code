# Advanced Features

Subtasks, new task attempts, and resolving rebase conflicts.

## Creating Subtasks

Break complex tasks into smaller pieces.

### How to Create

1. Open task attempt
2. Click triple dot icon (top right)
3. Select "Create Subtask"
4. Fill in title/description
5. Save

Subtask inherits base branch from parent attempt.

### Subtask Behavior

- Linked to **specific task attempt**, not just task
- Appears as regular task on kanban board
- Own lifecycle: To do → In Progress → In Review → Done
- Can have own attempts and agents
- Can create nested subtasks

### Viewing Relationships

**Parent task** shows:

- Child Tasks section with count
- Links to each subtask

**Subtask** shows:

- Parent Task section
- Link to parent
- Unlink action available when context allows (v0.1.7)

## New Task Attempts

Multiple attempts per task for fresh restarts.

### When to Create

- First approach didn't work
- Want different agent (Claude → Codex)
- Need different variant (DEFAULT → PLAN)
- Different base branch
- Reset conversation context

**Tip**: Most tasks need only one attempt.

### How to Create

1. Open task
2. Click triple dot icon
3. Select "Create New Attempt"
4. Configure agent, variant, branch
5. Click "Create Attempt"

### Impact on Subtasks

Subtasks linked to **original attempt** remain unchanged. New subtasks from new attempt use new attempt's branch.

## Resolving Rebase Conflicts

When your branch conflicts with target branch after rebase.

### Conflict Banner Options

| Option            | Action                               |
| ----------------- | ------------------------------------ |
| Resolve Conflicts | Auto-generate instructions for agent |
| Open in Editor    | Manually edit files                  |
| Abort Rebase      | Cancel, return to "Rebase needed"    |

### Automatic Resolution (Recommended)

1. Click "Resolve Conflicts"
2. Instructions generated in follow-up field
3. Review instructions
4. Click "Resolve Conflicts" (Send button changes)
5. Agent resolves conflicts

### Manual Resolution

**Single files**:

- Click "Open in Editor" from banner
- Edit one file at a time
- Refresh page for next file

**Multiple files** (recommended):

- Click triple dot → "Open in [Your IDE]"
- Opens entire worktree
- Resolve all conflicts
- Run:

```bash
git add .
git rebase --continue
```

### Merge Markers

```
<<<<<<< HEAD (your changes)
function newFeature() {
  return "new implementation";
}
=======
function oldFeature() {
  return "existing implementation";
}
>>>>>>> main (base branch changes)
```

### Rebasing onto Different Branch

If task was created from wrong branch:

1. Change base branch in task settings
2. See commits from old branch that shouldn't be there
3. Use:

```bash
git rebase <last-commit-before-your-work> --onto <new-base>
```

**Warning**: Identify correct commit hash. Consider backup branch first.

### Aborting

Click "Abort Rebase" to return to "Rebase needed" state. Can try again or create new attempt from updated branch.
