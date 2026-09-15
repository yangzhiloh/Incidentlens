# OpportunityLens SG One-Month MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first, evidence-grounded Singapore internship intelligence MVP that ingests two measured public ATS provider types, ranks jobs against a verified candidate profile, explains results with resolvable evidence, and evaluates ranking configurations reproducibly.

**Architecture:** A React client calls a versioned FastAPI API. FastAPI and a small database-backed worker share focused Python services for provider ingestion, canonicalization, lifecycle tracking, candidate profiles, eligibility, retrieval, reranking, evaluation, and bounded match analysis. PostgreSQL stores append-only source snapshots, canonical and derived records, full-text indexes, pgvector embeddings, run state, and provenance; every expensive or failure-prone stage has a deterministic fallback.

**Tech Stack:** Python 3.12, uv, Pydantic 2, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16 with pgvector, HTTPX, Hugging Face Transformers and Sentence Transformers, LangGraph, Ollama, React, TypeScript, Vite, TanStack Query, Vitest, Playwright, Docker Compose, GitHub Actions, Structlog, and OpenTelemetry.

**Spec:** `docs/superpowers/specs/2026-09-14-opportunitylens-sg-design.md`, sourced exactly from Git commit `426e8e4c88726824ee4e79e334d30841a5bea123`.

## Global Constraints

1. Work directly in the saved checkout after a read-only preflight, then create and use the normal branch `feature/opportunitylens-sg-mvp` from the latest `feature/milestone-2-scenario-data` commit. Do not create or use a Codex worktree. Do not reset, clean, or overwrite the untracked `scenarios/` directory or the empty `tmp/` directory.
2. The approved specification was restored from commit `426e8e4`. That historical setup step is complete and must not be repeated.
3. The legacy prototype is retired from active source, tests, commands, dependencies, and product documentation. Git history and historical branches remain the recovery path.
4. The MVP is local-first, single-user, and read-only with respect to external hiring systems. It never applies for a job, scrapes an authenticated page, or bypasses bot protection.
5. Select exactly two initial ATS adapter types from a read-only audit of at least 30 verified employers with Singapore operations. Do not select adapters from intuition.
6. Use the authoritative job identity `(provider, board_identifier, provider_job_identifier)`. A normalized application URL is only a fallback deduplication signal.
7. Raw posting snapshots are append-only. Derived classifications, requirements, embeddings, profiles, ranking configurations, prompts, and evaluation results are versioned.
8. An incomplete provider response must never close an unseen posting. Closure requires an explicit provider status or repeated absence across complete runs.
9. Eligibility has exactly three outcomes: `eligible`, `ineligible`, and `uncertain`. Unknown work-authorization language must not become automatic acceptance or rejection.
10. Every eligibility reason, extracted requirement, and generated match claim resolves to a stored `EvidenceRecord` or explicitly states that evidence is unavailable.
11. Rejected candidate facts never influence eligibility or ranking. Missing profile evidence must be described as “not evidenced in the profile,” never as proof that the candidate lacks a skill.
12. Retrieval compares lexical, dense, hybrid RRF, and hybrid plus cross-encoder configurations. The evaluation also compares hard filters on and off and analyst-only versus analyst-plus-critic on a fixed subset.
13. The initial Replay Lab dataset contains exactly three versioned profiles and at least 60 reviewed profile-posting pairs, including difficult negatives and ambiguous eligibility cases.
14. Record classification macro F1, false-eligible rate, Recall@50, nDCG@10, Precision@10, citation precision, unsupported-claim count, correct abstention rate, and p50 and p95 latency.
15. The LangGraph path is bounded to analyst, deterministic validation, critic, and at most one repair. Deterministic ranked results remain visible if generation is unavailable.
16. The fallback ladder is mandatory: lexical remains when vector search fails; fused results remain when reranking fails; ranked jobs and evidence remain when match generation fails.
17. Resume files and job descriptions are untrusted input. Validate PDF type and size, allowlist provider domains, bound HTTP time and response size, and exclude resume text and contact details from logs and traces.
18. Core review and CI require no paid API, employer account, or live local model. Model-facing tests use deterministic fakes; live Hugging Face and Ollama tests use explicit markers.
19. Published reports and resume text contain only repository-generated measurements. Do not invent, estimate, or silently round impact metrics.
20. Protect scope in this order: application tracking beyond save and hide, in-app digest, visual polish, separate LLM critic, dataset growth beyond 60 pairs, then employer count. Never cut provenance, idempotency, eligibility uncertainty, evaluation, two provider types, or graceful degradation.

---

## Repository Audit and Starting State

The audit performed before writing this plan found:

1. `HEAD` is `06758c4147325d5ea415d37a32c28061cfe9177f` on `feature/milestone-2-scenario-data`.
2. The saved checkout contains the OpportunityLens foundation and reproducible source-audit workflow with Typer, Pydantic, Structlog, Pytest, Ruff, and strict mypy.
3. `scenarios/` is an untracked user directory and `tmp/` is an empty ignored temporary directory. This plan does not modify either path.
4. The approved design branch points to `426e8e4`, whose merge base with the current branch is `b1db09d`. The approved commit contains the new spec plus older changes to several existing files, so it is a reference source, not a safe whole-commit integration.
5. No additional `AGENTS.md` file is present inside the repository. The task-level `AGENTS.md` instructions supplied by the user apply.
6. Ruff and mypy pass on the current source. The 40 current tests pass when pytest uses a writable alternate temporary directory.
7. The workstation’s WinGet `uv.exe` link currently fails to launch. This is an environment prerequisite, not a repository test failure, and must be repaired before lockfile changes.

## Execution Preflight, No Product Commit

- [ ] **Step 1: Reconfirm the saved checkout before creating the feature branch**

Run:

```powershell
git status --short --branch
git log -3 --oneline --decorate
git branch --show-current
```

Expected: `feature/milestone-2-scenario-data` and `06758c4` are displayed, and the untracked user-owned paths are recorded in the execution notes. Do not clean or stage them.

- [ ] **Step 2: Create and switch the normal feature branch in the saved checkout**

Run from the saved checkout:

```powershell
git switch -c feature/opportunitylens-sg-mvp
```

Do not create or use a Codex worktree. The branch must start from the current `HEAD`, not from `426e8e4`.

Expected: `git branch --show-current` reports `feature/opportunitylens-sg-mvp`, `git rev-parse HEAD` still reports `06758c4`, and the untracked user-owned paths remain unchanged.

- [ ] **Step 3: Restore only the approved specification into the saved checkout**

Run inside the saved checkout:

```powershell
git restore --source=426e8e4c88726824ee4e79e334d30841a5bea123 -- docs/superpowers/specs/2026-09-14-opportunitylens-sg-design.md
git diff -- docs/superpowers/specs/2026-09-14-opportunitylens-sg-design.md
```

Expected: the completed foundation diff contains one newly restored design document and preserves all pre-cleanup user files and `scenarios/`.

- [ ] **Step 4: Repair or replace the broken local uv launcher**

Run:

```powershell
uv --version
```

Expected: a version is printed. If Windows still reports that no application is associated with `uv.exe`, repair the user’s uv installation before continuing. Do not regenerate `uv.lock` with a different package manager.

- [ ] **Step 5: Establish the inherited baseline in the saved checkout**

Run:

```powershell
uv sync
uv run pytest -q -p no:cacheprovider --basetemp .test-tmp/baseline
uv run ruff check src tests
uv run mypy src
```

Expected: 40 tests pass, Ruff reports no violations, and mypy reports no issues. If the counts differ because the starting branch advanced or the approved audit commits add tests, record the exact output before making product changes.

## Four-Week Workload and Dependency Map

This is one integrated plan rather than four independent plans because every later slice depends on the same canonical records, evidence IDs, run versions, and failure semantics. The schedule assumes about 30 to 34 focused hours per week and keeps each day centered on one reviewable deliverable.

| Week | Tasks | Target hours | Completion gate |
| --- | --- | ---: | --- |
| 1 | 1 through 6 | 32 | Two repeated ingestions through the first adapter create no duplicate canonical jobs, preserve raw observations, and report partial failures. |
| 2 | 7 through 11 | 28 plus 4 hours buffer | Two provider types use one contract, changed postings re-enrich, incomplete fetches cannot close jobs, and requirements resolve to evidence. |
| 3 | 12 through 17 | 32 | Three profile versions and at least 60 labelled pairs justify a selected ranking configuration with uncertainty visible. |
| 4 | 18 through 23 | 34 | Docker Compose runs the demonstrated flow, CI is deterministic, citations resolve, and all published claims come from raw artifacts. |

Critical dependency chain:

```text
source audit
  -> selected adapter 1 -> canonical ingestion -> selected adapter 2 -> lifecycle and enrichment
  -> candidate profile -> eligibility -> lexical and dense retrieval -> RRF -> reranking
  -> Replay Lab -> API and worker -> React views -> bounded analysis -> release verification
```

## Planned File Structure

Files are grouped by responsibility. Keep modules small even when several are introduced in one task.

```text
data/source-audit/employers.csv
docs/source-audit/methodology.md
docs/source-audit/2026-09-14-findings.md
scripts/source_audit.py

src/opportunitylens/
  __init__.py
  cli.py
  config.py
  logging.py
  domain/{common,evidence,sources,jobs,profiles,ranking,runs}.py
  storage/{database,tables,repositories}.py
  providers/{base,http,registry}.py
  providers/{greenhouse,lever,ashby,workday}.py  # create exactly the two selected by audit
  ingestion/{hashing,normalization,lifecycle,service}.py
  enrichment/{cleanup,rules,requirements,models,service}.py
  profiles/{pdf,extraction,service}.py
  ranking/{eligibility,lexical,dense,fusion,rerank,service}.py
  evaluation/{schema,metrics,runner,report}.py
  analysis/{schemas,providers,citations,graph}.py
  api/{app,deps}.py
  api/routes/{health,sources,runs,profiles,jobs,recommendations,applications,evaluations}.py
  worker/{claim,main}.py

alembic.ini
migrations/env.py
migrations/versions/0001_opportunitylens_core.py
configs/models.yaml
configs/sources.yaml
configs/ranking/{lexical-v1,dense-v1,hybrid-v1,hybrid-rerank-v1,hybrid-no-hard-filters-v1}.yaml
configs/analysis/{analyst-only-v1,analyst-critic-v1}.yaml
configs/prompts/{match-analyst-v1,eligibility-critic-v1}.txt

evaluation/profiles/{verified-developer-redacted,synthetic-ai-intern,synthetic-backend-intern}.json
evaluation/corpora/replay-v1/postings.jsonl
evaluation/datasets/replay-v1.jsonl
evaluation/results/replay-v1-baseline.json
evaluation/results/replay-v1-analysis.json
evaluation/reports/replay-v1-baseline.md
evaluation/reports/replay-v1-analysis.md

web/
  package.json
  package-lock.json
  vite.config.ts
  playwright.config.ts
  src/{main,App}.tsx
  src/api/{client,types}.ts
  src/pages/{ProfilePage,OpportunitiesPage,OpportunityDetailPage,SourceStatusPage,ReplayLabPage}.tsx
  src/components/{EvidenceLink,EligibilityBadge,ScoreBreakdown,UncertaintyNotice}.tsx
  src/test/setup.ts
  tests/happy-path.spec.ts

docker/api.Dockerfile
docker/web.Dockerfile
docker-compose.yml
.github/workflows/ci.yml
docs/architecture.md
docs/evaluation.md
docs/limitations.md
docs/demo-script.md
```

The two adapter modules are the only conditional paths. The audit chooses exactly two from this fixed path mapping:

| Audit value | Adapter path | Fixture directory | Unit test path | Commit message |
| --- | --- | --- | --- | --- |
| `greenhouse` | `src/opportunitylens/providers/greenhouse.py` | `tests/fixtures/providers/greenhouse/` | `tests/unit/providers/test_greenhouse.py` | `feat: add Greenhouse provider adapter` |
| `lever` | `src/opportunitylens/providers/lever.py` | `tests/fixtures/providers/lever/` | `tests/unit/providers/test_lever.py` | `feat: add Lever provider adapter` |
| `ashby` | `src/opportunitylens/providers/ashby.py` | `tests/fixtures/providers/ashby/` | `tests/unit/providers/test_ashby.py` | `feat: add Ashby provider adapter` |
| `workday` | `src/opportunitylens/providers/workday.py` | `tests/fixtures/providers/workday/` | `tests/unit/providers/test_workday.py` | `feat: add Workday provider adapter` |

---

## Week 1: Pivot and Reliable Source Ingestion

### Task 1: Audit Singapore Employer ATS Coverage and Select Two Providers

**Estimate:** 6 hours

**Depends on:** execution preflight only

**Files:**

- Create: `data/source-audit/employers.csv`
- Create: `docs/source-audit/methodology.md`
- Create: `docs/source-audit/2026-09-14-findings.md`
- Create: `scripts/source_audit.py`
- Create: `tests/unit/test_source_audit.py`
- Modify: `.gitignore`

**Interfaces:**

- Produces: `load_audit(path: Path) -> tuple[AuditRow, ...]`
- Produces: `select_providers(rows: Sequence[AuditRow]) -> tuple[AtsProvider, AtsProvider]`
- Produces: a committed CSV with at least 30 verified rows and a findings document that names the measured top two feasible providers.
- Consumed by: Tasks 5 and 7, which must not start until the selection command succeeds.

- [ ] **Step 1: Define the audit method before collecting results**

Write `docs/source-audit/methodology.md` with these exact inclusion and exclusion rules:

```markdown
Include an employer only after its official careers site visibly offers Singapore as a location, office, or job location. Inspect public employer careers pages and public network responses only. Do not sign in, solve access challenges, bypass bot controls, or use aggregators as evidence. Record the official careers URL, observed ATS provider, board identifier, public accessibility, observed total posting count, observed Singapore posting count, observed Singapore internship count, completeness notes, evidence URL, and UTC observation time. If access is blocked or ownership is ambiguous, record that outcome rather than guessing.
```

Use this 30-name candidate set only as a starting queue, not as pre-verified audit facts: DBS, OCBC, UOB, Grab, Sea, Shopee, ByteDance, GovTech Singapore, ST Engineering, Singtel, NCS, Singapore Airlines, Changi Airport Group, Temasek, GIC, Standard Chartered, Citi, JPMorgan Chase, Goldman Sachs, Morgan Stanley, HSBC, Mastercard, Visa, Microsoft, Google, Amazon, Apple, Salesforce, SAP, and Siemens. Replace any candidate that cannot be verified with the next audited large employer until the CSV contains 30 included rows.

- [ ] **Step 2: Write the failing audit validation and selection tests**

```python
def test_select_providers_uses_measured_coverage() -> None:
    rows = (
        audit_row("a", "greenhouse", accessible=True, sg_internships=2),
        audit_row("b", "greenhouse", accessible=True, sg_internships=1),
        audit_row("c", "lever", accessible=True, sg_internships=4),
        audit_row("d", "ashby", accessible=True, sg_internships=1),
    )
    assert select_providers(rows) == (AtsProvider.GREENHOUSE, AtsProvider.LEVER)


def test_audit_requires_thirty_verified_employers() -> None:
    with pytest.raises(AuditValidationError, match="at least 30"):
        validate_audit((audit_row("a", "greenhouse", accessible=True),))
```

The selection rule is deterministic: count distinct publicly accessible employers with a nonempty board identifier, exclude providers marked infeasible, sort by employer coverage descending, then observed Singapore internship count descending, then provider enum value ascending. Workday is feasible only when a public JSON endpoint, pagination behavior, and stable board or tenant identifier are all verified.

- [ ] **Step 3: Run the focused tests and confirm the module is absent**

Run:

```powershell
uv run pytest tests/unit/test_source_audit.py -q
```

Expected: collection fails because `scripts.source_audit` does not exist.

- [ ] **Step 4: Implement the typed CSV loader and selector**

Use these exact columns and enums in `scripts/source_audit.py`:

```python
class AuditRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    company_slug: str
    company_name: str
    singapore_presence_evidence_url: HttpUrl
    careers_url: HttpUrl
    provider: Literal["greenhouse", "lever", "ashby", "workday", "other", "unknown"]
    board_identifier: str | None
    public_access: Literal["yes", "partial", "blocked", "no"]
    provider_feasible: bool
    total_postings_observed: int = Field(ge=0)
    singapore_postings_observed: int = Field(ge=0)
    singapore_internships_observed: int = Field(ge=0)
    evidence_url: HttpUrl
    observed_at: AwareDatetime
    notes: str
```

`validate_audit()` must reject duplicate company slugs, fewer than 30 included employers, future timestamps, accessible rows without a board identifier, and counts where internships exceed Singapore postings or Singapore postings exceed total postings.

- [ ] **Step 5: Run unit tests**

Run:

```powershell
uv run pytest tests/unit/test_source_audit.py -q
uv run ruff check scripts/source_audit.py tests/unit/test_source_audit.py
uv run mypy scripts/source_audit.py
```

Expected: all audit tests pass, Ruff is clean, and mypy reports no issues.

- [ ] **Step 6: Perform the read-only audit and populate all evidence fields**

For each employer, use the official careers site and browser network inspection. Save only public URLs, identifiers, counts, UTC observation time, and concise notes. Do not save cookies, tokens, email addresses, or response bodies in the audit CSV.

Run after every ten rows:

```powershell
uv run python scripts/source_audit.py validate data/source-audit/employers.csv
```

Expected at 30 included rows: `audit valid: 30 employers` or a higher verified count.

- [ ] **Step 7: Generate and review the provider decision**

Run:

```powershell
uv run python scripts/source_audit.py report data/source-audit/employers.csv docs/source-audit/2026-09-14-findings.md
```

Expected: the report lists coverage and observed counts for Greenhouse, Lever, Ashby, Workday, other, and unknown; names exactly two selected feasible provider types; links every conclusion to CSV rows; and states that observed counts are a dated sample rather than market coverage claims.

If fewer than two feasible providers are found, audit ten additional verified employers and rerun the report. Do not start adapter code with only one measured provider.

- [ ] **Step 8: Commit the audit decision boundary**

```powershell
git add data/source-audit/employers.csv docs/source-audit/methodology.md docs/source-audit/2026-09-14-findings.md scripts/source_audit.py tests/unit/test_source_audit.py .gitignore
git commit -m "docs: audit Singapore employer ATS coverage"
```

Expected: one commit contains the method, raw audit table, deterministic selection logic, tests, and generated findings.

### Task 2: Create the OpportunityLens Package and Configuration Foundation

**Estimate:** 4 hours

**Depends on:** Task 1

**Files:**

- Create: `src/opportunitylens/__init__.py`
- Create: `src/opportunitylens/cli.py`
- Create: `src/opportunitylens/config.py`
- Create: `src/opportunitylens/logging.py`
- Create: `tests/unit/test_opportunity_config.py`
- Create: `tests/unit/test_opportunity_cli.py`
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `.env.example`
- Modify: `.gitignore`

**Interfaces:**

- Produces: `Settings` with database, provider HTTP, model, upload, and run settings.
- Produces: Typer entry point `opportunitylens`.
- Produces: `configure_logging(settings: Settings) -> None` with automatic secret and PII key redaction.
- Consumed by: every later Python task.

- [ ] **Step 1: Write failing strict-settings tests**

```python
def test_provider_timeout_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Settings(provider_timeout_seconds=0)


def test_default_upload_limit_is_five_mebibytes() -> None:
    assert Settings().resume_max_bytes == 5 * 1024 * 1024


def test_cli_reports_opportunitylens_name() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "OpportunityLens SG" in result.stdout
```

- [ ] **Step 2: Run tests and confirm the new package is missing**

```powershell
uv run pytest tests/unit/test_opportunity_config.py tests/unit/test_opportunity_cli.py -q
```

Expected: imports fail for `opportunitylens`.

- [ ] **Step 3: Add focused runtime and development dependencies**

Add runtime dependencies for `alembic`, `asyncpg`, `fastapi`, `langgraph`, `opentelemetry-api`, `opentelemetry-sdk`, `pgvector`, `pypdf`, `python-multipart`, `sentence-transformers`, `sqlalchemy`, and `uvicorn`. Add development dependencies for `asgi-lifespan`, `pytest-asyncio`, and `respx`. Retain all dependencies required by the approved OpportunityLens architecture. Do not reintroduce dependencies used only by the retired prototype.

Run:

```powershell
uv lock
uv sync
```

Expected: `uv.lock` resolves on Python 3.12 with no paid service dependency.

- [ ] **Step 4: Implement settings and safe structured logging**

Use `OPPORTUNITYLENS_` as the environment prefix. Include exact defaults for:

```python
database_url = "postgresql+asyncpg://opportunitylens:opportunitylens@localhost:5432/opportunitylens"
provider_timeout_seconds = 20.0
provider_max_response_bytes = 5_000_000
provider_concurrency = 4
provider_retry_attempts = 2
missing_runs_before_close = 2
resume_max_bytes = 5 * 1024 * 1024
rrf_k = 60
retrieval_candidate_limit = 50
rerank_limit = 20
analysis_limit = 10
```

Redact structured-log keys matching `resume_text`, `email`, `phone`, `authorization`, `cookie`, and `token` before rendering.

- [ ] **Step 5: Expose the OpportunityLens console entry point**

```toml
[project.scripts]
opportunitylens = "opportunitylens.cli:app"
```

This makes the OpportunityLens package executable through its own command.

- [ ] **Step 6: Verify the foundation**

```powershell
uv run pytest tests/unit/test_opportunity_config.py tests/unit/test_opportunity_cli.py -q
uv run ruff check src/opportunitylens tests/unit/test_opportunity_config.py tests/unit/test_opportunity_cli.py
uv run mypy src/opportunitylens
uv run opportunitylens version
```

Expected: focused tests and static checks pass, and the CLI prints the package version and product name.

- [ ] **Step 7: Commit**

```powershell
git add pyproject.toml uv.lock .env.example .gitignore src/opportunitylens tests/unit/test_opportunity_config.py tests/unit/test_opportunity_cli.py
git commit -m "chore: scaffold OpportunityLens runtime"
```

### Task 3: Define Strict Domain and Evidence Contracts

**Estimate:** 6 hours

**Depends on:** Task 2

**Files:**

- Create: `src/opportunitylens/domain/common.py`
- Create: `src/opportunitylens/domain/evidence.py`
- Create: `src/opportunitylens/domain/sources.py`
- Create: `src/opportunitylens/domain/jobs.py`
- Create: `src/opportunitylens/domain/profiles.py`
- Create: `src/opportunitylens/domain/ranking.py`
- Create: `src/opportunitylens/domain/runs.py`
- Create: `src/opportunitylens/domain/__init__.py`
- Create: `tests/unit/domain/test_sources.py`
- Create: `tests/unit/domain/test_jobs.py`
- Create: `tests/unit/domain/test_evidence.py`
- Create: `tests/unit/domain/test_profiles.py`
- Create: `tests/unit/domain/test_ranking.py`
- Create: `tests/unit/domain/test_runs.py`

**Interfaces:**

- Produces: all cross-layer Pydantic contracts and enums.
- Produces: `JobIdentity(provider, board_identifier, provider_job_identifier)`.
- Produces: tagged `WebLocator`, `DocumentLocator`, and `UserInputLocator` union.
- Produces: `assert_evidence_resolves(claim_ids, available_ids) -> None`.
- Consumed by: storage, providers, ingestion, enrichment, ranking, evaluation, API, worker, and web OpenAPI types.

- [ ] **Step 1: Write failing tests for immutability, unknown fields, and job identity**

```python
def test_job_identity_uses_provider_board_and_provider_id() -> None:
    identity = JobIdentity(
        provider=AtsProvider.GREENHOUSE,
        board_identifier="example-board",
        provider_job_identifier="123",
    )
    assert identity.stable_key == "greenhouse:example-board:123"


def test_domain_models_forbid_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CompanySource.model_validate(valid_source() | {"surprise": True})
```

- [ ] **Step 2: Write failing evidence and candidate-state tests**

```python
def test_document_locator_rejects_reversed_offsets() -> None:
    with pytest.raises(ValidationError):
        DocumentLocator(document_id=uuid4(), page=1, start_offset=20, end_offset=10)


def test_rejected_fact_cannot_be_rankable() -> None:
    fact = candidate_fact(verification_status=VerificationStatus.REJECTED)
    assert fact.can_influence_ranking is False
```

- [ ] **Step 3: Write failing eligibility and claim-invariant tests**

```python
def test_match_result_rejects_unresolved_evidence() -> None:
    with pytest.raises(ValidationError, match="unresolved evidence"):
        MatchResult.model_validate(match_payload(evidence_ids=["missing"]), context={"available_evidence_ids": set()})


def test_eligibility_has_only_three_states() -> None:
    assert {item.value for item in EligibilityDecision} == {"eligible", "ineligible", "uncertain"}
```

- [ ] **Step 4: Run tests and see import failures**

```powershell
uv run pytest tests/unit/domain -q
```

Expected: tests fail because the domain modules do not exist.

- [ ] **Step 5: Implement the shared immutable base and enums**

Every boundary model inherits:

```python
class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
```

Define exact enums for `AtsProvider`, `LifecycleStatus`, `RunStatus`, `SourceFetchStatus`, `VerificationStatus`, `EligibilityDecision`, `RequirementImportance`, `EvidenceEntityType`, and `EvidenceSourceType`.

- [ ] **Step 6: Implement the source and observation contracts**

Create `CompanySource`, `RawProviderPosting`, `ProviderError`, `ProviderResult`, `RawPostingSnapshot`, `PostingObservation`, `IngestionRun`, and `SourceRunResult`. `ProviderResult.complete` is false whenever pagination ends unexpectedly, validation drops a record, a response is truncated, or the provider reports partial results.

- [ ] **Step 7: Implement canonical jobs and versioned derivations**

Create `StructuredLocation`, `JobPosting`, `JobRequirement`, `JobClassification`, and `PostingEmbedding`. Enforce timezone-aware timestamps, nonempty original location text, authoritative identity, and lifecycle transitions represented as new observations rather than mutation of raw source data.

- [ ] **Step 8: Implement profiles, evidence, and ranking contracts**

Create `EvidenceRecord`, locator union, `CandidateFact`, `CandidateConstraints`, `CandidatePreferences`, `CandidateProfileVersion`, `EligibilityReason`, `EligibilityResult`, `ComponentScores`, `RankingConfiguration`, `MatchClaim`, and `MatchResult`. Make evidence IDs explicit on each eligibility reason and match claim.

- [ ] **Step 9: Verify every contract**

```powershell
uv run pytest tests/unit/domain -q
uv run ruff check src/opportunitylens/domain tests/unit/domain
uv run mypy src/opportunitylens/domain
```

Expected: all domain tests pass; strict mypy reports no mismatched tagged-union handling.

- [ ] **Step 10: Commit**

```powershell
git add src/opportunitylens/domain tests/unit/domain
git commit -m "feat: define OpportunityLens domain contracts"
```

### Task 4: Add PostgreSQL, pgvector, Migrations, and Repositories

**Estimate:** 6 hours

**Depends on:** Task 3

**Files:**

- Create: `src/opportunitylens/storage/__init__.py`
- Create: `src/opportunitylens/storage/database.py`
- Create: `src/opportunitylens/storage/tables.py`
- Create: `src/opportunitylens/storage/repositories.py`
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/versions/0001_opportunitylens_core.py`
- Create: `tests/integration/storage/test_migrations.py`
- Create: `tests/integration/storage/test_repositories.py`
- Create: `tests/conftest.py`
- Create: `docker-compose.yml`
- Modify: `pyproject.toml`

**Interfaces:**

- Produces: `create_engine(settings: Settings) -> AsyncEngine` and `session_scope() -> AsyncIterator[AsyncSession]`.
- Produces: `SourceRepository`, `IngestionRepository`, `JobRepository`, `EvidenceRepository`, `ProfileRepository`, `RecommendationRepository`, and `EvaluationRepository`.
- Consumed by: every service and route after this task.

- [ ] **Step 1: Write the failing migration smoke test**

```python
@pytest.mark.postgres
async def test_migration_creates_pgvector_and_core_tables(db_url: str) -> None:
    await run_alembic_upgrade(db_url)
    names = await table_names(db_url)
    assert {"company_sources", "raw_posting_snapshots", "job_postings", "evidence_records", "run_records"} <= names
    assert await extension_exists(db_url, "vector")
```

- [ ] **Step 2: Write the failing repository invariants**

```python
@pytest.mark.postgres
async def test_job_upsert_is_idempotent(repositories: Repositories) -> None:
    first = await repositories.jobs.upsert(canonical_job())
    second = await repositories.jobs.upsert(canonical_job())
    assert first.job_id == second.job_id
    assert await repositories.jobs.count() == 1


@pytest.mark.postgres
async def test_raw_snapshots_are_append_only(repositories: Repositories) -> None:
    snapshot = await repositories.ingestion.append_snapshot(raw_snapshot())
    with pytest.raises(AppendOnlyViolation):
        await repositories.ingestion.replace_snapshot(snapshot.snapshot_id, {"changed": True})
```

- [ ] **Step 3: Start only the database service and confirm the tests fail**

Use `pgvector/pgvector:pg16`, a named volume, a health check using `pg_isready`, and port `5432` for local development.

```powershell
docker compose up -d db
uv run pytest tests/integration/storage -q -m postgres
```

Expected: tests fail because migrations and repositories are not implemented.

- [ ] **Step 4: Create the normalized schema**

The first migration creates tables for company sources, run records, per-source run results, raw snapshots, canonical postings, posting observations, evidence records, classifications, requirements, embeddings, candidate documents, candidate facts, profile versions, profile-version facts, recommendation runs, match results, recommendation feedback, application states, evaluation runs, and evaluation artifacts.

Required uniqueness and indexes:

```text
UNIQUE(provider, board_identifier, provider_job_identifier) on job_postings
UNIQUE(run_id, job_id) on posting_observations
INDEX(content_hash) on raw_posting_snapshots
GIN(to_tsvector('english', searchable_text)) on job_postings
HNSW(embedding vector_cosine_ops) on posting_embeddings
UNIQUE(profile_id, version_number) on candidate_profile_versions
```

Store original provider payloads as JSONB. Use `ON DELETE CASCADE` from candidate documents to extracted facts and embeddings. Evaluation artifacts must not reference private resume documents unless they were explicitly copied as redacted or synthetic data.

- [ ] **Step 5: Implement repository methods used by later tasks**

Use these exact signatures:

```python
async def append_snapshot(self, snapshot: RawPostingSnapshot) -> UUID: ...
async def upsert(self, posting: JobPosting) -> JobPosting: ...
async def record_observation(self, observation: PostingObservation) -> None: ...
async def list_seen_provider_ids(self, run_id: UUID, source_id: UUID) -> set[str]: ...
async def list_active_for_source(self, source_id: UUID) -> tuple[JobPosting, ...]: ...
async def save_evidence(self, records: Sequence[EvidenceRecord]) -> None: ...
async def create_run(self, kind: RunKind, configuration: Mapping[str, JsonValue]) -> RunRecord: ...
async def transition_run(self, run_id: UUID, expected: RunStatus, target: RunStatus) -> RunRecord: ...
```

Run transitions use an expected current status so duplicate workers cannot silently overwrite each other.

- [ ] **Step 6: Apply migrations and run integration tests**

```powershell
uv run alembic upgrade head
uv run pytest tests/integration/storage -q -m postgres
uv run alembic downgrade base
uv run alembic upgrade head
```

Expected: repository tests pass, and the downgrade and upgrade cycle succeeds on an empty test database.

- [ ] **Step 7: Run static checks and commit**

```powershell
uv run ruff check src/opportunitylens/storage tests/integration/storage migrations
uv run mypy src/opportunitylens/storage
git add pyproject.toml uv.lock docker-compose.yml alembic.ini migrations src/opportunitylens/storage tests/conftest.py tests/integration/storage
git commit -m "feat: persist OpportunityLens provenance"
```

Expected: the commit contains only database foundation and repository behavior.

### Task 5: Define the Provider Contract, Safe HTTP Policy, and First Selected Adapter

**Estimate:** 5 hours

**Depends on:** Tasks 1, 3, and 4

**Files:**

- Create: `src/opportunitylens/providers/__init__.py`
- Create: `src/opportunitylens/providers/base.py`
- Create: `src/opportunitylens/providers/http.py`
- Create: `src/opportunitylens/providers/registry.py`
- Create: `configs/sources.yaml`
- Create exactly one adapter path from the fixed mapping in Planned File Structure
- Create its matching fixture directory and unit test path
- Create: `tests/unit/providers/test_contract.py`
- Create: `tests/unit/providers/test_http.py`
- Create: `tests/unit/providers/test_registry.py`
- Create: `tests/integration/providers/test_live_sources.py`
- Modify: `docs/source-audit/2026-09-14-findings.md`

**Interfaces:**

- Produces: `ProviderAdapter.fetch_postings(source: CompanySource, context: FetchContext) -> ProviderResult`.
- Produces: `BoundedHttpClient.get_json(request: ProviderRequest) -> HttpPayload`.
- Produces: `get_adapter(provider: AtsProvider) -> ProviderAdapter` for the first selected provider.
- Produces: `load_sources(path: Path) -> tuple[CompanySource, ...]` for the curated runtime registry.
- Consumed by: Task 6 ingestion orchestration and Task 7’s second adapter.

- [ ] **Step 1: Copy two representative public responses for the first selected provider into fixtures**

Capture one single-page success and one pagination, empty-board, or provider-error case from an employer in the audit. Remove request headers, cookies, contact fields, tracking parameters, and unrelated personal data. Add `source.json` beside each response with the public URL, UTC capture time, provider type, and SHA-256 of the unmodified response.

Expected fixture layout is exactly one of these four fixed directory sets, chosen by the audit:

```text
tests/fixtures/providers/greenhouse/single-page/{response.json,source.json}
tests/fixtures/providers/greenhouse/edge-case/{response.json,source.json}
tests/fixtures/providers/lever/single-page/{response.json,source.json}
tests/fixtures/providers/lever/edge-case/{response.json,source.json}
tests/fixtures/providers/ashby/single-page/{response.json,source.json}
tests/fixtures/providers/ashby/edge-case/{response.json,source.json}
tests/fixtures/providers/workday/single-page/{response.json,source.json}
tests/fixtures/providers/workday/edge-case/{response.json,source.json}
```

Create only the two lines for the first selected provider in this task. No filename varies.

- [ ] **Step 2: Write the failing provider contract test**

```python
@pytest.mark.asyncio
async def test_adapter_preserves_provider_identity_and_original_payload(adapter: ProviderAdapter) -> None:
    result = await adapter.fetch_postings(source_fixture(), fetch_context())
    assert result.provider == source_fixture().provider
    assert result.company_id == source_fixture().company_id
    assert result.request_count >= 1
    assert result.raw_postings
    assert all(item.provider_job_identifier for item in result.raw_postings)
    assert all(item.original_payload for item in result.raw_postings)
```

- [ ] **Step 3: Write failing HTTP safety tests with respx**

```python
@pytest.mark.asyncio
async def test_http_client_rejects_non_allowlisted_host(client: BoundedHttpClient) -> None:
    with pytest.raises(ProviderConfigurationError, match="allowlisted"):
        await client.get_json(provider_request("https://example.invalid/jobs"))


@pytest.mark.asyncio
async def test_http_client_honors_retry_after(client: BoundedHttpClient, clock: FakeClock) -> None:
    route = respx.get(ALLOWED_URL).mock(side_effect=[Response(429, headers={"Retry-After": "2"}), Response(200, json={"jobs": []})])
    await client.get_json(provider_request(ALLOWED_URL))
    assert route.call_count == 2
    assert clock.sleeps == [2.0]


@pytest.mark.asyncio
async def test_http_client_stops_at_response_limit(client: BoundedHttpClient) -> None:
    with pytest.raises(ProviderResponseTooLarge):
        await client.get_json(provider_request(ALLOWED_URL), max_bytes=128)
```

- [ ] **Step 4: Run focused tests and confirm failure**

```powershell
uv run pytest tests/unit/providers -q
```

Expected: imports fail because provider modules are absent.

- [ ] **Step 5: Implement the common provider protocol and result semantics**

```python
class ProviderAdapter(Protocol):
    async def fetch_postings(
        self,
        source: CompanySource,
        context: FetchContext,
    ) -> ProviderResult: ...
```

`FetchContext` includes correlation ID, timeout seconds, max bytes, request budget, retry attempts, and allowlisted hosts. Each company returns one of `success`, `partial`, `rate_limited`, `unavailable`, `invalid_response`, or `configuration_error`. A failed company must return a typed error without raising past the run coordinator.

- [ ] **Step 6: Create and validate the curated source registry**

Copy only audited companies served by either selected provider into `configs/sources.yaml`. Each entry contains stable company UUID, slug, display name, provider enum, board identifier, careers URL, allowed API hosts, country scope `["SG"]`, and enabled state. Write `test_registry.py` to reject duplicate IDs or slugs, providers outside the selected pair, missing board identifiers, careers and API host mismatches, and non-HTTPS URLs.

- [ ] **Step 7: Implement the bounded HTTP client**

Use one shared `httpx.AsyncClient`, an `asyncio.Semaphore`, explicit connect/read/write/pool timeouts, a streaming byte counter, and at most two retries for timeout, HTTP 429, and HTTP 5xx. Respect numeric `Retry-After` values up to 60 seconds. Do not retry HTTP 401, 403, 404, schema validation errors, or configuration errors.

- [ ] **Step 8: Implement only the first measured adapter**

The adapter handles its provider’s pagination, validates each raw record with a provider-specific private Pydantic model, converts valid records to `RawProviderPosting`, records record-level errors, increments request count, and marks the result incomplete if any page or record cannot be trusted.

Do not classify internships, infer Singapore relevance, clean descriptions, or calculate hashes in the adapter.

- [ ] **Step 9: Verify fixtures and one opt-in live source**

```powershell
uv run pytest tests/unit/providers -q
uv run pytest tests/integration/providers/test_live_sources.py -q -m live_provider
```

Expected: fixture tests always pass. The live test is skipped unless `OPPORTUNITYLENS_LIVE_PROVIDER_TESTS=1`; when enabled, it fetches one allowlisted audited board and checks only the public contract, never a fixed posting count.

- [ ] **Step 10: Run static checks and commit with the exact provider-specific message**

```powershell
uv run ruff check src/opportunitylens/providers tests/unit/providers tests/integration/providers
uv run mypy src/opportunitylens/providers
git add src/opportunitylens/providers configs/sources.yaml tests/unit/providers tests/integration/providers tests/fixtures/providers docs/source-audit/2026-09-14-findings.md
```

Use the commit message from the selected provider’s row in the fixed mapping.

### Task 6: Normalize, Hash, Persist, and Expose Idempotent Ingestion

**Estimate:** 5 hours

**Depends on:** Tasks 4 and 5

**Files:**

- Create: `src/opportunitylens/ingestion/__init__.py`
- Create: `src/opportunitylens/ingestion/hashing.py`
- Create: `src/opportunitylens/ingestion/normalization.py`
- Create: `src/opportunitylens/ingestion/service.py`
- Create: `tests/unit/ingestion/test_hashing.py`
- Create: `tests/unit/ingestion/test_normalization.py`
- Create: `tests/integration/ingestion/test_service.py`
- Modify: `src/opportunitylens/cli.py`
- Modify: `src/opportunitylens/storage/repositories.py`
- Modify: `tests/unit/test_opportunity_cli.py`

**Interfaces:**

- Produces: `canonical_content_hash(payload: Mapping[str, JsonValue]) -> str`.
- Produces: `normalize_posting(source: CompanySource, raw: RawProviderPosting, fetched_at: datetime) -> NormalizedPosting`.
- Produces: `run_ingestion(source_ids: Sequence[UUID] | None, requested_by: str) -> IngestionRunSummary`.
- Consumed by: lifecycle, enrichment, API, and worker tasks.

- [ ] **Step 1: Write failing deterministic normalization tests**

```python
def test_hash_ignores_json_key_order_but_not_content() -> None:
    assert canonical_content_hash({"a": 1, "b": 2}) == canonical_content_hash({"b": 2, "a": 1})
    assert canonical_content_hash({"a": 1}) != canonical_content_hash({"a": 2})


def test_normalizer_preserves_original_description_and_location() -> None:
    normalized = normalize_posting(source(), raw_posting(description="<p>Build AI</p>", location="Singapore"), NOW)
    assert normalized.posting.original_description == "<p>Build AI</p>"
    assert normalized.posting.locations[0].original_text == "Singapore"
    assert normalized.evidence[0].locator.field_path == "description"
```

- [ ] **Step 2: Write the failing end-to-end idempotency test**

```python
@pytest.mark.postgres
async def test_repeating_same_fixture_does_not_duplicate_canonical_jobs(app_services: Services) -> None:
    first = await app_services.ingestion.run_ingestion([SOURCE_ID], "test")
    second = await app_services.ingestion.run_ingestion([SOURCE_ID], "test")
    assert first.canonical_jobs_seen == second.canonical_jobs_seen
    assert await app_services.repositories.jobs.count() == first.canonical_jobs_seen
    assert await app_services.repositories.ingestion.snapshot_count() == 2 * first.raw_postings_seen
    assert await app_services.repositories.ingestion.observation_count() == 2 * first.raw_postings_seen
```

This test deliberately expects a new immutable snapshot and observation per fetch while canonical job identity stays idempotent.

- [ ] **Step 3: Run focused tests and confirm failures**

```powershell
uv run pytest tests/unit/ingestion tests/integration/ingestion/test_service.py -q
```

Expected: the tests fail because the ingestion service is absent.

- [ ] **Step 4: Implement canonical normalization and evidence capture**

Normalize known HTML whitespace, application URLs, timestamps, and location aliases. Preserve the original payload, description, URL, and location string. Generate `EvidenceRecord` entries for title, description, location, employment type, published date, and deadline when present. Evidence identifiers must derive from snapshot ID plus provider field path so every value resolves to one observation.

- [ ] **Step 5: Implement per-source fault isolation and run summaries**

For each enabled source:

1. Append the raw snapshot before deriving a canonical job.
2. Upsert by authoritative identity.
3. Record the observation and content hash.
4. Continue after a typed company-level failure.
5. Mark the overall run `completed_with_errors` if any source is partial or failed.
6. Store counts and typed errors without resume or description content in the run record.

- [ ] **Step 6: Add the CLI command**

Expose:

```text
opportunitylens ingest --source fixture-first-provider
opportunitylens ingest --all-enabled
opportunitylens runs show latest
```

The CLI prints the run ID, final status, source counts, raw posting count, canonical job count, new count, changed count, error count, and completeness. It exits nonzero only if the run itself fails to start or reaches `failed`; `completed_with_errors` is displayed clearly but remains inspectable.

- [ ] **Step 7: Verify idempotency and partial failure**

```powershell
uv run pytest tests/unit/ingestion tests/integration/ingestion/test_service.py -q
uv run opportunitylens ingest --source fixture-first-provider
uv run opportunitylens ingest --source fixture-first-provider
uv run opportunitylens runs show latest
```

Expected: tests pass; the second fixture run adds snapshots and observations but no duplicate canonical job; a mixed fixture run preserves successes and reports the failed company.

- [ ] **Step 8: Commit**

```powershell
git add src/opportunitylens/ingestion src/opportunitylens/cli.py src/opportunitylens/storage/repositories.py tests/unit/ingestion tests/integration/ingestion tests/unit/test_opportunity_cli.py
git commit -m "feat: ingest jobs idempotently with provenance"
```

### Week 1 Completion Gate

- [ ] The audit contains at least 30 verified employers and names two providers from measured coverage.
- [ ] The first selected provider passes captured fixture tests and one opt-in public live-source contract test.
- [ ] Repeating a fixture creates no duplicate canonical jobs.
- [ ] Every fetch appends raw snapshots and observations with content hashes.
- [ ] One failed source cannot discard successful sources, and the run reports `completed_with_errors`.
- [ ] The OpportunityLens tests pass and no saved-checkout user files have changed.

Run:

```powershell
uv run pytest tests/unit tests/integration/ingestion tests/integration/storage -q -m "not live_provider and not model and not ollama"
uv run ruff check src tests scripts
uv run mypy src scripts
git status --short
```

Expected: deterministic tests and static checks pass. Git status lists only intentional Week 1 work, with no `scenarios/` or `tmp/` paths.

---

## Week 2: Coverage, Lifecycle, and Enrichment

### Task 7: Add the Second Selected Adapter and Complete HTTP Resilience

**Estimate:** 5 hours

**Depends on:** Week 1 gate

**Files:**

- Create exactly the second adapter path from the fixed mapping
- Create its matching fixture directory and unit test path
- Modify: `src/opportunitylens/providers/registry.py`
- Modify: `src/opportunitylens/providers/http.py`
- Modify: `tests/unit/providers/test_contract.py`
- Modify: `tests/unit/providers/test_http.py`
- Modify: `tests/integration/providers/test_live_sources.py`
- Modify: `docs/source-audit/2026-09-14-findings.md`

**Interfaces:**

- Extends: `get_adapter()` to resolve both measured provider types.
- Preserves: the exact `ProviderAdapter.fetch_postings()` contract from Task 5.
- Consumed by: all later ingestion and lifecycle tests.

- [ ] **Step 1: Sanitize two fixtures for the second provider**

Capture a representative success plus its hardest relevant case, such as pagination, embedded HTML, missing optional dates, partial validation, or provider-declared closure. Use the same `response.json` and `source.json` fixture convention from Task 5.

- [ ] **Step 2: Extend the shared contract tests before adapter code**

```python
@pytest.mark.parametrize("provider", SELECTED_PROVIDERS)
@pytest.mark.asyncio
async def test_selected_adapters_return_same_contract(provider: AtsProvider) -> None:
    adapter = fixture_adapter(provider)
    result = await adapter.fetch_postings(source_for(provider), fetch_context())
    assert result.provider is provider
    assert result.request_count >= 1
    assert result.complete is (not result.errors)
```

- [ ] **Step 3: Add retry and pagination edge cases**

Test a later-page timeout, malformed record, HTTP 429 with both seconds and HTTP-date `Retry-After`, and a request budget exhaustion. Assert every case returns a partial or failed `ProviderResult` with `complete=False` and does not lose earlier valid pages.

- [ ] **Step 4: Run tests and confirm the second adapter is unresolved**

```powershell
uv run pytest tests/unit/providers -q
```

Expected: the registry or fixture parameter for the second provider fails.

- [ ] **Step 5: Implement the second adapter and missing shared HTTP behavior**

Keep provider-specific request construction and raw schemas inside the adapter. Keep concurrency, retries, timeouts, response limits, error mapping, and request budgets inside `BoundedHttpClient`.

If Workday is selected, the adapter must use only the exact public tenant/site endpoint verified during the audit, handle offset pagination, and refuse sources lacking tenant and site identifiers. It must not use browser automation or authenticated endpoints.

- [ ] **Step 6: Verify both providers against fixtures and one live source each**

```powershell
uv run pytest tests/unit/providers -q
$env:OPPORTUNITYLENS_LIVE_PROVIDER_TESTS = "1"
uv run pytest tests/integration/providers/test_live_sources.py -q -m live_provider
Remove-Item Env:OPPORTUNITYLENS_LIVE_PROVIDER_TESTS
```

Expected: all fixture tests pass; each selected provider’s opt-in live contract test either passes or records a current, evidence-backed access limitation in the audit findings. A blocked source does not justify silently replacing the adapter unless the measured audit is rerun.

- [ ] **Step 7: Commit with the provider-specific message from the mapping**

Stage only the second adapter, shared resilience updates, fixtures, tests, registry, and findings.

### Task 8: Track Changed, Missing, and Closed Posting Lifecycles Safely

**Estimate:** 5 hours

**Depends on:** Task 7

**Files:**

- Create: `src/opportunitylens/ingestion/lifecycle.py`
- Create: `tests/unit/ingestion/test_lifecycle.py`
- Create: `tests/integration/ingestion/test_lifecycle_service.py`
- Modify: `src/opportunitylens/ingestion/service.py`
- Modify: `src/opportunitylens/storage/repositories.py`
- Modify: `migrations/versions/0001_opportunitylens_core.py` only if Week 1 has not been shared; otherwise create `migrations/versions/0002_posting_lifecycle.py`

**Interfaces:**

- Produces: `decide_lifecycle(previous: PostingState, observation: ObservationState, policy: LifecyclePolicy) -> LifecycleDecision`.
- Produces: `LifecyclePolicy(missing_runs_before_close=2)`.
- Consumed by: enrichment invalidation, jobs API, digest, and evaluation snapshots.

- [ ] **Step 1: Write the lifecycle truth-table tests**

```python
@pytest.mark.parametrize(
    ("complete", "observed", "explicitly_closed", "same_hash", "prior_misses", "expected"),
    [
        (True, True, False, True, 0, LifecycleStatus.ACTIVE),
        (True, True, False, False, 0, LifecycleStatus.CHANGED),
        (False, False, False, True, 0, LifecycleStatus.ACTIVE),
        (True, False, False, True, 0, LifecycleStatus.MISSING),
        (True, False, False, True, 1, LifecycleStatus.CLOSED),
        (False, True, True, True, 0, LifecycleStatus.CLOSED),
    ],
)
def test_lifecycle_policy(complete: bool, observed: bool, explicitly_closed: bool, same_hash: bool, prior_misses: int, expected: LifecycleStatus) -> None:
    assert decide_lifecycle(state(complete, observed, explicitly_closed, same_hash, prior_misses), POLICY).status is expected
```

For the incomplete and unseen row, also assert the previous status is retained and the missing counter is unchanged. Do not conflate “seen with same hash” and “not seen.”

- [ ] **Step 2: Write the failing integration sequence**

Run the sequence active, changed, incomplete absence, complete absence, complete absence. Assert statuses active, changed, changed, missing, closed; assert the changed observation queues enrichment; assert incomplete absence queues nothing.

- [ ] **Step 3: Run tests and confirm failure**

```powershell
uv run pytest tests/unit/ingestion/test_lifecycle.py tests/integration/ingestion/test_lifecycle_service.py -q
```

Expected: tests fail because lifecycle decisions are not implemented.

- [ ] **Step 4: Implement pure decisions and transactional application**

`decide_lifecycle()` is a pure function. The service applies all decisions for one source in a database transaction after the provider result is known. Explicit closure can close immediately only when the adapter captured and persisted provider evidence for that state.

- [ ] **Step 5: Verify safe absence behavior**

```powershell
uv run pytest tests/unit/ingestion/test_lifecycle.py tests/integration/ingestion/test_lifecycle_service.py -q
```

Expected: an incomplete fetch never increments absence or closes a job; two consecutive complete absences close it; reappearance returns it to active with history intact.

- [ ] **Step 6: Commit**

```powershell
git add src/opportunitylens/ingestion/lifecycle.py src/opportunitylens/ingestion/service.py src/opportunitylens/storage/repositories.py tests/unit/ingestion/test_lifecycle.py tests/integration/ingestion/test_lifecycle_service.py migrations/versions
git commit -m "feat: track posting lifecycle safely"
```

### Task 9: Add Deterministic Cleanup, Baseline Classification, and Evidence-Span Requirements

**Estimate:** 6 hours

**Depends on:** Task 8

**Files:**

- Create: `src/opportunitylens/enrichment/__init__.py`
- Create: `src/opportunitylens/enrichment/cleanup.py`
- Create: `src/opportunitylens/enrichment/rules.py`
- Create: `src/opportunitylens/enrichment/requirements.py`
- Create: `src/opportunitylens/enrichment/service.py`
- Create: `tests/unit/enrichment/test_cleanup.py`
- Create: `tests/unit/enrichment/test_rules.py`
- Create: `tests/unit/enrichment/test_requirements.py`
- Create: `tests/integration/enrichment/test_service.py`
- Modify: `src/opportunitylens/storage/repositories.py`

**Interfaces:**

- Produces: `clean_job_text(html: str) -> CleanedText` with a reversible source-offset map.
- Produces: `classify_with_rules(posting: JobPosting) -> JobClassification`.
- Produces: `extract_requirements(posting: JobPosting, cleaned: CleanedText) -> tuple[JobRequirement, ...]`.
- Produces: `enrich_changed_job(job_id: UUID, configuration: EnrichmentConfiguration) -> EnrichmentSummary`.
- Consumed by: Hugging Face enrichment, eligibility, retrieval, and dossier tasks.

- [ ] **Step 1: Write failing cleanup and offset tests**

```python
def test_cleaner_maps_evidence_back_to_original_html() -> None:
    original = "<p>Required: Python &amp; SQL.</p>"
    cleaned = clean_job_text(original)
    span = cleaned.find_original_span("Python & SQL")
    assert html.unescape(original[span.start:span.end]).replace("<p>", "").replace("</p>", "") == "Python & SQL"
```

- [ ] **Step 2: Write failing conservative classifier tests**

```python
def test_intern_title_is_high_confidence_internship() -> None:
    result = classify_with_rules(job(title="Software Engineer Intern", description="Singapore internship"))
    assert result.is_internship is True
    assert result.confidence >= 0.9


def test_unrelated_singapore_word_is_not_location_proof() -> None:
    result = classify_with_rules(job(title="Engineer", description="Works with Singapore team", location="London"))
    assert result.singapore_relevant is None
```

- [ ] **Step 3: Write failing requirement-evidence tests**

```python
def test_requirement_span_is_exact_substring_of_original() -> None:
    posting = job(description="Required qualifications: Python and SQL.")
    requirement = extract_requirements(posting, clean_job_text(posting.original_description))[0]
    evidence = requirement.evidence
    assert posting.original_description[evidence.locator.start_offset:evidence.locator.end_offset] == evidence.original_text
```

- [ ] **Step 4: Run tests and confirm failures**

```powershell
uv run pytest tests/unit/enrichment tests/integration/enrichment/test_service.py -q
```

Expected: enrichment modules are absent.

- [ ] **Step 5: Implement conservative deterministic baselines**

Support known Singapore aliases, explicit internship terms, a compact role-family vocabulary (`software_engineering`, `data`, `ai_ml`, `product`, `cybersecurity`, `design`, `business`, `other`), and seniority terms. Return `None` and lower confidence when evidence conflicts. Never infer work authorization from company location.

Extract skills, education, experience durations, availability dates, graduation windows, and authorization phrases using deterministic patterns. Store `required` versus `preferred`, confidence, extractor version `rules-v1`, and exact evidence.

- [ ] **Step 6: Enrich only new or changed content hashes**

Persist the enrichment configuration hash. `enrich_changed_job()` reuses cached output only when both posting content hash and configuration hash match. A changed hash creates new versioned classification, requirements, and evidence without overwriting old results.

- [ ] **Step 7: Verify evidence and cache invalidation**

```powershell
uv run pytest tests/unit/enrichment tests/integration/enrichment/test_service.py -q
```

Expected: every extracted requirement span resolves to the original posting; identical hashes reuse results; changed hashes create a new version.

- [ ] **Step 8: Commit**

```powershell
git add src/opportunitylens/enrichment src/opportunitylens/storage/repositories.py tests/unit/enrichment tests/integration/enrichment
git commit -m "feat: extract evidenced job requirements"
```

### Task 10: Add Versioned Hugging Face Classification, Embeddings, and Degraded Mode

**Estimate:** 6 hours

**Depends on:** Task 9

**Files:**

- Create: `src/opportunitylens/enrichment/models.py`
- Create: `tests/unit/enrichment/test_models.py`
- Create: `tests/integration/enrichment/test_huggingface.py`
- Create: `configs/models.yaml`
- Modify: `src/opportunitylens/enrichment/service.py`
- Modify: `src/opportunitylens/storage/repositories.py`
- Modify: `pyproject.toml`
- Modify: `uv.lock`

**Interfaces:**

- Produces: `TextClassifier.classify(text: str, labels: Sequence[str]) -> ClassificationScores`.
- Produces: `RequirementEntityExtractor.extract(text: str) -> tuple[ModelEntity, ...]`.
- Produces: `TextEmbedder.embed(texts: Sequence[str]) -> NDArray[float32]`.
- Produces: `ModelRevision(repository: str, revision_sha: str, task: str)` persisted with every output.
- Consumed by: dense retrieval, Replay Lab, observability, and README measurements.

- [ ] **Step 1: Write failing fake-model tests**

```python
def test_model_outputs_record_immutable_revision() -> None:
    model = FakeTextClassifier(revision=ModelRevision(repository="fake/classifier", revision_sha="abc123", task="zero-shot-classification"))
    result = model.classify("Software engineering intern in Singapore", ["software_engineering", "data"])
    assert result.revision.revision_sha == "abc123"


async def test_model_failure_preserves_rule_baseline(service: EnrichmentService) -> None:
    service.classifier = FailingClassifier()
    summary = await service.enrich_changed_job(JOB_ID, CONFIG)
    assert summary.status is EnrichmentStatus.COMPLETED_WITH_ERRORS
    assert summary.rule_classification_id is not None
    assert summary.fallbacks == ("classification_model_unavailable",)
```

- [ ] **Step 2: Run unit tests and confirm failure**

```powershell
uv run pytest tests/unit/enrichment/test_models.py -q
```

Expected: imports fail for the model interfaces.

- [ ] **Step 3: Add concrete initial model configuration**

Use these initial repositories, subject to measured replacement through a versioned config commit:

```yaml
classification:
  repository: facebook/bart-large-mnli
  task: zero-shot-classification
embeddings:
  repository: sentence-transformers/all-MiniLM-L6-v2
  task: feature-extraction
  dimensions: 384
requirement_entities:
  repository: jjzha/jobbert_skill_extraction
  task: token-classification
reranker:
  repository: cross-encoder/ms-marco-MiniLM-L-6-v2
  task: text-classification
```

Resolve each repository’s `main` reference to an immutable Hub commit SHA during model setup and write that actual SHA into `configs/models.yaml` before committing. The configuration loader must reject an empty revision or the literal floating reference `main`.

- [ ] **Step 4: Implement lazy model adapters and section embeddings**

Load models only inside worker operations. Classify role family, seniority, and Singapore relevance only when deterministic rules are uncertain. Run token classification on requirement sections, map predicted skill entities back to exact original source spans, and discard any entity whose span cannot be validated. Generate separate embeddings for role summary, responsibilities, required qualifications, and preferred qualifications; persist section name, vector, model revision, content hash, and configuration hash.

- [ ] **Step 5: Run marked local-model tests once**

```powershell
uv run pytest tests/integration/enrichment/test_huggingface.py -q -m model
```

Expected: configured revisions load, a 384-dimensional finite embedding is returned, classification label scores sum to approximately 1 for the test mode used, token-classified skills resolve to original spans, and no network call occurs after models are cached.

- [ ] **Step 6: Verify deterministic CI mode**

```powershell
$env:OPPORTUNITYLENS_MODEL_MODE = "fake"
uv run pytest tests/unit/enrichment tests/integration/enrichment/test_service.py -q -m "not model"
Remove-Item Env:OPPORTUNITYLENS_MODEL_MODE
```

Expected: all deterministic tests pass without downloading a model. Failure records the fallback and retains rule-based results.

- [ ] **Step 7: Commit**

```powershell
git add configs/models.yaml pyproject.toml uv.lock src/opportunitylens/enrichment tests/unit/enrichment tests/integration/enrichment
git commit -m "feat: version classification and embedding models"
```

### Task 11: Join Two Providers, Lifecycle, and Enrichment into One Worker-Ready Pipeline

**Estimate:** 4 hours

**Depends on:** Tasks 7 through 10

**Files:**

- Create: `tests/integration/pipeline/test_ingestion_enrichment.py`
- Create: `tests/fixtures/pipeline/two-provider-run.json`
- Modify: `src/opportunitylens/ingestion/service.py`
- Modify: `src/opportunitylens/enrichment/service.py`
- Modify: `src/opportunitylens/cli.py`
- Modify: `src/opportunitylens/storage/repositories.py`

**Interfaces:**

- Produces: database-backed `ingestion` and `enrichment` run records that a worker can claim later.
- Produces: `opportunitylens pipeline fixture-smoke` for a deterministic Week 2 gate.
- Consumed by: profile, ranking, API, and worker tasks.

- [ ] **Step 1: Write a failing two-provider pipeline test**

The fixture sequence includes unchanged, changed, malformed, and missing postings from both provider types.

```python
@pytest.mark.postgres
async def test_two_provider_pipeline_preserves_invariants(services: Services) -> None:
    first, second = await run_two_fixture_rounds(services)
    assert first.providers_seen == second.providers_seen == 2
    assert second.duplicate_canonical_jobs == 0
    assert second.changed_jobs == 1
    assert second.incomplete_sources == 1
    assert await services.repositories.jobs.closed_count() == 0
    assert await every_current_requirement_resolves(services.repositories)
```

- [ ] **Step 2: Run the test and confirm the orchestration gap**

```powershell
uv run pytest tests/integration/pipeline/test_ingestion_enrichment.py -q
```

Expected: the test fails because ingestion and enrichment run scheduling are not yet joined.

- [ ] **Step 3: Queue enrichment transactionally**

When ingestion records a new or changed content hash, create a pending enrichment run in the same database transaction. Use a uniqueness key of `(run_kind, job_id, content_hash, configuration_hash)` so retries cannot enqueue duplicate work.

- [ ] **Step 4: Add a deterministic synchronous fixture runner for development only**

`opportunitylens pipeline fixture-smoke` may claim and execute pending tasks in the current process, but production API routes must only enqueue. This command gives beginners one reproducible way to exercise the complete Week 2 path before the long-running worker exists.

- [ ] **Step 5: Run the Week 2 pipeline and inspect evidence**

```powershell
uv run opportunitylens pipeline fixture-smoke
uv run pytest tests/integration/pipeline/test_ingestion_enrichment.py -q
```

Expected: two provider types normalize through one contract; one changed job receives a new enrichment version; the incomplete source closes nothing; every requirement evidence ID resolves.

- [ ] **Step 6: Commit**

```powershell
git add src/opportunitylens/ingestion/service.py src/opportunitylens/enrichment/service.py src/opportunitylens/storage/repositories.py src/opportunitylens/cli.py tests/integration/pipeline tests/fixtures/pipeline
git commit -m "feat: join ingestion and enrichment runs"
```

### Week 2 Completion Gate

- [ ] Both selected provider types pass the common fixture contract.
- [ ] At least one allowlisted live source per provider can be attempted independently without breaking deterministic tests.
- [ ] Pagination, timeout, 429, size-limit, validation, and partial-response behavior are tested.
- [ ] A changed content hash creates a new derived version and re-enrichment run.
- [ ] Incomplete source runs cannot increment absence or close unseen jobs.
- [ ] Every current requirement resolves to an exact stored posting evidence span.
- [ ] Hugging Face revisions are immutable in configuration and fake-model mode requires no download.

Run:

```powershell
uv run pytest tests/unit tests/integration -q -m "not live_provider and not model and not ollama"
uv run ruff check src tests scripts migrations
uv run mypy src scripts
uv run opportunitylens pipeline fixture-smoke
```

Expected: all deterministic checks pass and the fixture smoke command reports two providers, zero duplicate canonical jobs, zero unsafe closures, and zero unresolved evidence references.

---

## Week 3: Candidate Profile, Eligibility, Ranking, and Replay Lab

### Task 12: Parse a Test PDF into Reviewable, Versioned Candidate Facts

**Estimate:** 6 hours

**Depends on:** Week 2 gate

**Files:**

- Create: `src/opportunitylens/profiles/__init__.py`
- Create: `src/opportunitylens/profiles/pdf.py`
- Create: `src/opportunitylens/profiles/extraction.py`
- Create: `src/opportunitylens/profiles/service.py`
- Create: `tests/unit/profiles/test_pdf.py`
- Create: `tests/unit/profiles/test_extraction.py`
- Create: `tests/integration/profiles/test_service.py`
- Create: `tests/fixtures/resumes/text-resume.pdf`
- Create: `tests/fixtures/resumes/scanned-resume.pdf`
- Modify: `src/opportunitylens/storage/repositories.py`

**Interfaces:**

- Produces: `parse_pdf(data: bytes, filename: str, max_bytes: int) -> ParsedResume`.
- Produces: `extract_fact_drafts(resume: ParsedResume, extractor_version: str) -> tuple[CandidateFact, ...]`.
- Produces: `confirm_fact()`, `correct_fact()`, `reject_fact()`, and `save_profile_version()` service methods.
- Consumed by: eligibility, ranking, API, frontend onboarding, and evaluation profiles.

- [ ] **Step 1: Create safe PDF fixtures**

Generate one small synthetic text PDF containing education, graduation date, two projects, technologies, availability, and no real contact details. Generate one image-only synthetic PDF for the unsupported scanned-document case. Keep both under 100 KiB.

- [ ] **Step 2: Write failing file safety and locator tests**

```python
def test_parser_rejects_non_pdf_magic_bytes() -> None:
    with pytest.raises(ResumeValidationError, match="PDF"):
        parse_pdf(b"not a pdf", "resume.pdf", max_bytes=5 * 1024 * 1024)


def test_parser_rejects_image_only_pdf_with_actionable_error() -> None:
    with pytest.raises(ResumeValidationError, match="searchable text"):
        parse_pdf(scanned_fixture(), "scanned-resume.pdf", max_bytes=5 * 1024 * 1024)


def test_candidate_fact_resolves_to_page_offsets() -> None:
    resume = parse_pdf(text_fixture(), "text-resume.pdf", max_bytes=5 * 1024 * 1024)
    fact = extract_fact_drafts(resume, "rules-v1")[0]
    assert resume.pages[fact.evidence.locator.page - 1].text[fact.evidence.locator.start_offset:fact.evidence.locator.end_offset] == fact.evidence.original_text
```

- [ ] **Step 3: Write failing profile version tests**

```python
@pytest.mark.postgres
async def test_rejected_fact_is_not_copied_into_rankable_profile(profile_service: ProfileService) -> None:
    document = await profile_service.upload(text_fixture(), "text-resume.pdf")
    fact = document.fact_drafts[0]
    await profile_service.reject_fact(fact.fact_id)
    version = await profile_service.save_profile_version(document.profile_id, constraints(), preferences())
    assert fact.fact_id not in version.active_fact_ids


@pytest.mark.postgres
async def test_correction_keeps_original_and_user_evidence(profile_service: ProfileService) -> None:
    corrected = await profile_service.correct_fact(FACT_ID, "December 2027")
    assert len(corrected.evidence_ids) == 2
    assert corrected.verification_status is VerificationStatus.CORRECTED
```

- [ ] **Step 4: Run tests and confirm failure**

```powershell
uv run pytest tests/unit/profiles tests/integration/profiles -q
```

Expected: profile modules are absent.

- [ ] **Step 5: Implement bounded PDF parsing**

Verify filename suffix, `%PDF` magic bytes, byte size, encrypted status, maximum 20 pages, and maximum 100,000 extracted characters. Store uploads under a nonpublic configured directory using a generated document ID, never the user filename. Reject image-only files in the MVP with a clear message that OCR is not supported.

- [ ] **Step 6: Implement conservative fact drafts with evidence**

Extract education, graduation date, technologies, project or work experiences, location, authorization statements, and availability only when a span is present. Drafts begin as `extracted`. Do not convert absence into a negative fact. Store `DocumentLocator(document_id, page, start_offset, end_offset)` and extractor version.

- [ ] **Step 7: Implement review actions and immutable profile versions**

Confirmation keeps resume evidence. Correction creates a new fact linked to the original resume evidence plus a `UserInputLocator`. Rejection preserves the audit record but excludes the fact from active versions. Saving constraints and preferences creates a monotonically increasing profile version with an immutable fact-ID set.

- [ ] **Step 8: Implement privacy-preserving deletion**

Deleting a candidate document deletes its stored file, extracted facts, dependent profile versions, and embeddings in one service operation. Keep separately committed synthetic or redacted evaluation profiles because they are independent artifacts, not references to the private document.

- [ ] **Step 9: Verify and commit**

```powershell
uv run pytest tests/unit/profiles tests/integration/profiles -q
uv run ruff check src/opportunitylens/profiles tests/unit/profiles tests/integration/profiles
uv run mypy src/opportunitylens/profiles
git add src/opportunitylens/profiles src/opportunitylens/storage/repositories.py tests/unit/profiles tests/integration/profiles tests/fixtures/resumes
git commit -m "feat: version verified candidate profiles"
```

### Task 13: Separate Hard Eligibility from Relevance with Explicit Uncertainty

**Estimate:** 4 hours

**Depends on:** Tasks 9 and 12

**Files:**

- Create: `src/opportunitylens/ranking/__init__.py`
- Create: `src/opportunitylens/ranking/eligibility.py`
- Create: `tests/unit/ranking/test_eligibility.py`

**Interfaces:**

- Produces: `evaluate_eligibility(profile: CandidateProfileVersion, job: JobPosting, classification: JobClassification, requirements: Sequence[JobRequirement]) -> EligibilityResult`.
- Produces: one typed reason per evaluated hard constraint, each with evidence IDs or an explicit unavailable-evidence flag.
- Consumed by: candidate generation, recommendation, Replay Lab, and dossier.

- [ ] **Step 1: Write the decision table as failing parametrized tests**

```python
@pytest.mark.parametrize(
    ("internship", "location", "availability", "graduation", "authorization", "expected"),
    [
        (True, "match", "match", "match", "match", EligibilityDecision.ELIGIBLE),
        (False, "match", "match", "match", "match", EligibilityDecision.INELIGIBLE),
        (True, "mismatch", "match", "match", "match", EligibilityDecision.INELIGIBLE),
        (True, "match", "unknown", "match", "match", EligibilityDecision.UNCERTAIN),
        (True, "match", "match", "unknown", "unknown", EligibilityDecision.UNCERTAIN),
        (True, "match", "match", "match", "mismatch", EligibilityDecision.INELIGIBLE),
    ],
)
def test_hard_eligibility_table(internship: bool, location: str, availability: str, graduation: str, authorization: str, expected: EligibilityDecision) -> None:
    assert evaluate_case(internship, location, availability, graduation, authorization).decision is expected
```

- [ ] **Step 2: Test that unknown authorization is not silently accepted**

```python
def test_unknown_work_authorization_is_uncertain() -> None:
    result = evaluate_eligibility(profile_without_authorization(), singapore_job_without_authorization_text(), classification(), ())
    assert result.decision is EligibilityDecision.UNCERTAIN
    assert result.reasons[-1].evidence_unavailable is True
```

- [ ] **Step 3: Run tests and confirm failure**

```powershell
uv run pytest tests/unit/ranking/test_eligibility.py -q
```

Expected: eligibility module is absent.

- [ ] **Step 4: Implement all hard filters as pure evaluators**

Evaluate internship type, accepted location, availability overlap, graduation window, explicit work authorization, and explicit user exclusions independently. Combine results with this order: any proven mismatch means `ineligible`; otherwise any unknown means `uncertain`; otherwise `eligible`.

Every proven match or mismatch includes evidence IDs from posting, profile, or user input. Unknown reasons set `evidence_unavailable=True` and name the missing information.

- [ ] **Step 5: Verify and commit**

```powershell
uv run pytest tests/unit/ranking/test_eligibility.py -q
uv run ruff check src/opportunitylens/ranking/eligibility.py tests/unit/ranking/test_eligibility.py
uv run mypy src/opportunitylens/ranking/eligibility.py
git add src/opportunitylens/ranking tests/unit/ranking/test_eligibility.py
git commit -m "feat: evaluate eligibility with uncertainty"
```

### Task 14: Implement Lexical Retrieval, Dense Retrieval, and Reciprocal Rank Fusion

**Estimate:** 6 hours

**Depends on:** Tasks 10 and 13

**Files:**

- Create: `src/opportunitylens/ranking/lexical.py`
- Create: `src/opportunitylens/ranking/dense.py`
- Create: `src/opportunitylens/ranking/fusion.py`
- Create: `tests/unit/ranking/test_fusion.py`
- Create: `tests/integration/ranking/test_lexical.py`
- Create: `tests/integration/ranking/test_dense.py`
- Create: `configs/ranking/lexical-v1.yaml`
- Create: `configs/ranking/dense-v1.yaml`
- Create: `configs/ranking/hybrid-v1.yaml`
- Create: `configs/ranking/hybrid-no-hard-filters-v1.yaml`
- Modify: `src/opportunitylens/storage/repositories.py`

**Interfaces:**

- Produces: `lexical_candidates(query: CandidateQuery, limit: int) -> tuple[RankedCandidate, ...]`.
- Produces: `dense_candidates(query: CandidateQuery, limit: int) -> tuple[RankedCandidate, ...]`.
- Produces: `reciprocal_rank_fusion(rankings: Sequence[Sequence[RankedCandidate]], k: int = 60) -> tuple[FusedCandidate, ...]`.
- Consumed by: reranking, recommendation, and evaluation.

- [ ] **Step 1: Write exact RRF tests before SQL**

```python
def test_rrf_combines_ranks_without_combining_raw_scores() -> None:
    lexical = [candidate("a", raw_score=20.0), candidate("b", raw_score=10.0)]
    dense = [candidate("b", raw_score=0.91), candidate("c", raw_score=0.88)]
    fused = reciprocal_rank_fusion([lexical, dense], k=60)
    assert [item.job_id for item in fused] == ["b", "a", "c"]
    assert fused[0].fused_score == pytest.approx(1 / 62 + 1 / 61)
```

- [ ] **Step 2: Write lexical and dense integration tests**

Seed one exact-term match, one semantic paraphrase, one irrelevant job, and one proven-ineligible job. Assert lexical ranks the exact term; dense ranks the paraphrase; hard-filter mode removes only the proven-ineligible job and retains uncertain jobs.

- [ ] **Step 3: Run tests and confirm failure**

```powershell
uv run pytest tests/unit/ranking/test_fusion.py tests/integration/ranking/test_lexical.py tests/integration/ranking/test_dense.py -q
```

Expected: retrieval modules and SQL methods are absent.

- [ ] **Step 4: Implement PostgreSQL lexical retrieval**

Build a weighted `searchable_text` document with title and required qualifications at weight A, responsibilities and role family at B, preferred qualifications and company name at C. Use `websearch_to_tsquery('english', :query)` and `ts_rank_cd`. Return rank and raw lexical score for inspection.

- [ ] **Step 5: Implement section-aware pgvector retrieval**

Embed the candidate query with the exact embedding revision recorded in the ranking configuration. Search role summary, responsibilities, required qualifications, and preferred qualifications. Collapse multiple section hits to one job by the best cosine distance while retaining the winning section and raw distance.

- [ ] **Step 6: Implement deterministic RRF**

Assign rank starting at 1 and calculate `sum(1 / (k + rank))` per job. Break equal fused scores by best individual rank, then stable job UUID string. Never min-max normalize lexical and cosine scores together.

- [ ] **Step 7: Add graceful vector fallback**

If pgvector or embedding generation raises a typed unavailable error, return lexical candidates with `degraded_components=("dense",)` and record the exception class, not job text, in structured logs.

- [ ] **Step 8: Verify configuration variants**

```powershell
uv run pytest tests/unit/ranking/test_fusion.py tests/integration/ranking/test_lexical.py tests/integration/ranking/test_dense.py -q
```

Expected: lexical, dense, hybrid, and hybrid-without-hard-filters configurations return deterministic rankings; uncertain eligibility stays visible.

- [ ] **Step 9: Commit**

```powershell
git add src/opportunitylens/ranking src/opportunitylens/storage/repositories.py tests/unit/ranking tests/integration/ranking configs/ranking
git commit -m "feat: add hybrid RRF retrieval"
```

### Task 15: Add Cross-Encoder Reranking and Recommendation Versioning

**Estimate:** 4 hours

**Depends on:** Task 14

**Files:**

- Create: `src/opportunitylens/ranking/rerank.py`
- Create: `src/opportunitylens/ranking/scoring.py`
- Create: `src/opportunitylens/ranking/service.py`
- Create: `tests/unit/ranking/test_rerank.py`
- Create: `tests/unit/ranking/test_scoring.py`
- Create: `tests/integration/ranking/test_service.py`
- Create: `configs/ranking/hybrid-rerank-v1.yaml`
- Modify: `src/opportunitylens/storage/repositories.py`

**Interfaces:**

- Produces: `CrossEncoderReranker.rerank(query: str, candidates: Sequence[FusedCandidate], limit: int) -> tuple[RerankedCandidate, ...]`.
- Produces: `score_components(profile: CandidateProfileVersion, job: JobPosting, ranking: RankedCandidate) -> ComponentScores`.
- Produces: `RecommendationService.run(profile_version_id: UUID, ranking_config_id: str) -> RecommendationRunSummary`.
- Consumed by: Replay Lab, API, dossier, and analyst graph.

- [ ] **Step 1: Write failing cascade and failure tests**

```python
def test_reranker_only_receives_top_twenty_fused_candidates() -> None:
    reranker = SpyReranker()
    service = recommendation_service(reranker=reranker, fused_candidates=50)
    service.run_sync(PROFILE_VERSION_ID, "hybrid-rerank-v1")
    assert len(reranker.received) == 20


def test_reranker_failure_returns_fused_order() -> None:
    result = recommendation_service(reranker=FailingReranker()).run_sync(PROFILE_VERSION_ID, "hybrid-rerank-v1")
    assert result.jobs == result.fused_fallback_jobs
    assert result.degraded_components == ("reranker",)
```

- [ ] **Step 2: Run tests and confirm failure**

```powershell
uv run pytest tests/unit/ranking/test_rerank.py tests/integration/ranking/test_service.py -q
```

Expected: rerank and recommendation services are absent.

- [ ] **Step 3: Implement a versioned cross-encoder adapter**

Use the immutable reranker revision from `configs/models.yaml`. Build each pair from candidate profile summary plus job title, responsibilities, required qualifications, and preferred qualifications. Batch at most 16 pairs. Rerank only the first 20 fused candidates and retain pre-rerank position and score for explanations.

- [ ] **Step 4: Implement transparent component scores**

Keep eligibility categorical and outside the relevance formula. Calculate scores from 0 to 1 as follows:

```text
role_relevance = cross-encoder sigmoid score when available, otherwise inverse fused-rank percentile
skill_evidence = sum(weights of job skills evidenced by confirmed candidate facts) / sum(weights of explicit job skills), with required weight 2 and preferred weight 1
experience_alignment = mean of explicit duration, education, and domain comparisons, using 1 for evidenced match, 0 for evidenced mismatch, and 0.5 for unknown
preference_alignment = matched explicit candidate preferences / applicable explicit preferences
overall_relevance = 0.45 * role_relevance + 0.25 * skill_evidence + 0.15 * experience_alignment + 0.15 * preference_alignment
```

If a denominator is empty, return `None` for that component and redistribute only its weight proportionally across present components. Persist unevidenced skills separately and describe them as not evidenced, not absent.

Add hand-calculated tests covering full evidence, missing components with weight redistribution, and unevidenced skills.

- [ ] **Step 5: Persist the complete ranking context**

Each recommendation run stores profile version, dataset or live-corpus version, model revisions, ranking configuration contents and hash, filter mode, random seed, git commit, start and finish timestamps, component latencies, fallback flags, and errors. Each `MatchResult` stores component scores, overall relevance band, eligibility, evidence IDs, and unevidenced requirements.

- [ ] **Step 6: Verify deterministic and local-model modes**

```powershell
$env:OPPORTUNITYLENS_MODEL_MODE = "fake"
uv run pytest tests/unit/ranking tests/integration/ranking -q -m "not model"
Remove-Item Env:OPPORTUNITYLENS_MODEL_MODE
uv run pytest tests/integration/ranking/test_service.py -q -m model
```

Expected: fake mode is deterministic; model mode reranks no more than 20 candidates; reranker failure returns fused results.

- [ ] **Step 7: Commit**

```powershell
git add src/opportunitylens/ranking src/opportunitylens/storage/repositories.py tests/unit/ranking tests/integration/ranking configs/ranking/hybrid-rerank-v1.yaml
git commit -m "feat: rerank versioned recommendations"
```

### Task 16: Build Replay Lab Schemas, Metrics, Runner, and Reports

**Estimate:** 6 hours

**Depends on:** Task 15

**Files:**

- Create: `src/opportunitylens/evaluation/__init__.py`
- Create: `src/opportunitylens/evaluation/schema.py`
- Create: `src/opportunitylens/evaluation/metrics.py`
- Create: `src/opportunitylens/evaluation/runner.py`
- Create: `src/opportunitylens/evaluation/report.py`
- Create: `tests/unit/evaluation/test_schema.py`
- Create: `tests/unit/evaluation/test_metrics.py`
- Create: `tests/integration/evaluation/test_runner.py`
- Create: `evaluation/profiles/verified-developer-redacted.json`
- Create: `evaluation/profiles/synthetic-ai-intern.json`
- Create: `evaluation/profiles/synthetic-backend-intern.json`
- Create: `evaluation/datasets/replay-regression-v1.jsonl`
- Create: `evaluation/results/replay-regression-v1.json`
- Create: `evaluation/reports/replay-regression-v1.md`
- Modify: `src/opportunitylens/cli.py`

**Interfaces:**

- Produces: `ReplayCase`, `ReplayDataset`, `EvaluationRunRecord`, and `EvaluationMetrics`.
- Produces: `run_evaluation(dataset_path: Path, config_ids: Sequence[str], output_path: Path) -> EvaluationRunRecord`.
- Produces: `render_report(run: EvaluationRunRecord) -> str`.
- Consumed by: full lab dataset, CI, Replay API, and final documentation.

- [ ] **Step 1: Write failing dataset-validation tests**

```python
def test_replay_case_requires_frozen_versions_and_reviewer_notes() -> None:
    with pytest.raises(ValidationError):
        ReplayCase.model_validate(case_payload() | {"profile_version_id": "", "reviewer_notes": ""})


def test_relevance_grade_is_zero_through_three() -> None:
    with pytest.raises(ValidationError):
        ReplayCase.model_validate(case_payload() | {"relevance_grade": 4})


def test_replay_case_requires_classification_and_abstention_labels() -> None:
    with pytest.raises(ValidationError):
        ReplayCase.model_validate(case_payload() | {"expected_classification": None, "should_abstain": None})
```

- [ ] **Step 2: Write metric unit tests using hand-calculated examples**

```python
def test_ndcg_at_ten_uses_graded_relevance() -> None:
    assert ndcg_at_k([3, 0, 2], ideal=[3, 2, 0], k=10) == pytest.approx(0.9558305893)


def test_false_eligible_rate_counts_ineligible_cases_predicted_eligible() -> None:
    assert false_eligible_rate([label(False, True), label(False, False), label(True, True)]) == 0.5


def test_latency_percentiles_are_nearest_rank() -> None:
    assert latency_percentiles_ms([10, 20, 30, 40, 50]) == {"p50": 30, "p95": 50}
```

Also test classification macro F1, Recall@50, Precision@10, citation precision, unsupported-claim count, and correct abstention rate with small hand-calculated inputs.

- [ ] **Step 3: Run tests and confirm failure**

```powershell
uv run pytest tests/unit/evaluation tests/integration/evaluation/test_runner.py -q
```

Expected: evaluation modules are absent.

- [ ] **Step 4: Implement immutable case and run schemas**

Each case stores dataset version, profile version ID, frozen posting snapshot ID, job ID, expected internship status, Singapore relevance, role families and seniority, eligibility label, relevance grade 0 to 3, expected evidence IDs, `should_abstain`, reviewer notes, and synthetic flags. Deduplicate job-level classification labels by job ID when computing macro F1. Each run stores dataset SHA-256, profile versions, posting snapshot hashes, model revisions, prompt version, ranking configuration, filter mode, random seed, git commit, latency samples, errors, and metric outputs.

- [ ] **Step 5: Implement metrics without hidden exclusions**

Metric functions accept explicit cases and predictions and return numerator, denominator, and value. Empty denominators return `None` plus a warning, never zero. Reports display the case count for every metric and list failures instead of silently removing them.

- [ ] **Step 6: Implement CLI runner and stable JSON plus Markdown output**

Expose:

```text
opportunitylens eval validate evaluation/datasets/replay-regression-v1.jsonl
opportunitylens eval run evaluation/datasets/replay-regression-v1.jsonl --config lexical-v1 --output evaluation/results/replay-regression-v1.json
opportunitylens eval report evaluation/results/replay-regression-v1.json --output evaluation/reports/replay-regression-v1.md
```

Sort JSON keys and cases by stable IDs. Markdown tables are generated from raw JSON, never maintained by hand.

- [ ] **Step 7: Create a small deterministic CI subset**

Commit 12 synthetic or redacted cases across the three profiles, including two ambiguous eligibility cases, two strong positives, four difficult negatives, and four ordinary cases. This subset is for logic regression only and must not be presented as the full evaluation result.

- [ ] **Step 8: Verify the runner**

```powershell
uv run opportunitylens eval validate evaluation/datasets/replay-regression-v1.jsonl
uv run pytest tests/unit/evaluation tests/integration/evaluation/test_runner.py -q
```

Expected: 12 cases validate; metric unit tests match hand calculations; a fake-model run produces byte-stable JSON after volatile timestamps are normalized in the test.

- [ ] **Step 9: Commit**

```powershell
git add src/opportunitylens/evaluation src/opportunitylens/cli.py tests/unit/evaluation tests/integration/evaluation evaluation/profiles evaluation/datasets/replay-regression-v1.jsonl evaluation/results/replay-regression-v1.json evaluation/reports/replay-regression-v1.md
git commit -m "feat: add reproducible Ranking Replay Lab"
```

### Task 17: Freeze 60 Reviewed Pairs and Select a Ranking Configuration from Measurements

**Estimate:** 6 hours

**Depends on:** Task 16

**Files:**

- Create: `evaluation/corpora/replay-v1/manifest.json`
- Create: `evaluation/corpora/replay-v1/postings.jsonl`
- Create: `evaluation/datasets/replay-v1.jsonl`
- Create: `evaluation/results/replay-v1-baseline.json`
- Create: `evaluation/reports/replay-v1-baseline.md`
- Modify: `evaluation/profiles/verified-developer-redacted.json`
- Modify: `evaluation/profiles/synthetic-ai-intern.json`
- Modify: `evaluation/profiles/synthetic-backend-intern.json`
- Modify: `docs/evaluation.md`
- Modify if a measured correction is required: `configs/ranking/lexical-v1.yaml`
- Modify if a measured correction is required: `configs/ranking/dense-v1.yaml`
- Modify if a measured correction is required: `configs/ranking/hybrid-v1.yaml`
- Modify if a measured correction is required: `configs/ranking/hybrid-rerank-v1.yaml`
- Modify if a measured correction is required: `configs/ranking/hybrid-no-hard-filters-v1.yaml`

**Interfaces:**

- Produces: frozen corpus version `replay-v1`, dataset version `replay-v1`, raw baseline result, readable report, and selected ranking configuration ID.
- Consumed by: API, Replay UI, final README, and resume measurement rendering.

- [ ] **Step 1: Freeze a reviewable corpus from stored public snapshots**

Export canonical jobs, original descriptions, posting evidence, classification versions, requirement versions, and source metadata from both provider types. Use stable snapshot IDs and hashes. Include Singapore internships, Singapore non-internships, non-Singapore internships, closed or changed listings, and ambiguous authorization language. Do not alter descriptions to make labels easier.

- [ ] **Step 2: Finalize exactly three candidate profiles**

Use one developer profile only if it is redacted and explicitly approved for repository storage. Otherwise make `verified-developer-redacted.json` synthetic and mark it as such. The other two profiles are always synthetic. Each profile includes confirmed facts, constraints, preferences, evidence, version ID, and a clear synthetic flag.

- [ ] **Step 3: Label at least 60 profile-posting pairs without viewing model ranks**

For each profile, label at least 20 distinct pairs with expected job classification, eligibility truth, relevance grade 0 to 3, expected evidence IDs, `should_abstain`, and reviewer notes. Include at least 12 difficult negatives total and at least 10 ambiguous eligibility cases total. Randomize presentation order and hide ranking scores during labeling to reduce confirmation bias. Compute Recall@50 over the judged pool and publish the judged pool size beside it; do not imply unlabelled corpus jobs were assessed as irrelevant.

- [ ] **Step 4: Validate labels and evidence before experiments**

```powershell
uv run opportunitylens eval validate evaluation/datasets/replay-v1.jsonl
```

Expected: validation reports three profiles, at least 60 pairs, both provider types, at least 12 difficult negatives, at least 10 ambiguous eligibility cases, and zero unresolved expected evidence IDs.

- [ ] **Step 5: Run every required ranking comparison**

```powershell
uv run opportunitylens eval run evaluation/datasets/replay-v1.jsonl --config lexical-v1 --config dense-v1 --config hybrid-v1 --config hybrid-rerank-v1 --config hybrid-no-hard-filters-v1 --output evaluation/results/replay-v1-baseline.json
uv run opportunitylens eval report evaluation/results/replay-v1-baseline.json --output evaluation/reports/replay-v1-baseline.md
```

Expected: raw JSON includes classification macro F1, false-eligible rate, Recall@50, nDCG@10, Precision@10, and p50 and p95 latency for each compatible configuration. Citation and abstention metrics are marked not measured until Task 20 adds the analyst comparison.

- [ ] **Step 6: Select the default with a written decision rule**

The selected default must have the lowest false-eligible rate among configurations whose Recall@50 is no worse than the lexical baseline. Break ties by nDCG@10, then p95 latency. If no hybrid configuration qualifies, keep `lexical-v1` as the product default and document dense or reranker failure honestly.

- [ ] **Step 7: Review the report for unsupported claims**

Every number in `docs/evaluation.md` must appear in `evaluation/results/replay-v1-baseline.json` with the same dataset hash, configuration ID, and case count. Describe this as a small local labelled dataset, not a population-level result or hiring probability.

- [ ] **Step 8: Commit data and measured output**

```powershell
git add evaluation/corpora/replay-v1 evaluation/profiles evaluation/datasets/replay-v1.jsonl evaluation/results/replay-v1-baseline.json evaluation/reports/replay-v1-baseline.md docs/evaluation.md configs/ranking
git commit -m "eval: compare OpportunityLens ranking configurations"
```

### Week 3 Completion Gate

- [ ] Candidate facts can be confirmed, corrected, and rejected with exact document or user-input evidence.
- [ ] Every saved recommendation records the immutable candidate profile version and ranking configuration.
- [ ] Eligibility is independent from relevance and unknown authorization remains `uncertain`.
- [ ] Lexical, dense, hybrid RRF, and reranked configurations run against one frozen corpus.
- [ ] Vector failure falls back to lexical and reranker failure falls back to fused results.
- [ ] The full lab has exactly three profiles and at least 60 human-reviewed pairs.
- [ ] The default ranking configuration is selected by the declared metric rule, not preference.

Run:

```powershell
uv run pytest tests/unit tests/integration -q -m "not live_provider and not model and not ollama"
uv run ruff check src tests scripts
uv run mypy src scripts
uv run opportunitylens eval validate evaluation/datasets/replay-v1.jsonl
uv run opportunitylens eval report evaluation/results/replay-v1-baseline.json --output evaluation/reports/replay-v1-baseline.md
git diff --exit-code -- evaluation/reports/replay-v1-baseline.md
```

Expected: deterministic tests and static checks pass; dataset validation reports at least 60 cases and zero broken evidence links; regenerating the report creates no diff.

---

## Week 4: Product, Bounded Analysis, and Portfolio Finish

### Task 18: Expose Versioned FastAPI Resources and an Atomic Database Worker

**Estimate:** 6 hours

**Depends on:** Week 3 gate

**Files:**

- Create: `src/opportunitylens/api/__init__.py`
- Create: `src/opportunitylens/api/app.py`
- Create: `src/opportunitylens/api/deps.py`
- Create: `src/opportunitylens/api/routes/__init__.py`
- Create: `src/opportunitylens/api/routes/health.py`
- Create: `src/opportunitylens/api/routes/sources.py`
- Create: `src/opportunitylens/api/routes/runs.py`
- Create: `src/opportunitylens/api/routes/profiles.py`
- Create: `src/opportunitylens/api/routes/jobs.py`
- Create: `src/opportunitylens/api/routes/recommendations.py`
- Create: `src/opportunitylens/api/routes/applications.py`
- Create: `src/opportunitylens/api/routes/feedback.py`
- Create: `src/opportunitylens/api/routes/evaluations.py`
- Create: `src/opportunitylens/worker/__init__.py`
- Create: `src/opportunitylens/worker/claim.py`
- Create: `src/opportunitylens/worker/main.py`
- Create: `tests/unit/worker/test_claim.py`
- Create: `tests/integration/api/test_health.py`
- Create: `tests/integration/api/test_profiles.py`
- Create: `tests/integration/api/test_jobs.py`
- Create: `tests/integration/api/test_feedback.py`
- Create: `tests/integration/api/test_runs.py`
- Create: `tests/integration/worker/test_worker.py`
- Modify: `pyproject.toml`

**Interfaces:**

- Produces: `create_app(settings: Settings) -> FastAPI`.
- Produces: `/api/v1` resources for sources, ingestion runs, profile documents and facts, profile versions, jobs and history, recommendation runs, feedback, applications, and evaluation runs.
- Produces: `/healthz` process health and `/readyz` dependency readiness.
- Produces: `claim_next_run(session: AsyncSession, worker_id: str) -> RunRecord | None` using `FOR UPDATE SKIP LOCKED`.
- Consumed by: React, Docker Compose, CI, and OpenTelemetry tasks.

- [ ] **Step 1: Write failing health and readiness tests**

```python
@pytest.mark.asyncio
async def test_health_does_not_depend_on_database(app: FastAPI) -> None:
    async with app_client(app, database=FailingDatabase()) as client:
        assert (await client.get("/healthz")).status_code == 200


@pytest.mark.asyncio
async def test_ready_reports_unavailable_database(app: FastAPI) -> None:
    async with app_client(app, database=FailingDatabase()) as client:
        response = await client.get("/readyz")
        assert response.status_code == 503
        assert response.json()["dependencies"]["database"] == "unavailable"
```

- [ ] **Step 2: Write failing asynchronous-run tests**

```python
@pytest.mark.asyncio
async def test_recommendation_endpoint_enqueues_instead_of_running_model(client: AsyncClient, model: SpyModel) -> None:
    response = await client.post("/api/v1/recommendation-runs", json={"profile_version_id": str(PROFILE_ID), "ranking_config_id": "hybrid-rerank-v1"})
    assert response.status_code == 202
    assert response.json()["status"] == "pending"
    assert model.calls == 0
```

- [ ] **Step 3: Write failing atomic-claim tests**

```python
@pytest.mark.postgres
async def test_two_workers_cannot_claim_same_run(run_repository: RunRepository) -> None:
    await run_repository.enqueue(run_record())
    first, second = await asyncio.gather(claim("worker-a"), claim("worker-b"))
    claimed_ids = [item.run_id for item in (first, second) if item is not None]
    assert claimed_ids == [RUN_ID]
```

- [ ] **Step 4: Run tests and confirm failure**

```powershell
uv run pytest tests/integration/api tests/unit/worker tests/integration/worker -q
```

Expected: API and worker modules are absent.

- [ ] **Step 5: Implement resource routes and response contracts**

Use Pydantic request and response models. Return `202 Accepted` with a run resource for ingestion, recommendation, and evaluation creation. Support pagination on jobs and run lists. Expose original posting, history, requirements, evidence, eligibility, score components, uncertainty, freshness, model versions, and ranking configuration through read routes.

For the MVP, the applications route must support at least `saved` and `hidden`. The complete state enum remains `discovered`, `saved`, `applied`, `interviewing`, `rejected`, `offer`, and `hidden`, so later expansion does not require a schema rewrite.

- [ ] **Step 6: Implement worker claim and dispatch**

Within one transaction, select the oldest pending run using `FOR UPDATE SKIP LOCKED`, set `running`, assign worker ID and heartbeat time, and commit. Dispatch by run kind to ingestion, enrichment, recommendation, analysis, or evaluation services. Transition to `completed`, `completed_with_errors`, `failed`, or `cancelled` using expected-state checks.

The worker polls with a configurable one-second interval and exits cleanly on SIGINT or SIGTERM after finishing the current database transaction.

- [ ] **Step 7: Verify OpenAPI and worker behavior**

```powershell
uv run pytest tests/integration/api tests/unit/worker tests/integration/worker -q
uv run python -c "from opportunitylens.api.app import create_app; print(sorted(create_app().openapi()['paths']))"
```

Expected: all required `/api/v1` resources plus `/healthz` and `/readyz` appear; tests prove API requests do not run long model work synchronously and duplicate workers cannot claim one run.

- [ ] **Step 8: Commit**

```powershell
git add pyproject.toml uv.lock src/opportunitylens/api src/opportunitylens/worker tests/integration/api tests/unit/worker tests/integration/worker
git commit -m "feat: expose API and database worker"
```

### Task 19: Build Resume Review, Opportunity Feed, and Match Dossier Views

**Estimate:** 8 hours

**Depends on:** Task 18

**Files:**

- Create: `web/package.json`
- Create: `web/package-lock.json`
- Create: `web/tsconfig.json`
- Create: `web/vite.config.ts`
- Create: `web/index.html`
- Create: `web/src/main.tsx`
- Create: `web/src/App.tsx`
- Create: `web/src/api/client.ts`
- Create: `web/src/api/types.ts`
- Create: `web/src/pages/ProfilePage.tsx`
- Create: `web/src/pages/OpportunitiesPage.tsx`
- Create: `web/src/pages/OpportunityDetailPage.tsx`
- Create: `web/src/pages/SourceStatusPage.tsx`
- Create: `web/src/components/EvidenceLink.tsx`
- Create: `web/src/components/EligibilityBadge.tsx`
- Create: `web/src/components/ScoreBreakdown.tsx`
- Create: `web/src/components/UncertaintyNotice.tsx`
- Create: `web/src/test/setup.ts`
- Create: `web/src/pages/ProfilePage.test.tsx`
- Create: `web/src/pages/OpportunitiesPage.test.tsx`
- Create: `web/src/pages/OpportunityDetailPage.test.tsx`
- Create: `web/src/pages/SourceStatusPage.test.tsx`
- Modify: `.gitignore`

**Interfaces:**

- Consumes: the generated FastAPI OpenAPI schema and `/api/v1` JSON contracts from Task 18.
- Produces: profile review and version save flow, source-status view, filterable opportunity feed, and evidence-resolving dossier.
- Consumed by: Playwright and final demonstration.

- [ ] **Step 1: Scaffold Vite React TypeScript and lock dependencies**

Use React, React Router, TanStack Query, and a small CSS module or plain CSS setup. Use Vitest, Testing Library, MSW, ESLint, and TypeScript for deterministic checks. Do not add a component framework during the four-week MVP.

Run:

```powershell
npm --prefix web install
```

Expected: `web/package-lock.json` is created and `npm audit` output is reviewed. Any unresolved high-severity production dependency is fixed or documented before committing.

- [ ] **Step 2: Write the failing profile review test**

```tsx
it("requires every extracted fact to be reviewed before saving a profile version", async () => {
  renderProfilePage(profileWithTwoExtractedFacts());
  await user.click(screen.getByRole("button", { name: /save profile version/i }));
  expect(screen.getByText(/review 2 extracted facts/i)).toBeVisible();
  expect(api.createProfileVersion).not.toHaveBeenCalled();
});
```

- [ ] **Step 3: Write the failing feed and uncertainty tests**

```tsx
it("keeps uncertain jobs visible and labels why", async () => {
  renderOpportunitiesPage([uncertainJob({ reason: "Work authorization is not stated" })]);
  expect(await screen.findByText("Uncertain eligibility")).toBeVisible();
  expect(screen.getByText("Work authorization is not stated")).toBeVisible();
});
```

- [ ] **Step 4: Write the failing evidence-link dossier test**

```tsx
it("opens the exact posting evidence for a match claim", async () => {
  renderOpportunityDetailPage(matchWithEvidence("job-evidence-17"));
  await user.click(screen.getByRole("button", { name: /view evidence/i }));
  expect(screen.getByTestId("evidence-job-evidence-17")).toHaveTextContent("Python and SQL");
});
```

- [ ] **Step 5: Run frontend tests and confirm failure**

```powershell
npm --prefix web run test -- --run
```

Expected: tests fail because pages and components are not implemented.

- [ ] **Step 6: Implement typed API access and onboarding**

Generate or validate TypeScript response types from FastAPI OpenAPI during `npm run generate-api`. The profile page uploads the PDF, shows page and excerpt for every draft fact, supports confirm, correct, and reject, collects constraints and preferences, and saves a new immutable profile version only after every extracted fact is reviewed.

- [ ] **Step 7: Implement the opportunity feed**

Each card shows company, title, original location, internship period if evidenced, eligibility, relevance band, top reasons, highest-priority uncertainty, source provider, and freshness. Filters cover role, eligibility, company, location, workplace type, age, relevance band, and application state.

- [ ] **Step 8: Implement source status and the dossier**

The source-status view lists each curated company, provider, most recent run status, completeness, posting count, last success, consecutive failures, and typed error summary without raw payload content.

Show original posting, structured requirements, candidate evidence, unevidenced requirements, eligibility reasons, component scores, overall relevance, cited claims when available, freshness, lifecycle history, model revisions, ranking configuration, and degraded components. Label scores as relevance signals, never hiring probabilities or employer ATS scores.

- [ ] **Step 9: Verify accessibility and tests**

```powershell
npm --prefix web run typecheck
npm --prefix web run lint
npm --prefix web run test -- --run
npm --prefix web run build
```

Expected: TypeScript, lint, tests, and production build pass. Every form field has a label, keyboard focus is visible, and uncertainty is text rather than color alone.

- [ ] **Step 10: Commit**

```powershell
git add web .gitignore
git commit -m "feat: add OpportunityLens core web flow"
```

### Task 20: Add Bounded Analyst, Deterministic Citation Validation, Critic, Repair, and Abstention

**Estimate:** 5 hours

**Depends on:** Tasks 15, 16, and 18

**Files:**

- Create: `src/opportunitylens/analysis/__init__.py`
- Create: `src/opportunitylens/analysis/schemas.py`
- Create: `src/opportunitylens/analysis/providers.py`
- Create: `src/opportunitylens/analysis/citations.py`
- Create: `src/opportunitylens/analysis/graph.py`
- Create: `src/opportunitylens/enrichment/llm_requirements.py`
- Create: `tests/unit/analysis/test_citations.py`
- Create: `tests/unit/analysis/test_graph.py`
- Create: `tests/unit/enrichment/test_llm_requirements.py`
- Create: `tests/integration/analysis/test_ollama.py`
- Create: `configs/prompts/match-analyst-v1.txt`
- Create: `configs/prompts/eligibility-critic-v1.txt`
- Create: `configs/analysis/analyst-only-v1.yaml`
- Create: `configs/analysis/analyst-critic-v1.yaml`
- Modify: `src/opportunitylens/worker/main.py`
- Modify: `src/opportunitylens/storage/repositories.py`
- Create: `evaluation/results/replay-v1-analysis.json`
- Create: `evaluation/reports/replay-v1-analysis.md`
- Modify: `docs/evaluation.md`

**Interfaces:**

- Produces: `StructuredGenerator.generate(schema: type[T], system_prompt: str, input_payload: Mapping[str, JsonValue]) -> T`.
- Produces: `validate_claims(claims: Sequence[MatchClaim], evidence: Mapping[str, EvidenceRecord]) -> ClaimValidationResult`.
- Produces: `build_match_graph(generator: StructuredGenerator, configuration: AnalysisConfiguration) -> CompiledStateGraph`.
- Consumed by: recommendation dossier, Replay comparisons, fallbacks, and traces.

- [ ] **Step 1: Write failing citation validation tests**

```python
def test_validator_rejects_unknown_evidence_id() -> None:
    result = validate_claims((claim("Strong Python evidence", ["missing"]),), {})
    assert result.valid is False
    assert result.errors[0].code == "unknown_evidence_id"


def test_validator_rejects_excerpt_not_found_in_evidence() -> None:
    result = validate_claims((claim("Candidate used Rust", ["resume-1"], excerpt="Rust"),), {"resume-1": evidence("Python")})
    assert result.valid is False
    assert result.errors[0].code == "excerpt_mismatch"
```

- [ ] **Step 2: Write failing graph-budget and fallback tests**

```python
def test_graph_allows_at_most_one_repair() -> None:
    generator = AlwaysInvalidGenerator()
    result = run_graph(generator, match_input())
    assert generator.calls == 3  # analyst, critic, one repair
    assert result.status == "abstained"


def test_unavailable_generator_keeps_deterministic_match() -> None:
    result = run_graph(UnavailableGenerator(), match_input())
    assert result.deterministic_match is not None
    assert result.generated_claims == ()
    assert result.degraded_components == ("generation",)
```

- [ ] **Step 3: Run tests and confirm failure**

```powershell
uv run pytest tests/unit/analysis -q
```

Expected: analysis modules are absent.

- [ ] **Step 4: Define strict graph state and outputs**

`AnalysisState` contains match ID, assembled evidence map, deterministic eligibility, analyst claims, citation errors, critic decision, repair count, final claims, abstention reason, prompt version, model revision, token counts when available, latency, and fallbacks. Job-description content is passed as delimited untrusted data and is never inserted into the system prompt.

- [ ] **Step 5: Implement deterministic validation before criticism**

For each claim, verify known evidence IDs, allowed entity types, exact excerpt containment, source offsets, and consistency with deterministic eligibility. Reject any claim that says the candidate lacks a skill when the only fact is absent evidence. Validation runs before the critic and after the single repair.

- [ ] **Step 6: Implement the bounded graph**

Graph order:

```text
assemble_evidence -> analyst -> validate_citations -> critic
critic pass -> finalize
critic repair -> repair_once -> validate_citations -> finalize_or_abstain
generator unavailable -> deterministic_fallback
```

The analyst handles only the highest-ranked ten jobs. The graph cannot ingest data, mutate posting or profile records, alter eligibility, or apply for jobs.

- [ ] **Step 7: Add Ollama and deterministic fake providers**

Ollama is the default local provider behind `StructuredGenerator`. Enforce JSON schema output and a configured timeout. Fake providers cover valid, unsupported-claim, bad-citation, contradiction, unavailable, and repair-success paths in CI.

- [ ] **Step 8: Add bounded structured extraction for ambiguous requirements**

Call `StructuredGenerator` only for passages the deterministic and token-classification extractors mark ambiguous. Require typed requirement kind, normalized value, importance, confidence, exact quoted span, and evidence ID. Validate the quote and offsets against the original posting before persisting extractor version `structured-v1`. On unavailable or invalid output, keep existing deterministic and token-classified requirements and record `structured_requirement_extraction_unavailable`.

- [ ] **Step 9: Run analyst-only and critic comparisons on a fixed subset**

Select and freeze at least 12 cases from `replay-v1`, including positives, difficult negatives, and abstention cases. Run both configs with the same evidence and model revision. Append citation precision, unsupported-claim count, correct abstention rate, token counts when exposed, and p50 and p95 latency to the raw result.

```powershell
uv run opportunitylens eval run evaluation/datasets/replay-v1.jsonl --config analyst-only-v1 --config analyst-critic-v1 --output evaluation/results/replay-v1-analysis.json --analysis-subset 12
uv run opportunitylens eval report evaluation/results/replay-v1-analysis.json --output evaluation/reports/replay-v1-analysis.md
```

Expected: the output records both analysis variants and every case failure. No report text claims the critic improved quality unless the raw metrics show it.

- [ ] **Step 10: Verify deterministic and optional Ollama modes**

```powershell
uv run pytest tests/unit/analysis tests/unit/enrichment/test_llm_requirements.py -q
uv run pytest tests/integration/analysis/test_ollama.py -q -m ollama
```

Expected: unit tests pass without Ollama. The marked test passes only when the configured local model is running; its absence leaves deterministic recommendations available.

- [ ] **Step 11: Commit**

```powershell
git add src/opportunitylens/analysis src/opportunitylens/enrichment/llm_requirements.py src/opportunitylens/worker/main.py src/opportunitylens/storage/repositories.py tests/unit/analysis tests/unit/enrichment/test_llm_requirements.py tests/integration/analysis configs/prompts configs/analysis evaluation/results/replay-v1-analysis.json evaluation/reports/replay-v1-analysis.md docs/evaluation.md
git commit -m "feat: add bounded cited match analysis"
```

### Task 21: Add Replay Lab UI and Minimal Application State

**Estimate:** 4 hours

**Depends on:** Tasks 18 through 20

**Files:**

- Create: `web/src/pages/ReplayLabPage.tsx`
- Create: `web/src/pages/ReplayLabPage.test.tsx`
- Create: `web/src/components/ConfigurationComparison.tsx`
- Create: `web/src/components/FailureCaseTable.tsx`
- Create: `web/src/components/ApplicationStateControl.tsx`
- Create: `web/src/components/ApplicationStateControl.test.tsx`
- Modify: `web/src/App.tsx`
- Modify: `web/src/pages/OpportunitiesPage.tsx`
- Modify: `web/src/pages/OpportunityDetailPage.tsx`

**Interfaces:**

- Consumes: evaluation, application, and match endpoints from Task 18.
- Produces: configuration comparison, ranking-change inspection, failure-case inspection, and save or hide controls.
- Consumed by: Playwright and final demo.

- [ ] **Step 1: Write failing comparison tests**

```tsx
it("shows metrics with case counts and configuration revisions", async () => {
  renderReplayLabPage(replayRun());
  expect(await screen.findByText("nDCG@10")).toBeVisible();
  expect(screen.getByText(/60 reviewed pairs/i)).toBeVisible();
  expect(screen.getByText("hybrid-rerank-v1")).toBeVisible();
});


it("does not render a missing metric as zero", async () => {
  renderReplayLabPage(replayRun({ citationPrecision: null }));
  expect(await screen.findByText("Not measured")).toBeVisible();
});
```

- [ ] **Step 2: Write failing application-state tests**

```tsx
it("saves and hides a posting without contacting an employer", async () => {
  renderApplicationStateControl();
  await user.click(screen.getByRole("button", { name: /save/i }));
  expect(api.setApplicationState).toHaveBeenCalledWith(JOB_ID, "saved");
  expect(api.externalRequests).toHaveLength(0);
});
```

- [ ] **Step 3: Run tests and confirm failure**

```powershell
npm --prefix web run test -- --run ReplayLabPage ApplicationStateControl
```

Expected: components are absent.

- [ ] **Step 4: Implement Replay Lab comparisons**

Allow selecting frozen run and configuration IDs. Show metric value, numerator or denominator where meaningful, case count, model revision, dataset hash, p50 and p95 latency, and fallback count. Show individual rank changes, eligibility changes, evidence expectations, reviewer notes, and documented failure cases.

- [ ] **Step 5: Implement save and hide only as the protected minimum**

Store state locally through the application API. Do not contact employer systems. If Week 4 is ahead of schedule, expose the remaining approved states in the same enum. Do not build the in-app digest until every core completion gate already passes.

- [ ] **Step 6: Verify and commit**

```powershell
npm --prefix web run typecheck
npm --prefix web run lint
npm --prefix web run test -- --run
npm --prefix web run build
git add web/src
git commit -m "feat: expose ranking replay comparisons"
```

### Task 22: Add Docker Compose, Health Checks, OpenTelemetry, Structured Metrics, and CI

**Estimate:** 6 hours

**Depends on:** Tasks 18 through 21

**Files:**

- Create: `docker/api.Dockerfile`
- Create: `docker/web.Dockerfile`
- Create: `.dockerignore`
- Create: `.github/workflows/ci.yml`
- Create: `src/opportunitylens/telemetry.py`
- Create: `tests/unit/test_telemetry.py`
- Create: `tests/integration/test_compose_contract.py`
- Modify: `docker-compose.yml`
- Modify: `src/opportunitylens/api/app.py`
- Modify: `src/opportunitylens/worker/main.py`
- Modify: `src/opportunitylens/logging.py`
- Modify: `.env.example`

**Interfaces:**

- Produces: Compose services `db`, `api`, `worker`, and `web`, with an optional external Ollama connection configured by environment.
- Produces: OpenTelemetry spans across API, run claim, ingestion, enrichment, retrieval, reranking, analysis, validation, and evaluation.
- Produces: deterministic CI jobs for backend, frontend, evaluation regression, and container builds.
- Consumed by: final clean-start and demo verification.

- [ ] **Step 1: Write failing telemetry redaction tests**

```python
def test_resume_and_contact_fields_are_not_exported(span_exporter: InMemorySpanExporter) -> None:
    instrument_operation("profile.extract", {"resume_text": "private", "email": "student@example.com", "profile_version_id": "pv-1"})
    attributes = span_exporter.get_finished_spans()[0].attributes
    assert "resume_text" not in attributes
    assert "email" not in attributes
    assert attributes["profile_version_id"] == "pv-1"
```

- [ ] **Step 2: Write the failing Compose contract test**

Validate parsed Compose YAML has the four required services; API waits for healthy database; web waits for API; worker and API use the same image and configuration; only web and API expose host ports; no secrets appear as literal values.

- [ ] **Step 3: Run tests and confirm failure**

```powershell
uv run pytest tests/unit/test_telemetry.py tests/integration/test_compose_contract.py -q
```

Expected: telemetry and full Compose configuration are absent.

- [ ] **Step 4: Containerize reproducibly**

The API image installs locked Python dependencies and runs migrations as an explicit one-shot Compose command before API startup. The worker uses the same immutable image with a different command. The web image builds static assets and serves them with a small nonroot HTTP server. Add health checks for database, API, worker heartbeat, and web.

Configure Ollama through `OPPORTUNITYLENS_OLLAMA_BASE_URL`; document `http://host.docker.internal:11434` for supported local Docker Desktop setups and keep generation optional.

- [ ] **Step 5: Instrument runs and degradation**

Every span includes correlation ID, run ID, operation, model revision, prompt version, ranking configuration ID, status, latency, retry count, validation-failure count, and fallback type when applicable. Metrics cover provider availability, queue depth, ingestion counts, classification failures, model latency, and fallback use. Never attach original job or resume text.

- [ ] **Step 6: Implement CI jobs**

The workflow runs:

1. Python lock check, Ruff, strict mypy, unit tests, and PostgreSQL integration tests with fake models.
2. The 12-case deterministic Replay regression and report regeneration check.
3. Frontend install from lockfile, typecheck, lint, Vitest, and production build.
4. API and web container builds plus Compose configuration validation.
5. Playwright after Task 23 adds the happy path.

Do not run live provider, Hugging Face download, or Ollama tests in pull-request CI.

- [ ] **Step 7: Verify local containers and fallbacks**

```powershell
docker compose config --quiet
docker compose build api worker web
docker compose up -d db api worker web
docker compose ps
Invoke-RestMethod http://localhost:8000/healthz
Invoke-RestMethod http://localhost:8000/readyz
```

Expected: all four services become healthy; both endpoints report success; the feed works in fake-model mode with Ollama absent.

- [ ] **Step 8: Run CI-equivalent checks and commit**

```powershell
uv run pytest tests/unit tests/integration -q -m "not live_provider and not model and not ollama"
uv run ruff check src tests scripts migrations
uv run mypy src scripts
npm --prefix web ci
npm --prefix web run typecheck
npm --prefix web run lint
npm --prefix web run test -- --run
npm --prefix web run build
git add docker .dockerignore docker-compose.yml .github/workflows/ci.yml src/opportunitylens/telemetry.py src/opportunitylens/api/app.py src/opportunitylens/worker/main.py src/opportunitylens/logging.py tests/unit/test_telemetry.py tests/integration/test_compose_contract.py .env.example
git commit -m "chore: containerize and observe OpportunityLens"
```

### Task 23: Verify the Happy Path and Publish a Reproducible Portfolio Story

**Estimate:** 5 hours

**Depends on:** Task 22

**Files:**

- Create: `web/playwright.config.ts`
- Create: `web/tests/happy-path.spec.ts`
- Create: `scripts/verify_measurements.py`
- Create: `tests/unit/test_verify_measurements.py`
- Create: `src/opportunitylens/demo.py`
- Create: `tests/integration/test_demo_seed.py`
- Create: `docs/architecture.md`
- Create: `docs/limitations.md`
- Create: `docs/demo-script.md`
- Modify: `docs/evaluation.md`
- Modify: `README.md`
- Modify: `src/opportunitylens/cli.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**

- Produces: one deterministic browser test, one measurement-verification command, final architecture and limitation docs, and a short demo script.
- Produces: the evidence needed for resume bullets without generating unmeasured numbers.

- [ ] **Step 1: Write the failing browser happy path**

```ts
import path from "node:path";

test("reviews a resume and opens a cited recommendation", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Resume PDF").setInputFiles(
    path.resolve("..", "tests", "fixtures", "resumes", "text-resume.pdf"),
  );
  await page.getByRole("button", { name: "Upload" }).click();
  await page.getByRole("button", { name: "Confirm all fixture facts" }).click();
  await page.getByRole("button", { name: "Save profile version" }).click();
  await page.getByRole("link", { name: "Opportunities" }).click();
  await page.getByRole("link", { name: /software engineer intern/i }).first().click();
  await page.getByRole("button", { name: /view evidence/i }).first().click();
  await expect(page.getByTestId("evidence-panel")).toContainText("Python");
  await expect(page.getByText(/ranking configuration/i)).toBeVisible();
});
```

Use a seeded database, captured provider fixtures, and fake models. The test must not access a live employer or Ollama.

- [ ] **Step 2: Run Playwright and confirm failure**

```powershell
npm --prefix web run test:e2e
```

Expected: the fixture bootstrap or browser flow is not yet wired.

- [ ] **Step 3: Add deterministic seed and complete the browser flow**

Provide `opportunitylens demo seed` to reset only the named demo database, load two-provider fixtures, run enrichment and recommendation with fake models, and create the synthetic PDF review state. Guard the command so it refuses any database not ending in `_demo` or `_test`.

- [ ] **Step 4: Write measurement-verification tests**

```python
def test_readme_numbers_resolve_to_raw_evaluation(tmp_path: Path) -> None:
    result = verify_measurements(Path("README.md"), Path("evaluation/results"))
    assert result.unresolved_claims == ()


def test_bracketed_resume_metric_is_rejected() -> None:
    unresolved_marker = "[" + "X" + "]"
    result = verify_text(f"Improved nDCG@10 by {unresolved_marker}%")
    assert result.errors == (f"unresolved metric marker: {unresolved_marker}",)
```

- [ ] **Step 5: Implement measured-claim verification**

Require every quantitative README and resume-ready statement to include a machine-readable footnote such as `<!-- metric: replay-v1-baseline.json#/configurations/hybrid-v1/ndcg_at_10 -->`. Resolve the JSON pointer, ensure displayed rounding matches the raw value, and reject bracketed metric markers, percentages without references, or case counts that differ from raw artifacts.

- [ ] **Step 6: Write beginner-first documentation**

`README.md` must contain:

1. The student problem and one-sentence product value.
2. A five-minute Docker Compose quick start using fixture and fake-model mode.
3. An optional live-source and local-model section with privacy and access warnings.
4. A small architecture diagram and links to `docs/architecture.md`.
5. A reproducible Replay command, selected configuration rule, raw result link, and limitations.
6. A clear distinction among eligibility, relevance, and employer hiring decisions.
7. Evidence, lifecycle, fallback, and privacy behavior.
8. No claim of large coverage, employer ATS scoring, or hiring probability.

`docs/architecture.md` maps the data flow, run state machine, evidence resolution, model cascade, and fallback ladder. `docs/limitations.md` records audit date, supported providers, small label set, subjective relevance labels, PDF text-only support, local hardware limits, live-source drift, and single-user status. `docs/demo-script.md` fits a three-to-five-minute recording and demonstrates idempotent ingestion, profile review, uncertainty, dossier evidence, Replay comparison, and one forced degraded mode.

- [ ] **Step 7: Run a clean Docker Compose demonstration**

From the saved checkout with no model cache. Do not create or use a Codex worktree for this demonstration:

```powershell
Copy-Item .env.example .env
docker compose build
docker compose up -d db
docker compose run --rm api uv run alembic upgrade head
docker compose run --rm api uv run opportunitylens demo seed
docker compose up -d api worker web
npm --prefix web run test:e2e
uv run python scripts/verify_measurements.py README.md evaluation/results
```

Expected: the complete deterministic flow works without a paid API or model download; Playwright passes; measurement verification reports zero unresolved claims.

- [ ] **Step 8: Run the full release verification**

```powershell
uv lock --check
uv run ruff check src tests scripts migrations
uv run mypy src scripts
uv run pytest tests/unit tests/integration -q -m "not live_provider and not model and not ollama"
uv run opportunitylens eval validate evaluation/datasets/replay-v1.jsonl
uv run opportunitylens eval report evaluation/results/replay-v1-baseline.json --output evaluation/reports/replay-v1-baseline.md
git diff --exit-code -- evaluation/reports/replay-v1-baseline.md
uv run opportunitylens eval report evaluation/results/replay-v1-analysis.json --output evaluation/reports/replay-v1-analysis.md
git diff --exit-code -- evaluation/reports/replay-v1-analysis.md
npm --prefix web ci
npm --prefix web run typecheck
npm --prefix web run lint
npm --prefix web run test -- --run
npm --prefix web run build
npm --prefix web run test:e2e
docker compose config --quiet
docker compose build api worker web
```

Expected: every command exits zero. Save exact test counts and measured latency from generated artifacts, not from console memory.

- [ ] **Step 9: Record the demonstration**

Follow `docs/demo-script.md` with a synthetic or explicitly approved redacted resume. Show the audit-derived provider coverage, a repeated idempotent fixture ingestion, one changed posting, one uncertain eligibility reason, one evidence-linked dossier, ranking comparisons, raw JSON, and a forced generation or vector fallback. Do not show personal contact information.

- [ ] **Step 10: Commit the portfolio finish**

```powershell
git add README.md docs/architecture.md docs/evaluation.md docs/limitations.md docs/demo-script.md web/playwright.config.ts web/tests/happy-path.spec.ts scripts/verify_measurements.py tests/unit/test_verify_measurements.py src/opportunitylens/demo.py src/opportunitylens/cli.py tests/integration/test_demo_seed.py .github/workflows/ci.yml
git commit -m "docs: publish reproducible OpportunityLens MVP"
```

### Week 4 Completion Gate

- [ ] A documented Docker Compose flow starts database, API, worker, and web.
- [ ] API long operations enqueue database-backed runs and the worker claims each run once.
- [ ] Resume review, opportunity feed, dossier, Replay Lab, and save or hide work in React.
- [ ] Every displayed eligibility reason and match claim resolves to evidence or explicitly identifies missing evidence.
- [ ] Analyst validation has at most one repair and abstains after unresolved errors.
- [ ] The deterministic feed survives unavailable vector, reranker, and generation components.
- [ ] CI passes without live providers, downloaded models, Ollama, paid APIs, or employer accounts.
- [ ] Raw evaluation JSON regenerates the report and supports every quantitative README statement.
- [ ] One deterministic Playwright happy path passes from PDF upload to evidence inspection.

---

## Scope-Cut Triggers and Protected Core

Use the weekly gates as hard decision points. A cut removes planned breadth, never a correctness invariant.

| Trigger | Immediate cut | Still required |
| --- | --- | --- |
| Week 1 exceeds 32 focused hours | Reduce configured employers after the 30-row audit to one live source per selected provider plus captured fixtures. | Keep the complete audit, two selected provider types, provider fault isolation, raw snapshots, and idempotency. |
| Week 2 gate is not green by the end of Day 10 | Stop adding classification labels and extraction patterns beyond the approved core vocabulary. | Keep strict evidence spans, versioning, both adapters, safe lifecycle, one classification model path, and deterministic fallback. |
| Week 3 lab exceeds 32 focused hours | Freeze at exactly 60 pairs and the required five ranking configurations. Add no extra profiles or model sweep. | Keep difficult negatives, ambiguous eligibility, raw results, selection rule, and all required metrics. |
| Week 4 core web flow is not green by the end of Day 17 | Use plain CSS and remove visual animations, charts, and nonessential responsiveness work. | Keep accessible forms, evidence inspection, uncertainty, configurations, and failure states. |
| Week 4 analysis tests are not green by the end of Day 18 | Ship analyst plus deterministic citation validation and omit the separate LLM critic, recording this approved cut in limitations. | Keep bounded execution, at most one repair where applicable, abstention, deterministic recommendations, and the analyst-only Replay result. |
| Less than one day remains before release verification | Limit application state to save and hide, and omit the in-app digest. | Keep API resource shape, source freshness, changed-posting visibility, and all resume-ready definition-of-done items. |

Never cut:

1. Raw source provenance and append-only snapshots.
2. Canonical job identity and idempotent ingestion.
3. Safe incomplete-run lifecycle behavior.
4. Candidate fact verification and versioned profiles.
5. Three-state eligibility and visible uncertainty.
6. Lexical baseline, reproducible evaluation, and at least 60 labelled pairs.
7. Evidence validation or abstention for generated claims.
8. Graceful degradation and deterministic CI.

## Principal Risks and Concrete Mitigations

| Risk | Early signal | Mitigation and decision point |
| --- | --- | --- |
| Audit yields poor public ATS coverage | Fewer than two feasible providers after 30 verified employers | Expand by ten employers before coding. If Workday dominates but public access is brittle, require one proven public tenant and captured pagination fixture before selecting it. |
| Live provider schema changes | Fixture passes but live contract reports missing required fields | Quarantine malformed records, mark the source incomplete, preserve raw payload and schema error, update fixtures in a separate evidence-backed commit. |
| Public endpoints rate-limit or block access | HTTP 429 or 403 during audit and live smoke | Respect `Retry-After`, stop after bounded retries, retain fixture mode, and state live limitations. Never add browser bypass logic. |
| Four-week scope exceeds student capacity | Weekly gate misses its stated hour budget | Apply the scope-cut table immediately. Do not borrow time from testing, evaluation, provenance, or documentation. |
| Too few Singapore internships are open | Audit and live ingestion find small or zero current counts | Preserve dated real snapshots, include carefully labelled non-Singapore and non-internship negatives, and avoid volume claims. Do not fabricate jobs. |
| Ranking labels reflect one reviewer | Large metric changes on a few cases | Use three profiles, publish pair counts and reviewer notes, retain difficult negatives, and state the single-reviewer limitation. |
| Local hardware cannot run configured models | Model smoke exceeds memory or p95 target | Keep fake CI and deterministic rules, reduce batch sizes, measure a smaller versioned model in a new config, and preserve the previous result. |
| pgvector or reranker is unavailable | Typed component health check fails | Serve lexical results or fused results, show degraded state in API and UI, and increment fallback metrics. |
| LLM output overstates evidence | Citation or contradiction validation fails | Allow one repair, then abstain. Never surface unvalidated generated claims. |
| Resume content leaks to telemetry | Test exporter contains raw text or contact keys | Fail CI on redaction tests, use identifier-only spans and logs, keep upload storage nonpublic, and demonstrate with synthetic data. |
| Metrics become marketing claims | README number has no JSON pointer | Fail `scripts/verify_measurements.py`, remove the statement, or regenerate the measured artifact. |
| Legacy files return during later work | Retired runtime names or paths reappear in active files | Use Git history only as reference, never copy retired runtime files into active paths, and preserve untracked user paths. |

## Final Resume-Ready Definition of Done

The MVP is resume-ready only when all items below are evidenced in the repository:

1. The source audit includes at least 30 verified employers and deterministically selects two feasible public ATS provider types.
2. Captured fixtures and at least one opt-in live source per selected provider use the same adapter contract.
3. Repeated ingestion creates no duplicate canonical jobs, appends source snapshots and observations, and reproduces changed, missing, reopened, and closed lifecycles.
4. An incomplete source response cannot close or advance the absence counter for an unseen job.
5. A synthetic or approved redacted PDF can be uploaded, parsed, reviewed, confirmed, corrected, rejected, and saved as an immutable profile version with evidence.
6. Eligibility is stored separately from relevance and represents unknown information as `uncertain`.
7. Lexical, dense, hybrid RRF, and cross-encoder reranked configurations run reproducibly against the same frozen corpus.
8. The Replay Lab contains exactly three profiles and at least 60 reviewed pairs, with difficult negatives, ambiguous eligibility, raw JSON, and generated Markdown.
9. The default ranking configuration follows the declared false-eligible, Recall@50, nDCG@10, and latency decision rule.
10. Generated match claims pass deterministic evidence and contradiction checks or the system abstains; the graph never exceeds one repair.
11. Vector, reranker, and generator failures each produce the specified lower-cost usable result and a visible degraded flag.
12. FastAPI and the worker expose and execute versioned asynchronous resources; React completes profile review, feed, dossier, Replay comparison, and save or hide.
13. Docker Compose starts the complete deterministic flow and exposes distinct health and readiness behavior.
14. CI verifies backend quality, PostgreSQL integration, a deterministic Replay subset, frontend tests, container builds, and one Playwright path without paid services.
15. OpenTelemetry and structured logs connect runs and fallbacks without resume text, job descriptions, contact data, cookies, or tokens.
16. README claims link to raw artifacts, limitations are explicit, and the demo uses synthetic or approved redacted data.
17. Resume bullets are written only after completion by substituting exact audit, ranking, citation, latency, and test measurements verified by `scripts/verify_measurements.py`.

## Requirements Traceability

| Approved design area | Implemented by |
| --- | --- |
| Curated registry and 30-employer audit | Task 1 |
| Two measured public ATS adapters and fetch policy | Tasks 5 and 7 |
| Strict source, job, evidence, profile, match, and run contracts | Task 3 |
| PostgreSQL, pgvector, append-only snapshots, and versioning | Task 4 |
| Idempotent normalization and per-source failures | Task 6 |
| Safe missing and closed lifecycle | Task 8 |
| Rules, classification, requirements, evidence spans, embeddings | Tasks 9 through 11 |
| PDF profile review, correction, rejection, and deletion | Task 12 |
| Hard eligibility with uncertainty | Task 13 |
| Lexical, dense, RRF, and reranker cascade | Tasks 14 and 15 |
| Three profiles, 60 pairs, required metrics, and raw reports | Tasks 16 and 17 |
| Versioned API resources and database worker | Task 18 |
| Onboarding, feed, dossier, tracking minimum, and Replay UI | Tasks 19 and 21 |
| Analyst, citation validator, critic, one repair, and abstention | Task 20 |
| Graceful degradation | Tasks 10, 14, 15, 20, and 22 |
| Docker Compose, health, readiness, OpenTelemetry, and CI | Task 22 |
| Playwright, documentation, measured claims, and demo | Task 23 |

## Suggested Commit Sequence

1. `docs: audit Singapore employer ATS coverage`
2. `chore: scaffold OpportunityLens runtime`
3. `feat: define OpportunityLens domain contracts`
4. `feat: persist OpportunityLens provenance`
5. Provider-specific first-adapter message from the fixed mapping
6. `feat: ingest jobs idempotently with provenance`
7. Provider-specific second-adapter message from the fixed mapping
8. `feat: track posting lifecycle safely`
9. `feat: extract evidenced job requirements`
10. `feat: version classification and embedding models`
11. `feat: join ingestion and enrichment runs`
12. `feat: version verified candidate profiles`
13. `feat: evaluate eligibility with uncertainty`
14. `feat: add hybrid RRF retrieval`
15. `feat: rerank versioned recommendations`
16. `feat: add reproducible Ranking Replay Lab`
17. `eval: compare OpportunityLens ranking configurations`
18. `feat: expose API and database worker`
19. `feat: add OpportunityLens core web flow`
20. `feat: add bounded cited match analysis`
21. `feat: expose ranking replay comparisons`
22. `chore: containerize and observe OpportunityLens`
23. `docs: publish reproducible OpportunityLens MVP`

Each commit must pass its focused tests before creation. At each weekly gate, run the broader deterministic suite. Do not stage unrelated files with `git add .`.

## Plan Self-Review Record

1. **Specification coverage:** All design sections map to tasks in Requirements Traceability. Full application-state tracking and the in-app digest are explicitly protected scope cuts; save and hide remain in the core.
2. **Prerequisites:** The plan calls out the broken uv launcher, PostgreSQL and Docker requirements, immutable Hugging Face revisions, optional Ollama, and direct saved-checkout branch setup before product work.
3. **Type consistency:** Provider, ingestion, profile, eligibility, ranking, evaluation, analysis, API, and worker signatures use the same domain types defined in Task 3. Ranking configuration IDs and evaluation paths are consistent across Tasks 14 through 23.
4. **Dependency consistency:** No adapter starts before the audit. Lifecycle follows canonical ingestion. Ranking follows profile and enrichment. Replay precedes API and UI. Generated analysis follows deterministic ranking and evidence.
5. **Workload:** Weekly estimates are 32, 28 plus buffer, 32, and 34 focused hours. The scope-cut triggers prevent polish, tracking breadth, extra model sweeps, or dataset growth from consuming core verification time.
6. **Evidence and safety:** Append-only snapshots, safe incomplete-run behavior, evidence resolution, unknown eligibility, private-data redaction, bounded graph behavior, and all three graceful fallbacks have both implementation and test steps.
7. **Metric integrity:** The plan never supplies an impact result. It defines how actual counts and scores are generated, traced to raw JSON, and checked before appearing in documentation or resume bullets.
8. **Repository safety:** The plan preserves untracked user paths and source-audit evidence, uses the approved normal feature branches in the saved checkout, and does not use a Codex worktree.

Plan complete and saved to `docs/superpowers/plans/2026-09-14-opportunitylens-sg-mvp.md`. Review and approve this plan before implementation starts. After approval, use one of these execution modes:

1. **Subagent-Driven, recommended:** use `superpowers:subagent-driven-development`, dispatch one fresh implementer per task, and review specification compliance and code quality between tasks.
2. **Inline Execution:** use `superpowers:executing-plans`, implement in small batches, and stop at each weekly gate for review.
