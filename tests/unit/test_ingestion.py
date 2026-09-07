import json
from pathlib import Path
from textwrap import dedent

import pytest

from incidentlens.ingestion import (
    ScenarioLoadError,
    _parse_changes,
    _parse_logs,
    _parse_runbook,
    load_scenario,
)
from incidentlens.models import SourceType


def _write_minimal_scenario(directory: Path) -> None:
    directory.mkdir()

    (directory / "manifest.yaml").write_text(
        dedent(
            """
            schema_version: 1
            scenario_version: "1.0.0"
            is_synthetic: true
            incident_definition:
              incident_id: payment-retry-storm
              title: Payment retry storm
              description: Unsafe retries amplified intermittent gateway failures.
              start_time: 2026-08-15T09:00:00Z
              end_time: 2026-08-15T10:00:00Z
              services:
                - payment-service
                - payment-gateway
            ground_truth:
              root_cause: An unsafe retry configuration amplified gateway failures.
              relevant_evidence_ids:
                - payment-retry-storm:log:retry-attempt-001
              distractor_evidence_ids:
                - payment-retry-storm:change:harmless-deploy
              expected_mitigation: Restore bounded exponential backoff.
            """
        ).lstrip(),
        encoding="utf-8",
    )

    (directory / "questions.yaml").write_text(
        dedent(
            """
            schema_version: 1
            questions:
              - question_id: root-cause
                question: What caused the incident?
                expected_evidence_ids:
                  - payment-retry-storm:log:retry-attempt-001
                should_abstain: false
            """
        ).lstrip(),
        encoding="utf-8",
    )

    (directory / "logs.jsonl").write_text(
        json.dumps(
            {
                "source_id": "retry-attempt-001",
                "timestamp": "2026-08-15T09:15:00Z",
                "service": "payment-service",
                "severity": "WARN",
                "environment": "production",
                "message": "Retrying immediately after gateway 503.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    (directory / "changes.jsonl").write_text(
        json.dumps(
            {
                "source_id": "harmless-deploy",
                "timestamp": "2026-08-15T08:00:00Z",
                "service": "payment-service",
                "change_type": "deployment",
                "environment": "production",
                "summary": "Dashboard labels updated.",
                "details": "The deployment changed display labels only.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    (directory / "runbook.md").write_text(
        "## Retry policy\n"
        "<!-- source-id: retry-policy -->\n"
        "Use capped exponential backoff with jitter.\n",
        encoding="utf-8",
    )

def test_parse_logs_normalizes_one_jsonl_record(tmp_path: Path) -> None:
    path = tmp_path / "logs.jsonl"
    path.write_text(
        json.dumps(
            {
                "source_id": "gateway-503-001",
                "timestamp": "2026-08-15T09:15:00Z",
                "service": "payment-gateway",
                "severity": "ERROR",
                "environment": "production",
                "message": "Payment gateway returned 503.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    chunks = _parse_logs(path, "payment-retry-storm")

    assert len(chunks) == 1
    assert chunks[0].evidence_id == "payment-retry-storm:log:gateway-503-001"
    assert chunks[0].source_type is SourceType.LOG
    assert chunks[0].service == "payment-gateway"
    assert chunks[0].text == "Payment gateway returned 503."
    assert chunks[0].metadata == {
        "severity": "ERROR",
        "environment": "production",
    }
    assert chunks[0].locator.path == "logs.jsonl"
    assert chunks[0].locator.line_start == 1
    assert chunks[0].locator.line_end == 1

def test_parse_logs_reports_filename_and_line_for_invalid_json(
    tmp_path: Path,
) -> None:
    path = tmp_path / "logs.jsonl"
    valid_record = json.dumps(
        {
            "source_id": "gateway-503-001",
            "timestamp": "2026-08-15T09:15:00Z",
            "service": "payment-gateway",
            "severity": "ERROR",
            "environment": "production",
            "message": "Payment gateway returned 503.",
        }
    )
    path.write_text(f"{valid_record}\nnot-json\n", encoding="utf-8")

    with pytest.raises(
        ScenarioLoadError,
        match=r"logs\.jsonl: line 2: invalid JSON",
    ):
        _parse_logs(path, "payment-retry-storm")


def test_parse_logs_rejects_timestamp_without_timezone(
    tmp_path: Path,
) -> None:
    path = tmp_path / "logs.jsonl"
    path.write_text(
        json.dumps(
            {
                "source_id": "gateway-503-001",
                "timestamp": "2026-08-15T09:15:00",
                "service": "payment-gateway",
                "severity": "ERROR",
                "environment": "production",
                "message": "Payment gateway returned 503.",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ScenarioLoadError, match="logs.jsonl: line 1"):
        _parse_logs(path, "payment-retry-storm")

def test_parse_changes_normalizes_one_jsonl_record(tmp_path: Path) -> None:
    path = tmp_path / "changes.jsonl"
    path.write_text(
        json.dumps(
            {
                "source_id": "retry-policy-deploy",
                "timestamp": "2026-08-15T09:10:00Z",
                "service": "payment-service",
                "change_type": "configuration",
                "environment": "production",
                "summary": "Retry policy changed.",
                "details": "Backoff was disabled and maximum attempts increased to eight.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    chunks = _parse_changes(path, "payment-retry-storm")

    assert len(chunks) == 1
    assert chunks[0].evidence_id == (
        "payment-retry-storm:change:retry-policy-deploy"
    )
    assert chunks[0].source_type is SourceType.CHANGE
    assert chunks[0].text == (
        "Retry policy changed.\n\n"
        "Backoff was disabled and maximum attempts increased to eight."
    )
    assert chunks[0].metadata == {
        "change_type": "configuration",
        "environment": "production",
    }
    assert chunks[0].locator.path == "changes.jsonl"

def test_parse_runbook_creates_one_chunk_per_marked_section(
    tmp_path: Path,
) -> None:
    path = tmp_path / "runbook.md"
    path.write_text(
        "# Payment Operations\n"
        "\n"
        "## Retry policy\n"
        "<!-- source-id: retry-policy -->\n"
        "Use capped exponential backoff with jitter.\n"
        "\n"
        "## Circuit breaker\n"
        "<!-- source-id: circuit-breaker -->\n"
        "Open the circuit after repeated gateway failures.\n",
        encoding="utf-8",
    )

    chunks = _parse_runbook(path, "payment-retry-storm")

    assert [chunk.evidence_id for chunk in chunks] == [
        "payment-retry-storm:runbook:retry-policy",
        "payment-retry-storm:runbook:circuit-breaker",
    ]
    assert chunks[0].source_type is SourceType.RUNBOOK
    assert chunks[0].text == (
        "## Retry policy\n\n"
        "Use capped exponential backoff with jitter."
    )
    assert chunks[0].locator.line_start == 3
    assert chunks[0].locator.line_end == 6
    assert chunks[0].locator.section == "Retry policy"
    assert chunks[1].locator.line_start == 7
    assert chunks[1].locator.line_end == 9

def test_parse_runbook_requires_a_source_id_marker(
    tmp_path: Path,
) -> None:
    path = tmp_path / "runbook.md"
    path.write_text(
        "## Retry policy\n"
        "Use bounded retries.\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ScenarioLoadError,
        match="valid source-id marker",
    ):
        _parse_runbook(path, "payment-retry-storm")

def test_load_scenario_returns_validated_components(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "payment-retry-storm"
    _write_minimal_scenario(directory)

    scenario = load_scenario(directory)

    assert scenario.directory == directory
    assert scenario.manifest.scenario_version == "1.0.0"
    assert scenario.manifest.is_synthetic is True
    assert scenario.questions.questions[0].question_id == "root-cause"
    assert len(scenario.evidence) == 3
    assert {chunk.source_type for chunk in scenario.evidence} == {
        SourceType.LOG,
        SourceType.CHANGE,
        SourceType.RUNBOOK,
    }

def test_load_scenario_reports_a_missing_required_file(tmp_path: Path) -> None:
    directory = tmp_path / "payment-retry-storm"
    directory.mkdir()

    with pytest.raises(
        ScenarioLoadError,
        match="manifest.yaml: required file is missing",
    ):
        load_scenario(directory)