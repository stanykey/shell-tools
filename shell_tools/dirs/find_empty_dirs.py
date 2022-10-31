from collections.abc import Callable
from pathlib import Path
from typing import Any

from click import argument
from click import command
from click import option


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


@command()
@argument("root-dir", type=Path, default=Path.cwd())
@option("--ignore-empty-files", is_flag=True, help="Treat empty files as absent.")
@option("--remove/--no-remove", is_flag=True, help="Indicate remove or not empty dirs")
def cli(root_dir: Path, ignore_empty_files: bool, remove: bool) -> None:
    root_dir = root_dir.absolute()
    if not root_dir.exists():
        print("The root directory is not set or doesn't exists.")

    empty_dirs = find_empty_dirs(root_dir, ignore_empty_files)
    processor = get_dirs_processor("remove" if remove else "print")
    processor(empty_dirs)


if __name__ == "__main__":
    cli()
