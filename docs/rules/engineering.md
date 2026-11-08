# Engineering — code, Python, lint, CI

## Code, in any language

- **The smallest change that fully solves the task.** No option, layer or
  abstraction nobody asked for; deletion beats addition.
- **Keep values in the form the platform already gives you** — no defensive
  re-wrapping, no parallel type for the same shape.
- **Errors are handled where they can be fixed, never swallowed.** An `except`
  that does nothing hides a failure the user will meet later; re-raise with
  `from exc`, or handle it and say why.
- **Validate at the trust boundary** (HTTP input, file, env var, LLM output):
  that is the one place a check is mandatory.
- **Comment the why, never the what.** A comment restating the code is a line
  that can be wrong.
- **Deprecate, do not delete** code someone may still import: mark it
  `@deprecated` and name the replacement.
- **Never hand-edit a generated file.** Regenerate it and commit the output.
- **One responsibility per module**; layers import downward only, enforced by
  `import-linter` when the project has layers.

## Python

- The version in `pyproject.toml` (`requires-python`), uv for dependencies.
- `from __future__ import annotations`; `str | None`, `list[...]`, `dict[...]`;
  no `Optional`/`List`/`Dict`.
- **Type hints on every signature.** `mypy` is a gate, not advice: no
  `# type: ignore` without an error code and a reason on the same line.
- Line length **100**; imports sorted by ruff. Constants at module top.
- Dataclass or `NamedTuple` for internal models; Pydantic only at the boundary
  (settings, API shapes). No mutable default argument.
- **Async**: never block the event loop (no `requests`, no `time.sleep`, no heavy
  CPU); every outbound call has a timeout.
- Settings via `pydantic-settings`, one prefix per product (`INT_`, `LET_`), and
  the `.env` loader never overrides a variable already set by the environment.
- SQLAlchemy 2 style only (`Mapped[...]`, `mapped_column`), never the 1.x API.

## Lint, format, types, security

Four commands, the same in CI, pre-commit and the README:

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run bandit -r <packages> -c pyproject.toml
gitleaks detect --source . --config .gitleaks.toml
```

- **Pinned versions** in the lockfile or pre-commit; the gate must not change
  because a tool released overnight.
- **No inline suppression without its rule id and a reason** — `# noqa: B008`
  yes, a bare `# noqa` no. The same for bandit skips.
- **Coverage floor: 85 % line + branch, on the aggregate.** A low new module is
  what the floor is for.
- Pre-commit runs the same set as CI, so a red CI means a skipped hook.

## Tool configuration

- **Every tool that takes a path has its configuration committed at the repo
  root** — ruff and mypy in `pyproject.toml`, the eslint flat config, prettier,
  tsconfig, pytest. Behaviour nobody wrote down changes silently when the tool
  upgrades.
- **Say what is checked, explicitly.** An `include` list plus `force-exclude`
  beats a bare `check .`: the tool then skips what it should even when the path
  is passed on the command line.
- **Documentation is never linted or formatted by a code tool.** Ruff 0.17+
  formats Markdown by default — `include = ["*.py"]`,
  `extend-exclude = ["*.md"]`, `force-exclude = true`. Measured on this toolkit's
  own corpus (302 Markdown files): `ruff check` ignores `.md` outright, while
  `ruff format` rewrites 15 of them — re-wrapping snippets inside *archived*
  planning documents, which are a record, not source. It also silently corrects
  a deliberately unformatted "don't do this" example, so the doc stops telling
  the truth. The same for prettier, which needs an ignore file rather than a
  scope in the command.
- **A new directory joins the ignore lists in the same PR that creates it.**
  Installed `docs/rules/` is generated: a formatter rewriting it produces a diff
  nobody can review, and the next install overwrites it anyway.
- **Pin the version next to the config** (lockfile, pre-commit `rev`). A tool
  that changed its defaults overnight must not change what CI checks.

## CI/CD

- **One workflow per concern**, one required check per job. The list of required
  jobs lives in branch protection **and** in the README — they drift otherwise.
- **Every gate is runnable locally**, and the README says how. A check only CI
  can run is a check nobody runs before pushing.
- **Order: cheap first.** Lint, format, types, secret scan, then unit, then the
  full suite, then images. A two-minute lint should not wait behind a
  ten-minute build.
- **Cache on the lockfile hash**, never on a branch name.
- **Images build on every pull request; they are pushed only from the
  integration branch, tagged by commit SHA.** A mutable `latest` tag is not a
  deployable artefact.
- **Deploys never run from a pull request.** A merge to the integration branch
  starts the deploy workflow; anything that touches production waits on its
  environment approval.
- **Secrets come from the secrets manager or the CI store**, are never echoed,
  and the variable names alone are committed (`.env.example`). gitleaks scans
  the full history, not just the diff.
- **A red integration branch is the first thing fixed.** No new branch is opened
  on top of a broken gate.
