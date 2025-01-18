"""Parsing of files and configs, and building of data structures."""

from .models import Website
from .parse import main as parse_website

__all__ = [
    'Website',
    'parse_website',
]
