# IncidentLens Design Specification

**Status:** Approved concept, pending review of this written specification

**Date:** 2026-08-28

**Target roles:** AI Engineer, Data Scientist, Forward Deployed Engineer

**Primary constraint:** The core portfolio project must be runnable locally without paid APIs.

## 1. Executive Summary

IncidentLens is an evidence-grounded incident investigation assistant for cloud reliability and incident response. It analyzes incident evidence such as logs, runbooks, deployment events, traces, and metrics, then produces a cited root cause report. The system is deliberately read-only and must abstain when the available evidence cannot support a conclusion.

The standout component is the Incident Replay Lab. Each replay scenario contains hidden ground truth, relevant evidence, distractors, and expected findings. The lab runs the same incident through different retrieval and agent configurations, measures their performance, and exposes both successful and failed reasoning. This changes the project from a generic chat interface into a reproducible AI engineering experiment.

Development is split into five progressive milestones. Milestones 1 through 4 form the complete resume project. Milestone 5 adds live observability and an on-demand AWS deployment after the local system is stable.

## 2. Goals

1. Teach core RAG concepts through a working evidence search baseline.
2. Implement modern retrieval using dense search, sparse search, Reciprocal Rank Fusion, metadata filtering, and reranking.
3. Implement a bounded LangGraph investigation workflow that creates competing hypotheses, grades their evidence, retries once, and abstains when appropriate.
4. Evaluate retrieval and root cause performance against known ground truth.
5. Provide exact, inspectable citations for every important claim.
6. Deliver a polished FastAPI and React application that runs through Docker Compose.
7. Include automated testing, evaluation regression checks, container builds, and CI/CD.
8. Keep the primary development and demonstration path local and free of paid API requirements.
9. Demonstrate optional AWS and live observability integration without making them prerequisites.

## 3. Non-goals

1. IncidentLens will not execute remediation commands or mutate cloud infrastructure.
2. The first release will not use a multi-agent architecture.
3. The first release will not support arbitrary enterprise data sources.
4. The first release will not require Kubernetes, Celery, Redis, Neo4j, or multiple vector databases.
5. The project will not claim production reliability or statistically generalizable results from a small synthetic scenario set.
6. AWS will not run continuously merely to keep a portfolio demo online.
7. Generated confidence will not be presented as a calibrated probability unless calibration is later implemented and measured.

## 4. Assumptions

1. The developer is learning RAG and agent workflows for the first time.
2. Development occurs primarily on a Windows machine with Docker Desktop.
3. The local machine can run a small instruction model through Ollama. The exact model will be selected after checking the available memory and accelerator support.
4. Synthetic and prerecorded incident evidence is acceptable for the main portfolio version.
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
3. A LangGraph investigation workflow.
4. Read-only evidence retrieval tools.
5. Qdrant for dense and sparse vector search.
6. FastEmbed for local embedding and reranking models.
7. Ollama for local answer generation and agent decisions.
8. Scenario packages containing evidence and hidden ground truth.
9. The Incident Replay Lab for experiments and regression evaluation.
10. Docker Compose for the API, web application, and Qdrant.

The web application calls FastAPI. FastAPI starts or reads an investigation. The LangGraph workflow invokes ordinary Python evidence tools. Those tools query Qdrant and source adapters. The model never receives unrestricted database, shell, or cloud access.

### 6.2 Agent workflow

The bounded workflow is:

1. Scope the incident.
2. Plan evidence queries.
3. Retrieve evidence.
4. Create two or three hypotheses.
5. Attach supporting and contradicting evidence.
6. Grade evidence sufficiency and citation validity.
7. If evidence is inadequate, revise the queries and retry once.
8. Write a cited report or abstain.

The workflow has configurable tool and token budgets. The initial design allows one retrieval retry and a small maximum number of tool calls. Exact limits will be tuned during evaluation and stored in configuration.

### 6.3 Live observability extension

Milestone 5 adds the OpenTelemetry Demo and Grafana LGTM stack. Provider adapters query:

1. Loki for logs.
2. Tempo for traces.
3. Prometheus for metrics.
4. Deployment and configuration event sources.

The adapters convert live responses into the same `EvidenceChunk` model used by prerecorded scenarios. This preserves the evaluation path and prevents the agent workflow from depending directly on a specific observability vendor.

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

### 7.1 Required data sources for the core project

Each scenario package contains:

1. `manifest.yaml` with incident metadata and hidden ground truth.
2. `logs.jsonl` with structured application logs.
3. `runbook.md` with operational procedures and troubleshooting guidance.
4. `changes.jsonl` with deployment and configuration events.
5. `questions.yaml` with evaluation queries and expected evidence.

At least three scenarios will be created:

1. Payment retry storm following a configuration deployment.
2. Database connection pool exhaustion.
3. Inventory service latency following a dependency change.

These are controlled scenarios created for the project. They will be labeled synthetic and will not be represented as real company incidents.

### 7.2 Live APIs added in Milestone 5

1. OTLP for receiving or replaying telemetry.
2. Loki `query_range` for time-bounded log retrieval.
3. Tempo trace search and trace lookup endpoints.
4. Prometheus instant and range query endpoints.
5. Qdrant query endpoints for vector and filtered search.
6. Ollama generation and embedding endpoints when configured.
7. AWS S3, DynamoDB, Bedrock, CloudWatch, ECR, Lambda, API Gateway, and STS APIs when AWS mode is configured.

### 7.3 Internal domain models

`IncidentManifest` contains the incident identifier, title, time range, affected services, ground truth root cause, relevant evidence IDs, distractor IDs, expected mitigation, and evaluation cases.

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
4. Trace spans remain atomic but may include summarized parent and child context in Milestone 5.
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

## 9. Agent Design

### 9.1 Why one graph rather than multiple agents

A single state graph is easier to inspect, test, reproduce, and constrain. It demonstrates agentic orchestration without adding coordination complexity that does not improve the initial use case.

### 9.2 Read-only tools

The initial agent tools are:

1. `search_logs`
2. `search_runbooks`
3. `search_change_events`
4. `get_evidence_by_id`
5. `expand_time_window`

Milestone 5 adds trace and metric tools. Tool implementations remain normal Python functions with independent unit and integration tests.

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

### 10.3 Metrics

Retrieval metrics include:

1. Recall at K
2. Mean Reciprocal Rank
3. nDCG
4. Relevant evidence coverage
5. Cross-incident leakage count

Answer and workflow metrics include:

1. Root cause correctness against scenario ground truth
2. Citation validity
3. Citation precision
4. Unsupported claim count
5. Abstention correctness
6. Tool calls
7. Retrieval latency
8. Generation latency
9. Total investigation latency

The primary metric will be declared before comparing configurations. Results from a small synthetic dataset will be reported as project evidence, not as a general benchmark.

### 10.4 Required comparisons

1. Dense retrieval against hybrid retrieval.
2. Hybrid retrieval with and without reranking.
3. Selected retrieval with and without metadata filters.
4. Single pass RAG against the bounded agent workflow.
5. Agent workflow with and without the retry step.

All raw results are stored in machine-readable JSON. A Markdown report summarizes the configuration, results, limitations, and notable failures.

## 11. Technology Stack

### 11.1 Python backend

1. Python 3.12
2. `uv` for environment and dependency management
3. FastAPI and Uvicorn
4. Pydantic and Pydantic Settings
5. HTTPX
6. Structlog
7. Tenacity for narrowly scoped retries
8. ORJSON where API serialization performance matters
9. Mangum for the optional Lambda deployment
10. Typer for the command line interface

### 11.2 RAG and agent workflow

1. LangGraph
2. LangChain Core for message and runnable interfaces
3. LangChain Ollama integration when it becomes more useful than direct HTTP calls
4. LangChain AWS integration for optional Bedrock support
5. Qdrant Client
6. FastEmbed
7. NetworkX for optional evidence relationship analysis
8. NumPy and scikit-learn for evaluation and analysis
9. Ranx for information retrieval metrics
10. SciPy for statistical analysis where the sample size supports it
11. Ragas only as an optional later comparison, not as the source of ground truth

### 11.3 Data processing

1. PyYAML
2. Polars
3. PyArrow when columnar evaluation artifacts become useful
4. Docling only in the advanced phase if PDF runbooks are added

### 11.4 Frontend

1. React
2. TypeScript
3. Vite
4. TanStack Query
5. React Flow for investigation and evidence relationships
6. Recharts for evaluation results
7. Vitest
8. Playwright

### 11.5 Infrastructure and quality

1. Docker and Docker Compose
2. Terraform
3. GitHub Actions
4. Pytest, pytest-asyncio, pytest-cov, and respx
5. Ruff
6. Mypy
7. Pre-commit
8. Pip Audit
9. Bandit
10. Trivy
11. Hadolint
12. OpenTelemetry Python instrumentation

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
| `.github/workflows/` | CI, evaluation, container, and project page workflows |
| `docs/` | Architecture, evaluation, operation, and demonstration documentation |

### 12.5 Milestone 5 additions

| Path | Responsibility |
| --- | --- |
| `src/incidentlens/telemetry/` | Loki, Tempo, Prometheus, and correlation adapters |
| `src/incidentlens/providers/` | Local and AWS provider implementations |
| `infra/terraform/` | AWS infrastructure modules and environments |
| `compose.observability.yaml` | OpenTelemetry Demo and Grafana LGTM |
| `.github/workflows/aws-deploy.yml` | Manual AWS deployment |
| `.github/workflows/aws-destroy.yml` | Explicit AWS teardown |

## 13. Step-by-Step Delivery Plan

## 13.1 Milestone 1: Evidence Search Baseline

**Learning objective:** Understand ingestion, chunking, embeddings, vector search, prompting, and citations.

Steps:

1. Initialize the Python project and quality tools.
2. Start Qdrant as one local container with a documented command.
3. Create the payment retry storm scenario and ground truth manifest.
4. Define typed incident, evidence, citation, query, and answer models.
5. Normalize logs, runbooks, and changes into evidence chunks.
6. Create stable evidence IDs and source locators.
7. Embed and index the evidence in Qdrant.
8. Implement dense retrieval with mandatory incident filtering.
9. Generate a structured cited answer through Ollama.
10. Validate every citation before returning it.
11. Expose indexing, listing, evidence inspection, and investigation through a CLI.
12. Add unit tests with a fake model and separately marked integration tests.

Completion gate:

1. A user can index and investigate the scenario from the CLI.
2. At least four of five initial questions retrieve their required evidence in the top five.
3. Every citation resolves to an original source.
4. The system abstains when evidence is missing.
5. Unit tests do not require an LLM.

## 13.2 Milestone 2: Modern RAG and Evaluation

**Learning objective:** Understand modern retrieval, controlled experiments, and evidence-based model selection.

Steps:

1. Add two more incidents with distractors and multiple question variants.
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
2. The selected retriever outperforms the frozen baseline on the declared primary metric.
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

## 13.4 Milestone 4: Resume Ready Product

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
9. Publish the static portfolio page.
10. Record a short demonstration and document the architecture, experiments, limitations, and setup.

Completion gate:

1. A clean checkout starts through the documented Docker workflow.
2. A recruiter can understand the project value within two minutes.
3. Claims can be opened and inspected at their original evidence.
4. Replay Lab reproduces the published comparisons.
5. CI passes without paid services or model credentials.
6. The README reports only measured results.

## 13.5 Milestone 5: Live Observability and AWS

**Learning objective:** Integrate a proven AI core with realistic telemetry and production-style cloud infrastructure.

Steps for live telemetry:

1. Run the OpenTelemetry Demo and Grafana LGTM locally.
2. Implement Loki, Tempo, and Prometheus adapters.
3. Convert live results into the existing evidence model.
4. Correlate logs, traces, metrics, and changes by time, service, and trace ID.
5. Replay a known fault and evaluate the investigation.
6. Preserve fixture mode for fast deterministic testing.

Steps for AWS:

1. Implement provider interfaces for model, state, evidence storage, and vector search.
2. Package FastAPI as a Lambda container.
3. Define S3, CloudFront, API Gateway, Lambda, ECR, DynamoDB, and CloudWatch through Terraform.
4. Configure GitHub Actions authentication through AWS OIDC.
5. Add manual deploy and destroy workflows.
6. Run post-deployment health and replay smoke tests.
7. Add budgets, short log retention, and documented cost controls.
8. Add Bedrock only as an optional provider.

Completion gate:

1. Fixture and live telemetry modes use the same investigation workflow.
2. Ollama and Bedrock use the same model interface.
3. AWS infrastructure can be created and removed reproducibly.
4. CI uses short-lived credentials.
5. The public portfolio remains useful while AWS is offline.

## 14. Testing Strategy

### 14.1 Unit tests

Unit tests cover parsing, normalization, chunk IDs, filtering, fusion, citation validation, metrics, state transitions, retry limits, and abstention policies. Models and external services are replaced with deterministic fakes.

### 14.2 Integration tests

Integration tests cover Qdrant indexing and search, FastAPI routes, Docker health checks, and optional Ollama output validation. Live model tests are separately marked because they are slower and less deterministic.

### 14.3 Evaluation regression tests

A small frozen subset runs in pull requests. It checks that retrieval recall, citation validity, incident isolation, and abstention do not fall below declared thresholds. Full experiments run manually or on a scheduled workflow.

### 14.4 End-to-end tests

Playwright verifies the primary flow from scenario selection to report and citation inspection. AWS deployment smoke tests verify health, one investigation, and artifact access.

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

## 17. Cost Strategy

Milestones 1 through 4 use locally hosted components and do not require a paid model API. Normal electricity, hardware, internet, and any applicable local software licensing costs still apply.

The optional AWS deployment is designed for short demonstrations rather than continuous operation. Lambda is preferred over continuously running compute. Resources are created on demand, log retention is short, storage is limited, and a destroy workflow is provided. The project documentation will not promise that AWS usage is free because pricing and account eligibility vary.

## 18. Principal Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Scope overwhelms a beginner | Treat Milestone 4 as the finish line and build only one milestone at a time |
| Synthetic data appears unrealistic | Use operationally plausible evidence, label it synthetic, and later validate with OpenTelemetry Demo scenarios |
| Retrieval gains are overstated | Freeze the baseline, declare the primary metric, publish raw results, and document dataset size |
| LLM output is nondeterministic | Use structured output, deterministic validation, fake models in CI, and versioned prompts |
| Agent loops become expensive or unreliable | Use one graph, read-only tools, one retry, and strict budgets |
| Citations look convincing but are invalid | Validate evidence IDs and expose the original source for every citation |
| AWS creates unexpected costs | Deploy manually, use budgets and short retention, avoid continuous compute, and destroy after use |
| Local hardware cannot run the chosen model | Keep model adapters configurable and select a smaller Ollama model after checking hardware |

## 19. Resume Impact Bullet Templates

Replace every bracketed field with a measured result from the completed project. Do not place estimated or invented numbers on the resume.

1. **Built** an evidence-grounded incident investigation assistant using hybrid Qdrant retrieval, local reranking, Ollama, and LangGraph to analyze logs, runbooks, and deployment events, **achieving [root cause accuracy]% accuracy and [Recall@K] evidence recall across [N] reproducible incident cases**.
2. **Designed** an Incident Replay Lab that benchmarked dense, hybrid, reranked, and agentic RAG configurations against hidden ground truth, **improving [primary metric] by [X]% over the dense baseline while reducing unsupported citations from [A] to [B]**.
3. **Delivered** the application end to end with FastAPI, React, Docker Compose, GitHub Actions, Terraform, and an on-demand AWS deployment, **reducing setup to [one command or measured time], maintaining [test count or coverage]% automated coverage, and keeping demonstrated cloud cost below [measured amount]**.

These bullets follow Action, Context, Result structure. The final wording will be adjusted after real evaluation and deployment measurements exist.

## 20. Definition of Done

The core portfolio project is complete at Milestone 4 when:

1. Three or more versioned replay scenarios contain ground truth and distractors.
2. Dense, hybrid, and reranked retrieval are compared reproducibly.
3. The bounded agent creates competing hypotheses and can abstain.
4. Every important claim has a valid, inspectable citation.
5. Replay Lab shows expected and predicted findings with metrics and traces.
6. The API, frontend, Qdrant, and model connection run through documented local setup.
7. CI verifies code quality, tests, retrieval regressions, frontend behavior, and container builds.
8. The public project page explains the problem, architecture, results, failures, and limitations.
9. Resume claims use measurements generated by the repository.
10. No AWS account or paid API is required to evaluate the core project.

Milestone 5 is complete only when live telemetry and AWS meet their separate completion gates. It is not required for the project to be resume ready.

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
