from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest import main

from click.testing import CliRunner

from shell_tools.cli import discover_empty_dirs


class CliTestCase(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_discover_empty_dirs_prints_empty_directories(self) -> None:
        with TemporaryDirectory() as root_dir_name:
            root_dir = Path(root_dir_name)
            empty_dir = root_dir / "empty"
            empty_dir.mkdir()

            result = self.runner.invoke(discover_empty_dirs, [str(root_dir)])

            self.assertEqual(0, result.exit_code)
            self.assertIn(str(empty_dir), result.output)

    def test_discover_empty_dirs_returns_error_for_invalid_root(self) -> None:
        with TemporaryDirectory() as root_dir_name:
            missing_path = Path(root_dir_name) / "missing"

            result = self.runner.invoke(discover_empty_dirs, [str(missing_path)])

            self.assertEqual(1, result.exit_code)
            self.assertIn("does not exist or is not a directory", result.output)


if __name__ == "__main__":
    main()
