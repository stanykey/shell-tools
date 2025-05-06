"""Contain set of CLI applications."""

from collections.abc import Callable
from datetime import datetime
from json import loads as json_from_str
from os import chdir
from pathlib import Path
from platform import system
from re import IGNORECASE
from re import search
from subprocess import Popen
from subprocess import run
from sys import argv
from typing import Any

from click import argument
from click import command
from click import echo
from click import option

from shell_tools.dirs.search import find_empty_dirs
from shell_tools.files.random import make_random_file
from shell_tools.git.misc import find_repositories
from shell_tools.git.misc import update_repository


def determine_file_size(size_string: str) -> int:
    multiplier = {"gb": 1024 * 1024 * 1024, "mb": 1024 * 1024, "kb": 1024}

    result = search(r"^(?P<number>\d+\.?\d*)(?P<multiplier>gb|mb|kb)?$", size_string, IGNORECASE)
    if result:
        number = float(result.group("number"))
        ratio = 1 if not result.group("multiplier") else multiplier[result.group("multiplier").lower()]
        return int(number * ratio)
    return 0


def get_program_name() -> str:
    return Path(argv[0]).stem


Processor = Callable[[list[Path]], None]


class ProcessorFactory:
    _state: dict[str, Any] = {}

    def __init__(self) -> None:
        self.__dict__ = self._state
        if not hasattr(self, "_registry"):
            self._registry: dict[str, Processor] = {}

    def register(self, name: str, processor: Processor) -> Processor:
        self._registry[name] = processor
        return processor

    @property
    def processors(self) -> dict[str, Processor]:
        return self._registry

    def get_processor(self, name: str) -> Processor:
        processor = self._registry.get(name)
        if not processor:
            raise KeyError(f"Unknown processor '{name}'")

        return processor


def dirs_processor(name: str) -> Callable[[Processor], Processor]:
    factory = ProcessorFactory()

    def decorator(processor: Processor) -> Processor:
        return factory.register(name, processor)

    return decorator


@dirs_processor(name="print")
def print_dirs(dirs: list[Path]) -> None:
    echo(*dirs, sep="\n")


@dirs_processor(name="remove")
def remove_dirs(dirs: list[Path]) -> None:
    for path in dirs:
        echo(f"removing '{path}'")
        path.rmdir()


def get_dirs_processor(name: str) -> Processor:
    factory = ProcessorFactory()
    return factory.get_processor(name)


@command()
@argument("path", type=Path)
@option("--size", type=str, default="10mb", help="File size in bytes[kb|mb|gb].", show_default=True)
@option("--line-size", type=int, default=64, help="Length of line/chunk.", show_default=True)
def generate_file(path: Path, size: str, line_size: int) -> None:
    """Generate files with random `trash` data."""
    path = path.absolute()
    if path.is_dir():
        echo(f"Script aborted: '{path}' exists and it's directory")
        return

    if path.is_file():
        answer = input(f"file '{path}' already exists. override? [yes/no]: ")
        if not answer.lower().startswith("y"):
            return

    file_size = determine_file_size(size)
    if not file_size:
        echo(f"Invalid file size was requested (file-size={size}).")
        echo(f"Use '{get_program_name()} --help' to see allowed options.")
        return

    echo(f"The file of {size} will be generated at '{path}'.")
    make_random_file(path, file_size, line_size)
    echo("The generation is finished.")


@command()
@argument("root-dir", type=Path, default=Path.cwd())
@option("--ignore-empty-files", is_flag=True, help="Treat empty files as absent.")
@option("--remove/--no-remove", is_flag=True, help="Indicate remove or not empty dirs")
def discover_empty_dirs(root_dir: Path, ignore_empty_files: bool, remove: bool) -> None:
    """Find empty directories."""
    root_dir = root_dir.absolute()
    if not root_dir.exists():
        echo("The root directory is not set or doesn't exists.")

    empty_dirs = find_empty_dirs(root_dir, ignore_empty_files)
    processor = get_dirs_processor("remove" if remove else "print")
    processor(empty_dirs)


@command()
@argument("root-dir", type=Path, default=Path.cwd())
@option("-r", "--recursive", is_flag=True, help="Search git repos recursively")
@option("--submodules/--no-submodules", is_flag=True, help="Update or not submodules")
def sync_repos(root_dir: Path, recursive: bool, submodules: bool) -> None:
    """Find repositories in <root-dir> and update them (pull changes from remote)."""
    root_dir = root_dir.absolute()
    suffix = "recursively " if recursive else ""
    echo(f"Scanning '{root_dir}' for git repositories {suffix}...")

    repos = find_repositories(root_dir, recursive)
    for repo in repos:
        update_repository(repo, submodules)
        echo(f"{repo.relative_to(root_dir)} was synced")

    input("Press Enter to exit...")


@command(options_metavar="")
def edit_nvim_config() -> None:
    """Shortcut to edit nvim config."""

    def get_nvim_config_directory() -> Path:
        path = Path("~/AppData/Local/nvim" if system() == "Windows" else "~/.config/nvim").expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path

    working_directory = Path.cwd()
    try:
        config_dir = get_nvim_config_directory()
        chdir(config_dir)

        arguments = ["nvim", str(config_dir)]
        with Popen(arguments) as nvim:
            nvim.wait()
    finally:
        chdir(working_directory)


@command(options_metavar="")
@argument("timestamp", type=float, required=False)
@option(
    "-f",
    "--date-format",
    type=str,
    default="%d-%b-%Y %H:%M:%S",
    help="Output date format. Standard C format codes (e.g., %Y, %m, %d, %H, %M, %S) are supported.",
)
def pretty_date(timestamp: float | None, date_format: str) -> None:
    """Print timestamp in human-readable format."""
    try:
        if timestamp is None:
            timestamp = datetime.now().timestamp() * 1000  # Default to current time in ms
        time = datetime.fromtimestamp(timestamp / 1000)  # Python timestamp in secs, unlike Unix in ms

        echo(time.strftime(date_format))
    except ValueError as ex:
        echo(f"Error: {ex}", err=True)
        exit(1)
    except (OverflowError, OSError):
        echo("Error: invalid timestamp value", err=True)
        exit(1)


@command(options_metavar="")
@option("--all/--outdated", is_flag=True, help="List only outdated packages.", default=True, show_default=True)
def update_python_packages(all: bool) -> None:
    """Update python packages in the environment."""
    if system() != "Windows":
        echo("This command only works on Windows yet.", err=True)
        return

    options = ["pip", "list", "--format=json", "--disable-pip-version-check"]
    if not all:
        options.append("--outdated")

    pip_output = run(options, capture_output=True, text=True, check=True).stdout

    packages = json_from_str(pip_output)
    if not packages:
        echo("All packages are up-to-date!")
        return

    for package in packages:
        package_name = package["name"]
        echo(f"Upgrading {package_name}...")
        if package_name == "pip":
            run(["python", "-m", "pip", "install", "--upgrade", "pip"], check=True)
        else:
            run(["pip", "install", "--upgrade", package_name], check=True)
