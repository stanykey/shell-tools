from pathlib import Path


def find_empty_dirs(root: Path, ignore_empty_files: bool = False) -> list[Path]:
    """Find all empty dirs recursively from given `root` directory."""
    result = []

    items = [path for path in root.iterdir()]
    dirs = [path for path in items if path.is_dir()]
    if not dirs:
        files = [path for path in items if path.is_file()]
        if not files:
            result.append(root)
        elif ignore_empty_files:
            non_empty = any(file.stat().st_size > 0 for file in files)
            if not non_empty:
                result.append(root)

    for child_dir in dirs:
        result.extend(find_empty_dirs(child_dir, ignore_empty_files))

    return result
