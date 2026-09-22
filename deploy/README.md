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
| `CONFIG_REPO_PAT` | app repo | GitHub PAT used to push branches and open/update deploy PRs on the config repo. |

The default `GITHUB_TOKEN` is used to push images to GHCR (no extra secret).

#### Creating `CONFIG_REPO_PAT`

The `Release` workflow needs to push branches and open pull requests on the
config repository (`SBillion/medical-appointment-config`). The default
`GITHUB_TOKEN` is scoped to the app repo only, so you need a Personal Access
Token with access to the config repo.

1. **Create the PAT** (GitHub → Settings → Developer settings → Personal access
   tokens → Fine-grained tokens → Generate new token):
   - **Resource owner**: your GitHub account (or the org owning the config repo)
   - **Repository access**: select `SBillion/medical-appointment-config`
   - **Permissions**:
     - `Contents`: Read and write (push branches, force-push pending branches)
     - `Pull requests`: Read and write (create/update deploy PRs, enable auto-merge)
     - `Metadata`: Read (required by GitHub)
   - **Expiration**: 90 days (or your org's policy)

2. **Add it as a repository secret** on the app repo
   (`SBillion/medical-appointment` → Settings → Secrets and variables →
   Actions → New repository secret):
   - Name: `CONFIG_REPO_PAT`
   - Value: paste the token

3. **Verify**: merge a test PR into `main` on the app repo and check the
   `Release` workflow run — it should open a deploy PR on the config repo.

#### ArgoCD repo credentials

ArgoCD also needs to clone both repositories. If they are **public**, no
configuration is needed. If either repo is **private**, register credentials
in ArgoCD:

```bash
argocd repo add https://github.com/SBillion/medical-appointment.git \
  --username <github-username> --password <github-token>

argocd repo add https://github.com/SBillion/medical-appointment-config.git \
  --username <github-username> --password <github-token>
```

Use a separate PAT (or the same one) with `Contents: Read` on both repos.

## Local development

For local development, see the [config repo's LOCAL_SETUP.md](https://github.com/SBillion/medical-appointment-config/blob/main/docs/LOCAL_SETUP.md)
which covers starting minikube, installing ArgoCD, and registering the
ApplicationSet — ArgoCD handles the deployment from there.

To render the chart templates locally without a cluster (requires `helm`):

```bash
helm template medical-appointment deploy/charts/medical-appointment \
  -f deploy/charts/medical-appointment/values-develop.yaml
```
