from argparse import ArgumentParser
from argparse import Namespace
from pathlib import Path
from random import choice
from re import IGNORECASE
from re import search
from string import ascii_uppercase
from string import digits


def get_file_size_in_bytes(size_string: str) -> int:
    multiplier = {"gb": 1024 * 1024 * 1024, "mb": 1024 * 1024, "kb": 1024}

    result = search(r"(?P<number>^\d+\.?\d+)(?P<multiplier>gb|mb|kb$)?", size_string, IGNORECASE)
    if result:
        number = float(result.group("number"))
        ratio = 1 if not result.group("multiplier") else multiplier[result.group("multiplier").lower()]
        return int(number * ratio)
    return 0


def generate_random_string(size: int = 1024, allowed_chars: str = ascii_uppercase + digits) -> str:
    return "".join(choice(allowed_chars) for _ in range(size))


def generate_file(path: Path, size: int, line_length: int = 1024) -> None:
    with open(path, "w") as file:
        for _ in range(size // line_length):
            generated_line = generate_random_string(line_length) + "\n"
            file.write(generated_line)


def default_file_location() -> Path:
    return Path("generated-file.txt").absolute()


def parse_options() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--file-path", "-fp", type=str, default=default_file_location(), help="Location for generated file."
    )
    parser.add_argument(
        "-fs",
        "--file-size",
        type=str,
        default="10Mb",
        help="Required file size in bytes. Note you can use one next suffixes [kb, mb, gb].",
    )
    parser.add_argument("-ls", "--line-size", type=int, default=100, help="Length of line/chunk.")

    return parser.parse_args()


def cli() -> None:
    options = parse_options()

    file_path = Path(options.file_path).absolute() if options.file_path else default_file_location()
    if not options.file_path:
        print("Option <file-path> is empty. The default value location will be used.")

    file_size = get_file_size_in_bytes(options.file_size)
    if not file_size:
        print(f"Invalid file size was requested (file-size={options.file_size}).")
        print(f'Use "{Path(__file__).name} -h" to see allowed options.')
    else:
        print(f'The file of {options.file_size} will be generated at "{file_path}".')
        generate_file(file_path, file_size, options.line_size)
        print("The generation is finished.")
