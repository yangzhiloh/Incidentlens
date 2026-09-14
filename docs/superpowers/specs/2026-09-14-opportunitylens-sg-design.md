# OpportunityLens SG Design Specification

**Status:** Approved in chat, written review pending

**Date:** 2026-09-14

**Target:** A resume-ready solo AI engineering MVP completed in one month

**Primary users:** University students seeking AI and software internships in Singapore

## 1. Executive summary

OpportunityLens SG is an evidence-grounded internship intelligence system. It ingests public job postings directly from employer applicant tracking systems, normalizes inconsistent source data, identifies Singapore internships, tracks listing changes, and ranks opportunities against a verified candidate profile.

The product explains each recommendation using evidence from both the job posting and the candidate's resume. It distinguishes confirmed facts, inferred requirements, hard eligibility constraints, preferences, and unknown information. It does not claim that a user lacks a skill merely because that skill is absent from the resume.

The portfolio differentiator is the Ranking Replay Lab. The lab runs versioned candidate profiles against frozen real-world posting snapshots and compares lexical, dense, hybrid, and reranked retrieval configurations using human relevance labels. It also measures eligibility errors, citation validity, unsupported claims, latency, and degraded behavior.

The MVP is local-first, single-user, and read-only with respect to external hiring systems. It does not submit applications.

## 2. One-month objective

At the end of four weeks, a reviewer must be able to:

1. Start the application through a documented Docker Compose workflow.
2. Ingest real postings from at least two public ATS provider types selected through a Singapore employer coverage audit.
3. Observe idempotent ingestion, changed-posting detection, and safe missing-posting handling.
4. Upload a test resume and review extracted candidate facts with source evidence.
5. Configure internship, location, availability, role, and technology preferences.
6. Receive ranked Singapore internship recommendations.
7. Open a match dossier containing transparent subscores, uncertainties, and resolvable citations.
8. Compare at least three retrieval configurations in the Ranking Replay Lab.
9. Inspect raw evaluation results and a generated report containing only measured claims.
10. Run deterministic tests and a small evaluation regression suite in CI without paid APIs.

The project is resume-ready when these behaviors work reliably. Large posting counts, cloud deployment, and a polished multi-user service are not completion requirements.

## 3. Goals

1. Solve a real student problem: fragmented internship discovery and poor relevance filtering.
2. Demonstrate ingestion from inconsistent real-world APIs.
3. Preserve source snapshots and provenance for reproducibility.
4. Use Hugging Face classification, feature extraction, sentence similarity, and text ranking tasks as measurable pipeline components.
5. Implement hybrid retrieval and a model cascade that limits expensive inference.
6. Provide evidence-backed explanations and explicit uncertainty.
7. Evaluate ranking quality against frozen, human-labelled cases.
8. Demonstrate bounded LangGraph orchestration where model reasoning adds value.
9. Include production-oriented validation, idempotency, observability, graceful degradation, containers, and CI.
10. Keep the system understandable and feasible for one student to finish in four weeks.

## 4. Non-goals

1. The MVP will not submit applications or fill external forms.
2. The MVP will not scrape authenticated pages or bypass bot protection.
3. The MVP will not support every Singapore employer or ATS provider.
4. The MVP will not scrape LinkedIn, Indeed, or Google Jobs.
5. The MVP will not provide email or mobile notifications.
6. The MVP will not rewrite resumes or generate cover letters.
7. The MVP will not implement authentication, multi-tenancy, billing, or organization accounts.
8. The MVP will not use an autonomous agent swarm.
9. The MVP will not train a custom neural model unless labelled data and evaluation justify it.
10. The MVP will not describe a relevance score as an employer ATS score or calibrated hiring probability.
11. The MVP will not require Pinecone, Celery, Redis, Kubernetes, or a paid model API.
12. Workday is included in the first month only if the source audit shows that it materially improves target-employer coverage and its implementation fits the schedule.

## 5. Architecture

The local application contains:

1. A React and TypeScript web application.
2. A FastAPI backend.
3. A PostgreSQL database with pgvector.
4. A small database-backed worker for ingestion, enrichment, recommendation, and evaluation runs.
5. Public ATS provider adapters implemented with HTTPX.
6. Hugging Face models for classification, embeddings, and reranking.
7. A bounded LangGraph match-analysis workflow.
8. Ollama as the default local generation provider behind a provider interface.
9. Docker Compose for the web application, API, worker, database, and optional local model connection.
10. OpenTelemetry and structured logs for operational visibility.

The main data flow is:

```text
Company registry
    -> provider adapters
    -> raw posting snapshots
    -> canonical job postings
    -> classification and requirement extraction
    -> PostgreSQL full-text index and pgvector embeddings
    -> hard eligibility filters
    -> lexical and dense retrieval
    -> Reciprocal Rank Fusion
    -> cross-encoder reranking
    -> bounded match analysis
    -> cited recommendation dossier
```

Ingestion, lifecycle decisions, filtering, score calculation, and citation validation remain deterministic. LangGraph operates only after ranking and cannot mutate source data or submit an application.

## 6. Core data contracts

All domain models use strict Pydantic validation. Immutable value objects use `frozen=True`, and unknown fields are forbidden at validation boundaries.

### 6.1 Source and observation models

`CompanySource` records a stable company identifier, display name, ATS provider, board identifier, careers URL, country scope, and enabled state.

`RawPostingSnapshot` records a snapshot identifier, provider, board identifier, provider job identifier, fetch timestamp, content hash, and original payload. Raw snapshots are append-only.

`IngestionRun` records run status, timestamps, source counts, posting counts, errors, and whether every provider response was complete.

`PostingObservation` links an ingestion run, canonical posting, raw snapshot, observation time, and content hash.

### 6.2 Canonical posting model

`JobPosting` records:

1. Stable internal posting identifier.
2. Company identifier.
3. Provider, board identifier, and provider job identifier.
4. Canonical application URL.
5. Title and original description.
6. Structured locations with the original location text preserved.
7. Employment and workplace type.
8. Departments or teams when provided.
9. Published and application deadline timestamps when available.
10. First-seen, last-seen, and lifecycle status.

The authoritative identity is the tuple of provider, board identifier, and provider job identifier. A normalized URL is a fallback deduplication signal, not the primary identity.

Lifecycle states are `active`, `changed`, `missing`, and `closed`. A posting cannot become closed because of an incomplete source fetch. Repeated absence across complete runs is required unless the provider explicitly marks it closed.

### 6.3 Derived posting information

`JobRequirement` records a requirement kind, normalized value, required or preferred importance, extraction confidence, evidence identifier, and extractor version.

`JobClassification` records internship status, one or more role families, seniority, Singapore relevance, confidence, evidence identifiers, and classifier version.

Derived records never overwrite the original posting. Changing a model or extraction policy creates a new versioned result.

### 6.4 Candidate profile

`CandidateFact` records the fact kind, value, verification status, resume evidence, and extractor version. Verification states are `extracted`, `confirmed`, `corrected`, and `rejected`. Rejected facts cannot influence ranking.

`CandidateConstraints` contains categorical eligibility conditions such as accepted locations, work authorization, graduation date, and internship availability.

`CandidatePreferences` contains ranking signals such as target role families, industries, companies, technologies, and workplace preferences.

Every saved candidate profile receives a version. A recommendation run records the exact profile version it used.

### 6.5 Evidence and match models

`EvidenceRecord` is domain-neutral and records an evidence identifier, entity type, entity identifier, source type, original text, typed locator, capture timestamp, and metadata.

Typed locators include:

1. `WebLocator` for a URL, capture time, and provider field path.
2. `DocumentLocator` for a resume document, page, and text offsets.
3. `UserInputLocator` for a profile version and field name.

`MatchResult` records the posting, profile version, eligibility decision, eligibility reasons, component scores, overall relevance, supporting evidence, unevidenced requirements, ranking configuration, and creation timestamp.

The central invariant is:

> Every eligibility decision, extracted requirement, and generated match claim must resolve to stored evidence or explicitly state that evidence is unavailable.

## 7. Ingestion and enrichment

### 7.1 Source selection

The first implementation task is a read-only audit of approximately 30 larger employers with Singapore operations. The audit records each careers URL, ATS provider, board identifier, public accessibility, and rough posting volume.

The first two adapters are selected by measured employer coverage. Greenhouse, Lever, Ashby, and Workday are candidates. The design does not assume that the first three providers cover large enterprises adequately.

The MVP uses a curated company registry. Automatic ATS discovery is postponed.

### 7.2 Provider contract

Each provider implements one common operation:

```text
fetch_postings(source, fetch_context) -> ProviderResult
```

`ProviderResult` contains the provider, company, fetch time, raw postings, errors, request count, and a completeness flag.

Adapters handle endpoint access, pagination, provider-specific rate limiting, and raw response validation. They do not classify roles, calculate matches, or generate explanations.

### 7.3 Fetch policy

HTTP requests use bounded asynchronous concurrency, explicit timeouts, response-size limits, and narrowly scoped retries. The system respects `Retry-After` for HTTP 429 and does not retry permanent validation or authorization errors.

Each company produces an independent success, partial, rate-limited, unavailable, invalid-response, or configuration-error result. One source failure cannot discard successful results from other companies.

### 7.4 Enrichment cascade

Only new or changed postings are enriched:

1. Deterministic HTML cleanup, whitespace normalization, date parsing, and known location aliases.
2. Rule-based internship and role classification as a baseline.
3. Hugging Face text or zero-shot classification for role family, seniority, and Singapore relevance.
4. Deterministic patterns and token classification for skills, education, dates, and experience requirements.
5. Structured LLM extraction only for ambiguous passages.
6. Evidence-span validation against the original stored description.
7. Embedding generation for the role summary, responsibilities, required qualifications, and preferred qualifications.

Cached enrichment remains valid until the posting content hash or enrichment configuration changes.

## 8. Retrieval and ranking

### 8.1 Eligibility

Hard filters evaluate internship type, location, availability, graduation windows, explicit work authorization, and explicit user exclusions. Results are `eligible`, `ineligible`, or `uncertain`.

Unknown work-authorization language cannot become an automatic rejection or acceptance. The primary eligibility safety metric is the false-eligible rate.

### 8.2 Candidate generation

PostgreSQL full-text search provides the lexical baseline. pgvector provides dense retrieval over posting sections. Reciprocal Rank Fusion combines the ranked results without treating incomparable raw scores as equivalent.

A Hugging Face cross-encoder reranks only the top candidate set. Expensive match analysis runs only for the highest-ranked results.

### 8.3 Explainability

The displayed breakdown includes eligibility, role relevance, skill evidence, experience alignment, preference alignment, and overall relevance. Scores are versioned heuristic or learned ranking signals, not calibrated hiring probabilities.

If a skill is absent from confirmed candidate evidence, the system states that it is not evidenced in the profile. It does not claim the candidate lacks the skill.

### 8.4 Bounded graph

The LangGraph flow contains:

1. Evidence assembly.
2. A match analyst that produces structured claims.
3. Deterministic citation validation.
4. An eligibility critic that checks contradictions and overstatement.
5. At most one repair attempt.
6. A final dossier or explicit abstention.

If the LLM is unavailable, deterministic recommendations and evidence remain visible.

## 9. Ranking Replay Lab

Evaluation cases combine a versioned candidate profile, frozen posting corpus, posting identifier, eligibility label, graded relevance label, expected evidence identifiers, and reviewer notes.

The initial dataset targets three candidate profiles and at least 60 carefully reviewed profile-posting pairs. One profile may be the developer's verified profile. Additional profiles are synthetic and clearly labelled. Difficult negatives and ambiguous eligibility cases are required.

Relevance grades are:

1. `0`: irrelevant.
2. `1`: weak possibility.
3. `2`: reasonable match.
4. `3`: strong match.

Required comparisons are:

1. Lexical retrieval.
2. Dense retrieval.
3. Hybrid retrieval.
4. Hybrid retrieval with cross-encoder reranking.
5. Ranking with and without hard filters.
6. Match analysis with and without the critic on a small fixed subset.

Primary metrics are classification macro F1, false-eligible rate, Recall@50, nDCG@10, Precision@10, citation precision, unsupported-claim count, correct abstention rate, and p50 and p95 latency.

Every experiment records dataset version, posting snapshots, profile version, model revisions, prompt version, ranking configuration, randomness settings, git commit, latency, and errors. Raw JSON results and a readable Markdown report are stored as artifacts.

Pull requests run a small deterministic regression subset. Full local-model experiments run manually or on a schedule.

## 10. Product experience

### 10.1 Onboarding

The user uploads a PDF resume, reviews extracted facts with source locations, confirms or corrects those facts, configures hard constraints and preferences, and saves a profile version.

### 10.2 Opportunity feed

Each card shows company, title, location, internship period, eligibility, match band, top reasons, important uncertainty, source, and freshness. Users can filter by role, eligibility, company, location, workplace type, age, match band, and application state.

### 10.3 Match dossier

The detail view shows the original posting, structured requirements, candidate evidence, unevidenced requirements, eligibility reasoning, score breakdown, cited explanation, source freshness, and ranking configuration.

### 10.4 Tracking

Application states are `discovered`, `saved`, `applied`, `interviewing`, `rejected`, `offer`, and `hidden`. The MVP includes an in-app digest for new strong matches, changed postings, and closing-soon listings. External notification channels are postponed.

### 10.5 Ranking Replay Lab

The lab allows a reviewer to select frozen configurations and compare metrics, latency, individual ranking changes, and documented failure cases.

## 11. API and background runs

The API exposes versioned resources for sources, ingestion runs, profile documents and facts, candidate constraints and preferences, jobs and history, recommendation runs, feedback, applications, and evaluation runs.

Long operations create database-backed runs with `pending`, `running`, `completed`, `completed_with_errors`, `failed`, or `cancelled` status. A small worker atomically claims pending work. API requests do not perform full ingestion or model inference synchronously.

The system provides `/healthz` for process health and `/readyz` for dependency readiness.

## 12. Reliability, security, and privacy

1. Resume files and job descriptions are untrusted input.
2. Uploads have validated type and size and are stored outside public static paths.
3. Resume text and contact information do not appear in logs or traces.
4. Job-description instructions are treated as data, never system instructions.
5. Model outputs use strict structured schemas and deterministic evidence validation.
6. Provider domains are configured and allowlisted.
7. External requests have timeouts, response-size limits, and bounded retries.
8. ATS integrations remain read-only.
9. Deleting a resume deletes its extracted facts and embeddings, except separately approved anonymized evaluation artifacts.
10. Incomplete ingestion runs cannot close unseen jobs.
11. Lexical results remain available when vector retrieval fails.
12. Fused results remain available when reranking fails.
13. Ranked jobs remain available when match generation fails.

## 13. Observability and LLMOps

Every run records a correlation identifier, run identifier, model revisions, prompt version, ranking configuration, latency, validation failures, retries, degraded fallbacks, and final status. Token counts are recorded when the provider exposes them.

OpenTelemetry traces connect API requests, background runs, retrieval, reranking, analysis, validation, and critique. Structured metrics cover provider availability, queue depth, ingestion counts, classification failures, model latency, and fallback use.

Model and prompt changes are evaluated against the frozen Replay Lab before published metrics are updated.

## 14. Four-week delivery scope

### Week 1: Pivot and reliable source ingestion

1. Replace the old incident design with the approved opportunity-intelligence specification.
2. Define strict job, source, observation, evidence, and run models through tests.
3. Create the Singapore employer source-audit format and audit approximately 30 employers.
4. Choose the first two ATS providers from the audit results.
5. Implement the first provider adapter from captured fixtures.
6. Add raw snapshots, canonical normalization, and idempotent persistence.
7. Expose ingestion through a CLI and record run summaries.

**Week 1 gate:** A repeated fixture and live-source ingestion produces no duplicate canonical jobs, preserves raw snapshots, and reports partial failures.

### Week 2: Coverage, lifecycle, and enrichment

1. Implement the second provider adapter.
2. Add pagination, bounded concurrency, rate-limit handling, and response-size limits.
3. Add observation history and safe missing and closed transitions.
4. Add Singapore, internship, role-family, and seniority classification baselines.
5. Extract structured requirements with evidence spans.
6. Generate versioned posting embeddings.
7. Add provider contract, lifecycle, idempotency, and enrichment tests.

**Week 2 gate:** Two provider types ingest through one contract, changed postings re-enrich, incomplete runs cannot close jobs, and extracted requirements resolve to source evidence.

### Week 3: Candidate profile, ranking, and evaluation

1. Parse a test resume and create candidate evidence records.
2. Implement fact confirmation, correction, rejection, constraints, preferences, and profile versioning.
3. Implement hard eligibility decisions.
4. Implement lexical and dense retrieval.
5. Add Reciprocal Rank Fusion and cross-encoder reranking.
6. Label at least 60 profile-posting pairs across three profiles.
7. Implement Replay Lab metrics and raw result artifacts.
8. Compare lexical, dense, hybrid, and reranked configurations.

**Week 3 gate:** The selected ranking configuration is justified by measured results, every recommendation records its profile and model versions, and eligibility uncertainty remains visible.

### Week 4: Product, bounded analysis, and portfolio finish

1. Add FastAPI endpoints for profiles, jobs, recommendations, runs, applications, and evaluations.
2. Build the resume review, opportunity feed, match dossier, source-status, and Replay Lab views.
3. Add the bounded analyst, citation validator, critic, one repair attempt, and abstention path.
4. Add graceful fallbacks for unavailable vector, reranking, and generation components.
5. Add Docker Compose, health checks, structured logs, OpenTelemetry, and CI.
6. Add one deterministic Playwright happy-path test.
7. Publish measured evaluation results, architecture documentation, limitations, and setup instructions.
8. Record a short demonstration using a test resume and real posting snapshots.

**Week 4 gate:** A clean checkout runs the complete demonstrated flow, CI passes without paid services, citations resolve, and the README contains only reproducible measurements.

## 15. Scope protection

If the schedule slips, reduce scope in this order:

1. Remove application tracking beyond save and hide.
2. Remove the in-app digest.
3. Reduce frontend visual polish.
4. Use one analyst node plus deterministic validation instead of a separate LLM critic.
5. Reduce the labelled dataset to the 60-pair minimum while retaining the required ranking comparisons.
6. Reduce the number of configured employers while preserving two provider adapters and one live source for each.

Do not remove provenance, idempotency, eligibility uncertainty, evaluation, or graceful degradation. Those features define the project's engineering value.

## 16. Definition of done

The one-month MVP is complete when:

1. At least one live source per selected provider and captured fixtures run through the full ingestion path.
2. Two provider adapters are supported.
3. Repeated ingestion is idempotent and lifecycle changes are reproducible.
4. Candidate facts can be confirmed, corrected, and rejected with evidence.
5. Eligibility is distinct from relevance and supports uncertainty.
6. Lexical, dense, hybrid, and reranked results can be compared reproducibly.
7. At least 60 labelled pairs support a documented evaluation.
8. Generated match claims have valid evidence or the system abstains.
9. The main workflow runs through FastAPI and React.
10. Docker Compose and CI reproduce the deterministic application path.
11. Raw metrics and limitations are published.
12. No paid service or employer account is required to review the core project.

## 17. Resume impact templates

Replace every bracketed value with a measured result:

1. Built an evidence-grounded Singapore internship intelligence platform that normalized `[N]` postings from `[M]` employers across `[P]` ATS providers, with idempotent ingestion, change tracking, and `[X]%` successful source coverage.
2. Designed a hybrid retrieval and cross-encoder ranking pipeline that improved nDCG@10 from `[baseline]` to `[result]` across `[K]` human-labelled profile-posting pairs while maintaining a `[Y]%` false-eligible rate.
3. Implemented a bounded LangGraph match-analysis workflow with deterministic citation validation, achieving `[C]%` citation precision and reducing unsupported claims from `[A]` to `[B]`.
4. Delivered the local-first product using FastAPI, React, PostgreSQL, pgvector, Hugging Face models, Docker Compose, GitHub Actions, and OpenTelemetry, with `[T]` automated tests and p95 recommendation latency of `[L]`.

## 18. Principal risks

| Risk | Mitigation |
| --- | --- |
| Target employers use unsupported or proprietary ATS platforms | Perform the coverage audit before selecting adapters and publish coverage honestly |
| Live provider responses change | Preserve fixtures, validate strictly, quarantine malformed records, and detect schema drift |
| Too few Singapore internships are open during development | Store real snapshots across all locations, evaluate Singapore classification, and avoid inventing volume claims |
| Ranking labels reflect only one person's preferences | Use several versioned profiles and publish dataset limitations |
| LLM work consumes the month | Complete deterministic retrieval and evaluation before adding the graph |
| Frontend polish displaces core engineering | Protect ingestion, provenance, ranking, and evaluation before optional interface work |
| Resume parsing exposes personal data | Use test or redacted resumes in demonstrations and exclude content from telemetry |
| Scores look more certain than they are | Separate eligibility from relevance, use match bands, and disclose heuristic components |
