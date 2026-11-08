# Secrets and data

## Secrets

- **One store, one project.** Secrets live in the team's secret manager (one
  project, never a second personal or staging copy) or in CI. A secret split
  across two stores is a secret you will rotate in the wrong one.
- **Commit only variable names** in `.env.example`, never a value. `.env` is
  git-ignored and stays local.
- **A server authenticates with a machine identity**, injected at process start
  (the `with-secrets` wrapper or the platform equivalent). Never copy a
  production `.env` onto a host, never export secrets by hand.
- **Never log a secret** — redact tokens, headers and connection strings at the
  logging boundary, not at each call site.
- If a secret leaks: rotate it first, then rewrite or purge, then say so. Deleting
  the commit does not un-leak a key.

## Personal data

- **Never commit real personal data**, exports or customer values — not in
  fixtures, comments, doc examples or screenshots. Build synthetic data with the
  same shape and invented values, keeping the useful relations (order, formats,
  identifiers).
- **Keep it out of issues, PRs and test artifacts** too, not only out of source.
- A scan that looks for copies is a safety net, not a privacy review.

## Behaviour

- Validation and calculation are separate: the layer that computes does not
  decide, the layer that validates refuses with a named reason.
- Anything a user can trigger has a bound: timeouts, size limits, rate limits,
  bounded concurrency.
