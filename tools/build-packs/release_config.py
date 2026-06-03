#!/usr/bin/env python3
from __future__ import annotations


VERSION = "2026.06.03"
CREATED_AT = "2026-06-03T00:00:00Z"
MIN_APP_VERSION = "1.2.0"
REPOSITORY = "huarangmeng/vocabulary-packs"
RELEASE_TITLE_PREFIX = "Vocabulary Trainpacks"
DEFAULT_RELEASE_NOTES = "V2 official speaking-action packs with dynamic daily queue metadata and stress-aware PackVerified pronunciation references."

TAG = f"trainpack-{VERSION}"


def version_to_zip_timestamp(version: str) -> tuple[int, int, int, int, int, int]:
    year_text, month_text, day_text = version.split(".")
    return int(year_text), int(month_text), int(day_text), 0, 0, 0


ZIP_TIMESTAMP = version_to_zip_timestamp(VERSION)


def release_title() -> str:
    return f"{RELEASE_TITLE_PREFIX} {VERSION}"
