#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from trainpack_builder import build_from_content_path, discover_content_paths


def _resolve_content_paths(argv: list[str]) -> list[Path]:
    if not argv:
        return discover_content_paths()

    paths: list[Path] = []
    for raw in argv:
        path = Path(raw)
        if not path.is_absolute():
            path = Path.cwd() / path
        if path.is_dir():
            paths.extend(sorted(path.glob("*.json")))
        else:
            paths.append(path)
    return sorted(paths)


def main() -> None:
    paths = _resolve_content_paths(sys.argv[1:])
    if not paths:
        raise SystemExit("No content pack JSON files found.")

    for path in paths:
        result = build_from_content_path(path)
        print(f"{path.name} -> {result.package_path.name}")
        print(f"  units={result.unit_count} items={result.item_count} size={result.size_bytes} sha256={result.sha256}")


if __name__ == "__main__":
    main()
