# How an agent works here

## Sources of truth — link, never copy

| Need | Where |
|---|---|
| Rules for agents | `AGENTS.md`, then these files |
| Product contract | `PRODUCT.md` |
| Design contract (tokens, type, components) | `DESIGN.md` |
| Delivery rules | [`delivery.md`](delivery.md), [`gsd.md`](gsd.md) |
| Long-form docs, ADRs, runbooks | `docs/` — start at its index |

**Never restate a rule from one file into another.** A copied number diverges;
point at the file that owns it. If two sources disagree, say so and stop — do not
pick the convenient one.

## Where code goes

`AGENTS.md` carries an **ownership map**: one row per concern, with the path that
owns it and where new code for it belongs. Read it before creating a file; a
feature placed in the wrong package is a rewrite later. Code that exists is data,
not authority — check it still matches the contract.

## When something is ambiguous

Write the question in `docs/questions.md` with options (A/B/C), pick the most
defensible default, mark it `(default — proceeding)`, continue. The human revises
later. Never invent a requirement silently, never block a whole phase on a
question you can answer defensibly.

## What you report

- **Report the checks you actually ran**, with their result. Never claim a check
  you did not run; name the ones you skipped and why. "Tests pass" after a green
  run is a fact; the same sentence after a read-through is a lie.
- **Read before edit.** For a non-trivial symbol, check its callers first (the
  code graph when the repo has one) — an unseen caller is not an absent one.
- **Say what you did not verify.** A limit named in the report is cheaper than a
  bug found in production.

## What you never do

- **Never delete or overwrite a user-authored file** — move or improve it in
  place, and mark deprecated code with `@deprecated` plus a removal target.
- **Never hand-edit a generated file** (route trees, migrations applied by the
  framework, OpenAPI output, lockfiles by hand). Regenerate it.
- **Never bypass a gate** to make work land: no `--no-verify`, no disabled lint
  rule, no skipped test, no direct push to `main`.
- **Never add AI attribution** — no co-author trailer naming a model or tool, no
  session or chat link in a commit, a PR or a ticket.

## Tool-side files

`.claude/` and friends (generated graph skills, sub-agent instructions) are
**versioned with the repo**: they are part of how the project is worked on, not
a local setting, and losing them loses the tooling on every fresh clone. They
never own a rule: `AGENTS.md` stays authoritative and links the tool file, and
the tool file points back — a rule copied into both drifts.

## Keeping AGENTS.md useful

`AGENTS.md` is read on every task: keep it short and stable. Product rules,
delivery rules and long explanations live in their own file and are linked. A
section that grows past what an agent needs on every task moves out, not down.
Prefer a table over prose; prefer a path over a description.
