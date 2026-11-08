# Testing

## Three kinds, three folders

| Kind | What it proves | What it may touch |
|---|---|---|
| `unit` | one function or module behaves | nothing external — no network, no database, no clock |
| `integration` | the wiring between components holds | real components, external boundaries **mocked** |
| `functional` | the product works through its real entry point | the real entry point, end to end |

A test that needs a database is not a unit test. A test that mocks the parser is
not functional. Put each in its own folder (`tests/unit`, `tests/integration`,
`tests/functional` or the project's equivalent) and tag it so `-m` selection works.

## Gates

- **CI runs all three**, with a coverage floor on the aggregate, not per file.
  A kind nobody runs is a kind that rots.
- **Every commit leaves CI green.** A red gate is fixed before the next task, not
  carried.
- Tests never call a real API, a real mailbox or a paid provider. Boundaries are
  mocks or fakes; the one suite allowed to hit a real service runs against a
  dedicated test installation, never production.

## Writing them

- **New behaviour ships with its test**; a bug fix ships the test that would have
  caught it. A new branch (a condition, a parser, money, security) without a test
  is an unfinished change.
- **Parametrise multi-case tests**, with readable ids — never copy-paste the same
  test function.
- **AAA**: arrange, act, assert, in that order, visibly.
- Name the test after the unit and the scenario: `test_<unit>_<scenario>`.
- **Assert the contract, not the implementation**: what the caller can observe.
  A test that only checks the happy path lets the wrong model through.
- Fixtures are shared from one place; a test owns its data and leaves nothing
  behind.

## What a test is not

- Not a substitute for the verification gate, and a green verification is not a
  green build.
- Not a place to disable a rule to make a check pass. An inline suppression names
  its rule and says why.
