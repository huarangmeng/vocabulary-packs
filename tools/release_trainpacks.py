#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_PACKS_DIR = ROOT / "tools" / "build-packs"
if str(BUILD_PACKS_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_PACKS_DIR))

from build_core_chunks_pack import build as build_core_chunks_pack  # noqa: E402
from build_meeting_communication_pack import build as build_meeting_communication_pack  # noqa: E402
from build_small_talk_pack import build as build_small_talk_pack  # noqa: E402
from print_release_command import format_release_create_command, format_release_upload_command  # noqa: E402
from trainpack_builder import OUTPUT_DIR, write_catalog  # noqa: E402
from validate_trainpack import validate  # noqa: E402


def main() -> None:
    results = [
        build_core_chunks_pack(),
        build_small_talk_pack(),
        build_meeting_communication_pack(),
    ]
    catalog_path = write_catalog(results)
    for result in results:
        validate(result.package_path, catalog_path)

    print("Generated trainpacks:")
    for result in results:
        print(
            f"- {result.file_name} | units={result.unit_count} | "
            f"items={result.item_count} | size={result.size_bytes} | sha256={result.sha256}"
        )
    print(f"Catalog: {catalog_path}")
    print(f"Catalog checksum: {OUTPUT_DIR / 'latest.json.sha256'}")
    print("Validation: OK")
    print()
    print("gh release create:")
    print(format_release_create_command())
    print()
    print("gh release upload:")
    print(format_release_upload_command())


if __name__ == "__main__":
    main()
