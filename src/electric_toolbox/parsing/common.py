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
    """Post data."""

    model_config = ConfigDict(frozen=True)
    complete: Template
    hx: Template
    llm: Optional[str] = None
