# plannotator-auto-last

The Stop hook that decides, after each Claude reply, whether to open Plannotator so the user can answer inline instead of in the terminal.

## Language

**Awaiting input**:
A reply that leaves Claude waiting on the user, either to answer something or to review a set of proposed actions. This is the concept the hook tries to detect; an explicit question is one sign of it, not the definition.
_Avoid_: has questions, needs annotation

**Yes/no offer**:
A reply whose only ask is a single yes/no offer to take the next step ("Want me to commit this?"). It counts as awaiting input, but it is quicker to answer in the terminal, so the hook skips it.
_Avoid_: confirmation question

**Gate**:
An exact, cheap rule that settles the decision before any fuzzy judgment runs (feedback loop in progress, Inbox used this turn, reply too short).
_Avoid_: filter, precheck

**Saved case**:
A real turn recorded with the decision the user expected, used to check any change to the rules.
_Avoid_: fixture, sample
