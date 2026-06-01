"""Load inline SVG icons from a directory.

Icons live as individual ``resources/icons/<name>.svg`` files (raw SVG pastes
cleanly with no escaping). They are exposed to the templates as an ``icons``
Jinja global, e.g. ``{{ icons.menu | safe }}``.
"""

from pathlib import Path


def load_icons(directory: Path) -> dict[str, str]:
    """Read every ``*.svg`` in ``directory`` into a ``{stem: markup}`` mapping.

    Args:
        directory: Folder containing the SVG files.

    Returns:
        A mapping of icon name (file stem) to its SVG markup. Empty if the
        directory does not exist.
    """
    if not directory.is_dir():
        return {}
    return {path.stem: path.read_text(encoding='utf-8').strip() for path in sorted(directory.glob('*.svg'))}
