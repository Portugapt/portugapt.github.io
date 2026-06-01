"""Common code for parsing."""

from typing import Optional

from pydantic import BaseModel, ConfigDict

from electric_toolbox.constants import ExistingTemplates


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
