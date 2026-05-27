# Promotion Decision

Use this reference in Step 1 when deciding whether the input should become an independent agent.

## Decide in This Order

1. Is there a long-lived identity?
2. Is there durable workspace value?
3. Does it need resume logic and path semantics?
4. Would a simpler abstraction solve it already?
5. Does it actually require plugin-level runtime changes?

## Promote to an Independent Agent When

- The agent has a stable public role, not just a one-off output.
- The value depends on long-lived workspace contract, file-backed state, or canonical deliverables.
- The work needs durable root rules such as resume, overwrite policy, capability boundaries, or routing.
- The workspace must be reusable by future sessions or by another user on the same host profile.

## Keep It as a Skill or Simpler Workflow When

- The task is a bounded workflow without long-lived identity.
- A single `SKILL.md + references + scripts` package already captures the value cleanly.
- The work does not need root-file governance, workspace layout, or recovery rules.
- The request is really "give me a plan" or "do this once", not "maintain this workspace over time".

## Consider a Private Skill When

- The behavior is narrow, personal, or highly local to one workspace.
- Reuse matters, but a full agent workspace would be heavier than the value it adds.
- The durable contract belongs inside another agent as a routed sub-skill.

## Consider a Plugin When

- The capability requires new host tools, channels, providers, runtime hooks, or background services.
- The requirement changes the host capability surface, not just the workspace prompt and files.
- `skill + references + scripts + TOOLS.md` is no longer enough.
- If the brief involves `src/channels/`, `extensions/`, or `src/plugins/` runtime extensions, consult `references/openclaw-modules.md` to confirm plugin-level scope.

## Control Pattern Defaults

- Fixed multi-step generation: `prompt chaining`
- Multiple input families or request classes: `routing`
- Independent side analyses: `parallel`
- Multi-part generation with explicit evaluation loops: `orchestrator-workers` or `evaluator-optimizer`
- Open-ended exploration only after simpler patterns fail: `autonomous loop`

## Minimum Proposal Output

Before you can say "this is an independent agent", the proposal must state:

- `judgment_result`
- `promotion_rationale`
- `preferred_control_pattern`
- a simpler alternative if the answer is not `独立 agent`

## Common Mistakes

- Promoting something just because it is complicated once.
- Confusing "many files" with "needs an agent".
- Using plugin as a label for any task that feels advanced.
- Treating root-file scaffolding as proof that the promotion decision was correct.

