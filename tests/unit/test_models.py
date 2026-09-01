from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from incidentlens.models import (
    AnswerDraft,
    Citation,
    Confidence,
    EvaluationQuestion,
    EvidenceChunk,
    GroundTruth,
    IncidentDefinition,
    InvestigationAnswer,
    LoadedScenario,
    RetrievedEvidence,
    ScenarioManifest,
    ScenarioQuestionSet,
    SearchQuery,
    SourceLocator,
    SourceType,
)


def test_evidence_chunk_is_immutable() -> None:
    chunk = EvidenceChunk(
        evidence_id="incident-1:log:log-1",
        incident_id="incident-1",
        source_type=SourceType.LOG,
        service="payment-service",
        timestamp=datetime(2025, 12, 3, 7, 15, tzinfo=UTC),
        text="Payment gateway returned 503.",
        locator=SourceLocator(
            path="scenarios/incident-1/logs.jsonl",
            line_start=1,
            line_end=1,
        ),
    )
    with pytest.raises(ValidationError):
        chunk.text = "DUMMY"  # type: ignore[misc]


def test_search_query_rejects_invalid_top_k() -> None:
    with pytest.raises(ValidationError):
        SearchQuery(
            incident_id="incident-1",
            question="What failed?",
            top_k=0,  # Requests zero results, should be at least 1
        )


def test_supported_answer_requires_root_cause() -> None:
    with pytest.raises(ValidationError):
        AnswerDraft(
            summary="A retry storm occurred.",
            suspected_root_cause=None,
            citation_ids=("incident-1:log:log-1",),
            next_checks=(),
            confidence=Confidence.HIGH,
            sufficient_evidence=True,  # Contradiction no root cause but evidence is sufficient
        )


def test_supported_answer_requires_citations() -> None:
    with pytest.raises(ValidationError):
        AnswerDraft(
            summary="A retry storm occurred.",
            suspected_root_cause="Unbounded retries overloaded the payment gateway",
            citation_ids=(),
            next_checks=(),
            confidence=Confidence.HIGH,
            sufficient_evidence=True,  # Contradiction no citations but evidence is sufficient
        )


def test_abstention_cannot_claim_a_root_cause() -> None:
    with pytest.raises(ValidationError):
        AnswerDraft(
            summary="Evidence is missing.",
            suspected_root_cause="Database corruption",
            citation_ids=(),
            next_checks=("Collect database logs.",),
            confidence=Confidence.LOW,
            sufficient_evidence=False,  # Contradiction since there is root cause
            # but evidence is insufficient
        )


def test_supported_answer_accepts_root_cause_and_citations() -> None:
    draft = AnswerDraft(
        summary="A retry storm occurred.",
        suspected_root_cause="Unbounded retries overloaded the payment gateway.",
        citation_ids=("incident-1:log:log-1",),
        next_checks=("Review the retry policy.",),
        confidence=Confidence.HIGH,
        sufficient_evidence=True,
    )

    assert draft.sufficient_evidence is True


def test_abstention_accepts_missing_root_cause() -> None:
    draft = AnswerDraft(
        summary="There is not enough evidence to identify the cause.",
        suspected_root_cause=None,
        citation_ids=(),
        next_checks=("Collect payment-service logs.",),
        confidence=Confidence.LOW,
        sufficient_evidence=False,
    )

    assert draft.sufficient_evidence is False


def test_retrieved_evidence_preserves_backend_score() -> None:
    chunk = EvidenceChunk(
        evidence_id="incident-1:log:log-1",
        incident_id="incident-1",
        source_type=SourceType.LOG,
        text="Payment gateway returned 503.",
        locator=SourceLocator(
            path="scenarios/incident-1/logs.jsonl",
            line_start=1,
            line_end=1,
        ),
    )

    retrieved = RetrievedEvidence(
        chunk=chunk,
        score=-0.1,
    )

    assert retrieved.score == -0.1


def test_citation_contains_a_resolvable_excerpt() -> None:
    citation = Citation(
        evidence_id="incident-1:log:log-1",
        source_type=SourceType.LOG,
        locator=SourceLocator(
            path="scenarios/incident-1/logs.jsonl",
            line_start=1,
            line_end=1,
        ),
        excerpt="Payment gateway returned 503.",
    )

    assert citation.excerpt == "Payment gateway returned 503."


def test_investigation_answer_contains_resolved_citations() -> None:
    citation = Citation(
        evidence_id="incident-1:log:log-1",
        source_type=SourceType.LOG,
        locator=SourceLocator(
            path="scenarios/incident-1/logs.jsonl",
            line_start=1,
            line_end=1,
        ),
        excerpt="Payment gateway returned 503.",
    )

    answer = InvestigationAnswer(
        summary="The payment gateway was unavailable.",
        suspected_root_cause="The payment gateway returned repeated 503 responses.",
        citations=(citation,),
        next_checks=("Review the gateway health dashboard.",),
        confidence=Confidence.HIGH,
        sufficient_evidence=True,
    )

    assert answer.citations[0].evidence_id == "incident-1:log:log-1"


def test_incident_definition_requires_a_forward_time_range() -> None:
    with pytest.raises(ValidationError):
        IncidentDefinition(
            incident_id="incident-1",
            title="Payment retry storm",
            description="Payment requests repeatedly failed.",
            start_time=datetime(2026, 8, 15, 11, 0, tzinfo=UTC),
            end_time=datetime(2026, 8, 15, 10, 0, tzinfo=UTC),
            services=("payment-service",),
        )


def test_ground_truth_requires_relevant_evidence() -> None:
    with pytest.raises(ValidationError):
        GroundTruth(
            root_cause="Unbounded retries overloaded the payment gateway.",
            relevant_evidence_ids=(),
            distractor_evidence_ids=(),
            expected_mitigation="Apply a bounded retry policy.",
        )


def test_scenario_manifest_rejects_invalid_schema_version() -> None:
    incident_definition = IncidentDefinition(
        incident_id="incident-1",
        title="Payment retry storm",
        description="Payment requests repeatedly failed.",
        start_time=datetime(2026, 8, 15, 9, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 15, 10, 0, tzinfo=UTC),
        services=("payment-service",),
    )

    ground_truth = GroundTruth(
        root_cause="Unbounded retries overloaded the payment gateway.",
        relevant_evidence_ids=("incident-1:log:log-1",),
        expected_mitigation="Apply a bounded retry policy.",
    )

    with pytest.raises(ValidationError):
        ScenarioManifest(
            schema_version=0,  # Invalid schema version
            incident_definition=incident_definition,
            ground_truth=ground_truth,
        )


def test_abstention_question_cannot_require_evidence() -> None:
    with pytest.raises(ValidationError):
        EvaluationQuestion(
            question_id="question-1",
            question="What caused the outage?",
            expected_evidence_ids=("incident-1:log:log-1",),
            should_abstain=True,  # Contradiction since abstention questions cannot require evidence
        )


def test_answerable_question_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        EvaluationQuestion(
            question_id="question-2",
            question="What caused the outage?",
            expected_evidence_ids=(),
            should_abstain=False,  # Contradiction since answerable questions
            # require at least one expected evidence ID
        )


def test_scenario_question_set_contains_at_least_one_question() -> None:
    with pytest.raises(ValidationError):
        ScenarioQuestionSet(
            schema_version=1,
            questions=(),  # Empty question set
        )


def test_loaded_scenario_groups_validated_components(tmp_path: Path) -> None:
    incident_definition = IncidentDefinition(
        incident_id="incident-1",
        title="Payment retry storm",
        description="Payment requests repeatedly failed.",
        start_time=datetime(2026, 8, 15, 9, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 15, 10, 0, tzinfo=UTC),
        services=("payment-service",),
    )

    ground_truth = GroundTruth(
        root_cause="Unbounded retries overloaded the payment gateway.",
        relevant_evidence_ids=("incident-1:log:log-1",),
        expected_mitigation="Apply a bounded retry policy.",
    )

    manifest = ScenarioManifest(
        schema_version=1,
        incident_definition=incident_definition,
        ground_truth=ground_truth,
    )

    questions = ScenarioQuestionSet(
        schema_version=1,
        questions=(
            EvaluationQuestion(
                question_id="question-1",
                question="What caused the outage?",
                expected_evidence_ids=("incident-1:log:log-1",),
                should_abstain=False,
            ),
        ),
    )

    evidence = EvidenceChunk(
        evidence_id="incident-1:log:log-1",
        incident_id="incident-1",
        source_type=SourceType.LOG,
        text="Payment gateway returned 503.",
        locator=SourceLocator(
            path="scenarios/incident-1/logs.jsonl",
            line_start=1,
            line_end=1,
        ),
    )

    scenario = LoadedScenario(
        directory=tmp_path,
        manifest=manifest,
        questions=questions,
        evidence=(evidence,),
    )

    assert scenario.directory == tmp_path
    assert scenario.manifest.incident_definition.incident_id == "incident-1"
    assert scenario.evidence[0].evidence_id == "incident-1:log:log-1"
