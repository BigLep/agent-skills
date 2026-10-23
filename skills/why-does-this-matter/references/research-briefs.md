# Research briefs

Four agents, launched together in one message. Each writes one file in `why-it-matters/<topic-slug>/research/` and returns a summary of ten lines or fewer.

Fill the placeholders before sending:

- `{TOPIC}`: the topic as the person wrote it, plus any link or file they gave.
- `{HINT}`: your one line on who the person seems to be, or "unknown so far".
- `{RUN_DIR}`: absolute path to the run folder.
- `{TODAY}`: today's date.

Put this paragraph at the top of the three web briefs (Facts, In the wild, Skeptic):

> You are researching something that may have launched after your training data ends. Do not rely on what you remember about it. Search the web, read the pages, and report what the sources say. Every claim in your file carries a source link and the date it was published. If sources disagree, say so and name both. If you cannot find the thing at all, or the name matches several different products, say that in the first line of your file and list the candidates. Today is {TODAY}.

---

## Facts

> **Topic:** {TOPIC}
>
> Find out what this is and what is new about it. Start with primary sources: the maker's announcement, documentation, pricing page, changelog, model card, or release notes. Use press coverage only to fill gaps.
>
> Write `{RUN_DIR}/research/facts.md` with these sections:
>
> 1. **One sentence:** what it is, in plain words, as you would say it to a colleague.
> 2. **Who made it and when it launched.** The official name and how the maker spells it.
> 3. **Where it lives:** what it sits inside (a product, a plan, a platform) and what it contains. Two or three levels.
> 4. **How it works:** what goes in, what it does with it, what comes out, as the maker's docs describe it. Name the parts in the maker's own terms. If the docs do not explain the inside, say "not documented" rather than guessing; this section becomes an animated diagram, and a guessed mechanism would be drawn as fact.
> 5. **What is new:** three to six capabilities that did not exist before, or got much better. For each: what it does, the evidence (a number, a demo, a benchmark), and what it replaces.
> 6. **Numbers people will repeat:** two to four figures (price, speed, size, a benchmark), each exactly as the source writes it, with who measured it. Mark which ones are the maker's own.
> 7. **Who can use it:** plans, prices, regions, waitlists, usage limits, what you need installed.
> 8. **How you start:** the literal first steps to get access and run it once.
> 9. **Sources:** every link with its date. Mark the single best page for someone who has never heard of it; handoff prompts will send other agents there.
>
> Keep it under 800 words. Return a summary of ten lines or fewer.

## In the wild

> **Topic:** {TOPIC}
> **Who is asking:** {HINT}
>
> Find what real people are doing with this right now. Look at the last 30 days: demos, write-ups, newsletters, forum threads, videos, social posts from named practitioners. If you know who is asking, search for uses in their role and industry first, then look more widely.
>
> Separate what someone showed working from what someone said should be possible. A screen recording of a finished result counts as shown. A thread of ideas counts as claimed.
>
> Write `{RUN_DIR}/research/in-the-wild.md` with these sections:
>
> 1. **Ten to fifteen use cases.** For each: the job being done, who did it (name and role), what they used alongside it, the result, shown or claimed, and the link with its date.
> 2. **What is trending:** the three uses people are most excited about, and why.
> 3. **Closest to this person:** the three to five uses nearest to the role and industry in the hint. If the hint is "unknown so far", skip this section.
> 4. **News:** anything from the last two weeks that changes the picture (a price change, a new integration, an outage, a competitor's reply).
>
> Keep it under 900 words. Return a summary of ten lines or fewer.

## Skeptic

> **Topic:** {TOPIC}
>
> Your job is to find where this falls short. Launch coverage is mostly praise, and the person relying on your research will spend real hours on what we recommend. Look for independent reviews, critical threads, bug reports, benchmark disputes, and comparisons with alternatives.
>
> Write `{RUN_DIR}/research/skeptic.md` with these sections:
>
> 1. **Known limits:** what it cannot do, does badly, or does slowly. Evidence for each.
> 2. **Hype check:** claims from the launch that reviewers could not reproduce, or that depend on conditions most people will not have.
> 3. **Cost and access traps:** usage caps, price jumps at scale, features held back for higher plans, regions left out.
> 4. **Data and compliance:** what happens to what you put in, and anything a regulated industry should check first.
> 5. **Alternatives:** the two or three nearest options and when each is the better choice.
> 6. **Do not recommend:** uses that look attractive and currently fail. Be specific.
> 7. **Sources:** every link with its date.
>
> Be fair. If the criticism is thin, say the criticism is thin. Keep it under 700 words. Return a summary of ten lines or fewer.

## Context

This agent does not search the web. It reads what is already known about the person.

> Build a profile of the person who is asking, so recommendations can be aimed at their real work. Read only. Do not change, send, or delete anything.
>
> Look in these places, in this order, and stop when the profile is solid:
>
> 1. Memory files and any project or user instruction files (for example `CLAUDE.md`, a memory folder, project knowledge).
> 2. Files the person attached or named in this conversation.
> 3. The working directory: folder names, READMEs, recent documents, plans, decks, notes. Read titles and openings first, and go deeper only where it pays.
> 4. Connected tools (notes, docs, calendar, CRM, email), if any are available and the first three left gaps. Search for what describes the person's work. Do not browse private messages out of curiosity.
>
> Write `{RUN_DIR}/research/profile.md` with these fields.
>
> **Every fact carries its source.** The person will be shown what we know about them and where we learned it, because people often do not know which memories or files an AI is drawing on, and a stale fact can only be corrected if they can see it. So for each fact, record:
>
> - **Kind:** Memory, File, Connected tool (name it), This chat, or Project instructions.
> - **Name:** what the person would recognize. A memory's title, a file's name, a page's title. Not a full path, and never an internal id.
> - **When:** the date on it, if there is one. An old fact may no longer be true; say so.
> - **Evidence:** the few words in the source that support the fact, quoted.
> - **Confidence:** high, medium, low.
>
> A fact you inferred (from folder names, from tone) is marked **Inferred**, with what you inferred it from. Inferred facts are useful for ranking and weak as stated reasons.
>
> Write it as a list, one fact per line, in this form:
>
> `- You run workshops on agentic automation. · File: Workshops/Agentic Automation outline.md · Aug 2026 · "Session 3: build your first n8n flow" · high`
>
> The fields:
>
> - **Role:** what they do, day to day.
> - **Organization and industry:** and roughly what size.
> - **Who they serve:** customers, clients, audience, or internal teams.
> - **Tools they use now:** by name. Mark the ones they clearly use daily.
> - **Recurring jobs:** five to ten things they do every week or month (write proposals, run workshops, close the books, review contracts). These matter most.
> - **Current projects:** what they are working on right now, with dates if known.
> - **Goals and pressures:** what they are trying to achieve or fix this quarter.
> - **Constraints:** budget, team size, compliance, technical comfort.
> - **How they like things:** voice, format, and style preferences that should shape a deck made for them.
> - **Already using AI for:** so we do not recommend what they already do.
>
> End with three lists:
>
> - **Gaps:** fields still unknown.
> - **Sensitive:** details you saw that are useful for ranking and should not be printed on a slide someone else might see (money figures, names of clients or private individuals, personal matters, anything unannounced). For each, give the kind and the source name, so the person can be told "your pricing notes were used" without the numbers being shown.
> - **Sources read:** every memory, file, and tool you opened, by name. This list is shown to the person.
>
> Never copy credentials, keys, or account numbers into the file.
>
> Do not guess to fill a field. "Unknown" is the right answer when you did not find it. Keep the file under 800 words. Return a summary of ten lines or fewer, leading with role, industry, and the gaps.

---

## When there are no sub-agents

Do the same four passes yourself, in this order: Context, Facts, In the wild, Skeptic. Context goes first so it can aim the rest. Write the same four files. Keep the Skeptic pass even when time is short; it is the one people skip and the one that prevents bad recommendations.
