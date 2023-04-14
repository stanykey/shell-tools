from os import PathLike
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen


def find_repositories(root: str | PathLike[str], recursive: bool = False) -> list[Path]:
    """
    Find all git repositories in `root` directory.

    The main criterion is the presence of the **.git** directory inside.
    """
    root = Path(root)
    if not root.is_dir():
        return list()

    pattern = r"**/.git" if recursive else r"*/.git"
    return [folder.parent for folder in root.glob(pattern)]


def execute_command(*arguments: str) -> list[str]:
    """Execute `arguments` as the single shell command."""
    with Popen(arguments, stdout=PIPE) as shell:
        stdout, _ = shell.communicate()
        return stdout.decode("utf-8").strip().split("\n")


def update_repository(path: str | PathLike[str], submodules: bool) -> list[str]:
    """Pull the latest changes for given repository at `path`."""
    output = execute_command("git", "-C", str(path), "pull")
    if submodules:
        output += execute_command("git", "-C", str(path), "submodule", "update", "--init", "--recursive")
    return output
