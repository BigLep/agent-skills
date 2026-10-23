# agent-skills

Personal [Agent Skills](https://agentskills.io) (the `SKILL.md` format read by Claude Code, Codex, and other agents), installable with the [`skills` CLI](https://github.com/vercel-labs/skills).

## Skills

| Skill | What it does |
|---|---|
| [copy-to-clipboard](skills/copy-to-clipboard) | Copy text to the macOS clipboard as plain text, Slack-ready, or rich HTML. macOS only. |
| [humble-relay](skills/humble-relay) | Rewrite an agent-drafted message so it reads as the user relaying partly verified agent work. |
| [incorporate-pr-comments](skills/incorporate-pr-comments) | Single pass over PR review comments: evaluate, fix, commit, push, reply, resolve. |
| [review-pr](skills/review-pr) | Two-phase PR feedback handling: fix locally and report, then commit and respond on request. |
| [why-does-this-matter](skills/why-does-this-matter) | Turn a new release or technology into a personalized explainer-and-pitches slide deck. |

## Install

```sh
npx skills add <owner>/agent-skills -g            # all skills
npx skills add <owner>/agent-skills -g --skill review-pr   # one skill
```

## Local development

On the authoring machine, skills are symlinked rather than installed, so edits take effect immediately:

```sh
ln -s ~/Code/PersonalProjects/agent-skills/skills/<name> ~/.agents/skills/<name>
ln -s ../../.agents/skills/<name> ~/.claude/skills/<name>
```

## Authoring rules

- Frontmatter uses only spec fields: `name`, `description`, and optionally `license`, `compatibility`, `metadata`, `allowed-tools`.
- No agent-specific argument placeholders (`$ARGUMENTS`, `arguments:`); describe the input in prose.
- Reference bundled files relative to the skill directory, never by an agent-specific install path.
