"""Configs model types."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Union

from expression.collections import Block
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class FileData:
    """Metadata and data of a file."""

    path: Path
    file_name: str
    contents: str


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
    file: FileData


class ReadFromPlural(BaseModel):
    """Read from plural files."""

    model_config = ConfigDict(frozen=True, strict=True)
    type: Literal['plural']
    path: str
    files: Block[FileData]


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
    settings: ConfigSettings
    base_url: str
    website_name: str
    sections: dict[str, Section] = Field(..., min_length=1)
