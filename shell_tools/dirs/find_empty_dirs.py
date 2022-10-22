from argparse import ArgumentParser
from argparse import Namespace
from collections.abc import Callable
from pathlib import Path


def get_empty_directories(root_dir: Path, empty_files: bool = False) -> list[Path]:
    result = []

    dirs = [path for path in root_dir.iterdir() if path.is_dir()]
    if not dirs:
        files = [path for path in root_dir.iterdir() if path.is_file()]
        if not files:
            result.append(root_dir)
        elif empty_files:
            files_size = sum(file.stat().st_size for file in files)
            if not files_size:
                result.append(root_dir)

    for child in dirs:
        result.extend(get_empty_directories(child, empty_files))

    return result


def print_dirs(dirs: list[Path]) -> None:
    print(*dirs, sep="\n")


def remove_dirs(dirs: list[Path]) -> None:
    actions = [f'remove "{path}"' for path in dirs]
    print(*actions, sep="\n")


Action = Callable[[list[Path]], None]


def get_action(name: str) -> Action:
    actions = {"print": print_dirs, "remove": remove_dirs}

    return actions[name] if name in actions else print_dirs


def parse_options() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-r", "--root-dir", type=Path, required=True, help="root directory ")
    parser.add_argument("-f", "--empty-files", type=bool, default=False, help="treat empty files as absent.")
    parser.add_argument(
        "-a",
        "--action",
        type=str,
        default="print",
        help="action will be performed for each empty directory:\n" "\tprint (default)" "\tremove",
    )

    return parser.parse_args()


def cli() -> None:
    options = parse_options()

    root_dir = options.root_dir.absolute()
    if not root_dir.exists():
        print("the root directory is not set or doesn't exists")

    empty_dirs = get_empty_directories(root_dir, options.empty_files)
    action = get_action(options.action)
    action(empty_dirs)
