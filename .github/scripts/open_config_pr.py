#!/usr/bin/env python3
"""Open or update a stacked deploy PR on the config repository.

Invoked by the Release workflow in the app repository every time a pull
request is merged into ``main``. For a given environment it:

1. Resets the environment's pending branch onto the config repo base branch.
2. Bumps the image tags (backend + frontend) to the newly built commit SHA.
3. Force-pushes the pending branch.
4. Creates a deploy PR if none is open, otherwise updates the existing PR's
   body so that every merged app PR is listed as a checklist item until the
   deploy PR itself is merged.

The PR body always advertises the *latest* SHA on ``main`` ("using the last
sha commit on main in app repository") while accumulating the list of merged
app PRs that will be deployed by merging the deploy PR.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def run(*cmd: str, **kwargs: object) -> subprocess.CompletedProcess[str]:
    """Run a command, streaming output, failing loudly."""
    print(f"$ {' '.join(cmd)}", flush=True)
    return subprocess.run(list(cmd), check=True, text=True, **kwargs)  # type: ignore[arg-type]


def run_capture(*cmd: str) -> str:
    return subprocess.run(
        list(cmd), check=True, text=True, capture_output=True
    ).stdout.strip()


def short(sha: str) -> str:
    return sha[:10]


# --------------------------------------------------------------------------- #
# Git / file mutation
# --------------------------------------------------------------------------- #


def configure_git(repo: Path) -> None:
    run(
        "git",
        "-C",
        str(repo),
        "config",
        "user.name",
        "github-actions[bot]",
    )
    run(
        "git",
        "-C",
        str(repo),
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )


def bump_tags(values_file: Path, image_tag: str) -> bool:
    """Set image.backend.tag and image.frontend.tag to ``image_tag``.

    Uses ``yq`` (mikefarah) which is preinstalled on GitHub-hosted runners.
    Returns True if the file changed.
    """
    before = values_file.read_text()
    run(
        "yq",
        "-i",
        f'.image.backend.tag = "{image_tag}"',
        str(values_file),
    )
    run(
        "yq",
        "-i",
        f'.image.frontend.tag = "{image_tag}"',
        str(values_file),
    )
    return values_file.read_text() != before


def reset_pending_branch(
    repo: Path, base: str, pending: str
) -> None:
    # Fetch into a remote-tracking ref (not the local branch, which is
    # already checked out by actions/checkout and cannot be force-updated).
    run("git", "-C", str(repo), "fetch", "origin", base)
    run(
        "git",
        "-C",
        str(repo),
        "checkout",
        "-B",
        pending,
        f"origin/{base}",
    )


def commit_and_push(repo: Path, pending: str, image_tag: str, env: str) -> None:
    run("git", "-C", str(repo), "add", "-A")
    # exit-code 0 means nothing staged; `git diff --cached --quiet` returns 0
    # when there are no changes and 1 when there are.
    staged = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--quiet"],
        text=True,
    )
    if staged.returncode == 0:
        print("No tag change to commit (already up to date).")
        return
    run(
        "git",
        "-C",
        str(repo),
        "commit",
        "-m",
        f"deploy({env}): bump image tag to {short(image_tag)}",
    )
    run(
        "git",
        "-C",
        str(repo),
        "push",
        "--force-with-lease",
        "origin",
        pending,
    )


# --------------------------------------------------------------------------- #
# PR body
# --------------------------------------------------------------------------- #

BODY_HEADER_RE = re.compile(r"^## .*$", re.MULTILINE)
CHECKLIST_LINE_RE = re.compile(r"^- \[ \] \[#(\d+) ")


def render_body(
    env: str,
    image_tag: str,
    app_repo_full: str,
    entries: list[tuple[int, str, str]],
) -> str:
    checklist = "\n".join(
        f"- [ ] [#{num} {title}]({url})"
        for num, title, url in entries
    )
    return f"""## 🚀 Deploy to {env}

This PR bumps the image tags to deploy commit `{image_tag}` to **{env}**.

**Image tag:** `ghcr.io/sbillion/medical-appointment-{{backend,frontend}}:{image_tag}`

### App changes included

{checklist}

---

_Maintained automatically by the `Release` workflow in
[`{app_repo_full}`](https://github.com/{app_repo_full}). Every PR merged into
`main` is appended here, and the image tag is moved to the latest commit on
`main`, until this deploy PR is merged._
"""


def parse_existing_entries(body: str) -> list[tuple[int, str, str]]:
    """Extract (number, title, url) tuples from an existing PR body."""
    entries: list[tuple[int, str, str]] = []
    for line in body.splitlines():
        m = re.match(r"^- \[ \] \[#(\d+) (.+?)\]\((https?://\S+)\)\s*$", line)
        if m:
            entries.append((int(m.group(1)), m.group(2), m.group(3)))
    return entries


def find_open_pr(
    config_full: str, head: str, base: str
) -> tuple[int, str] | None:
    """Return (number, body) for the open PR from ``head`` into ``base``."""
    out = run_capture(
        "gh",
        "pr",
        "list",
        "--repo",
        config_full,
        "--head",
        head,
        "--base",
        base,
        "--state",
        "open",
        "--json",
        "number,body",
        "--limit",
        "1",
    )
    if not out or out == "[]":
        return None
    import json

    data = json.loads(out)
    if not data:
        return None
    return int(data[0]["number"]), data[0].get("body", "")


def ensure_label(config_full: str, label: str) -> None:
    """Create the label on the config repo if it doesn't exist."""
    subprocess.run(
        ["gh", "label", "create", label, "--repo", config_full],
        text=True,
        capture_output=True,
    )


def create_pr(
    config_full: str,
    base: str,
    head: str,
    title: str,
    body: str,
    label: str,
    auto_merge: bool,
) -> None:
    ensure_label(config_full, label)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(body)
        body_file = f.name
    run(
        "gh",
        "pr",
        "create",
        "--repo",
        config_full,
        "--base",
        base,
        "--head",
        head,
        "--title",
        title,
        "--body-file",
        body_file,
        "--label",
        label,
    )
    if auto_merge:
        # Enable auto-merge (fast-tracked env). Ignore errors if repo lacks
        # the feature or branch protection blocks it.
        subprocess.run(
            [
                "gh",
                "pr",
                "merge",
                "--repo",
                config_full,
                head,
                "--auto",
                "--squash",
                "--delete-branch",
            ],
            text=True,
        )
    os.unlink(body_file)


def update_pr(
    config_full: str, number: int, title: str, body: str
) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(body)
        body_file = f.name
    run(
        "gh",
        "pr",
        "edit",
        str(number),
        "--repo",
        config_full,
        "--title",
        title,
        "--body-file",
        body_file,
    )
    os.unlink(body_file)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="config repo checkout path")
    p.add_argument("--config-full", required=True, help="owner/name of config repo")
    p.add_argument("--app-full", required=True, help="owner/name of app repo")
    p.add_argument("--env", required=True, help="development | production")
    p.add_argument("--base", required=True, help="config repo base branch")
    p.add_argument("--pending", required=True, help="pending head branch")
    p.add_argument("--values", required=True, help="env values file relpath")
    p.add_argument("--label", required=True, help="PR label")
    p.add_argument("--image-tag", required=True, help="commit SHA image tag")
    p.add_argument("--app-pr-number", type=int, required=True)
    p.add_argument("--app-pr-title", required=True)
    p.add_argument("--app-pr-url", required=True)
    p.add_argument("--auto-merge", action="store_true", help="fast-track the PR")
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"Config repo not found at {repo}", file=sys.stderr)
        return 2

    configure_git(repo)
    reset_pending_branch(repo, args.base, args.pending)
    changed = bump_tags(repo / args.values, args.image_tag)
    if changed:
        commit_and_push(repo, args.pending, args.image_tag, args.env)

    # Ensure the pending branch is pushed even when nothing changed (so the
    # PR branch tracks the latest base and the body can be updated).
    run(
        "git",
        "-C",
        str(repo),
        "push",
        "--force-with-lease",
        "origin",
        args.pending,
    )

    title = f"deploy({args.env}): update image tag to {short(args.image_tag)}"
    existing = find_open_pr(args.config_full, args.pending, args.base)

    new_entry = (args.app_pr_number, args.app_pr_title, args.app_pr_url)

    if existing is None:
        entries = [new_entry]
        body = render_body(
            args.env, args.image_tag, args.app_full, entries
        )
        create_pr(
            args.config_full,
            args.base,
            args.pending,
            title,
            body,
            args.label,
            args.auto_merge,
        )
        print(f"Created deploy PR for {args.env}.")
        return 0

    number, prev_body = existing
    entries = parse_existing_entries(prev_body)
    if not any(e[0] == new_entry[0] for e in entries):
        entries.append(new_entry)
    body = render_body(args.env, args.image_tag, args.app_full, entries)
    update_pr(args.config_full, number, title, body)
    print(f"Updated deploy PR #{number} for {args.env}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
