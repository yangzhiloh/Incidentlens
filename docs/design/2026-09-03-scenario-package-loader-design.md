# Scenario Package and Loader Design

**Status:** Implementation in progress

Implemented so far: versioned models, source-aware log and change parsing, runbook-section parsing, required-file checks, YAML validation, and `LoadedScenario` assembly.

Outstanding before completion: cross-file relationship validation, the committed payment-retry-storm package, tests for invalid relationships, and a test that loads the repository scenario.

## Objective

Create one complete synthetic payment-retry-storm scenario and a deterministic loader that validates the package and returns a `LoadedScenario`.

This milestone does not include indexing, retrieval, Qdrant, LLM generation, or CLI integration.

## Package Structure

The scenario will be stored at:

scenarios/payment-retry-storm/

It contains:

- `manifest.yaml`
- `questions.yaml`
- `logs.jsonl`
- `changes.jsonl`
- `runbook.md`

## Loader Architecture

The public entry point is:

`load_scenario(directory: Path) -> LoadedScenario`

Source-aware parsers handle each file format:

- The manifest parser returns `ScenarioManifest`.
- The question parser returns `ScenarioQuestionSet`.
- The log parser returns log `EvidenceChunk` objects.
- The change parser returns change `EvidenceChunk` objects.
- The runbook parser returns runbook `EvidenceChunk` objects.

`load_scenario()` coordinates these parsers, validates relationships between their results, and constructs `LoadedScenario`.

Ground truth remains available for evaluation through the manifest. Runtime retrieval and answer-generation components must receive only incident information and evidence, preventing ground-truth leakage.

## Evidence Identity

Every log record, change record, and runbook section declares a stable `source_id`.

The loader constructs the final evidence ID using:

`<incident-id>:<source-type>:<source-id>`

Example:

`payment-retry-storm:log:gateway-503-001`

Ground truth and evaluation questions reference complete evidence IDs.

IDs must not depend on line numbers because unrelated file edits must not change evidence identity.

## Parsing Rules

YAML files are parsed safely and validated using Pydantic models.

Each nonempty JSONL line represents one record. Invalid JSON reports its filename and line number.

Each runbook evidence section begins with a level-two heading and an invisible marker:

`<!-- source-id: retry-policy -->`

The heading and its body form one evidence chunk.

Timestamps must include a timezone. Source locators contain scenario-relative paths and one-based line ranges.

The manifest gains:

- `scenario_version`, initially `"1.0.0"`
- `is_synthetic`, set to `true`

`schema_version` describes the file structure. `scenario_version` describes the scenario content.

## Validation and Errors

Loading proceeds through these stages:

1. Confirm the directory and required files exist.
2. Parse every file.
3. Validate individual records.
4. Validate cross-file relationships.
5. Construct `LoadedScenario`.

Cross-file validation ensures:

- Evidence IDs are unique.
- Relevant and distractor evidence IDs exist.
- Relevant and distractor sets do not overlap.
- Evaluation-question evidence IDs exist.
- Answerable questions reference relevant evidence.
- All evidence belongs to the manifest incident.

Any failure raises `ScenarioLoadError` with the scenario directory, filename, optional line number, relevant field or evidence ID, and a human-readable reason.

The loader never returns a partially valid scenario and never modifies source files. Applications may catch the error for one invalid scenario while continuing to serve other valid scenarios.

## Scenario Narrative

The payment gateway begins returning intermittent `503` responses.

A configuration deployment removed bounded exponential backoff and allowed rapid repeated retries. These retries amplify traffic, increasing gateway failures and payment latency.

The expected mitigation is to restore capped exponential backoff with jitter and limit retry attempts.

The package contains approximately:

- 12 structured log records
- 3 deployment or configuration events
- 3 runbook sections
- 5 evaluation questions
- Relevant evidence and plausible distractors

Distractors may include an unrelated database warning, an earlier harmless deployment, and inventory-service latency. They must not create a second valid root cause.

The questions cover root cause, triggering change, supporting evidence, mitigation, and one question that requires abstention because its answer is unavailable.

## Test Strategy

Development follows small red, green, refactor cycles:

1. Test the new manifest fields.
2. Test log parsing.
3. Test change parsing.
4. Test runbook-section parsing.
5. Test manifest and question loading.
6. Test successful scenario assembly.
7. Test missing files and malformed input.
8. Test duplicate and unknown evidence IDs.
9. Test overlapping relevant and distractor sets.
10. Test loading the repository’s real scenario package.

Parser unit tests may exercise focused internal functions. Public contract tests use `load_scenario()`.

Tests require no Qdrant, LLM, Docker, or network access.

## Completion Criteria

This milestone is complete when:

- The repository scenario loads into `LoadedScenario`.
- Evidence IDs and source locators are stable and resolvable.
- Invalid packages fail with useful errors.
- Ground-truth references are validated.
- Ground truth is not included inside runtime evidence.
- Pytest, Ruff, and mypy pass.
