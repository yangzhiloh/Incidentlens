from __future__ import annotations

import csv
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal

import typer
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl, ValidationError


class AuditValidationError(ValueError):
    """Raised when an employer audit cannot support a safe provider decision."""


class AtsProvider(StrEnum):
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKDAY = "workday"


AuditProvider = Literal["greenhouse", "lever", "ashby", "workday", "other", "unknown"]


class AuditRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    company_slug: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    singapore_presence_evidence_url: HttpUrl
    careers_url: HttpUrl
    provider: AuditProvider
    board_identifier: str | None
    public_access: Literal["yes", "partial", "blocked", "no"]
    provider_feasible: bool
    total_postings_observed: int = Field(ge=0)
    singapore_postings_observed: int = Field(ge=0)
    singapore_internships_observed: int = Field(ge=0)
    evidence_url: HttpUrl
    observed_at: AwareDatetime
    notes: str


_CSV_COLUMNS = frozenset(AuditRow.model_fields)
_MEASURED_PROVIDERS = frozenset(provider.value for provider in AtsProvider)


def validate_audit(rows: Sequence[AuditRow]) -> None:
    """Validate safety and completeness invariants for the source audit."""

    slugs = [row.company_slug for row in rows]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise AuditValidationError(f"duplicate company slug: {duplicates[0]}")

    if len(rows) < 30:
        raise AuditValidationError("audit must contain at least 30 verified employers")

    now = datetime.now(UTC)
    for row in rows:
        if row.observed_at > now:
            raise AuditValidationError(f"observation for {row.company_slug} is in the future")

        if row.public_access in {"yes", "partial"} and not row.board_identifier:
            raise AuditValidationError(
                f"accessible row {row.company_slug} requires a board identifier"
            )

        if row.singapore_postings_observed > row.total_postings_observed:
            raise AuditValidationError(
                f"Singapore postings exceed total postings for {row.company_slug}"
            )

        if row.singapore_internships_observed > row.singapore_postings_observed:
            raise AuditValidationError(
                f"Singapore internships exceed Singapore postings for {row.company_slug}"
            )


def select_providers(rows: Sequence[AuditRow]) -> tuple[AtsProvider, AtsProvider]:
    """Select the two feasible providers using measured employer coverage."""

    coverage: dict[AtsProvider, set[str]] = defaultdict(set)
    internships: dict[AtsProvider, int] = defaultdict(int)
    for row in rows:
        if (
            row.provider in _MEASURED_PROVIDERS
            and row.provider_feasible
            and row.public_access == "yes"
            and row.board_identifier
        ):
            provider = AtsProvider(row.provider)
            coverage[provider].add(row.company_slug)
            internships[provider] += row.singapore_internships_observed

    ranked = sorted(
        coverage,
        key=lambda provider: (
            -len(coverage[provider]),
            -internships[provider],
            provider.value,
        ),
    )
    if len(ranked) < 2:
        raise AuditValidationError("audit must identify at least two feasible providers")
    return ranked[0], ranked[1]


def _parse_bool(value: str | None, field: str) -> bool:
    normalized = (value or "").strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise AuditValidationError(f"{field} must be true or false")


def _parse_int(value: str | None, field: str) -> int:
    normalized = (value or "").strip()
    try:
        return int(normalized)
    except ValueError as exc:
        raise AuditValidationError(f"{field} must be an integer") from exc


def _parse_row(raw: dict[str, str | None], row_number: int) -> AuditRow:
    board_identifier = (raw.get("board_identifier") or "").strip() or None
    payload: dict[str, object] = {
        "company_slug": raw.get("company_slug"),
        "company_name": raw.get("company_name"),
        "singapore_presence_evidence_url": raw.get("singapore_presence_evidence_url"),
        "careers_url": raw.get("careers_url"),
        "provider": raw.get("provider"),
        "board_identifier": board_identifier,
        "public_access": raw.get("public_access"),
        "provider_feasible": _parse_bool(raw.get("provider_feasible"), "provider_feasible"),
        "total_postings_observed": _parse_int(
            raw.get("total_postings_observed"), "total_postings_observed"
        ),
        "singapore_postings_observed": _parse_int(
            raw.get("singapore_postings_observed"), "singapore_postings_observed"
        ),
        "singapore_internships_observed": _parse_int(
            raw.get("singapore_internships_observed"), "singapore_internships_observed"
        ),
        "evidence_url": raw.get("evidence_url"),
        "observed_at": raw.get("observed_at"),
        "notes": raw.get("notes") or "",
    }
    try:
        return AuditRow.model_validate(payload)
    except ValidationError as exc:
        raise AuditValidationError(f"invalid audit row {row_number}: {exc}") from exc


def load_audit(path: Path) -> tuple[AuditRow, ...]:
    """Load and type-check an employer audit CSV without selecting providers."""

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = frozenset(reader.fieldnames or ())
        missing = sorted(_CSV_COLUMNS - fieldnames)
        if missing:
            raise AuditValidationError(f"audit CSV is missing columns: {', '.join(missing)}")
        if fieldnames - _CSV_COLUMNS:
            unexpected = sorted(fieldnames - _CSV_COLUMNS)
            raise AuditValidationError(f"audit CSV has unexpected columns: {', '.join(unexpected)}")

        rows: list[AuditRow] = []
        for row_number, raw in enumerate(reader, start=2):
            if None in raw:
                raise AuditValidationError(f"audit row {row_number} has an unnamed column")
            rows.append(_parse_row(raw, row_number))
    return tuple(rows)


def _provider_rows(rows: Sequence[AuditRow], provider: AtsProvider) -> tuple[AuditRow, ...]:
    return tuple(
        row
        for row in rows
        if row.provider == provider.value
        and row.provider_feasible
        and row.public_access == "yes"
        and row.board_identifier
    )


def render_report(rows: Sequence[AuditRow]) -> str:
    """Render dated provider measurements and the deterministic decision."""

    selected = select_providers(rows)
    lines = [
        "# Singapore Employer ATS Coverage Findings",
        "",
        "This is a dated sample of public employer careers data, not a market coverage claim.",
        "",
        "| Provider | Public feasible employers | Singapore postings observed | "
        "Singapore internships observed |",
        "| --- | ---: | ---: | ---: |",
    ]
    for provider in AtsProvider:
        provider_rows = _provider_rows(rows, provider)
        lines.append(
            f"| {provider.value} | {len(provider_rows)} | "
            f"{sum(row.singapore_postings_observed for row in provider_rows)} | "
            f"{sum(row.singapore_internships_observed for row in provider_rows)} |"
        )

    for provider_name in ("other", "unknown"):
        provider_rows = tuple(row for row in rows if row.provider == provider_name)
        lines.append(
            f"| {provider_name} | {len(provider_rows)} | "
            f"{sum(row.singapore_postings_observed for row in provider_rows)} | "
            f"{sum(row.singapore_internships_observed for row in provider_rows)} |"
        )

    lines.extend(
        [
            "",
            f"## Selected providers: {selected[0].value} and {selected[1].value}",
            "",
            "Selection sorts feasible, fully public boards by distinct employer coverage, "
            "then observed Singapore internship count, then provider name.",
            "",
            "## Evidence rows",
            "",
        ]
    )
    for row in rows:
        lines.append(
            f"- `{row.company_slug}` {row.company_name}: "
            f"[{row.evidence_url}]({row.evidence_url}) ({row.provider}, {row.public_access}); "
            f"{row.notes}"
        )
    return "\n".join(lines) + "\n"


app = typer.Typer(add_completion=False)


@app.command()
def validate(path: Path) -> None:
    """Validate an employer audit CSV."""

    try:
        rows = load_audit(path)
        validate_audit(rows)
    except AuditValidationError as exc:
        typer.echo(f"audit invalid: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"audit valid: {len(rows)} employers")


@app.command()
def report(path: Path, output_path: Path) -> None:
    """Generate provider findings from a validated employer audit CSV."""

    try:
        rows = load_audit(path)
        validate_audit(rows)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_report(rows), encoding="utf-8")
    except AuditValidationError as exc:
        typer.echo(f"audit invalid: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"wrote findings: {output_path}")


if __name__ == "__main__":
    app()
