"""Configs model types."""

from pydantic import BaseModel, ConfigDict


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


class SiteConfigs(BaseModel):
    """Website data."""

    model_config = ConfigDict(frozen=True)
    human_number: str
    settings: ConfigSettings
    head: ConfigHead
    contents: ConfigContents
