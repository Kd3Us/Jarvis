# Contributing to Jarvis

Thanks for helping out! This guide explains how we work together.

## Branching model

- `main`: stable, demo-ready code. Only updated from `develop`.
- `develop`: integration branch. All feature branches start here.
- Feature branches: `type/JAR-XX-short-description`

Allowed types: `feat`, `fix`, `chore`, `docs`, `test`, `ci`, `refactor`.
Example: `docs/JAR-03-contributing-templates`

```bash
git checkout develop
git pull
git checkout -b feat/JAR-08-frontend-init
```

Never commit directly to `main` or `develop`.

## Commit messages

Format: `type(JAR-XX): short imperative message`

Examples:
- `feat(JAR-08): initialize Vite frontend`
- `docs(JAR-03): add CONTRIBUTING.md`

Keep commits small and focused.

## Pull requests

1. Push your branch and open a PR targeting `develop`.
2. Fill in the PR template.
3. Make sure CI is green (lint and tests) once it is set up.
4. Request a review. A PR needs **1 approval from the project lead** (Code Owner) before merging.
5. Merge with **Squash and merge**, then delete the branch.

Only `develop` -> `main` PRs are used for releases and demos.

## Local checks before pushing

```bash
ruff check .
pytest
```

## Secrets

- Never commit API keys or tokens. Use `.env` (git-ignored) and keep `.env.example` up to date with empty values.
- If a key is pushed by mistake, revoke it immediately. Removing it from the repo is not enough.

## Issues

Use the issue templates (bug report, feature request) and reference the ticket ID (`JAR-XX`) when it exists.