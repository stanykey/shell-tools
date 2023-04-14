"""Contain set of CLI applications."""
from collections.abc import Callable
from pathlib import Path
from re import IGNORECASE
from re import search
from sys import argv
from typing import Any

from click import argument
from click import command
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
    print(*dirs, sep="\n")


@dirs_processor(name="remove")
def remove_dirs(dirs: list[Path]) -> None:
    for path in dirs:
        print(f"removing '{path}'")
        path.rmdir()


def get_dirs_processor(name: str) -> Processor:
    factory = ProcessorFactory()
    return factory.get_processor(name)


@command()
@argument("path", type=Path)
@option("--size", type=str, default="10mb", help="File size in bytes[kb|mb|gb].", show_default=True)
@option("--line-size", type=int, default=64, help="Length of line/chunk.", show_default=True)
def generate_file(path: Path, size: str, line_size: int) -> None:
    path = path.absolute()
    if path.is_dir():
        print(f"Script aborted: '{path}' exists and it's directory")
        return

    if path.is_file():
        answer = input(f"file '{path}' already exists. override? [yes/no]: ")
        if not answer.lower().startswith("y"):
            return

    file_size = determine_file_size(size)
    if not file_size:
        print(f"Invalid file size was requested (file-size={size}).")
        print(f"Use '{get_program_name()} --help' to see allowed options.")
        return

    print(f"The file of {size} will be generated at '{path}'.")
    make_random_file(path, file_size, line_size)
    print("The generation is finished.")


@command()
@argument("root-dir", type=Path, default=Path.cwd())
@option("--ignore-empty-files", is_flag=True, help="Treat empty files as absent.")
@option("--remove/--no-remove", is_flag=True, help="Indicate remove or not empty dirs")
def discover_empty_dirs(root_dir: Path, ignore_empty_files: bool, remove: bool) -> None:
    root_dir = root_dir.absolute()
    if not root_dir.exists():
        print("The root directory is not set or doesn't exists.")

    empty_dirs = find_empty_dirs(root_dir, ignore_empty_files)
    processor = get_dirs_processor("remove" if remove else "print")
    processor(empty_dirs)


@command()
@argument("root-dir", type=Path, default=Path.cwd())
@option("-r", "--recursive", is_flag=True, help="Search git repos recursively")
@option("--submodules/--no-submodules", is_flag=True, help="Update or not submodules")
def sync_repos(root_dir: Path, recursive: bool, submodules: bool) -> None:
    root_dir = root_dir.absolute()
    suffix = "recursively " if recursive else ""
    print(f"Scanning '{root_dir}' for git repositories {suffix}...")

    repos = find_repositories(root_dir, recursive)
    for repo in repos:
        update_repository(repo, submodules)
        print(f"{repo.relative_to(root_dir)} was synced")

    input("Press Enter to exit...")
