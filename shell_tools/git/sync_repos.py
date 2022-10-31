from pathlib import Path
from subprocess import PIPE
from subprocess import Popen

from click import argument
from click import command
from click import option


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


@command()
@argument("root-dir", type=Path, default=Path.cwd())
@option("-r", "--recursive", is_flag=True, help="Search git repos recursively")
@option("--submodules/--no-submodules", is_flag=True, help="Update or not submodules")
def cli(root_dir: Path, recursive: bool, submodules: bool) -> None:
    root_dir = root_dir.absolute()
    suffix = "recursively " if recursive else ""
    print(f"Scanning '{root_dir}' for git repositories {suffix}...")

    repos = gather_repos(root_dir, recursive)
    for repo in repos:
        update_repo(repo, submodules)
        print(f"{repo.relative_to(root_dir)} was synced")

    input("Press Enter to exit...")


if __name__ == "__main__":
    cli()
