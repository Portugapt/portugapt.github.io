"""Breadcrumbs internal functions."""

from expression import Option, Some, pipe
from expression.collections import Block

from .models import Breadcrumbs


def _handle_full_url(head: str, tail: Block[str]) -> str:
    """Handles the case where the first segment is a full URL."""
    match len(tail):
        case 0:
            return head
        case _:
            return f'{head}/{pipe(tail, lambda xs: "/".join(xs))}'


def _handle_segments(segments: Block[str], base_url: str) -> str:
    """Handles the case where segments is not empty."""
    match segments.head().startswith('http'):
        case True:
            return _handle_full_url(segments.head(), segments.tail())
        case _:
            return _handle_relative_path(segments, base_url)


def _handle_relative_path(segments: Block[str], base_url: str) -> str:
    """Handles the case where the path is relative."""
    path = '/'.join(filter(None, segments))

    if base_url:
        if base_url.endswith('/'):
            return base_url + path
        else:
            return base_url + '/' + path if path else base_url
    else:
        return '/' + path if path else '/'


def _handle_empty_segments(base_url: str) -> str:
    """Handles the case where segments is empty."""
    match base_url:
        case '':
            return '/'
        case _:
            return base_url if base_url.endswith('/') else base_url


def block_of_paths(crumb: Breadcrumbs) -> Block[str]:
    """Creates a Block of path segments in order (from root to current) using pattern matching."""

    def _back(current: Option[Breadcrumbs]) -> Block[str]:
        """Recursive helper function to accumulate path segments into a Block."""
        match current:
            case Option(tag='some', some=c):
                match c.path:
                    case path if path.startswith('http'):
                        return Block.of_seq([path])
                    case path if path.strip('/') == '':
                        return _back(c.previous_crumb)
                    case _ as path:
                        return _back(c.previous_crumb) + Block.of_seq([path.strip('/')])
            case _:
                return Block.empty()

    return _back(Some(crumb))


def generate_url(crumb: Breadcrumbs, base_url: str = '') -> str:
    """Generates a URL from a Breadcrumbs object."""
    segments = block_of_paths(crumb)

    match len(segments):
        case 0:
            return _handle_empty_segments(base_url)
        case _:
            return _handle_segments(segments, base_url)
