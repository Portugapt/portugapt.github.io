"""Common code for parsing."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict

from electric_toolbox.constants import ExistingTemplates


def isoformat_with_tz(value: datetime) -> str:
    """Return an ISO 8601 string that always carries a timezone offset.

    Frontmatter datetimes are usually naive (``2025-02-01 15:30:00``); Google's
    structured-data tooling warns when ``datePublished`` / ``dateModified`` lack
    an offset. Naive values are assumed UTC; timezone-aware values (e.g. a
    frontmatter date written with ``+01:00``) are kept as-is.
    """
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


class Template(BaseModel):
    """Template data."""

    model_config = ConfigDict(frozen=True)
    destination: str
    template: ExistingTemplates
    extension: str


class TargetFiles(BaseModel):
    """The single output document for a page (one file per page under hx-boost)."""

    model_config = ConfigDict(frozen=True)
    complete: Template
    llm: Optional[str] = None
