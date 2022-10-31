"""Update recursively all repos."""
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen

from click import argument
from click import command
from click import option


def gather_repos(root_dir: Path, recursive: bool = False) -> tuple[Path, ...]:
    pattern = r"**/.git" if recursive else r"*/.git"
    return tuple(folder.parent for folder in root_dir.glob(pattern))


def update_repo(repo: Path) -> list[str]:
    process = Popen(["git", "-C", str(repo), "pull"], stdout=PIPE)
    stdout, _ = process.communicate()
    return stdout.decode("utf-8").strip().split("\n")


@command()
@argument("root-dir", type=Path, default=Path.cwd(), help="Repos root dir")
@option("-r", "--recursive", is_flag=True, help="Search git repos recursively")
def cli(root_dir: Path, recursive: bool) -> None:
    root_dir = root_dir.absolute()
    suffix = "recursively " if recursive else ""
    print(f"Scanning '{root_dir}' for git repositories {suffix}...")

    repos = gather_repos(root_dir, recursive)
    for repo in repos:
        update_repo(repo)
        print(f"{repo.relative_to(root_dir)} was synced")

    input("Press Enter to exit...")


if __name__ == "__main__":
    cli()
