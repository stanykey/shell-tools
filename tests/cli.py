from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest import main
from unittest.mock import patch

from click.testing import CliRunner

from shell_tools.cli import discover_empty_dirs
from shell_tools.cli import generate_file
from shell_tools.cli import pretty_date
from shell_tools.cli import sync_repos
from shell_tools.cli import update_python_packages


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

    def test_discover_empty_dirs_remove_deletes_directories(self) -> None:
        with TemporaryDirectory() as root_dir_name:
            root_dir = Path(root_dir_name)
            empty_dir = root_dir / "empty"
            empty_dir.mkdir()

            result = self.runner.invoke(discover_empty_dirs, [str(root_dir), "--remove"])

            self.assertEqual(0, result.exit_code)
            self.assertFalse(empty_dir.exists())
            self.assertIn("Removing", result.output)

    def test_generate_file_creates_expected_output_file(self) -> None:
        with TemporaryDirectory() as dir_name:
            output_path = Path(dir_name) / "sample.bin"

            result = self.runner.invoke(generate_file, [str(output_path), "--size", "1kb", "--line-size", "32"])

            self.assertEqual(0, result.exit_code)
            self.assertTrue(output_path.exists())
            self.assertGreaterEqual(output_path.stat().st_size, 1024)

    def test_generate_file_with_invalid_size_keeps_exit_zero(self) -> None:
        with TemporaryDirectory() as dir_name:
            output_path = Path(dir_name) / "sample.bin"

            result = self.runner.invoke(generate_file, [str(output_path), "--size", "11zb"])

            self.assertEqual(0, result.exit_code)
            self.assertFalse(output_path.exists())
            self.assertIn("Invalid file size", result.output)

    def test_pretty_date_default_timestamp_exit_zero(self) -> None:
        result = self.runner.invoke(pretty_date, [])

        self.assertEqual(0, result.exit_code)
        self.assertTrue(result.output.strip())

    def test_pretty_date_with_invalid_timestamp_returns_non_zero(self) -> None:
        result = self.runner.invoke(pretty_date, ["1e20"])

        self.assertEqual(1, result.exit_code)
        self.assertIn("Error:", result.output)

    def test_sync_repos_prints_synced_repositories(self) -> None:
        with TemporaryDirectory() as root_dir_name:
            root_dir = Path(root_dir_name)
            repo_one = root_dir / "repo-one"
            repo_two = root_dir / "repo-two"
            repo_one.mkdir()
            repo_two.mkdir()

            with (
                patch("shell_tools.cli.find_repositories", return_value=[repo_one, repo_two]),
                patch("shell_tools.cli.update_repository", return_value=[]),
            ):
                result = self.runner.invoke(sync_repos, [str(root_dir)], input="\n")

            self.assertEqual(0, result.exit_code)
            self.assertIn("Synced: repo-one", result.output)
            self.assertIn("Synced: repo-two", result.output)

    def test_update_python_packages_uses_active_interpreter(self) -> None:
        with (
            patch("shell_tools.cli.system", return_value="Windows"),
            patch("shell_tools.cli.executable", "C:/Python/python.exe"),
            patch(
                "shell_tools.cli.run",
                side_effect=[
                    SimpleNamespace(stdout='[{"name":"pip"},{"name":"ruff"}]'),
                    SimpleNamespace(stdout=""),
                    SimpleNamespace(stdout=""),
                ],
            ) as run_mock,
        ):
            result = self.runner.invoke(update_python_packages, ["--all"])

        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            [
                ["C:/Python/python.exe", "-m", "pip", "list", "--format=json", "--disable-pip-version-check"],
                ["C:/Python/python.exe", "-m", "pip", "install", "--upgrade", "pip"],
                ["C:/Python/python.exe", "-m", "pip", "install", "--upgrade", "ruff"],
            ],
            [call.args[0] for call in run_mock.call_args_list],
        )


if __name__ == "__main__":
    main()
