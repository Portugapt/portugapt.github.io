"""Common code for parsing."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class TargetFiles(BaseModel):
    """Post data."""

    model_config = ConfigDict(frozen=True)
    complete: str
    hx: str
    llm: Optional[str] = None
