---
name: incorporate-pr-comments
description: Fetch PR review comments, evaluate them critically, make code changes, commit, push, reply to each comment, and resolve threads. A single-pass workflow that handles everything end-to-end.
---

# Incorporate PR Comments

You are incorporating reviewer feedback on a pull request in a single pass: fetch comments, evaluate, fix, commit, push, reply, and resolve.

Use `gh` CLI for all GitHub interactions.

---

## Step 1 — Parse the PR reference

Extract owner, repo, and PR number from the PR reference the user gave. Accepted formats:
- `https://github.com/owner/repo/pull/123`
- `owner/repo#123`
- `#123` or just a number (infer owner/repo from the current git remote)

## Step 2 — Checkout the PR branch

```bash
gh pr view <number> -R <owner>/<repo> --json headRefName,baseRefName,title,state
```

Fetch and checkout the head branch:
```bash
git fetch origin <head-branch>
git checkout <head-branch>
```

## Step 3 — Fetch all comments

Use **both** of these API calls to get the full picture:

```bash
# Inline review comments (code-level)
gh api repos/<owner>/<repo>/pulls/<number>/comments \
  --jq '.[] | {id, path, line, body, user: .user.login, in_reply_to_id}'

# Issue-level comments (top-of-PR)
gh api repos/<owner>/<repo>/issues/<number>/comments \
  --jq '.[] | {id, body, user: .user.login}'
```

**Do NOT use `gh pr view --comments`** — it has issues with pagination and formatting for programmatic use.

Also fetch review thread metadata via GraphQL (needed for resolving later):

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
              }
            }
          }
        }
      }
    }
  }
' -F owner=<owner> -F repo=<repo> -F number=<number>
```

For each thread, note:
- The thread node ID (`PRRT_...`) for resolving later
- The first comment's `databaseId` (integer) for replying later
- Whether it's already resolved or outdated

**Skip** threads that are already resolved.

## Step 4 — Evaluate each comment critically

For each unresolved comment:
1. **Read the relevant file and surrounding context** before deciding anything.
2. **Be opinionated.** Do not blindly accept every suggestion.
3. **Accept** comments that fix genuine issues: correctness bugs, clarity improvements, consistency problems.
4. **Push back** on comments that are subjective style preferences or that would make things worse.
5. **Skip** bot comments that are purely informational (CI status, manifest diffs, automated summaries, etc.).
6. **Check for patterns** — if a reviewer flags an issue in one place, check if the same issue exists elsewhere in your changes.

## Step 5 — Make changes

- Read each file before editing it.
- Make targeted edits addressing the accepted feedback.
- Group related changes logically.

## Step 6 — Commit and push

1. Stage specific changed files (do not use `git add -A` or `git add .`).
2. Commit using conventional commit format matching the repo's style. Check for CLAUDE.md in the repo root for commit conventions. Include the Co-Authored-By trailer:
   ```bash
   git commit -m "$(cat <<'EOF'
   fix: address PR review feedback

   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   EOF
   )"
   ```
3. Push to the PR branch:
   ```bash
   git push origin <head-branch>
   ```
4. Capture the commit SHA:
   ```bash
   git rev-parse HEAD
   ```
   **Never fabricate a commit SHA.** Always use the real one.

## Step 7 — Reply to each comment

For every review comment that was addressed, reply using:

```bash
gh api repos/<owner>/<repo>/pulls/<number>/comments/<comment-databaseId>/replies \
  -f body='Addressed in <commit-sha>.'
```

**Important:** The reply endpoint is `/comments/{comment_id}/replies`. This is the correct way to reply to inline review comments.

For comments you **disagree** with, reply explaining your reasoning:
```bash
gh api repos/<owner>/<repo>/pulls/<number>/comments/<comment-databaseId>/replies \
  -f body='I considered this but chose to keep it as-is because <reason>.'
```

Be concise and professional in all replies.

## Step 8 — Resolve threads

Resolve threads where the feedback has been **fully addressed**. Use the GraphQL mutation:

```bash
gh api graphql -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: {threadId: $threadId}) {
      thread { isResolved }
    }
  }
' -f threadId='<thread-node-id>'
```

You can batch multiple resolves in a single mutation for efficiency:

```bash
gh api graphql -f query='
mutation {
  t1: resolveReviewThread(input: {threadId: "PRRT_abc"}) { thread { isResolved } }
  t2: resolveReviewThread(input: {threadId: "PRRT_def"}) { thread { isResolved } }
}'
```

**Do NOT resolve threads if:**
- The comment asks a question that needs the reviewer's input
- You disagree and want the reviewer to see your response first
- The change requires discussion or a decision from the team

## Step 9 — Report

Present a summary:

```
## PR Comments Incorporated: <PR title>

### Changes made
- <file>: <what changed and why>
- ...

### Replies sent
- <N> comments addressed and threads resolved
- <N> comments replied to but left unresolved (with reasons)

### Not addressed
- <any comments skipped or disagreed with, and why>

Commit: <sha>
PR: <url>
```

---

## Important rules

- **Never fabricate commit SHAs.** Use the real SHA from `git rev-parse HEAD`.
- **Be honest about disagreements.** If feedback does not make sense, say so and explain why in the reply.
- **Check for CLAUDE.md** in the repo root for commit conventions and project-specific rules.
- **Respect the repo's existing patterns.** Match the style of surrounding code.
- **Do not use `gh pr view --comments`** for fetching comments. Use the REST API calls specified above.
