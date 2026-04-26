from os import PathLike
from pathlib import Path


def find_empty_dirs(root: str | PathLike[str], ignore_empty_files: bool = False) -> list[Path]:
    """Find all empty dirs recursively from a given `root` directory."""
    start_directory = Path(root)
    if not start_directory.is_dir():
        return list()

    return _find_empty_dirs(start_directory, ignore_empty_files, set())


def _find_empty_dirs(start_directory: Path, ignore_empty_files: bool, visited: set[Path]) -> list[Path]:
    try:
        resolved = start_directory.resolve()
    except OSError:
        resolved = start_directory.absolute()

    if resolved in visited:
        return []
    visited.add(resolved)

    result = []
    items = [path for path in start_directory.iterdir()]
    dirs = [path for path in items if path.is_dir()]
    if not dirs:
        files = [path for path in items if path.is_file()]
        if not files:
            result.append(start_directory)
        elif ignore_empty_files:
            non_empty = any(file.stat().st_size > 0 for file in files)
            if not non_empty:
                result.append(start_directory)

    for child_dir in dirs:
        if child_dir.is_symlink():
            continue
        result.extend(_find_empty_dirs(child_dir, ignore_empty_files, visited))

    return result
