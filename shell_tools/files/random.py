from pathlib import Path
from random import choice
from string import ascii_uppercase
from string import digits


def make_trash_string(size: int = 1024, allowed_chars: str = ascii_uppercase + digits) -> str:
    return "".join(choice(allowed_chars) for _ in range(size))


def make_random_file(path: Path, size: int, line_length: int = 1024) -> None:
    with open(path, "w") as file:
        full_rows_count, remains = divmod(size, line_length)
        for _ in range(full_rows_count):
            generated_line = make_trash_string(line_length) + "\n"
            file.write(generated_line)

        if remains:
            generated_line = make_trash_string(remains) + "\n"
            file.write(generated_line)
