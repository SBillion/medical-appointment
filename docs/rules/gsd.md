# GSD delivery

GSD is the planning method; the conventions in [`delivery.md`](delivery.md) are
what lands the work. These rules only cover what GSD adds.

## Planning artifacts

- **Commit `.planning/` with the code**: roadmap, requirements, verification
  report ride in the same PR as the phase (on its stack layer). An untracked
  `.planning/` — `.git/info/exclude`, or `commit_docs: false` — makes
  workstreams and parallel milestones a one-machine feature.
- **Commit granularity**: one commit per plan, not per task; the plan is the unit
  you revert. One docs commit per phase at the end (`PROJECT.md`,
  `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md` and that phase's `CONTEXT.md`,
  `RESEARCH.md`, `PLAN.md`s, `VERIFICATION.md`) — not one per workflow step.
- **GSD ids stay in `.planning/`.** A phase number, a plan id or a workstream
  name never appears in a branch, a commit, a PR or a ticket. A description that
  needs the reasoning links the file (`.planning/phases/03-billing/PLAN.md`).
- **A literal commit message inside a GSD workflow is a template**, not a
  command: translate `docs(${phase}): …` into the real subject. The hook rejects
  the rest.

## Running a phase

- `git.branching_strategy` is `none`: **open the stack layer before running the
  phase**, and keep the ticket's branch checked out. GSD commits on it.
- **Publish with `gh stack submit --auto`, never `/gsd-ship`** — its
  `gh pr create` step bypasses the stack.
- **One phase, one owner.** Two people executing the same phase rewrite
  `STATE.md`, `ROADMAP.md` and the verification digest; the merge is wrong in
  ways no linter catches. Split phases, or split the tickets inside a phase.
- **Verification runs once**, at the end of execution. Re-running it "to see" is
  the most expensive habit in the workflow.
- **Small work is `/gsd-quick`**, not a phase. A quick task costs cents; a phase
  costs dollars.
- **Keep the plan-check.** It is the cheapest gate and the only one that
  disagrees with the planner. A phase with a `stale` verification is not done:
  re-run the gate, never hand-edit the digest.

## Parallel milestones

- Use `/gsd-workstreams` and carry `--ws <name>` on every command, or set
  `GSD_WORKSTREAM`. `.planning/active-workstream` is a fallback for sessions with
  no identity — never the selector while two sessions run.
- Phase numbers repeat per workstream: key every mapping on
  `<workstream>/<phase>`.
- Workstreams isolate planning, not source: give each stream its own branch and
  disjoint file scopes.
