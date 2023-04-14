from pathlib import Path
from random import choice
from string import ascii_uppercase
from string import digits
from typing import TextIO


def make_trash_string(size: int = 1024, allowed_chars: str = ascii_uppercase + digits) -> str:
    """Make a string of `size` from the set of `allowed_chars`."""
    return "".join(choice(allowed_chars) for _ in range(size))


def write_random_data(io: TextIO, size: int, chunk_size: int = 1024) -> None:
    """Write random data into `io`-object in the amount equal to `size`."""
    full_rows_count, remains = divmod(size, chunk_size)
    for _ in range(full_rows_count):
        generated_line = make_trash_string(chunk_size - 1) + "\n"
        io.write(generated_line)

    if remains:
        generated_line = make_trash_string(remains - 1) + "\n"
        io.write(generated_line)


def make_random_file(path: Path, size: int, line_length: int = 1024) -> None:
    """Write random data to the `file` in the amount equal to `size`."""
    with open(path, "w") as file:
        write_random_data(file, size, line_length)
