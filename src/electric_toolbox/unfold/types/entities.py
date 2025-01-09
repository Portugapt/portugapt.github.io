from typing import Any, Generic, TypeVar

from expression import Nothing, Option
from expression.collections import Block
from pydantic import BaseModel, Field, computed_field

from electric_toolbox.unfold.types.common import Breadcrumbs

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
        return self.breadcrumbs.generate_url()


class PluralEntity(BaseModel, Generic[T, S]):
    """Base model for a plural entity.

    T is the type of the singular entity.
    """

    parent: Option['PluralEntity[Any, S]'] = Field(default=Nothing)  # Allow PluralEntities to have parents
    title: str
    breadcrumbs: Breadcrumbs
    items: Block[T]

    @computed_field  # type: ignore[misc]
    @property
    def url(self) -> str:
        """The relative URL of the plural entity."""
        return self.breadcrumbs.generate_url()


PluralEntity.model_rebuild()
