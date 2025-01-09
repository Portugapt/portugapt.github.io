"""Common types for metadata."""

from typing import Any, Literal, Optional, TypeVar

from expression import Nothing, Option, Some, pipe
from expression.collections import Block
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar('T')
U = TypeVar('U')


class HeaderExtra(BaseModel):
    """An header extra."""

    model_config = ConfigDict(frozen=True)
    tag: str
    value: str

    def __str__(self) -> str:
        """To string."""
        return f'<{self.tag}>{self.value}</{self.tag}>'


class OpenGraph(BaseModel):
    """OpenGraph data."""

    model_config = ConfigDict(frozen=True)
    title: str
    ogtype: str
    image: str
    locale: str
    description: Option[str] = Field(default=Nothing)
    site_name: Option[str] = Field(default=Nothing)
    url: Option[str] = Field(default=Nothing)


class Image(BaseModel):
    """Represents an image."""

    model_config = ConfigDict(frozen=True)
    url: str
    alt_text: str = ''
    title: Optional[str] = None
    caption: Optional[str] = None


class Author(BaseModel):
    """Represents a profile.

    https://ogp.me/#type_profile
    """

    model_config = ConfigDict(frozen=True)
    first_name: str
    last_name: str
    username: str
    gender: Literal['male', 'female']
    email: Option[str] = Field(default=Nothing)
    url: Option[str] = Field(default=Nothing)


class Breadcrumbs(BaseModel):
    """Breadcrumbs for a page. Generic implementation."""

    path: str  # Could be a relative path segment or a full URL
    title: str
    data: Option[Any] = Field(default=Nothing)  # Any extra data
    previous_crumb: Option['Breadcrumbs'] = Field(default=Nothing)  # Link to previous breadcrumb (towards the root)

    def __str__(self) -> str:
        """Returns a string representation of the breadcrumb path."""
        return self.generate_url()

    def _block_back(self) -> Block[str]:
        """Creates a Block of path segments in order (from root to current) using pattern matching."""

        def _back(current: Option[Breadcrumbs]) -> Block[str]:
            """Recursive helper function to accumulate path segments into a Block."""
            match current:
                case Option(tag='some', some=c):
                    if c.path:
                        segment = Block.of_seq([c.path.strip('/')])
                    else:
                        segment = Block.empty()
                    return segment + _back(c.previous_crumb)
                case _:
                    return Block.empty()

        return _back(Some(self))

    def generate_url(self, base_url: str = '') -> str:
        """Generates a URL from a Breadcrumbs object."""
        segments = self._block_back()

        # If the first segment is a full URL, return it as-is
        if segments and segments.head().startswith('http'):
            return segments.head()

        path = pipe(segments, lambda xs: '/'.join(xs))

        # Handle the base URL case
        if base_url:
            # Ensure the base_url ends with a single slash
            base_url = base_url.rstrip('/') + '/'
            return f'{base_url}{path}'

        return f'/{path}'

    # @classmethod
    # def from_url(cls, url: str, title_prefix: str = 'Page') -> Option['Breadcrumbs']:
    #     """Creates a Breadcrumbs object from a URL.

    #     Args:
    #         url: The URL to parse.
    #         title_prefix: An optional prefix for generated titles.

    #     Returns:
    #         An Option containing the Breadcrumbs object if successful, Nothing otherwise.
    #     """
    #     try:
    #         parsed_url = urlparse(url)

    #         # Handle invalid URLs
    #         if not parsed_url.path:
    #             return Nothing

    #         # Handle full URLs as a special case
    #         if parsed_url.scheme and parsed_url.netloc:
    #             return Some(cls(path=url, title=f'{title_prefix}: {url}', next_page=Nothing))

    #         # Handle root path
    #         if parsed_url.path == '/':
    #             return Some(cls(path='/', title=f'{title_prefix}: /', next_page=Nothing))

    #         # Handle relative URLs
    #         path_segments = parsed_url.path.strip('/').split('/')

    #         root_crumb = cls(
    #             path='/' + path_segments[0], title=f'{title_prefix}: {path_segments[0]}', next_page=Nothing
    #         )
    #         current_crumb = root_crumb

    #         for segment in path_segments[1:]:
    #             next_crumb = cls(path=segment, title=f'{title_prefix}: {segment}', next_page=Nothing)
    #             current_crumb.next_page = Some(next_crumb)
    #             current_crumb = next_crumb

    #         return Some(root_crumb)

    #     except ValueError:
    #         return Nothing


ContentType = Literal['blog', 'article', 'tutorial', 'documentation']

StageType = Literal['draft', 'published']
