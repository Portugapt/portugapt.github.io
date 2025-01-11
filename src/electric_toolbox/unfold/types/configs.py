"""Configs model types."""

from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ConfigSettings(BaseModel):
    """Website settings."""

    model_config = ConfigDict(frozen=True, strict=True)
    include_drafts: bool


class ConfigHead(BaseModel):
    """Head data."""

    model_config = ConfigDict(frozen=True, strict=True)
    title: str


class ConfigContents(BaseModel):
    """Website contents data."""

    model_config = ConfigDict(frozen=True)
    index: str
    posts: str


class ReadFromSingular(BaseModel):
    """Read from singular file."""

    model_config = ConfigDict(frozen=True, strict=True)
    type: Literal['singular']
    path: str


class ReadFromPlural(BaseModel):
    """Read from plural files."""

    model_config = ConfigDict(frozen=True, strict=True)
    type: Literal['plural']
    path: str
    each: Optional[Literal['singular', 'plural']] = None


ReadFrom = Union[ReadFromSingular, ReadFromPlural]


class Section(BaseModel):
    """Section data."""

    model_config = ConfigDict(frozen=True, strict=True)
    title: str
    description: str
    url: str
    read_from: ReadFrom


class ConfigSections(BaseModel):
    """Website sections data."""

    model_config = ConfigDict(frozen=True, strict=True)
    sections: dict[str, Section] = Field(..., min_length=1)


class SiteConfigs(BaseModel):
    """Website data."""

    model_config = ConfigDict(frozen=True)
    human_number: str
    settings: ConfigSettings
    head: ConfigHead
    contents: ConfigContents
    sections: dict[str, Section] = Field(..., min_length=1)
