"""Breadcrumbs internal functions."""

from typing import NamedTuple

from expression import Option, Some
from expression.collections import Block

from .models import Breadcrumbs


class StructuredPart(NamedTuple):
    """Structured parts of a path."""

    push: str
    push_extension: str
    get: str
    get_extension: str

    def full_push(self) -> str:
        """Gets full push url."""
        if self.push.startswith('http'):
            return self.push
        else:
            return f'{self.push}.{self.push_extension}'

    def full_get(self) -> str:
        """Gets full get url."""
        return f'{self.get}.{self.get_extension}'


def _handle_full_url(segments: Block[StructuredPart], base_url: str) -> str:
    """Handles the case where the first segment is a full URL."""
    head = segments.head()
    tail = segments.tail()

    if not tail:
        return head.full_push()
    else:
        return f"{head.full_push()}/{'/'.join(tail.map(lambda x: x.push))}"


def _handle_relative_path(segments: Block[StructuredPart], base_url: str) -> str:
    """Handles the case where the path is relative."""
    path = '/'.join(x.push for x in segments)
    extension = segments.take_last(1).item(0).get_extension

    if base_url:
        if not base_url.endswith('/'):
            base_url += '/'
        return base_url + path + '.' + extension
    else:
        return '/' + path + '.' + extension


def _handle_segments(segments: Block[StructuredPart], base_url: str) -> str:
    """Handles URL generation based on whether the first segment is a full URL or relative path."""
    head = segments.head()

    if head.push.startswith('http'):
        return _handle_full_url(segments, base_url)
    else:
        return _handle_relative_path(segments, base_url)


def _handle_empty_segments(base_url: str) -> str:
    """Handles the case where segments is empty."""
    return base_url if base_url.endswith('/') else base_url + '/' if base_url else '/'


def block_of_paths(crumb: Breadcrumbs) -> Block[StructuredPart]:
    """Creates a Block of path segments in order (from root to current) using pattern matching."""

    def _back(current: Option[Breadcrumbs]) -> Block[StructuredPart]:
        """Recursive helper function to accumulate path segments into a Block."""
        match current:
            case Option(tag='some', some=c):
                match c.path:
                    case path if path.startswith('http'):
                        return Block.of_seq(
                            [
                                StructuredPart(
                                    push='index',
                                    get='index_hx',
                                    push_extension='',
                                    get_extension='html',
                                )
                            ]
                        )
                    case path if path.strip('/') == '':
                        return _back(c.previous_crumb)
                    case _ as path:
                        return _back(c.previous_crumb) + Block.of_seq(
                            [
                                StructuredPart(
                                    push=c.targets.complete.destination,
                                    push_extension=c.targets.complete.extension,
                                    get=c.targets.hx.destination,
                                    get_extension=c.targets.hx.extension,
                                )
                            ]
                        )
            case _:
                return Block.empty()

    return _back(Some(crumb))


def generate_url(crumb: Breadcrumbs, base_url: str = '') -> str:
    """Generates a URL from a Breadcrumbs object."""
    segments = block_of_paths(crumb)

    if not segments:
        return _handle_empty_segments(base_url)
    else:
        return _handle_segments(segments, base_url)


def get_push_url(crumb: Breadcrumbs, base_url: str) -> str:
    """Gets the push URL for a breadcrumb."""
    segments = block_of_paths(crumb)

    if not segments:
        return _handle_empty_segments(base_url)
    else:
        return _handle_segments(segments, base_url)


def get_hx_url(crumb: Breadcrumbs) -> str:
    """Gets the get URL for a breadcrumb."""
    segments = block_of_paths(crumb)

    if not segments:
        return '/'
    else:
        tail = segments.take_last(1).item(0)
        return f"/{'/'.join(x.get for x in segments)}.{tail.get_extension}"
