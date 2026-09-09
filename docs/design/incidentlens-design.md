# IncidentLens Design Specification

**Status:** Approved, implementation in progress

**Date:** 2026-08-28

**Last updated:** 2026-09-09

**Target roles:** AI Engineer, Data Scientist, Forward Deployed Engineer

**Primary constraint:** The core portfolio project must be runnable locally without paid APIs.

## 1. Executive Summary

IncidentLens is an evidence-grounded incident investigation assistant for cloud reliability and incident response. It analyzes incident evidence such as logs, runbooks, deployment events, traces, and metrics, then produces a cited root cause report. The system is deliberately read-only and must abstain when the available evidence cannot support a conclusion.

The standout component is the Incident Replay Lab. Each replay scenario contains hidden ground truth, relevant evidence, distractors, and expected findings. The lab runs the same incident through different retrieval and agent configurations, measures their performance, and exposes both successful and failed reasoning. This changes the project from a generic chat interface into a reproducible AI engineering experiment.

Development is split into five progressive milestones. Milestones 1 through 4 form the complete resume project and include one evaluated live incident from the OpenTelemetry Demo. Milestone 5 is an optional on-demand AWS deployment after the local system is stable.

## 2. Goals

1. Teach core RAG concepts through a working evidence search baseline.
2. Implement modern retrieval using dense search, sparse search, Reciprocal Rank Fusion, metadata filtering, and reranking.
3. Implement a bounded LangGraph investigation workflow that creates competing hypotheses, grades their evidence, retries once, and abstains when appropriate.
4. Evaluate retrieval and root cause performance against known ground truth.
5. Provide exact, inspectable citations for every important claim.
6. Deliver a polished FastAPI and React application that runs through Docker Compose.
7. Include automated testing, evaluation regression checks, container builds, and CI/CD.
8. Keep the primary development and demonstration path local and free of paid API requirements.
9. Demonstrate one live OpenTelemetry incident through the same evidence and investigation interfaces used by deterministic replay scenarios.
10. Keep AWS deployment optional and separate from the portfolio completion criteria.

## 3. Non-goals

1. IncidentLens will not execute remediation commands or mutate cloud infrastructure.
2. The first release will not use an autonomous agent swarm. It will use one bounded LangGraph with role-separated investigation, evidence-critique, and report-writing nodes.
3. The first release will not support arbitrary enterprise data sources.
4. The first release will not require Kubernetes, Celery, Redis, Neo4j, or multiple vector databases.
5. The project will not claim production reliability or statistically generalizable results from a small synthetic scenario set.
6. AWS will not run continuously merely to keep a portfolio demo online.
7. Generated confidence will not be presented as a calibrated probability unless calibration is later implemented and measured.

## 4. Assumptions

1. The developer is learning RAG and agent workflows for the first time.
2. Development occurs primarily on a Windows machine with Docker Desktop.
3. The local machine can run a small instruction model through Ollama. The exact model will be selected after checking the available memory and accelerator support.
4. Synthetic and prerecorded incident evidence is acceptable for deterministic evaluation, but the portfolio version also includes one live OpenTelemetry Demo incident.
5. A public GitHub repository will be used to expose source code, documentation, CI results, and the project page.
6. An AWS account may be used later for short demonstrations. AWS cost and free tier eligibility cannot be assumed.

## 5. Product Experience

### 5.1 Primary user

The primary user is an on-call engineer who needs to understand an incident quickly while retaining control over every operational decision.

### 5.2 Primary workflow

1. The user selects an incident or replay scenario.
2. The user asks a question or starts a standard investigation.
3. IncidentLens identifies the service and time scope.
4. It searches logs, runbooks, changes, and later traces and metrics.
5. It creates two or three competing root cause hypotheses.
6. It shows supporting and contradicting evidence for each hypothesis.
7. It either selects a supported explanation or abstains.
8. The user opens any citation to inspect its original source.
9. In Replay Lab mode, the user compares the result with hidden ground truth and other configurations.

### 5.3 Final report

The report contains:

1. Incident summary
2. Most likely root cause, or an explicit abstention
3. Affected services and time window
4. Supporting evidence with exact citations
5. Contradicting or ambiguous evidence
6. Confidence category with an explanation
7. Recommended next diagnostic checks
8. Suggested mitigation, clearly marked as advisory
9. Investigation trace and tool usage summary

## 6. System Architecture

### 6.1 Local portfolio architecture

The main local path consists of:

1. A React and TypeScript web application.
2. A FastAPI backend.
3. A bounded LangGraph with role-separated investigator, evidence critic, and report writer nodes.
4. Read-only evidence retrieval tools.
5. Qdrant for dense and sparse vector search.
6. FastEmbed for local embedding and reranking models.
7. Ollama for local answer generation and agent decisions.
8. Scenario packages containing evidence and hidden ground truth.
9. The Incident Replay Lab for experiments and regression evaluation.
10. Docker Compose for the API, web application, and Qdrant.

The web application calls FastAPI. FastAPI starts or reads an investigation. The LangGraph workflow invokes ordinary Python evidence tools. Those tools query Qdrant and source adapters. The model never receives unrestricted database, shell, or cloud access.

### 6.2 Agent workflow

The bounded workflow is implemented as role-separated nodes inside one state graph:

1. The investigator scopes the incident and plans evidence queries.
2. Deterministic retrieval tools return evidence.
3. The investigator creates two or three hypotheses and attaches supporting and contradicting evidence.
4. The evidence critic grades evidence sufficiency, citation validity, and unresolved contradictions.
5. If evidence is inadequate, the graph revises the queries and retries once.
6. The report writer produces a cited report or explicitly abstains.

The workflow has configurable tool and token budgets. The initial design allows one retrieval retry and a small maximum number of tool calls. Exact limits will be tuned during evaluation and stored in configuration.

### 6.3 Live observability portfolio scenario

Milestone 4 adds one evaluated incident from the OpenTelemetry Demo and Grafana LGTM stack. Provider adapters query:

1. Loki for logs.
2. Tempo for traces.
3. Prometheus for metrics.
4. Deployment and configuration event sources.

The adapters convert live responses into the same `EvidenceChunk` model used by prerecorded scenarios. Fixture mode remains the deterministic regression path. This preserves the evaluation architecture and prevents the agent workflow from depending directly on a specific observability vendor.

### 6.4 AWS extension

The optional AWS deployment uses:

1. S3 and CloudFront for the React application.
2. API Gateway for the backend HTTP interface.
3. A Lambda container image for FastAPI and LangGraph.
4. ECR for container storage.
5. S3 for evidence packages and evaluation artifacts.
6. DynamoDB for investigation state.
7. CloudWatch for runtime logs and metrics.
8. Qdrant Cloud or another configured external Qdrant endpoint.
9. Optional Amazon Bedrock behind the same model provider interface as Ollama.
10. Terraform and GitHub Actions with AWS OIDC for deployment.

The AWS environment is created on demand and removed after demonstrations. The public GitHub Pages project page remains available while the backend is offline.

## 7. Data Sources and Interfaces

### 7.1 Required replay data for the core project

Each scenario package contains:

1. `manifest.yaml` with incident metadata and hidden ground truth.
2. `logs.jsonl` with structured application logs.
3. `runbook.md` with operational procedures and troubleshooting guidance.
4. `changes.jsonl` with deployment and configuration events.
5. `questions.yaml` with evaluation queries and expected evidence.

At least four scenarios will be created:

1. Payment retry storm following a configuration deployment.
2. Database connection pool exhaustion.
3. Inventory service latency following a dependency change.
4. One additional incident chosen to test a distinct failure pattern and abstention behavior.

These are controlled scenarios created for the project. They will be labeled synthetic and will not be represented as real company incidents.

### 7.2 Live APIs used in Milestone 4

1. OTLP for receiving or replaying telemetry.
2. Loki `query_range` for time-bounded log retrieval.
3. Tempo trace search and trace lookup endpoints.
4. Prometheus instant and range query endpoints.
5. Qdrant query endpoints for vector and filtered search.
6. Ollama generation and embedding endpoints when configured.
7. Optional AWS APIs only when the separate Milestone 5 deployment is configured.

### 7.3 Internal domain models

`ScenarioManifest` contains the incident identifier, title, time range, affected services, ground truth root cause, relevant evidence IDs, distractor IDs, and expected mitigation. Evaluation cases remain in the versioned question set.

`EvidenceChunk` contains a stable evidence ID, incident ID, source type, service, timestamp or time range, original text, searchable text, structured metadata, and a resolvable source locator.

`Citation` references an evidence ID and includes the source locator needed to open the original data.

`Hypothesis` contains a claim, supporting citations, contradicting citations, missing evidence, and an evidence-based confidence category.

`InvestigationState` contains the incident scope, user question, attempted queries, retrieved evidence, hypotheses, tool usage, retry count, and final decision.

`ExperimentResult` contains the scenario version, configuration version, predictions, expected answers, retrieval metrics, answer metrics, latency, errors, and reproducibility metadata.

### 7.4 Backend API

The first product API exposes:

1. `GET /healthz`
2. `GET /readyz`
3. `GET /api/v1/incidents`
4. `GET /api/v1/incidents/{incident_id}`
5. `POST /api/v1/investigations`
6. `GET /api/v1/investigations/{investigation_id}`
7. `GET /api/v1/investigations/{investigation_id}/evidence`
8. `POST /api/v1/replays`
9. `GET /api/v1/replays/{replay_id}`
10. `GET /api/v1/evaluations/latest`

Streaming is postponed until it clearly improves the experience. Polling is sufficient for the first complete product.

## 8. Retrieval Design

### 8.1 Ingestion and chunking

Chunking is source aware:

1. A log event remains an atomic unit unless a small adjacent window is necessary for context.
2. Deployment events remain atomic and preserve timestamps and changed fields.
3. Runbooks are split by heading and paragraph boundaries.
4. Trace spans remain atomic but may include summarized parent and child context in Milestone 4.
5. Metric evidence stores the query, time range, values, and derived observation rather than embedding raw high-volume samples.

Every chunk keeps its original source locator. The generated answer is never the source of a citation.

### 8.2 Retrieval configurations

The Replay Lab compares:

1. Dense vector retrieval.
2. Dense and sparse retrieval combined with Reciprocal Rank Fusion.
3. Hybrid retrieval followed by local reranking.
4. The selected retriever inside single pass RAG.
5. The selected retriever inside the bounded agent workflow.

### 8.3 Filtering

Retrieval supports filters for:

1. Incident ID
2. Service
3. Time range
4. Environment
5. Evidence type
6. Severity

Incident isolation is mandatory. Evidence from another scenario must not appear in an investigation unless a future feature explicitly requests historical similarity search.

### 8.4 Grounding controls

1. The generator may cite only evidence supplied in the current context.
2. Every returned evidence ID is validated against retrieved evidence.
3. Important causal claims require more than one supporting item when the scenario permits it.
4. Contradicting evidence is shown rather than silently discarded.
5. Retrieved documents are treated as untrusted data and cannot redefine system instructions or tool permissions.
6. Missing evidence produces an abstention or a request for a specific next check.

### 8.5 Hugging Face task mapping

The project demonstrates Hugging Face tasks through measurable system components rather than disconnected model demos:

1. Sentence Similarity powers dense evidence retrieval.
2. Text Ranking powers cross-encoder reranking after hybrid retrieval.
3. Text Generation produces structured hypotheses and incident reports.
4. Summarization condenses timelines and retrieved evidence when context limits require it.
5. Text Classification is optional for evidence categorization only if evaluation shows that deterministic metadata is insufficient.

## 9. Agent Design

### 9.1 Why one bounded graph rather than an agent swarm

A single state graph is easier to inspect, test, reproduce, and constrain. Role-separated investigator, evidence-critic, and report-writer nodes demonstrate orchestration and shared state without adding independent agent runtimes or uncontrolled delegation.

### 9.2 Read-only tools

The initial agent tools are:

1. `search_logs`
2. `search_runbooks`
3. `search_change_events`
4. `get_evidence_by_id`
5. `expand_time_window`

Milestone 4 adds trace and metric tools for one live OpenTelemetry scenario. Tool implementations remain normal Python functions with independent unit and integration tests.

### 9.3 Failure and stopping behavior

1. Invalid structured model output receives one repair attempt.
2. A failed evidence source produces a partial result with a visible source error.
3. Empty retrieval produces an abstention, not an unsupported answer.
4. The graph cannot exceed its configured retry or tool budget.
5. A timeout records the partial state and returns a diagnosable error.
6. Tool failures and model failures are distinguished in logs and API responses.

## 10. Incident Replay Lab

### 10.1 Purpose

The Replay Lab is both an evaluation harness and a product feature. It provides known ground truth, reproducible comparisons, ablation experiments, and regression protection.

### 10.2 Experiment inputs

1. Scenario version
2. Question set
3. Embedding model
4. Sparse model
5. Reranker model
6. Chunking configuration
7. Retrieval configuration
8. Agent policy
9. Generation model
10. Randomness settings when supported
11. Exact model revisions where the provider exposes them
12. Prompt version
13. Tool and token budgets
14. Git commit

### 10.3 Metrics

The primary retrieval metric is Recall@5. Retrieval metrics include:

1. Recall@5
2. Mean Reciprocal Rank
3. nDCG@5
4. Relevant evidence coverage
5. Cross-incident leakage count

The primary answer-quality metrics are root-cause correctness, citation precision, unsupported-claim count, and correct abstention rate. Answer and workflow metrics include:

1. Root cause correctness against scenario ground truth
2. Citation validity
3. Citation precision
4. Unsupported claim count
5. Abstention correctness
6. Tool calls
7. Retrieval latency
8. Generation latency
9. Total investigation latency

The frozen evaluation set contains approximately 30 to 40 questions across at least four scenarios. Reports include raw counts alongside percentages. Results are project evidence, not a statistically generalizable benchmark.

### 10.4 Required comparisons

1. Dense retrieval against hybrid retrieval.
2. Hybrid retrieval with and without reranking.
3. Selected retrieval with and without metadata filters.
4. Single pass RAG against the bounded agent workflow.
5. Agent workflow with and without the retry step.

All raw results are stored in machine-readable JSON. A Markdown report summarizes the exact configuration, raw counts, metrics, limitations, and notable failures. Pull-request regression thresholds are established only after the dense baseline is frozen.

## 11. Technology Stack

### 11.1 Core stack

The core stack is introduced progressively and is sufficient to complete Milestone 4:

1. Python 3.12 and `uv`
2. Pydantic, Pydantic Settings, HTTPX, Structlog, PyYAML, and Typer
3. Qdrant Client and FastEmbed
4. Ollama behind a configurable model-provider interface
5. LangGraph and only the LangChain Core interfaces needed by the graph
6. NumPy, scikit-learn, and Ranx for evaluation
7. FastAPI and Uvicorn
8. React, TypeScript, Vite, TanStack Query, Recharts, Vitest, and Playwright
9. Docker, Docker Compose, and GitHub Actions
10. Pytest, Ruff, Mypy, and focused dependency and container security checks
11. OpenTelemetry instrumentation with the Grafana LGTM stack

### 11.2 Optional dependencies

Optional tools are added only when a completed milestone and measured need justify them:

1. Tenacity for narrowly scoped external-call retries
2. ORJSON after serialization profiling
3. NetworkX for evidence-relationship analysis
4. Polars and PyArrow for larger evaluation artifacts
5. SciPy when the evaluation sample supports statistical analysis
6. Ragas as a comparison, never as the source of ground truth
7. Docling if PDF runbooks become part of an evaluated scenario
8. React Flow if the investigation graph materially improves the user experience
9. Terraform, Mangum, LangChain AWS, and Bedrock for the optional AWS milestone
10. Additional security scanners when the deployment artifacts they inspect exist

## 12. Progressive Repository Structure

Only the folders required by the current milestone are created.

### 12.1 Milestone 1

| Path | Responsibility |
| --- | --- |
| `pyproject.toml` | Project metadata, dependencies, and tool configuration |
| `.env.example` | Environment variable template without secrets |
| `src/incidentlens/config.py` | Typed configuration |
| `src/incidentlens/models.py` | Core domain models |
| `src/incidentlens/ingestion.py` | Scenario ingestion and source-aware chunking |
| `src/incidentlens/index.py` | Embedding and Qdrant indexing |
| `src/incidentlens/retrieval.py` | Dense retrieval baseline |
| `src/incidentlens/generation.py` | Cited answer generation |
| `src/incidentlens/cli.py` | Command line interface |
| `scenarios/<scenario>/` | Manifest, logs, runbook, changes, and questions |
| `tests/unit/` | Isolated tests |
| `tests/integration/` | Qdrant and optional Ollama integration tests |

### 12.2 Milestone 2 additions

| Path | Responsibility |
| --- | --- |
| `src/incidentlens/retrieval/` | Dense, sparse, fusion, filtering, and reranking modules |
| `src/incidentlens/evaluation/` | Evaluation runner and metrics |
| `configs/retrieval/` | Reproducible retrieval configurations |
| `artifacts/evaluations/` | Generated results and reports |
| `tests/evaluation/` | Retrieval regression tests |

### 12.3 Milestone 3 additions

| Path | Responsibility |
| --- | --- |
| `src/incidentlens/agent/state.py` | Typed graph state |
| `src/incidentlens/agent/graph.py` | Workflow construction |
| `src/incidentlens/agent/nodes.py` | Investigation steps |
| `src/incidentlens/agent/tools.py` | Read-only tools |
| `src/incidentlens/agent/prompts.py` | Versioned prompts |
| `src/incidentlens/agent/policies.py` | Budgets, retries, and abstention rules |
| `tests/agent/` | Graph and grounding tests |

### 12.4 Milestone 4 additions

| Path | Responsibility |
| --- | --- |
| `src/incidentlens/api/` | FastAPI routes and schemas |
| `apps/web/` | React application |
| `lab/` | Replay orchestration and reporting |
| `containers/` | API and web Dockerfiles |
| `compose.yaml` | Local stack |
| `compose.observability.yaml` | OpenTelemetry Demo and Grafana LGTM |
| `src/incidentlens/telemetry/` | Minimum Loki, Tempo, Prometheus, and correlation adapters for one evaluated fault |
| `.github/workflows/` | CI, evaluation, container, and project page workflows |
| `docs/` | Architecture, evaluation, operation, and demonstration documentation |

### 12.5 Milestone 5 additions

| Path | Responsibility |
| --- | --- |
| `src/incidentlens/providers/` | Local and AWS provider implementations |
| `infra/terraform/` | AWS infrastructure modules and environments |
| `.github/workflows/aws-deploy.yml` | Manual AWS deployment |
| `.github/workflows/aws-destroy.yml` | Explicit AWS teardown |

## 13. Step-by-Step Delivery Plan

## 13.1 Milestone 1: Evidence Search Baseline

**Learning objective:** Understand ingestion, chunking, embeddings, vector search, prompting, and citations.

Steps:

1. Initialize the Python project and quality tools.
2. Define typed incident, evidence, citation, query, answer, and evaluation models.
3. Define the versioned scenario package and source-aware parsers.
4. Normalize logs, runbooks, and changes into evidence chunks with stable IDs and source locators.
5. Validate all cross-file evidence and ground-truth relationships.
6. Commit the payment retry storm scenario and its evaluation questions.
7. Start Qdrant as one local container with a documented command.
8. Embed and index the evidence in Qdrant.
9. Implement dense retrieval with mandatory incident filtering.
10. Generate a structured cited answer through Ollama.
11. Validate every citation before returning it.
12. Expose indexing, listing, evidence inspection, and investigation through a CLI.
13. Add unit tests with a fake model and separately marked integration tests.

Completion gate:

1. A user can index and investigate the scenario from the CLI.
2. At least four of five initial questions retrieve their required evidence in the top five, measured as Recall@5.
3. Every citation resolves to an original source.
4. The system abstains when evidence is missing.
5. Unit tests do not require an LLM.

## 13.2 Milestone 2: Modern RAG and Evaluation

**Learning objective:** Understand modern retrieval, controlled experiments, and evidence-based model selection.

Steps:

1. Expand to at least four incidents and approximately 30 to 40 total evaluation questions, including distractors and abstention cases.
2. Freeze the dense baseline and record its configuration.
3. Add sparse retrieval for exact operational terms.
4. Fuse dense and sparse rankings using Reciprocal Rank Fusion.
5. Add incident, service, time, environment, source, and severity filters.
6. Add an optional local reranker.
7. Build an evaluation runner and metric calculations.
8. Compare dense, hybrid, and hybrid plus reranking configurations.
9. Run ablations for sparse retrieval, filters, reranking, and chunking.
10. Export raw JSON and readable Markdown reports.

Completion gate:

1. All configurations are reproducible from versioned files.
2. The selected retriever outperforms the frozen dense baseline on Recall@5 without reducing citation precision or incident isolation.
3. Cross-incident evidence leakage is zero.
4. Evaluation reports are regenerated with one command.
5. Negative or inconclusive experiments are documented honestly.

## 13.3 Milestone 3: Agentic Investigation

**Learning objective:** Understand stateful tool use, bounded iteration, reflection, and abstention.

Steps:

1. Define the typed investigation state.
2. Refactor retrieval operations into independently tested tools.
3. Build incident scoping and query planning nodes.
4. Generate two or three candidate hypotheses.
5. Attach supporting, contradicting, and missing evidence.
6. Add deterministic citation and evidence sufficiency checks.
7. Add one bounded query revision and retrieval retry.
8. Add final reporting and explicit abstention.
9. Test every transition and stopping rule.
10. Compare single pass RAG, the full agent, and the agent without retry.

Completion gate:

1. The graph cannot exceed its configured budgets.
2. Unsupported citations are rejected.
3. Weak evidence causes abstention.
4. Agent and baseline results use the same scenario set.
5. Added complexity is justified with measured quality and latency results.

## 13.4 Milestone 4: Resume Ready Product and Live Telemetry

**Learning objective:** Turn the AI system into a reproducible, observable, and usable software product.

Steps:

1. Add the versioned FastAPI interface.
2. Build the incident selector, timeline, hypothesis view, and evidence inspector in React.
3. Build Replay Lab controls and result comparisons.
4. Containerize the API, frontend, and Qdrant.
5. Support host Ollama and an optional container profile.
6. Add health checks and startup dependency handling.
7. Add backend, frontend, evaluation, and container CI checks.
8. Add a deterministic fake model mode for CI.
9. Run the OpenTelemetry Demo and Grafana LGTM locally.
10. Implement the minimum Loki, Tempo, and Prometheus adapters required for one known fault.
11. Convert live responses into the existing evidence model and evaluate the known fault through the same investigation workflow.
12. Preserve fixture mode as the deterministic regression path.
13. Publish the static portfolio page.
14. Record a short demonstration and document the architecture, experiments, limitations, and setup.

Completion gate:

1. A clean checkout starts through the documented Docker workflow.
2. A recruiter can understand the project value within two minutes.
3. Claims can be opened and inspected at their original evidence.
4. Replay Lab reproduces the published comparisons.
5. CI passes without paid services or model credentials.
6. The README reports only measured results.
7. One known OpenTelemetry Demo fault is investigated through the same workflow as replay scenarios.

## 13.5 Milestone 5: Optional AWS Deployment

**Learning objective:** Deploy the proven local portfolio system through reproducible, cost-controlled cloud infrastructure.

Steps:

1. Implement provider interfaces for model, state, evidence storage, and vector search.
2. Package FastAPI as a Lambda container.
3. Define S3, CloudFront, API Gateway, Lambda, ECR, DynamoDB, and CloudWatch through Terraform.
4. Configure GitHub Actions authentication through AWS OIDC.
5. Add manual deploy and destroy workflows.
6. Run post-deployment health and replay smoke tests.
7. Add budgets, short log retention, and documented cost controls.
8. Add Bedrock only as an optional provider.

Completion gate:

1. Ollama and Bedrock use the same model interface.
2. AWS infrastructure can be created and removed reproducibly.
3. CI uses short-lived credentials.
4. The public portfolio remains useful while AWS is offline.

## 14. Testing Strategy

### 14.1 Unit tests

Unit tests cover parsing, normalization, chunk IDs, filtering, fusion, citation validation, metrics, state transitions, retry limits, and abstention policies. Models and external services are replaced with deterministic fakes.

### 14.2 Integration tests

Integration tests cover Qdrant indexing and search, FastAPI routes, Docker health checks, and optional Ollama output validation. Live model tests are separately marked because they are slower and less deterministic.

### 14.3 Evaluation regression tests

A small frozen subset runs in pull requests. It checks that retrieval recall, citation validity, incident isolation, and abstention do not fall below declared thresholds. Full experiments run manually or on a scheduled workflow.

### 14.4 End-to-end tests

Playwright verifies the primary flow from scenario selection to report and citation inspection. The OpenTelemetry end-to-end test injects one known fault and verifies evidence collection through report generation. Optional AWS deployment smoke tests verify health, one investigation, and artifact access.

## 15. CI/CD Design

### 15.1 Pull request CI

1. Python formatting and linting
2. Static type checking
3. Unit tests and coverage
4. Deterministic integration tests
5. Retrieval smoke evaluation
6. Frontend linting and tests
7. API and frontend container builds
8. Dependency and container security scans

### 15.2 Main branch delivery

1. Build versioned containers.
2. Publish the static project page.
3. Store evaluation reports as build artifacts.
4. Optionally publish container images after the local application is stable.

### 15.3 AWS delivery

AWS deployment is manual. GitHub Actions obtains short-lived credentials through OIDC, runs Terraform, deploys the application, performs smoke tests, and exposes a separate explicit teardown workflow. Production mutation is never triggered by an ordinary pull request.

## 16. Observability, Security, and Reliability

1. Every investigation receives a correlation ID.
2. Structured logs record node duration, tool calls, retrieval counts, retries, and errors without storing secrets.
3. OpenTelemetry instruments the API and investigation workflow.
4. Evidence content is treated as untrusted input.
5. Tools are read-only and operate through allowlisted interfaces.
6. Secrets come from environment configuration locally and approved secret stores in deployment environments.
7. Repository history must never contain credentials or private incident data.
8. External calls have bounded timeouts and narrowly scoped retries.
9. Health and readiness checks distinguish process health from dependency readiness.
10. Generated remediation remains advisory and requires human review.
11. Live telemetry is filtered for secrets and sensitive values before persistence, embedding, or model use.

## 17. Cost Strategy

Milestones 1 through 4 use locally hosted components and do not require a paid model API. Normal electricity, hardware, internet, and any applicable local software licensing costs still apply.

The optional AWS deployment is designed for short demonstrations rather than continuous operation. Lambda is preferred over continuously running compute. Resources are created on demand, log retention is short, storage is limited, and a destroy workflow is provided. The project documentation will not promise that AWS usage is free because pricing and account eligibility vary.

## 18. Principal Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Scope overwhelms a beginner | Treat Milestone 4 as the finish line, build only one milestone at a time, and keep AWS optional |
| Synthetic data appears unrealistic | Use operationally plausible evidence, label it synthetic, and validate one known fault with the OpenTelemetry Demo in Milestone 4 |
| Retrieval gains are overstated | Freeze the baseline, declare the primary metric, publish raw results, and document dataset size |
| LLM output is nondeterministic | Use structured output, deterministic validation, fake models in CI, and versioned prompts |
| Agent loops become expensive or unreliable | Use one graph, read-only tools, one retry, and strict budgets |
| Citations look convincing but are invalid | Validate evidence IDs and expose the original source for every citation |
| AWS creates unexpected costs | Deploy manually, use budgets and short retention, avoid continuous compute, and destroy after use |
| Local hardware cannot run the chosen model | Keep model adapters configurable and select a smaller Ollama model after checking hardware |

## 19. Resume Impact Bullet Templates

Replace every bracketed field with a measured result from the completed project. Do not place estimated or invented numbers on the resume.

1. **Built** an evidence-grounded incident investigation assistant using hybrid Qdrant retrieval, local reranking, Ollama, and LangGraph to analyze logs, runbooks, and deployment events, **achieving [root cause accuracy]% accuracy and [Recall@5] evidence recall across [N] reproducible incident cases**.
2. **Designed** an Incident Replay Lab that benchmarked dense, hybrid, reranked, and agentic RAG configurations against hidden ground truth, **improving Recall@5 by [X]% over the dense baseline while reducing unsupported citations from [A] to [B]**.
3. **Delivered** the application end to end with FastAPI, React, Docker Compose, GitHub Actions, and OpenTelemetry, **reproducing one live fault through Loki, Tempo, and Prometheus while maintaining [test count or coverage]% automated coverage**.
4. **Optional:** Deployed the validated application through Terraform and an on-demand AWS environment, **completing smoke tests in [measured time] and keeping demonstrated cloud cost below [measured amount]**.

These bullets follow Action, Context, Result structure. The final wording will be adjusted after real evaluation and deployment measurements exist.

## 20. Definition of Done

The core portfolio project is complete at Milestone 4 when:

1. At least four versioned replay scenarios contain ground truth and distractors, with approximately 30 to 40 evaluation questions in total.
2. Dense, hybrid, and reranked retrieval are compared reproducibly.
3. The bounded agent creates competing hypotheses and can abstain.
4. Every important claim has a valid, inspectable citation.
5. Replay Lab shows expected and predicted findings with metrics and traces.
6. The API, frontend, Qdrant, and model connection run through documented local setup.
7. CI verifies code quality, tests, retrieval regressions, frontend behavior, and container builds.
8. The public project page explains the problem, architecture, results, failures, and limitations.
9. Resume claims use measurements generated by the repository.
10. No AWS account or paid API is required to evaluate the core project.
11. One known OpenTelemetry Demo fault is investigated and evaluated through the same workflow used by replay scenarios.

Milestone 5 is complete only when the optional AWS deployment meets its separate completion gate. It is not required for the project to be resume ready.

## 21. Reference Technologies

1. OpenTelemetry Demo: <https://opentelemetry.io/docs/demo/>
2. Grafana Docker OpenTelemetry LGTM: <https://grafana.com/docs/opentelemetry/docker-lgtm/>
3. Loki HTTP API: <https://grafana.com/docs/loki/latest/reference/loki-http-api/>
4. Tempo API: <https://grafana.com/docs/tempo/latest/api_docs/>
5. Prometheus HTTP API: <https://prometheus.io/docs/prometheus/latest/querying/api/>
6. Qdrant hybrid queries: <https://qdrant.tech/documentation/search/hybrid-queries/>
7. Qdrant FastEmbed: <https://qdrant.tech/documentation/fastembed/>
8. LangGraph overview: <https://docs.langchain.com/oss/python/langgraph/overview>
9. AWS Lambda container images: <https://docs.aws.amazon.com/lambda/latest/dg/images-create.html>
10. uv project dependencies: <https://docs.astral.sh/uv/concepts/projects/dependencies/>
11. OpenTelemetry Python: <https://opentelemetry.io/docs/languages/python/>
