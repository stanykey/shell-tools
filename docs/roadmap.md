# Roadmap

This list focuses on fixes and reliability improvements that are currently needed.

## High Priority

- [x] Handle invalid root directory in `find-empty-dirs` with a non-zero exit path.
  - Current behavior only prints an error and continues.
- [ ] Remove blocking `input("Press Enter to exit...")` from `sync-repos`.
  - This breaks non-interactive usage (scripts/CI).
- [ ] Surface git command failures in `sync-repos`.
  - `execute_command` does not check return codes or stderr, so failed pulls can look successful.

## Medium Priority

- [x] Make package updates use the active interpreter consistently.
  - Replace direct `pip` calls with `python -m pip` in `update-python-packages`.
- [ ] Improve command output UX for `sync-repos`.
  - Show failed repos separately and summarize updated/skipped/failed counts.
- [x] Add tests for CLI command behavior and exit codes.
  - Added baseline command coverage in `tests/cli.py` for `discover_empty_dirs`, `generate_file`, `pretty_date`, and `sync_repos`.

## Low Priority

- [x] Align documentation and CLI naming consistently (`find-empty-dirs`).
- [x] Improve wording and grammar in user-facing messages.
