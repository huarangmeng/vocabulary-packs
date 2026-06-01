#!/usr/bin/env python3
from __future__ import annotations

import shlex
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_PACKS_DIR = ROOT / "tools" / "build-packs"
if str(BUILD_PACKS_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_PACKS_DIR))

from release_config import DEFAULT_RELEASE_NOTES, REPOSITORY, TAG, release_title  # noqa: E402
from trainpack_builder import OUTPUT_DIR  # noqa: E402


def _asset_paths() -> list[Path]:
    trainpacks = sorted(OUTPUT_DIR.glob("*.trainpack"))
    return trainpacks + [OUTPUT_DIR / "latest.json", OUTPUT_DIR / "latest.json.sha256"]


def _quote(path: Path | str) -> str:
    if isinstance(path, Path):
        try:
            path = path.relative_to(ROOT)
        except ValueError:
            path = path
    return shlex.quote(str(path))


def format_release_create_command() -> str:
    assets = " \\\n  ".join(_quote(path) for path in _asset_paths())
    return (
        f"gh release create {shlex.quote(TAG)} \\\n"
        f"  --repo {shlex.quote(REPOSITORY)} \\\n"
        f"  --title {_quote(release_title())} \\\n"
        f"  --notes {_quote(DEFAULT_RELEASE_NOTES)} \\\n"
        f"  {assets}"
    )


def format_release_upload_command() -> str:
    assets = " \\\n  ".join(_quote(path) for path in _asset_paths())
    return (
        f"gh release upload {shlex.quote(TAG)} \\\n"
        f"  --repo {shlex.quote(REPOSITORY)} \\\n"
        f"  {assets} \\\n"
        f"  --clobber"
    )


def print_release_commands() -> None:
    print("gh release create:")
    print(format_release_create_command())
    print()
    print("gh release upload:")
    print(format_release_upload_command())


def main() -> None:
    print_release_commands()


if __name__ == "__main__":
    main()
