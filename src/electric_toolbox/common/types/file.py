"""Types and Dataclasses related to files."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileData:
    """Metadata and data of a file."""

    path: Path
    file_name: str
    contents: str
