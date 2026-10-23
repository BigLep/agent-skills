---
name: incorporate-pr-comments
description: Handle reviewer feedback on a GitHub pull request. Fetch review comments and CI status, evaluate each comment critically, make the code changes, then (after the user approves) commit, push, reply to each comment, and resolve threads. Use when the user shares a PR URL or says to address, handle, or incorporate PR feedback, review comments, or reviewer suggestions.
---

# Incorporate PR Comments

You are handling reviewer feedback on a pull request in two phases:

- **Phase 1 (automatic):** read comments, check CI, evaluate critically, make local changes, draft replies, report back.
- **Phase 2 (after the user approves):** commit, push, post replies, resolve threads.

Stop between the phases by default. Commits, pushes, and replies are visible to other people, and replies are posted as the user. Run both phases in one pass only when the user explicitly asks for that (for example "incorporate and ship it", "do it end to end", "no need to check with me").

Use the `gh` CLI for all GitHub interactions.

---

## Phase 1: Review and fix

### Step 1: Parse the PR reference

Extract owner, repo, and PR number from the PR reference the user gave. Accepted formats:
- `https://github.com/owner/repo/pull/123`
- `owner/repo#123`
- `#123` or just a number (infer owner/repo from the current git remote)

### Step 2: Get PR details and check out the branch

```bash
gh pr view <number> -R <owner>/<repo> --json headRefName,baseRefName,title,state,url
```

Fetch and check out the head branch:
```bash
git fetch origin <head-branch>
git checkout <head-branch>
```

If the working tree has uncommitted changes, stop and ask before switching branches.

### Step 3: Fetch all comments

Fetch review threads via GraphQL. This gives the thread IDs needed for resolving and the comment IDs needed for replying:

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

Also fetch top-level PR comments (feedback not attached to a line):
```bash
gh api repos/<owner>/<repo>/issues/<number>/comments \
  --jq '.[] | {id, body, user: .user.login}'
```

**Do not use `gh pr view --comments`**; its pagination and formatting are unreliable for programmatic use.

For each thread, note:
- The thread node ID (`PRRT_...`), for resolving later
- The first comment's `databaseId` (integer), for replying later
- Whether it is resolved or outdated
- The file, line, and content of the feedback

**Skip** threads that are already resolved.

### Step 4: Check CI status

```bash
gh pr checks <number> -R <owner>/<repo>
```

If any checks are failing:
1. Read the failed logs: `gh run view <run-id> -R <owner>/<repo> --log-failed`
2. Decide whether each failure is caused by the PR or is pre-existing/flaky.
3. Fix failures caused by the PR alongside the review feedback.
4. Note pre-existing or flaky failures in the report; do not try to fix them.

### Step 5: Evaluate each comment critically

For each unresolved comment:
1. **Read the relevant file and surrounding context** before deciding anything.
2. **Be opinionated.** Do not blindly accept every suggestion. Ask whether the reviewer is correct, and whether there is a reason the code was written this way.
3. **Accept** comments that fix genuine issues: correctness bugs, clarity improvements, consistency problems.
4. **Fix the problem, not necessarily the suggestion.** Reviewers sometimes spot a real issue but propose the wrong fix.
5. **Push back** on subjective preferences or changes that would make things worse.
6. **Skip** bot comments that are purely informational (CI status, manifest diffs, automated summaries).
7. **Check for patterns.** If a reviewer flags an issue in one place, check whether it recurs elsewhere in the PR.

### Step 6: Make changes

Read each file before editing it. Make targeted edits for the accepted feedback and the fixable CI failures, and match the style of the surrounding code.

### Step 7: Report and draft replies

Present a summary, including the exact reply you plan to post on each thread:

```
## PR Feedback: <PR title>

### Changes made
- <file>: <what changed and why, referencing the reviewer's comment>

### CI
- <what was failing and how it was fixed>, or "All checks passing", or "Pre-existing failures: <details>"

### Discussion points
- <comments you disagree with, or where the right approach is ambiguous, with your reasoning>

### Not addressed
- <comments skipped (resolved, bot, not actionable) and why>

### Draft replies
- <reviewer> on <file>:<line>: "<reply text>" (resolve: yes/no)
```

**Stop here** unless the user asked for a single pass. Wait for the user to settle any discussion points and to approve committing, pushing, and the draft replies.

---

## Phase 2: Ship and respond

### Step 1: Commit and push

1. Stage the specific changed files (do not use `git add -A` or `git add .`).
2. Commit following the repo's conventions (check `AGENTS.md` or `CLAUDE.md` at the repo root, and recent `git log`). Reference the review, for example `fix: address review feedback (<concise summary>)`. Add any attribution trailer your environment requires.
3. Push to the PR branch: `git push origin <head-branch>`
4. Capture the real commit SHA with `git rev-parse HEAD`. **Never fabricate a commit SHA.**

### Step 2: Reply to each comment

Post the approved replies. For inline review comments:

```bash
gh api repos/<owner>/<repo>/pulls/<number>/comments/<comment-databaseId>/replies \
  -f body='Addressed in <commit-sha>.'
```

The reply endpoint is `/comments/{comment_id}/replies`, using the first comment's `databaseId`.

Replies should be concise and professional. For addressed comments, confirm the change and cite the SHA; if you deviated from the reviewer's exact suggestion, say briefly what you did instead and why. For comments you disagree with, explain your reasoning specifically and respectfully.

### Step 3: Resolve threads

Resolve threads whose feedback has been **fully addressed**:

```bash
gh api graphql -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: {threadId: $threadId}) {
      thread { isResolved }
    }
  }
' -f threadId='<thread-node-id>'
```

Multiple threads can be resolved in one mutation:

```bash
gh api graphql -f query='
mutation {
  t1: resolveReviewThread(input: {threadId: "PRRT_abc"}) { thread { isResolved } }
  t2: resolveReviewThread(input: {threadId: "PRRT_def"}) { thread { isResolved } }
}'
```

**Do not resolve a thread if:**
- It asks a question that needs the reviewer's input
- You disagreed and the reviewer should read your response first
- The change needs discussion or a decision from the team

### Step 4: Report

Tell the user:
- The commit SHA
- How many comments were addressed and resolved
- How many were replied to but left unresolved, and why
- The PR URL

---

## Important rules

- **Stop after Phase 1 by default.** Commit, push, reply, and resolve only after the user approves, unless they asked for a single pass.
- **Never fabricate commit SHAs.** Use the real SHA from `git rev-parse HEAD`.
- **Be honest about disagreements.** Raise them in the Phase 1 report; do not silently skip or blindly apply feedback.
- **Follow project instructions** in `AGENTS.md` or `CLAUDE.md` for commit conventions and code style.
- **Respect the repo's existing patterns.** Match the style of surrounding code.
