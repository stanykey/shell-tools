from pathlib import Path


def find_empty_dirs(root_dir: Path, ignore_empty_files: bool = False) -> list[Path]:
    result = []

    items = tuple(path for path in root_dir.iterdir())
    dirs = tuple(filter(lambda path: path.is_dir(), items))
    if not dirs:
        files = tuple(filter(lambda path: path.is_file(), items))
        if not files:
            result.append(root_dir)
        elif ignore_empty_files:
            non_empty = any(file.stat().st_size > 0 for file in files)
            if not non_empty:
                result.append(root_dir)

    for child_dir in dirs:
        result.extend(find_empty_dirs(child_dir, ignore_empty_files))

    return result
