from collections.abc import Callable
from io import StringIO
from itertools import repeat
from itertools import starmap
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import main
from unittest import TestCase

from shell_tools.files.random import make_random_file
from shell_tools.files.random import make_trash_string
from shell_tools.files.random import write_random_data


def repeat_func(func: Callable[..., Any], times: int, *args: Any) -> Any:
    """Repeat calls to func with specified arguments."""
    return starmap(func, repeat(args, times))


class RandomTestCase(TestCase):
    def test_make_trash_string(self) -> None:
        calls_count = 10
        values = set(repeat_func(make_trash_string, calls_count))
        self.assertEqual(calls_count, len(values))

        values = set(repeat_func(make_trash_string, calls_count, 10, "a"))
        self.assertEqual(1, len(values))

    def test_write_random_data(self) -> None:
        for expected_size in (16, 32, 64, 128, 256, 512, 1024, 2048, 4096):
            with StringIO() as buffer:
                write_random_data(buffer, expected_size, expected_size)

                content = buffer.getvalue()
                self.assertEqual(expected_size, len(content))

    def test_make_random_file(self) -> None:
        with TemporaryDirectory() as dir_name:
            root = Path(dir_name)
            expected_file_size = 4096
            expected_line_size = 256

            files = [root / "one", root / "two", root / "three"]
            for file in files:
                make_random_file(file, expected_file_size, expected_line_size)
                self.assertTrue(file.exists())
                self.assertTrue(file.is_file())
                self.assertTrue(expected_file_size <= file.stat().st_size)  # Windows use \r\n as line separator

            trash = {file.read_text(encoding="utf-8") for file in files}
            self.assertEqual(len(files), len(trash))


if __name__ == "__main__":
    main()
