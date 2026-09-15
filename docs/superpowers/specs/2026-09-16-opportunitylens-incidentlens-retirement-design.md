# OpportunityLens IncidentLens Active-Code Retirement Design

**Date:** 2026-09-16

**Status:** Approved for implementation

## Context

OpportunityLens began as an in-place pivot beside the earlier IncidentLens prototype. The
foundation milestone deliberately retained both packages so the new configuration, CLI, logging,
and audit tooling could be verified without risking the existing baseline. That checkpoint has now
been merged into `main`.

The coexistence phase is complete. IncidentLens names, source files, tests, documentation,
configuration, console entry points, and dependencies now make the active repository harder to
understand and can cause new work to target the wrong application.

## Decision

Remove IncidentLens from the active codebase in a dedicated cleanup milestone before implementing
the OpportunityLens domain and evidence contracts. Preserve Git history and historical milestone
branches so every removed file remains recoverable and the project evolution remains inspectable.

This cleanup does not rewrite Git history, delete remote branches, rename the GitHub repository,
rename the local repository directory, or modify the private `.env` file.

## Active-Code Removal Scope

Delete these tracked IncidentLens implementation files:

- `src/incidentlens/__init__.py`
- `src/incidentlens/cli.py`
- `src/incidentlens/config.py`
- `src/incidentlens/ingestion.py`
- `src/incidentlens/models.py`

Delete the matching IncidentLens tests:

- `tests/unit/test_cli.py`
- `tests/unit/test_config.py`
- `tests/unit/test_ingestion.py`
- `tests/unit/test_models.py`

Delete the obsolete IncidentLens design documents:

- `docs/design/incidentlens-design.md`
- `docs/design/2026-09-03-scenario-package-loader-design.md`

Update these shared files:

- Rewrite `README.md` around OpportunityLens, its current implemented foundation, its measured
  source audit, its planned architecture, and its limitations. Do not publish unmeasured claims.
- Remove all `INCIDENTLENS_` variables from `.env.example` while retaining the OpportunityLens
  variables.
- Change the project name and description in `pyproject.toml` to OpportunityLens.
- Remove the `incidentlens` console entry point.
- Remove `incidentlens` from Ruff's first-party package list.
- Remove `fastembed` and `qdrant-client`, which belong to the IncidentLens Qdrant architecture.
- Retain `pyyaml` because the approved OpportunityLens plan uses YAML source, model, ranking, and
  analysis configuration files.
- Update the OpportunityLens implementation plan so it no longer instructs contributors to retain
  the IncidentLens runtime, tests, console entry point, or dependencies.
- Regenerate `uv.lock` from the revised `pyproject.toml` using the installed Python 3.12 and uv
  toolchain.

## Preserved Scope

Keep the following:

- All Git commits and historical branches.
- The local repository directory name and GitHub repository name.
- The private, untracked `.env` file.
- `src/opportunitylens/` and all OpportunityLens tests.
- Singapore employer source-audit data, tooling, tests, methodology, and findings.
- The OpportunityLens design specification and implementation plan, updated only where the old
  coexistence decision is now obsolete.
- Shared libraries required by the approved OpportunityLens architecture, including Pydantic,
  Typer, HTTPX, Structlog, FastAPI, SQLAlchemy, PostgreSQL and pgvector support, LangGraph,
  Sentence Transformers, OpenTelemetry, pypdf, and PyYAML.

Generated caches are not repository source. Python bytecode, test caches, type-checking caches, and
the virtual environment may be refreshed by normal tooling but are not part of the tracked cleanup
commit.

## Implementation Sequence

1. Add failing project-identity tests that require the package metadata and console scripts to name
   only OpportunityLens.
2. Confirm the tests fail because `pyproject.toml` still identifies IncidentLens.
3. Delete the scoped IncidentLens source, test, and design files.
4. Update `README.md`, `.env.example`, `pyproject.toml`, and the OpportunityLens implementation
   plan.
5. Regenerate `uv.lock` and synchronize the environment without changing the global uv
   installation.
6. Run the focused identity tests and the remaining deterministic suite.
7. Run Ruff, strict mypy, `uv lock --check`, and `opportunitylens version`.
8. Search tracked product code, tests, runtime configuration, `README.md`, and the active
   implementation plan for case-insensitive `incidentlens` references. The search must return no
   matches. This retirement decision record, its implementation plan, Git history, and historical
   branch contents are excluded from the check.
9. Review the complete deletion and modification diff before committing.

## Verification and Acceptance Criteria

The cleanup is complete only when:

1. `git ls-files` contains no `src/incidentlens`, IncidentLens unit tests, or obsolete IncidentLens
   design paths.
2. Tracked product code, tests, runtime configuration, `README.md`, and the active OpportunityLens
   MVP plan contain no case-insensitive `incidentlens` references. This retirement decision record
   and its implementation plan are retained as historical rationale.
3. `pyproject.toml` names the project `opportunitylens` and exposes only the OpportunityLens console
   entry point.
4. The dependency lock no longer includes FastEmbed or Qdrant Client as direct project
   dependencies.
5. The remaining tests pass with a writable temporary directory.
6. Ruff reports no issues for the remaining source, tests, and scripts. Strict mypy reports no
   issues for `src` and `scripts`, matching the established project verification scope.
7. `uv lock --check` succeeds.
8. `opportunitylens version` prints the expected product name and version.
9. The diff contains no changes to Git history, historical branches, the private `.env` file, or
   source-audit evidence.

## Recovery

All removals occur in an ordinary Git commit on
`feature/milestone-2-opportunitylens-cleanup`. Before the branch is merged, the cleanup can be
reviewed as a pull-request diff. After merge, any removed file can still be recovered from the
historical commits and branches without rewriting repository history.

After this cleanup is merged, Task 3 begins from updated `main` on
`feature/milestone-3-opportunitylens-domain-evidence`.
