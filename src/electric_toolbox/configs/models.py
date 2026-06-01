"""Configs model types."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Tuple, Union

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
    resource_path: str
    read_from: ReadFrom


class SiteAuthor(BaseModel):
    """The person behind the site.

    Feeds the schema.org ``Person`` node and the default article author when a
    post's frontmatter does not declare its own ``authors``.
    """

    model_config = ConfigDict(frozen=True)
    first_name: str = 'João'
    last_name: str = 'Monteiro'
    username: str = 'Portugapt'
    url: str = 'https://portugapt.github.io/'
    email: Optional[str] = None
    same_as: Tuple[str, ...] = ()  # social/profile URLs -> schema.org `sameAs`

    @property
    def full_name(self) -> str:
        """The author's display name."""
        return f'{self.first_name} {self.last_name}'.strip()


class SitePublisher(BaseModel):
    """The publishing entity, mapped to a schema.org ``Organization``."""

    model_config = ConfigDict(frozen=True)
    name: str
    logo: Optional[str] = None


class WebsiteInfo(BaseModel):
    """Site-wide identity and SEO defaults.

    Per-page values (title/description/image/...) always win over these;
    these are the fallbacks and the source for site-level structured data.
    """

    model_config = ConfigDict(frozen=True)
    title: str
    description: str
    image: str  # absolute URL of the default social-share image
    locale: str
    name: Optional[str] = None  # og:site_name / WebSite name (defaults to title)
    twitter: Optional[str] = None  # @handle for the twitter:site card
    author: SiteAuthor = SiteAuthor()
    publisher: Optional[SitePublisher] = None

    @property
    def site_name(self) -> str:
        """The site name, falling back to the title when unset."""
        return self.name or self.title


class ConfigSections(BaseModel):
    """Website sections data."""

    model_config = ConfigDict(frozen=True, strict=True)
    sections: dict[str, Section] = Field(..., min_length=1)


class SiteConfigs(BaseModel):
    """Website data."""

    model_config = ConfigDict(frozen=True)
    base_url: str
    website: WebsiteInfo
    settings: ConfigSettings
    sections: dict[str, Section] = Field(..., min_length=1)
