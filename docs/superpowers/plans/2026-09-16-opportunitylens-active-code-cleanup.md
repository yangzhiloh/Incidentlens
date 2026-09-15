# OpportunityLens Active-Code Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove the retired IncidentLens product from the active checkout so OpportunityLens is the only application represented by source, tests, runtime configuration, project metadata, dependencies, and current product documentation.

**Architecture:** Treat this as one atomic repository cleanup. First add durable project-identity tests and observe them fail against the mixed repository. Then delete only the approved legacy paths, update shared files, regenerate the lockfile, and run the complete deterministic verification suite. Git history, historical branches, source-audit evidence, the private `.env`, and all OpportunityLens implementation remain untouched.

**Tech Stack:** Python 3.12, uv, Pytest, Ruff, strict mypy, Typer, Pydantic Settings, Structlog, PowerShell, Git

**Spec:** `docs/superpowers/specs/2026-09-16-opportunitylens-incidentlens-retirement-design.md`

## Global Constraints

1. Work only in the saved checkout on `feature/milestone-2-opportunitylens-cleanup`.
2. Do not create or use a Codex worktree.
3. Do not rewrite Git history, delete branches, rename the local folder, or rename the remote repository.
4. Do not modify the private, untracked `.env` file.
5. Preserve `src/opportunitylens/`, all OpportunityLens tests, and all source-audit evidence and tooling.
6. Delete only the paths approved in the design specification.
7. Keep `pyyaml` and every dependency required by the approved OpportunityLens architecture.
8. Remove `fastembed` and `qdrant-client` because they support only the retired Qdrant design.
9. Use the installed uv executable at `C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe`. Do not reinstall or modify the global uv launcher.
10. Do not push or merge during this implementation task.
11. Do not claim success until focused tests, the full deterministic suite, Ruff, strict mypy, lock validation, CLI smoke testing, reference searches, and final diff review all pass.

---

## File Map

### Create

- `tests/unit/test_project_identity.py`: A packaging-boundary check that the installed distribution is discoverable as OpportunityLens and exposes only its intended console command.

### Delete

- `src/incidentlens/__init__.py`: Retired package marker.
- `src/incidentlens/cli.py`: Retired command-line application.
- `src/incidentlens/config.py`: Retired runtime settings.
- `src/incidentlens/ingestion.py`: Retired scenario ingestion pipeline.
- `src/incidentlens/models.py`: Retired incident domain models.
- `tests/unit/test_cli.py`: Tests for the retired CLI.
- `tests/unit/test_config.py`: Tests for the retired settings.
- `tests/unit/test_ingestion.py`: Tests for the retired ingestion pipeline.
- `tests/unit/test_models.py`: Tests for the retired domain models.
- `docs/design/incidentlens-design.md`: Obsolete product design.
- `docs/design/2026-09-03-scenario-package-loader-design.md`: Obsolete scenario-loader design.

### Modify

- `README.md`: Replace the retired product overview with an accurate OpportunityLens overview, current status, principles, setup, and documentation links.
- `.env.example`: Remove every `INCIDENTLENS_` variable and retain the complete `OPPORTUNITYLENS_` block.
- `pyproject.toml`: Rename the distribution, update its description, remove retired dependencies and script, and narrow Ruff first-party packages.
- `uv.lock`: Regenerate from the revised project metadata and dependency set.
- `docs/superpowers/plans/2026-09-14-opportunitylens-sg-mvp.md`: Remove obsolete coexistence instructions from the current MVP plan.
- `docs/superpowers/specs/2026-09-16-opportunitylens-incidentlens-retirement-design.md`: Clarify that this cleanup plan, like the design record, is retained as historical rationale.

---

### Task 1: Retire the Legacy Product From the Active Codebase

**Files:**

- Create: `tests/unit/test_project_identity.py`
- Delete: `src/incidentlens/__init__.py`
- Delete: `src/incidentlens/cli.py`
- Delete: `src/incidentlens/config.py`
- Delete: `src/incidentlens/ingestion.py`
- Delete: `src/incidentlens/models.py`
- Delete: `tests/unit/test_cli.py`
- Delete: `tests/unit/test_config.py`
- Delete: `tests/unit/test_ingestion.py`
- Delete: `tests/unit/test_models.py`
- Delete: `docs/design/incidentlens-design.md`
- Delete: `docs/design/2026-09-03-scenario-package-loader-design.md`
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `docs/superpowers/plans/2026-09-14-opportunitylens-sg-mvp.md`
- Modify: `docs/superpowers/specs/2026-09-16-opportunitylens-incidentlens-retirement-design.md`

**Step 1: Confirm the branch and protected paths before editing**

Run:

```powershell
git status --short --branch
git branch --show-current
git diff --exit-code -- data/source-audit docs/source-audit scripts/source_audit.py tests/unit/test_source_audit.py
```

Expected:

- The branch is `feature/milestone-2-opportunitylens-cleanup`.
- Only the approved cleanup planning documents are changed or untracked.
- The source-audit paths have no diff.

If any unrelated file is changed, stop and preserve it. Do not overwrite or include it in the cleanup.

**Step 2: Add a failing project-identity test**

Create `tests/unit/test_project_identity.py`:

```python
from importlib.metadata import PackageNotFoundError, distribution

import pytest


def test_installed_distribution_exposes_only_opportunitylens_command() -> None:
    try:
        package = distribution("opportunitylens")
    except PackageNotFoundError:
        pytest.fail("the OpportunityLens distribution is not installed")

    console_scripts = {
        entry_point.name: entry_point.value
        for entry_point in package.entry_points
        if entry_point.group == "console_scripts"
    }

    assert console_scripts == {"opportunitylens": "opportunitylens.cli:app"}
```

This test exercises installed package behavior rather than inspecting `pyproject.toml` text. Before cleanup, Python cannot discover a distribution named `opportunitylens`. After the rename, the distribution must be discoverable and must expose only the intended command.

**Step 3: Run the focused tests and confirm the expected red state**

Run:

```powershell
New-Item -ItemType Directory -Force -Path .test-tmp | Out-Null
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' run pytest tests/unit/test_project_identity.py -q --basetemp=.test-tmp/project-identity-red
```

Expected: one intentional failure with `the OpportunityLens distribution is not installed`. This proves the current installed package identity is still the legacy name.

If a failure has a different cause, diagnose it before deleting anything.

**Step 4: Delete only the approved tracked files**

Run this exact path-scoped removal:

```powershell
git rm -- src/incidentlens/__init__.py src/incidentlens/cli.py src/incidentlens/config.py src/incidentlens/ingestion.py src/incidentlens/models.py tests/unit/test_cli.py tests/unit/test_config.py tests/unit/test_ingestion.py tests/unit/test_models.py docs/design/incidentlens-design.md docs/design/2026-09-03-scenario-package-loader-design.md
```

Then inspect the staged deletion names:

```powershell
git diff --cached --name-status
```

Expected: exactly the eleven approved paths are staged as deletions. The count is five source files, four test files, and two design documents.

**Step 5: Make `pyproject.toml` identify only OpportunityLens**

Apply these exact metadata changes:

```toml
[project]
name = "opportunitylens"
version = "0.1.0"
description = "Evidence-grounded Singapore internship intelligence"
```

Delete these two dependency entries:

```toml
"fastembed>=0.8.0",
"qdrant-client>=1.19.0",
```

Keep all other runtime and development dependencies unchanged, including `pyyaml`.

Replace the scripts table with:

```toml
[project.scripts]
opportunitylens = "opportunitylens.cli:app"
```

Replace the Ruff first-party list with:

```toml
[tool.ruff.lint.isort]
known-first-party = ["opportunitylens", "scripts"]
```

**Step 6: Reduce `.env.example` to the OpportunityLens template**

Delete the complete leading `INCIDENTLENS_` block. The resulting file must contain exactly:

```dotenv
OPPORTUNITYLENS_ENVIRONMENT=development
OPPORTUNITYLENS_LOG_LEVEL=INFO
OPPORTUNITYLENS_DATABASE_URL=postgresql+asyncpg://opportunitylens:opportunitylens@localhost:5432/opportunitylens
OPPORTUNITYLENS_PROVIDER_TIMEOUT_SECONDS=20
OPPORTUNITYLENS_PROVIDER_MAX_RESPONSE_BYTES=5000000
OPPORTUNITYLENS_PROVIDER_CONCURRENCY=4
OPPORTUNITYLENS_PROVIDER_RETRY_ATTEMPTS=2
OPPORTUNITYLENS_MISSING_RUNS_BEFORE_CLOSE=2
OPPORTUNITYLENS_RESUME_MAX_BYTES=5242880
OPPORTUNITYLENS_RRF_K=60
OPPORTUNITYLENS_RETRIEVAL_CANDIDATE_LIMIT=50
OPPORTUNITYLENS_RERANK_LIMIT=20
OPPORTUNITYLENS_ANALYSIS_LIMIT=10
```

Do not read or edit `.env`.

**Step 7: Rewrite `README.md` around the current OpportunityLens reality**

Replace the file with this content:

````markdown
# OpportunityLens SG

OpportunityLens is a local-first portfolio project for evidence-grounded Singapore internship intelligence. It is designed to collect public employer career data, preserve source provenance, and help a candidate compare opportunities without automating job applications.

## Why This Project

Internship information is scattered across employer career sites and applicant tracking systems. Eligibility rules, role status, and evidence quality are often inconsistent or unclear.

OpportunityLens is being built around four principles:

- Keep every material claim linked to inspectable source evidence.
- Represent eligibility as eligible, ineligible, or unknown instead of forcing certainty.
- Make uncertainty and stale data visible.
- Keep the system read-only. It does not submit applications or act on a candidate's behalf.

## Current Status

The OpportunityLens foundation is implemented:

- Typed environment settings with an `OPPORTUNITYLENS_` prefix.
- A Typer command-line entry point with a version command.
- Structured logging configuration.
- A reproducible source-audit workflow for Singapore employer career systems.
- Tests for the implemented foundation and audit tooling.

The domain and evidence contracts, persistence layer, provider adapters, ranking pipeline, evaluation harness, API, and web interface are planned but not implemented yet.

The repository does not claim measured product performance before those evaluations exist. Current source-audit findings are documented separately from future product metrics.

## Technology Direction

The approved architecture uses Python 3.12, PostgreSQL with pgvector, SQLAlchemy, FastAPI, LangGraph, Sentence Transformers, OpenTelemetry, PyYAML, Typer, Structlog, Ruff, mypy, and Pytest. A web interface is planned for a later milestone.

## Local Setup

Install Python 3.12, uv, and Git. Then synchronize the project:

```powershell
uv sync
```

Copy `.env.example` to `.env` and adjust local values when a milestone requires them. The current version command does not require a running database:

```powershell
uv run opportunitylens version
```

Run the deterministic test suite:

```powershell
uv run pytest -q
```

## Project Documentation

- Product design: `docs/superpowers/specs/2026-09-14-opportunitylens-sg-design.md`
- MVP implementation plan: `docs/superpowers/plans/2026-09-14-opportunitylens-sg-mvp.md`
- Source-audit methodology: `docs/source-audit/methodology.md`
- Source-audit findings: `docs/source-audit/findings.md`

Work proceeds in small milestone branches so each concept can be implemented, tested, reviewed, and understood before the next layer is added.
````

**Step 8: Remove obsolete coexistence instructions from the current MVP plan**

In `docs/superpowers/plans/2026-09-14-opportunitylens-sg-mvp.md`, make these exact conceptual replacements:

1. Replace the instruction to restore only the spec from `426e8e4` with a historical note that this restoration is complete and must not be repeated.
2. Replace the instruction to retain `src/incidentlens/` and its tests with: `The legacy prototype is retired from active source, tests, commands, dependencies, and product documentation. Git history and historical branches remain the recovery path.`
3. Replace the repository audit statement describing an incident-analysis prototype with a statement that the checkout now contains the OpportunityLens foundation and source-audit workflow.
4. Replace the expected-diff statement about preserving incident source and tests with a statement that the completed foundation diff preserved all pre-cleanup user files.
5. Replace the dependency instruction to retain inherited incident dependencies with: `Retain all dependencies required by the approved OpportunityLens architecture. Do not reintroduce dependencies used only by the retired prototype.`
6. Replace the scripts example with only:

```toml
[project.scripts]
opportunitylens = "opportunitylens.cli:app"
```

7. Replace the checklist item about inherited incident tests with: `The OpportunityLens tests pass and no saved-checkout user files have changed.`
8. Replace the risk row about losing incident work with a risk about legacy files returning during later work. Its mitigation is to use Git history only as reference and never copy retired runtime files into active paths.
9. Replace the self-review repository-safety statement with one that preserves untracked user paths and source-audit evidence while using only the saved checkout.

After editing, run:

```powershell
rg -n -i "incident" docs/superpowers/plans/2026-09-14-opportunitylens-sg-mvp.md
```

Expected: no output and exit code 1, meaning no obsolete incident references remain in the active MVP plan.

**Step 9: Regenerate and validate the dependency lock**

Run:

```powershell
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' lock
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' sync
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' lock --check
```

Expected:

- Locking, synchronization, and lock validation succeed.
- The local environment removes packages that are no longer reachable from OpportunityLens dependencies.
- The global uv installation is unchanged.

Check that the retired direct dependencies are gone from project metadata and the resolved lock:

```powershell
rg -n -i 'fastembed|qdrant-client' pyproject.toml uv.lock
```

Expected: no output and exit code 1.

**Step 10: Run the focused tests and observe the green state**

Run:

```powershell
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' run pytest tests/unit/test_project_identity.py -q --basetemp=.test-tmp/project-identity-green
```

Expected: the packaging-boundary test passes.

**Step 11: Run the complete deterministic verification suite**

Run each command separately:

```powershell
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' run pytest -q -m "not model and not ollama" --basetemp=.test-tmp/full-cleanup
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' run ruff check src tests scripts
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' run mypy src scripts
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' lock --check
& 'C:\Users\Loh Yang Zhi\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe' run opportunitylens version
```

Expected:

- All remaining deterministic tests pass. Record the actual test count from the command output rather than predicting it.
- Ruff reports no issues.
- Strict mypy reports success for the established `src` and `scripts` scope. Test behavior and
  style remain covered by Pytest and Ruff; pre-existing test-annotation cleanup is deferred.
- The lockfile is current.
- The CLI prints `OpportunityLens SG 0.1.0`.

**Step 12: Prove the retired product is absent from active files**

Run:

```powershell
git ls-files src/incidentlens tests/unit/test_cli.py tests/unit/test_config.py tests/unit/test_ingestion.py tests/unit/test_models.py docs/design/incidentlens-design.md docs/design/2026-09-03-scenario-package-loader-design.md
git grep -n -i incidentlens -- ':!docs/superpowers/specs/2026-09-16-opportunitylens-incidentlens-retirement-design.md' ':!docs/superpowers/plans/2026-09-16-opportunitylens-active-code-cleanup.md'
git diff --exit-code -- data/source-audit docs/source-audit scripts/source_audit.py tests/unit/test_source_audit.py
```

Expected:

- The tracked-path query prints nothing.
- The reference search prints nothing. The two retirement records are intentionally excluded because they explain what was removed and how it can be recovered.
- Source-audit evidence and tooling still have no diff.

Also inspect the untracked-file list without reading private contents:

```powershell
git status --short --untracked-files=all
```

Expected: `.env` remains untracked or ignored and unmodified. No unexpected path is included in the cleanup.

**Step 13: Review the complete diff before committing**

Run:

```powershell
git diff --stat
git diff -- README.md .env.example pyproject.toml tests/unit/test_project_identity.py docs/superpowers/plans/2026-09-14-opportunitylens-sg-mvp.md docs/superpowers/specs/2026-09-16-opportunitylens-incidentlens-retirement-design.md
git diff -- uv.lock
git diff --cached --stat
```

Confirm:

- Every deletion is in the approved list.
- The README contains no unmeasured claims.
- The environment template contains only OpportunityLens variables.
- Project metadata exposes only OpportunityLens.
- Lockfile changes follow only from the project rename and dependency removals.
- No source-audit evidence, OpportunityLens source, OpportunityLens tests, or private user file changed unexpectedly.

**Step 14: Stage the reviewed changes and commit the atomic cleanup**

Stage only the approved paths:

```powershell
git add README.md .env.example pyproject.toml uv.lock tests/unit/test_project_identity.py docs/superpowers/plans/2026-09-14-opportunitylens-sg-mvp.md docs/superpowers/plans/2026-09-16-opportunitylens-active-code-cleanup.md docs/superpowers/specs/2026-09-16-opportunitylens-incidentlens-retirement-design.md
git diff --cached --check
git diff --cached --stat
git status --short
```

The scoped deletions from Step 4 are already staged by `git rm`. If the staged diff includes any path outside the file map, unstage only that unexpected path and investigate before continuing.

Commit:

```powershell
git commit -m "chore: complete OpportunityLens pivot"
```

Then verify the commit without pushing:

```powershell
git status --short --branch
git show --stat --oneline --decorate HEAD
```

Expected:

- The branch is ahead of its base by the new cleanup commit and the earlier approved design commit.
- The working tree is clean except for pre-existing ignored or untracked user files.
- Nothing has been pushed or merged.

---

## Plan Self-Review

1. The plan uses one atomic task because deletion, project identity, dependency locking, and documentation must stay coherent in the same commit.
2. The red test state proves the intended OpportunityLens distribution is not installed before cleanup. The green state proves the installed distribution and console-command boundary afterward.
3. Every destructive operation names exact approved paths. There is no recursive broad deletion, `git clean`, reset, or history rewrite.
4. The private `.env`, historical branches, OpportunityLens implementation, and source-audit evidence are explicitly protected and rechecked.
5. The README distinguishes implemented work from planned work and avoids invented performance claims.
6. Dependency verification checks both direct metadata and the resolved lock.
7. The verification sequence covers behavior, style, production and script types, lock consistency, console packaging, stale references, protected paths, and the final staged diff.
8. Push and merge are deliberately outside this plan so the user can inspect the file changes and commit first.
