from enum import StrEnum
from pathlib import Path

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

JsonScalar = str | int | float | bool | None


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SourceType(StrEnum):
    LOG = "log"
    RUNBOOK = "runbook"
    CHANGE = "change"


class Confidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourceLocator(FrozenModel):
    path: str
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    section: str | None = None

    @model_validator(mode="after")
    def validate_line_range(self) -> "SourceLocator":
        if self.line_end < self.line_start:
            raise ValueError("line_end must be greater than or equal to line_start")
        return self


class EvidenceChunk(FrozenModel):
    evidence_id: str = Field(min_length=1)
    incident_id: str = Field(min_length=1)
    source_type: SourceType
    service: str | None = None
    timestamp: AwareDatetime | None = None
    text: str = Field(min_length=1)
    locator: SourceLocator
    metadata: dict[str, JsonScalar] = Field(default_factory=dict)


class SearchQuery(FrozenModel):
    incident_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1)


class AnswerDraft(FrozenModel):
    summary: str = Field(min_length=1)
    suspected_root_cause: str | None = None
    citation_ids: tuple[str, ...] = ()
    next_checks: tuple[str, ...] = ()
    confidence: Confidence
    sufficient_evidence: bool

    @model_validator(mode="after")
    def validate_evidence_contract(self) -> "AnswerDraft":
        if not self.sufficient_evidence:
            if self.suspected_root_cause is not None:
                raise ValueError("an answer with insufficient evidence cannot claim a root cause.")

            return self

        if self.suspected_root_cause is None:
            raise ValueError("a supported answer must have a suspected root cause.")

        if not self.citation_ids:
            raise ValueError("a supported answer must include at least one citation.")

        return self


class RetrievedEvidence(FrozenModel):
    chunk: EvidenceChunk
    score: float


class Citation(FrozenModel):
    evidence_id: str = Field(min_length=1)
    source_type: SourceType
    locator: SourceLocator
    excerpt: str = Field(min_length=1)


class InvestigationAnswer(FrozenModel):
    summary: str = Field(min_length=1)
    suspected_root_cause: str | None = None
    citations: tuple[Citation, ...] = ()
    next_checks: tuple[str, ...] = ()
    confidence: Confidence
    sufficient_evidence: bool


class IncidentDefinition(FrozenModel):
    incident_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    start_time: AwareDatetime
    end_time: AwareDatetime
    services: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_time_range(self) -> "IncidentDefinition":
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time.")
        return self


class GroundTruth(FrozenModel):
    root_cause: str = Field(min_length=1)
    relevant_evidence_ids: tuple[str, ...] = Field(min_length=1)
    distractor_evidence_ids: tuple[str, ...] = ()
    expected_mitigation: str = Field(min_length=1)


class ScenarioManifest(FrozenModel):
    schema_version: int = Field(ge=1)
    scenario_version: str = Field(min_length=1)
    is_synthetic: bool
    incident_definition: IncidentDefinition
    ground_truth: GroundTruth


class EvaluationQuestion(FrozenModel):
    question_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected_evidence_ids: tuple[str, ...] = ()
    should_abstain: bool = False

    @model_validator(mode="after")
    def validate_expected_evidence(self) -> "EvaluationQuestion":
        if self.expected_evidence_ids and self.should_abstain:
            raise ValueError("abstention questions cannot require evidence IDS")

        if not self.expected_evidence_ids and not self.should_abstain:
            raise ValueError("answerable questions require at least one expected evidence ID")

        return self


class ScenarioQuestionSet(FrozenModel):
    schema_version: int = Field(ge=1)
    questions: tuple[EvaluationQuestion, ...] = Field(min_length=1)


class LoadedScenario(FrozenModel):
    directory: Path
    manifest: ScenarioManifest
    questions: ScenarioQuestionSet
    evidence: tuple[EvidenceChunk, ...]
