from pathlib import Path
from subprocess import PIPE
from subprocess import Popen


def gather_repos(root_dir: Path, recursive: bool = False) -> tuple[Path, ...]:
    pattern = r"**/.git" if recursive else r"*/.git"
    return tuple(folder.parent for folder in root_dir.glob(pattern))


def execute_command(*arguments: str) -> list[str]:
    with Popen(arguments, stdout=PIPE) as shell:
        stdout, _ = shell.communicate()
        return stdout.decode("utf-8").strip().split("\n")


def update_repo(repo: Path, submodules: bool) -> list[str]:
    output = execute_command("git", "-C", str(repo), "pull")
    if submodules:
        output += execute_command("git", "-C", str(repo), "submodule", "update", "--init", "--recursive")
    return output
