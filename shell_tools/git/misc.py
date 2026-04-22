from os import PathLike
from pathlib import Path
from subprocess import run


def find_repositories(root: str | PathLike[str], recursive: bool = False) -> list[Path]:
    """
    Find all git repositories in the `root` directory.

    The main criterion is the presence of the **.git** directory inside.
    """
    start_directory = Path(root)
    if not start_directory.is_dir():
        return list()

    pattern = r"**/.git" if recursive else r"*/.git"
    return [folder.parent for folder in start_directory.glob(pattern)]


def execute_command(*arguments: str) -> list[str]:
    """Execute `arguments` as a single shell command."""
    result = run(arguments, capture_output=True, text=True, check=True)
    return result.stdout.strip().splitlines()


def update_repository(path: str | PathLike[str], submodules: bool) -> list[str]:
    """Pull the latest changes for the given repository at `path`."""
    output = execute_command("git", "-C", str(path), "pull")
    if submodules:
        output += execute_command("git", "-C", str(path), "submodule", "update", "--init", "--recursive")
    return output
