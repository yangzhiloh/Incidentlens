import json
import re
from json import JSONDecodeError
from pathlib import Path

import yaml
from pydantic import AwareDatetime, BaseModel, Field, ValidationError

from incidentlens.models import (
    EvidenceChunk,
    FrozenModel,
    LoadedScenario,
    ScenarioManifest,
    ScenarioQuestionSet,
    SourceLocator,
    SourceType,
)

_REQUIRED_FILES = (
    "manifest.yaml",
    "questions.yaml",
    "logs.jsonl",
    "changes.jsonl",
    "runbook.md",
)

class ScenarioLoadError(ValueError):
    def __init__(
        self,
        directory: Path,
        reason: str,
        *,
        filename: str | None = None,
        line: int | None = None,
    ) -> None:
        self.directory = directory
        self.filename = filename
        self.line = line
        self.reason = reason

        context = [str(directory)]
        if filename is not None:
            context.append(filename)
        if line is not None:
            context.append(f"line {line}")
        context.append(reason)
        super().__init__(": ".join(context))


class _LogRecord(FrozenModel):
    source_id: str = Field(min_length=1)
    timestamp: AwareDatetime
    service: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    environment: str = Field(min_length=1)
    message: str = Field(min_length=1)

class _ChangeRecord(FrozenModel):
    source_id: str = Field(min_length=1)
    timestamp: AwareDatetime
    service: str = Field(min_length=1)
    change_type: str = Field(min_length=1)
    environment: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    details: str = Field(min_length=1)


def _read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ScenarioLoadError(
            path.parent,
            str(exc),
            filename=path.name,
        ) from exc


def _parse_logs(path: Path, incident_id: str) -> tuple[EvidenceChunk, ...]:
    chunks: list[EvidenceChunk] = []

    for line_number, line in enumerate(_read_lines(path), start=1):
        if not line.strip():
            continue

        try:
            raw = json.loads(line)
        except JSONDecodeError as exc:
            raise ScenarioLoadError(
                path.parent,
                "invalid JSON",
                filename=path.name,
                line=line_number,
            ) from exc

        try:
            record = _LogRecord.model_validate(raw)
        except ValidationError as exc:
            raise ScenarioLoadError(
                path.parent,
                str(exc),
                filename=path.name,
                line=line_number,
            ) from exc

        chunks.append(
            EvidenceChunk(
                evidence_id=(
                    f"{incident_id}:{SourceType.LOG.value}:{record.source_id}"
                ),
                incident_id=incident_id,
                source_type=SourceType.LOG,
                service=record.service,
                timestamp=record.timestamp,
                text=record.message,
                locator=SourceLocator(
                    path=path.name,
                    line_start=line_number,
                    line_end=line_number,
                ),
                metadata={
                    "severity": record.severity,
                    "environment": record.environment,
                },
            )
        )

    return tuple(chunks)


def _parse_changes(path: Path, incident_id: str) -> tuple[EvidenceChunk, ...]:
    chunks: list[EvidenceChunk] = []

    for line_number, line in enumerate(_read_lines(path), start=1):
        if not line.strip():
            continue

        try:
            raw = json.loads(line)
        except JSONDecodeError as exc:
            raise ScenarioLoadError(
                path.parent,
                "invalid JSON",
                filename=path.name,
                line=line_number,
            ) from exc

        try:
            record = _ChangeRecord.model_validate(raw)
        except ValidationError as exc:
            raise ScenarioLoadError(
                path.parent,
                str(exc),
                filename=path.name,
                line=line_number,
            ) from exc

        chunks.append(
            EvidenceChunk(
                evidence_id=(
                    f"{incident_id}:{SourceType.CHANGE.value}:"
                    f"{record.source_id}"
                ),
                incident_id=incident_id,
                source_type=SourceType.CHANGE,
                service=record.service,
                timestamp=record.timestamp,
                text=f"{record.summary}\n\n{record.details}",
                locator=SourceLocator(
                    path=path.name,
                    line_start=line_number,
                    line_end=line_number,
                ),
                metadata={
                    "change_type": record.change_type,
                    "environment": record.environment,
                },
            )
        )

    return tuple(chunks)

_RUNBOOK_HEADING = re.compile(r"^##\s+(?P<title>\S.*)$")

_SOURCE_ID_MARKER = re.compile(
    r"^<!--\s*source-id:\s*(?P<source_id>[a-z0-9][a-z0-9-]*)\s*-->$"
)


def _parse_runbook(
    path: Path,
    incident_id: str,
) -> tuple[EvidenceChunk, ...]:
    lines = _read_lines(path)

    headings = [
        index
        for index, line in enumerate(lines)
        if _RUNBOOK_HEADING.match(line)
    ]

    if not headings:
        raise ScenarioLoadError(
            path.parent,
            "no level-two sections",
            filename=path.name,
        )

    chunks: list[EvidenceChunk] = []

    for position, start in enumerate(headings):
        end = (
            headings[position + 1]
            if position + 1 < len(headings)
            else len(lines)
        )

        heading_match = _RUNBOOK_HEADING.match(lines[start])
        assert heading_match is not None
        title = heading_match.group("title").strip()

        marker_index: int | None = None

        for candidate in range(start + 1, end):
            if lines[candidate].strip():
                marker_index = candidate
                break

        if marker_index is None:
            raise ScenarioLoadError(
                path.parent,
                "runbook section is missing a source-id marker",
                filename=path.name,
                line=start + 1,
            )

        marker_match = _SOURCE_ID_MARKER.match(
            lines[marker_index].strip()
        )

        if marker_match is None:
            raise ScenarioLoadError(
                path.parent,
                "runbook section is missing a valid source-id marker",
                filename=path.name,
                line=marker_index + 1,
            )

        body = "\n".join(lines[marker_index + 1 : end]).strip()

        if not body:
            raise ScenarioLoadError(
                path.parent,
                "runbook section has no body",
                filename=path.name,
                line=start + 1,
            )

        source_id = marker_match.group("source_id")

        chunks.append(
            EvidenceChunk(
                evidence_id=(
                    f"{incident_id}:{SourceType.RUNBOOK.value}:"
                    f"{source_id}"
                ),
                incident_id=incident_id,
                source_type=SourceType.RUNBOOK,
                text=f"## {title}\n\n{body}",
                locator=SourceLocator(
                    path=path.name,
                    line_start=start + 1,
                    line_end=end,
                    section=title,
                ),
            )
        )

    return tuple(chunks)


def _load_yaml[ModelT: BaseModel](path: Path, model_type: type[ModelT]) -> ModelT:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ScenarioLoadError(
            path.parent,
            str(exc),
            filename=path.name,
        ) from exc

    try:
        return model_type.model_validate(raw)
    except ValidationError as exc:
        raise ScenarioLoadError(
            path.parent,
            str(exc),
            filename=path.name,
        ) from exc


def _validate_unique_evidence_ids(
    directory: Path,
    evidence: tuple[EvidenceChunk, ...],
) -> None:
    seen: set[str] = set()

    for chunk in evidence:
        if chunk.evidence_id in seen:
            raise ScenarioLoadError(
                directory,
                f"duplicate evidence ID: {chunk.evidence_id}"
            )

        seen.add(chunk.evidence_id)


def _validate_ground_truth_evidence_ids(
    directory: Path,
    manifest: ScenarioManifest,
    evidence: tuple[EvidenceChunk, ...],
) -> None:
    available_ids = {chunk.evidence_id for chunk in evidence}

    referenced_ids = {
        *manifest.ground_truth.relevant_evidence_ids,
        *manifest.ground_truth.distractor_evidence_ids,
    }

    missing_ids = sorted(referenced_ids - available_ids)

    if missing_ids:
        raise ScenarioLoadError(
            directory,
            (
                "ground truth references missing evidence IDs: "
                f"{', '.join(missing_ids)}"
            ),
            filename="manifest.yaml",
        )


def load_scenario(directory: Path) -> LoadedScenario:
    if not directory.is_dir():
        raise ScenarioLoadError(
            directory,
            "scenario directory does not exist",
        )

    for filename in _REQUIRED_FILES:
        if not (directory / filename).is_file():
            raise ScenarioLoadError(
                directory,
                "required file is missing",
                filename=filename,
            )

    manifest = _load_yaml(
        directory / "manifest.yaml",
        ScenarioManifest,
    )
    questions = _load_yaml(
        directory / "questions.yaml",
        ScenarioQuestionSet,
    )

    incident_id = manifest.incident_definition.incident_id

    evidence = (
        *_parse_logs(directory / "logs.jsonl", incident_id),
        *_parse_changes(directory / "changes.jsonl", incident_id),
        *_parse_runbook(directory / "runbook.md", incident_id),
    )

    _validate_unique_evidence_ids(directory, evidence)
    _validate_ground_truth_evidence_ids(directory, manifest, evidence)

    return LoadedScenario(
        directory=directory,
        manifest=manifest,
        questions=questions,
        evidence=evidence,
    )
