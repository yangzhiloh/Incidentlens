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
