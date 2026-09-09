# IncidentLens

IncidentLens is a learning-focused AI engineering project for investigating cloud reliability incidents using evidence-grounded retrieval-augmented generation and bounded agentic workflows.

The system is being designed to retrieve operational evidence from logs, runbooks, deployment events, metrics, and traces. It will generate incident reports where every important conclusion links back to inspectable evidence.

## Why This Project

Incident investigation requires engineers to search across multiple disconnected sources, reconstruct timelines, compare possible causes, and avoid drawing conclusions from incomplete evidence.

IncidentLens explores how modern RAG and controlled AI agents can support that process while remaining:

- Evidence-grounded
- Reproducible
- Measurable
- Read-only
- Capable of abstaining when evidence is insufficient

The planned standout feature is an Incident Replay Lab that runs investigations against incidents with known ground truth. This makes it possible to compare retrieval strategies, measure root-cause accuracy, and detect regressions.

## Current Status

Current phase: **Milestone 1, scenario ingestion in progress**

Currently implemented:

- Python package scaffold
- Dependency and lockfile configuration
- Development tool configuration
- Environment variable template
- Typed local configuration and command-line entry point
- Immutable incident, evidence, citation, query, answer, and evaluation models
- Citation and abstention validation contracts
- Versioned scenario manifests and evaluation question sets
- Source-aware parsing for logs, deployment changes, and runbook sections
- Deterministic unit tests for the implemented foundation

Not implemented yet:

- Cross-file scenario validation
- The first committed payment-retry-storm scenario package
- Qdrant indexing
- Dense evidence retrieval with mandatory incident filtering
- Ollama generation
- Citation validation
- Incident Replay Lab and retrieval evaluation
- Bounded LangGraph investigation
- API or web interface
- Docker deployment
- Live OpenTelemetry Demo integration
- Optional AWS infrastructure

The project is being built progressively so that each milestone produces a working and measurable result.

## Planned Milestones

| Milestone | Focus | Intended Result |
|---|---|---|
| 1 | Evidence search baseline | Investigate one prerecorded incident using dense retrieval and cited generation |
| 2 | Modern RAG | Add hybrid retrieval, metadata filtering, reranking, and evaluation |
| 3 | Agentic investigation | Build a bounded LangGraph workflow with hypotheses, retries, and abstention |
| 4 | Resume-ready product | Add FastAPI, React, Docker, CI/CD, the Incident Replay Lab, and one live OpenTelemetry incident |
| 5 | Optional cloud extension | Add an on-demand AWS deployment after the local portfolio version is complete |

Milestone 4 is the portfolio finish line. Milestone 5 is optional and is not required for the project to be resume ready.

## Technology Stack

Current foundation:

- Python 3.12
- uv
- Pydantic
- Pydantic Settings
- Qdrant Client
- FastEmbed
- HTTPX
- PyYAML
- Typer
- Structlog
- Ruff
- Mypy
- Pytest

Planned core additions include LangGraph, FastAPI, React, Docker, GitHub Actions, and OpenTelemetry. AWS and Terraform remain optional extensions.

## Prerequisites

Install:

1. Python 3.12
2. uv
3. Git
4. Ollama, required later for local generation

Ollama does not need a downloaded model during the initial project setup.

## Local Setup

Install the project and its development dependencies:

```powershell
uv sync
