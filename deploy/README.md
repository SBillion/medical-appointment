# Deployment

This directory holds the Helm chart for deploying the medical-appointment
stack (backend, frontend, PostgreSQL) to Kubernetes.

## GitOps model

The chart templates live **here**, next to the application source. The
per-environment value overrides (and the image tags) live in the
[`medical-appointment-config`](https://github.com/SBillion/medical-appointment-config)
repository. ArgoCD renders the chart from this repo's `main` branch and
applies the env values from the config repo (multi-source Application).

### Release flow

1. A pull request is merged into `main` here.
2. The [`Release`](../.github/workflows/release.yml) workflow builds and pushes
   `ghcr.io/sbillion/medical-appointment-backend:<sha>` and
   `ghcr.io/sbillion/medical-appointment-frontend:<sha>` to GHCR, tagged with
   the merge commit SHA.
3. The workflow opens (or updates) one stacked deploy PR per environment on
   the config repo, bumping the image tag to that SHA.
4. Each deploy PR body lists every app PR that will be deployed, with a
   hyperlink and a checkbox. The image tag is moved to the latest commit on
   `main` on every new merge, until the deploy PR is merged.
   - **development** deploy PR is fast-tracked (auto-merge enabled) → ArgoCD
     auto-syncs the development Application.
   - **production** deploy PR is gated for manual approval → ArgoCD auto-syncs
     the production Application once the PR is merged.

### Required secrets

| Secret | Where | Purpose |
|-------|-------|---------|
| `CONFIG_REPO_PAT` | app repo | GitHub PAT with `repo` scope on the config repo, used to push branches and open/update deploy PRs. |

The default `GITHUB_TOKEN` is used to push images to GHCR (no extra secret).

## Local development

Build images inside your minikube Docker daemon and install the chart with
the local values:

```bash
eval "$(minikube docker-env)"

docker build -t medical-appointment-backend:local  ./backend
docker build -t medical-appointment-frontend:local ./frontend

helm install medical-appointment deploy/charts/medical-appointment \
  -f deploy/charts/medical-appointment/values-develop.yaml
```
