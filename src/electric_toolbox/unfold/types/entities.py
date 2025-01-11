"""Entities for the site."""

import os
from typing import Generic, TypeVar

from expression import Nothing, Option
from expression.collections import Block
from pydantic import BaseModel, Field, computed_field

from electric_toolbox.unfold.components.breadcrumbs import Breadcrumbs, generate_url

T = TypeVar('T')
S = TypeVar('S')


class SingularEntity(BaseModel, Generic[T]):
    """Base model for a singular entity (e.g., Post, Project, Article).

    T is the type of the plural entity.
    """

    parent: Option[T] = Field(default=Nothing)  # To make a computed_field, we need to add it as field.
    slug: str
    title: str
    breadcrumbs: Breadcrumbs

    @computed_field  # type: ignore[misc]
    @property
    def url(self) -> str:
        """The relative URL of the singular entity."""
        return generate_url(crumb=self.breadcrumbs)


class PluralEntity(BaseModel, Generic[T]):
    """Base model for a plural entity.

    T is the type of the singular entity.
    """

    title: str
    breadcrumbs: Breadcrumbs
    items: Block[T]

    @computed_field  # type: ignore[misc]
    @property
    def url(self) -> str:
        """The relative URL of the plural entity."""
        return generate_url(crumb=self.breadcrumbs, base_url=os.getenv('ETBX_WEBSITE_DOMAIN', 'localhost:8000'))


PluralEntity.model_rebuild()
