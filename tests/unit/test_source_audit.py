import csv
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.source_audit import (
    AtsProvider,
    AuditRow,
    AuditValidationError,
    load_audit,
    select_providers,
    validate_audit,
)


def audit_row(
    company_slug: str,
    provider: str = "greenhouse",
    *,
    accessible: bool = True,
    provider_feasible: bool = True,
    singapore_postings: int = 0,
    sg_internships: int = 0,
    observed_at: datetime | None = None,
    board_identifier: str | None = None,
) -> AuditRow:
    return AuditRow(
        company_slug=company_slug,
        company_name=company_slug.title(),
        singapore_presence_evidence_url=f"https://{company_slug}.example/singapore",
        careers_url=f"https://{company_slug}.example/careers",
        provider=provider,
        board_identifier=(
            f"board-{company_slug}" if board_identifier is None else board_identifier
        ) if accessible else None,
        public_access="yes" if accessible else "blocked",
        provider_feasible=provider_feasible,
        total_postings_observed=singapore_postings,
        singapore_postings_observed=singapore_postings,
        singapore_internships_observed=sg_internships,
        evidence_url=f"https://{company_slug}.example/jobs",
        observed_at=observed_at or datetime.now(UTC) - timedelta(days=1),
        notes="Official careers page lists Singapore.",
    )


def test_select_providers_uses_measured_coverage() -> None:
    rows = (
        audit_row("a", "greenhouse", singapore_postings=2, sg_internships=2),
        audit_row("b", "greenhouse", singapore_postings=1, sg_internships=1),
        audit_row("c", "lever", singapore_postings=4, sg_internships=4),
        audit_row("d", "ashby", singapore_postings=1, sg_internships=1),
    )

    assert select_providers(rows) == (AtsProvider.GREENHOUSE, AtsProvider.LEVER)


def test_audit_requires_thirty_verified_employers() -> None:
    with pytest.raises(AuditValidationError, match="at least 30"):
        validate_audit((audit_row("a"),))


def test_audit_rejects_duplicate_company_slugs() -> None:
    rows = tuple(audit_row(slug) for slug in ("a", "a"))

    with pytest.raises(AuditValidationError, match="duplicate company slug"):
        validate_audit(rows)


def test_audit_rejects_accessible_rows_without_board_identifier() -> None:
    rows = [audit_row(f"company-{index}") for index in range(30)]
    rows[0] = audit_row("company-0", board_identifier="")

    with pytest.raises(AuditValidationError, match="board identifier"):
        validate_audit(tuple(rows))


def test_audit_rejects_inconsistent_posting_counts() -> None:
    rows = [audit_row(f"company-{index}") for index in range(30)]
    rows[0] = audit_row("company-0", singapore_postings=1, sg_internships=2)

    with pytest.raises(AuditValidationError, match="internships"):
        validate_audit(tuple(rows))


def test_audit_rejects_future_observation_time() -> None:
    rows = [audit_row(f"company-{index}") for index in range(30)]
    rows[0] = audit_row("company-0", observed_at=datetime.now(UTC) + timedelta(minutes=1))

    with pytest.raises(AuditValidationError, match="future"):
        validate_audit(tuple(rows))


def test_load_audit_parses_typed_csv_rows(tmp_path: Path) -> None:
    path = tmp_path / "employers.csv"
    fieldnames = [
        "company_slug",
        "company_name",
        "singapore_presence_evidence_url",
        "careers_url",
        "provider",
        "board_identifier",
        "public_access",
        "provider_feasible",
        "total_postings_observed",
        "singapore_postings_observed",
        "singapore_internships_observed",
        "evidence_url",
        "observed_at",
        "notes",
    ]
    row = audit_row("example", singapore_postings=3, sg_internships=1).model_dump(mode="json")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)

    loaded = load_audit(path)

    assert loaded[0].company_slug == "example"
    assert loaded[0].provider_feasible is True
    assert loaded[0].singapore_postings_observed == 3
