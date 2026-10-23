---
name: review-pr
description: Handle PR feedback — review comments, make changes, and respond to reviewers. Use when the user shares a PR URL or says to address/handle PR feedback, review comments, or reviewer suggestions.
---

# PR Feedback Handler

You are handling reviewer feedback on a pull request. This is a two-phase workflow:

**Phase 1 (automatic):** Review comments, check CI, evaluate critically, make local changes, report back.
**Phase 2 (on user request):** Commit, push, respond to comments, resolve threads.

Use `gh` CLI for all GitHub interactions — it's faster than MCP tools. Only fall back to MCP tools if `gh` can't do something.

---

## Phase 1: Review & Fix

### Step 1 — Parse the PR reference

Extract owner, repo, and PR number from the PR reference the user gave. Accepted formats:
- `https://github.com/owner/repo/pull/123`
- `owner/repo#123`
- `#123` (infer owner/repo from the current git remote)

### Step 2 — Get PR details and checkout the branch

1. Get PR metadata:
   ```bash
   gh pr view <number> -R <owner>/<repo> --json headRefName,baseRefName,title,state,statusCheckRollup
   ```
2. Fetch and checkout the PR's head branch locally:
   ```bash
   git fetch origin <head-branch>
   git checkout <head-branch>
   ```

### Step 3 — Read all review comments

Fetch review threads via GraphQL (gives thread IDs needed for resolving, plus inline code context):

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            isOutdated
            comments(first: 50) {
              nodes {
                id
                databaseId
                author { login }
                body
                path
                line
                createdAt
              }
            }
          }
        }
      }
    }
  }
' -F owner=<owner> -F repo=<repo> -F number=<number>
```

Also check for top-level PR comments (non-inline feedback):
```bash
gh pr view <number> -R <owner>/<repo> --json comments --jq '.comments[] | {id: .id, author: .author.login, body: .body}'
```

For each thread, note:
- The thread node ID (`PRRT_...` — for resolving later)
- The first comment's `databaseId` (integer — for replying later)
- Whether it's already resolved or outdated
- The file, line, and content of the feedback

**Skip** threads that are already resolved — don't re-address old feedback.

### Step 4 — Check CI status

Check for failing CI checks:
```bash
gh pr checks <number> -R <owner>/<repo>
```

If any checks are failing:
1. Identify which checks failed and read the logs:
   ```bash
   gh run view <run-id> -R <owner>/<repo> --log-failed
   ```
2. Determine if the failures are related to the PR changes or are pre-existing/flaky.
3. If they're related to the PR changes, fix them alongside the review feedback.
4. If they're pre-existing or flaky, note them in the report but don't try to fix them.

### Step 5 — Evaluate feedback critically

For each unresolved comment, think through:
- **Does this feedback make sense?** Is the reviewer correct? Is there a reason the code was written this way?
- **Is this a real issue or a style preference?** Substantive bugs and correctness issues always get fixed. Style preferences get fixed too unless there's a strong reason not to.
- **Is the suggested fix the right fix?** Sometimes reviewers identify a real problem but suggest the wrong solution. Fix the problem, not necessarily the exact suggestion.
- **Are there related issues nearby?** If a reviewer points out a problem in one place, check if the same pattern exists elsewhere in your changes.

### Step 6 — Make changes

Read the relevant files and make the changes. Be thorough — address every actionable comment and every fixable CI failure.

### Step 7 — Report back

Present a summary to the user:

```
## PR Feedback Summary: <PR title>

### Changes made
- <file>: <what changed and why, referencing the reviewer's comment>
- ...

### CI fixes
- <what was failing and how it was fixed>
- (or "All checks passing" / "Failures are pre-existing: <details>")

### Discussion points
- <any comment where you disagree with the reviewer, or where the right approach is ambiguous — explain your reasoning>

### Not addressed
- <any comment that was already resolved, not actionable, or that you think is incorrect — explain why>
```

If there are discussion points, **wait for the user's input** before proceeding. If everything is straightforward, say so and wait for the user to tell you to commit.

**STOP HERE.** Do not commit, push, or respond to comments until the user explicitly asks.

---

## Phase 2: Ship & Respond

Only proceed here when the user says to commit/push/ship the changes.

### Step 1 — Commit and push

1. Stage the changed files (be specific — don't `git add -A`).
2. Commit with a message following the repo's commit conventions (check CLAUDE.md if present). The message should reference the review, e.g.: `fix: address review feedback — <concise summary>`.
3. Push to the PR branch: `git push origin <head-branch>`.
4. Capture the commit SHA from the push output or `git rev-parse HEAD`.

### Step 2 — Respond to each comment

For every unresolved review comment that was addressed:

1. Reply to the comment using `gh api`:
   ```bash
   gh api repos/<owner>/<repo>/pulls/<number>/comments/<comment-databaseId>/replies \
     -f body='Addressed in <commit-sha>.'
   ```
   The reply should:
   - Be concise and professional
   - Confirm the feedback was incorporated
   - Link to the commit SHA
   - If you deviated from the reviewer's exact suggestion, briefly explain what you did instead and why

2. Resolve the thread using GraphQL:
   ```bash
   gh api graphql -f query='
     mutation($threadId: ID!) {
       resolveReviewThread(input: {threadId: $threadId}) {
         thread { isResolved }
       }
     }
   ' -f threadId='<thread-node-id>'
   ```

For comments that were **not** addressed (discussed with user, disagreed, not actionable):
1. Reply explaining why — be respectful and specific.
2. Do **not** resolve the thread — leave it for the reviewer to resolve after reading the reply.

### Step 3 — Report

Tell the user:
- The commit SHA
- How many comments were addressed and resolved
- How many were replied to but left unresolved
- The PR URL for easy access

---

## Important rules

- **Never auto-commit.** Phase 2 only happens when the user explicitly asks.
- **Never fabricate commit SHAs.** Use the real SHA from `git rev-parse HEAD` after committing.
- **Be honest about disagreements.** If reviewer feedback doesn't make sense, say so in Phase 1 — don't silently skip it or blindly apply it.
- **Check for CLAUDE.md** in the repo root for commit conventions, code style, and other project-specific rules.
- **Respect the repo's existing patterns.** When making fixes, match the style of surrounding code.
