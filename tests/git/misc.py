from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest import main

from shell_tools.git.misc import find_repositories


class MiscTestCase(TestCase):
    def test_find_repositories_includes_root_repository(self) -> None:
        with TemporaryDirectory() as dir_name:
            root = Path(dir_name)
            (root / ".git").mkdir()

            repositories = find_repositories(root, recursive=False)

            self.assertEqual([root], repositories)

    def test_find_repositories_non_recursive_includes_direct_children_only(self) -> None:
        with TemporaryDirectory() as dir_name:
            root = Path(dir_name)
            (root / ".git").mkdir()

            direct = root / "direct-repo"
            (direct / ".git").mkdir(parents=True)

            nested = root / "group" / "nested-repo"
            (nested / ".git").mkdir(parents=True)

            repositories = find_repositories(root, recursive=False)

            self.assertCountEqual([root, direct], repositories)

    def test_find_repositories_recursive_includes_nested_repositories(self) -> None:
        with TemporaryDirectory() as dir_name:
            root = Path(dir_name)
            (root / ".git").mkdir()

            direct = root / "direct-repo"
            (direct / ".git").mkdir(parents=True)

            nested = root / "group" / "nested-repo"
            (nested / ".git").mkdir(parents=True)

            repositories = find_repositories(root, recursive=True)

            self.assertCountEqual([root, direct, nested], repositories)


if __name__ == "__main__":
    main()
