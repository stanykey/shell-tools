from pathlib import Path
from random import choice
from re import IGNORECASE
from re import search
from string import ascii_uppercase
from string import digits
from sys import argv

from click import command
from click import option


def generate_random_string(size: int = 1024, allowed_chars: str = ascii_uppercase + digits) -> str:
    return "".join(choice(allowed_chars) for _ in range(size))


def generate_file(path: Path, size: int, line_length: int = 1024) -> None:
    with open(path, "w") as file:
        full_rows_count, remains = divmod(size, line_length)
        for _ in range(full_rows_count):
            generated_line = generate_random_string(line_length) + "\n"
            file.write(generated_line)

        if remains:
            generated_line = generate_random_string(remains) + "\n"
            file.write(generated_line)


def determine_file_size(size_string: str) -> int:
    multiplier = {"gb": 1024 * 1024 * 1024, "mb": 1024 * 1024, "kb": 1024}

    result = search(r"(?P<number>^\d+\.?\d+)(?P<multiplier>gb|mb|kb$)?", size_string, IGNORECASE)
    if result:
        number = float(result.group("number"))
        ratio = 1 if not result.group("multiplier") else multiplier[result.group("multiplier").lower()]
        return int(number * ratio)
    return 0


def default_file_location() -> Path:
    return Path("generated-file.txt").absolute()


def get_program_name() -> str:
    return Path(argv[0]).stem


@command()
@option("--path", type=Path, default=default_file_location(), help="Location for generated file.")
@option("--size", type=str, default="10mb", help="Required file size in bytes (optional suffixes: kb, mb, gb).")
@option("--line-size", type=int, default=64, help="Length of line/chunk.")
def cli(path: Path, size: str, line_size: int) -> None:
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
    generate_file(path, file_size, line_size)
    print("The generation is finished.")
