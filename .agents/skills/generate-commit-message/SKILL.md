---
name: generate-commit-message
description: This skill generates a commit message based on your changes and recent sessions.
---

- This skill generates a commit message that summarizes the most recent changes - if there are staged changes, summarize just those changes, otherwise summarize the unstaged changes.

# Sources

- `git --no-pager diff` to get the complete diff
  - Deeply analyze the diff to understand what changes were made, including added, modified, and deleted lines of code. But try to summarize the changes in a concise way, focusing on the most important aspects of the changes.
  - Also read the entire contents of the files that were changed to understand the context of the changes and how they fit into the full context of those files and the entire codebase.

- Recent Session information for context on what the changes are about. Restrict this information to queries that are relevant to the changes being made.

# What to flag and not generate a commit message

- Sometimes if there are bad changes, you may want to flag them and not generate a commit message.
- If there are a lot of changes flag the commit message as "Too many changes to summarize" and do not generate a commit message. Recommend breaking the changes into smaller commits.
