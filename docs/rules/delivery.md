# Delivery — ticket, branch, commit, PR

Project settings: tracker **`none`**, ticket prefix **``**, integration
branch **`main`**.

When the tracker is **`none`**, every ticket rule below drops: branch on the slug
alone (`fix/provider-retry`), commit without an id, and let the PR body say what it
delivers. The rest — branches, commits, pull requests, stacks — is unchanged.

## Tracking

- **When work is tracked, one ticket = one shippable outcome.** If the work spans
  slices, split the ticket *before* you start. A merged PR closes the ticket only
  because the PR finishes it.
- **If a merge closes a ticket with work left**, reopen it and file the remainder
  the same day. That is the most common drift.
- **Everything written in the tracker is in English.**

### With Linear

- **Every ticket belongs to a project.** A projectless ticket falls out of every
  view. When no milestone project fits, use the standing catch-all
  `Tech debt and conventions` — never leave it projectless, never open a project
  for a single ticket.
- **One milestone = one Linear project**, named after its outcome: `Test
  coverage`, `Paid MVP`. Never after a version — the version lives in the tag and
  in the project description.
- **No project milestone by default.** One project already *is* one milestone; a
  milestone named `v1.1` duplicates the project and a version nobody reads. Put a
  project milestone only when one project ships several deliveries, and name it
  after the outcome with a target date.
- **One GSD phase = one or more tickets.** Plan the phase, then cut it into
  tickets — one per shippable slice — when it carries more than one outcome.
  Several tickets for one phase are stacked, bottom layer first.
- **Create the project with the milestone, not after it.** A milestone whose
  project does not exist is a plan with nowhere to report.
- **Ticket titles start with their area** so the board reads without opening the
  ticket: `[Backend / API] …`, `[Frontend] …`, `[Delivery] …`. One area per
  ticket — the widest honest one, never a list joined by `+`. The area prefix
  never appears in a branch, a commit or a PR title.
- **Linear is link-only.** It may link an existing branch or PR; it must never
  create one — the hook, the stack and the no-auto-merge rule only apply to
  branches you opened. Disable the integration's automations.

### With Outline

Documents replace tickets: the page states the outcome and its acceptance, and
the PR body links it. No id in the branch or the subject — the link is the join.

## Branches

```
<type>/-<n>-<short-slug>      # with a tracker
<type>/<short-slug>                  # with tracker: none
fix/INT-42-provider-retry
chore/provider-retry
```

- `<type>` is the commit type of the main change (`feat`, `fix`, `chore`,
  `docs`, `test`, `refactor`, `perf`, `ci`).
- **One objective per branch.** A review fix is another commit on the open
  branch, not a new one.
- **Stacked layers keep the same ticket id** on every layer (with a tracker).
- **Never commit or push directly to `main`.** Branch, pull request,
  wait for CI, stop.
- **Open branches and PRs with `gh` or `gh stack` only — never from a linked
  tool.** Linear and friends use whichever branch is checked out and can target
  `main` with a whole stack; that produced duplicate PRs more than once.
  The link between a PR and its ticket is the id in the title, nothing else.
- `git config core.hooksPath .githooks` once per clone when the repo installs
  the hook: it reads the ticket from the branch, closes the subject with it and
  refuses a phase-number scope.

## Commits

```
<type>(<scope>): <summary> (-<n>)     # with a tracker
<type>(<scope>): <summary>                   # with tracker: none
fix(deploy): probe /v1/health in the container healthcheck (EXS-7)
feat(runs): stop leaving a finished run on "Read the offer" (INT-42)
```

- Conventional Commits: imperative, lowercase, no trailing period, under 72
  characters. Types: `feat` `fix` `docs` `test` `chore` `refactor` `perf` `style`
  `ci`.
- **The scope names the feature or module, never the phase number.** `fix(runs)`,
  never `fix(03)` or `feat(02-01)`. Someone reading `git log` without
  `.planning/` open must understand the change.
- **The ticket id closes the subject**, in parentheses, when the project has a
  tracker. A commit that has no ticket says so in its body — never invent an id.
  The id never opens the subject.
- **GSD ids never enter the git or tracker record**: no phase number, no plan id
  (`02-01`), no workstream name in a commit subject or body, a branch, a PR
  title or body, a ticket or document title or description. They are internal to
  `.planning/`; the map is `.planning/LINEAR.md`. Pointing at the GSD *files*
  that explain a decision is welcome in a PR or ticket description —
  `.planning/phases/03-billing/PLAN.md` — as a reference, never as a label.
- **Atomic commits**: one logical change each, and every commit leaves CI green.
  Do not mix a refactor with a behaviour change.
- Breaking change: `!` after the type/scope plus a `BREAKING CHANGE:` footer.
- **Rebase, not squash**: the individual commits are the record. Never force a
  push onto a branch you do not own.
- **No AI attribution**: no co-author trailer naming a model or tool, no session
  or chat link in a commit or a PR.

## Pull requests

- **Title**: the top commit subject, ticket id included when there is one.
- **Body**, written by hand and passed with `--body-file`:
  `What this changes` / `Why` (`Closes -<n>`, or the link to the
  document) / `How it works` / `Tests`, plus `Notes` when it applies
  (screenshot, breaking change, stack layer, follow-up). Never paste the commit
  list.
- **Never merge.** An open, verified PR means the work is done: CI green, stop.
  Do not run `gh pr merge`, do not click Merge. Merging is a human decision.
- **Related, dependent changes are stacked** (`gh stack init` / `add` /
  `submit --auto`), not parallel PRs off `main`. One logical concern per
  layer, one ticket id per layer, `gh stack merge` only on an explicit request.
- **A layer that depends on an unmerged layer starts on that layer's branch**,
  never on `main`: otherwise it compiles against code that does not
  exist yet and its CI proves nothing. Retarget it to `main` when the
  dependency merges.
- Open as a draft until CI is green; then request review.
