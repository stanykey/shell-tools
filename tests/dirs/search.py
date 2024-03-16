from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest import main

from shell_tools.dirs.search import find_empty_dirs


class SearchTestCase(TestCase):
    def test_find_empty_dirs(self) -> None:
        with TemporaryDirectory() as dir_name:
            root = Path(dir_name)
            result = find_empty_dirs(root)
            self.assertEqual(1, len(result))
            self.assertEqual(root, result[0])

            (root / "one").mkdir()
            (root / "two").mkdir()
            result = find_empty_dirs(root)
            self.assertEqual(2, len(result))
            self.assertTrue(all(child.parent.stem == root.stem for child in result))

            file_path = root / "one" / "file"
            file_path.touch()
            result = find_empty_dirs(root)
            self.assertEqual(1, len(result))
            self.assertEqual("two", result[0].stem)
            self.assertEqual(2, len(find_empty_dirs(root, ignore_empty_files=True)))

            file_path.write_bytes(b"test data")
            self.assertEqual(1, len(find_empty_dirs(root, ignore_empty_files=True)))


if __name__ == "__main__":
    main()
