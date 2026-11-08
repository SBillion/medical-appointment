# Work across several repositories

Most products here are a small graph of repos — an app, sometimes a
config/deploy repo, sometimes an e2e gate. State that graph in `AGENTS.md` (one
line per repo and its role) before anything else; a rule that does not say
*which* repo it applies to is half a rule. Not every product has all three: the
sections below say when they apply.

## One ticket, several PRs

With no tracker, read "ticket" as "the tracked outcome" — the change you can
name in one sentence. The PR links are the same.

- **One ticket can span repos, and one repo can take several PRs for the same
  ticket.** Split when each PR is reviewable on its own — a stack layer each —
  and keep one ticket: every PR links the others in its body.
- **`gh stack` does not stack across repositories.** Land in dependency order —
  the producer (app, API, schema) first, the consumer second — and say the order
  in the ticket. A consumer PR opened against unmerged producer code proves
  nothing.
- **Every repo has its own CI gate.** Green in one says nothing about another;
  check each before calling the work done.

## Contracts between repos

These apply only to products that have a second repo asserting the first one's
surface — an e2e suite, a config/deploy repo. A single-repo product has no such
contract to keep in sync.

- **A change to a shared surface lands on both sides in the same work.** If the
  app changes an API path, a payload field, a DOM id, a route, an env-var name or
  a published file the e2e or config repo asserts, update that repo in the same
  ticket. "Later" means the gate goes red at promotion, 35 minutes and a paid run
  after the cause.
- **The producing repo carries a contract test** that pins what the consumer
  uses: the paths, ids, keys, copy and routes the other repo asserts. A rename
  then fails in minutes, locally, instead of in the other repo's pipeline.
- **A new user path is covered only when the e2e repo gains its test.** Plan it
  in the same ticket: a feature that ships without it is untested where it
  matters. Covering it by hand at promotion is not coverage.
- **A new env var, secret, image tag or port** lands a PR in the config/deploy
  repo too, referencing the app PR. A feature that only works on the author's
  machine is not delivered.

## Never copy between repos

- **Share by link or by installer, never by copy.** A block of rules pasted into
  three `AGENTS.md` files drifts: the copy in this product still said `Plan:
  NN-NN` a month after the rule was dropped. Install `docs/rules/` once per repo
  and point at the index.
- **The same for workflows, hooks and helpers**: a copied file is a fork nobody
  remembers to merge.
- **`.planning/` lives in the repo that owns the work.** A phase spanning several
  repos keeps its plan in the owning repo and lists the other repos' PRs in the
  phase notes — do not create three half-plans.
