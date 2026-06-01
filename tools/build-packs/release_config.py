#!/usr/bin/env python3
from __future__ import annotations


VERSION = "2026.06.02"
CREATED_AT = "2026-06-02T00:00:00Z"
MIN_APP_VERSION = "1.1.0"
REPOSITORY = "huarangmeng/vocabulary-packs"
RELEASE_TITLE_PREFIX = "Vocabulary Trainpacks"
DEFAULT_RELEASE_NOTES = "Initial official speaking trainpacks."

TAG = f"trainpack-{VERSION}"


def version_to_zip_timestamp(version: str) -> tuple[int, int, int, int, int, int]:
    year_text, month_text, day_text = version.split(".")
    return int(year_text), int(month_text), int(day_text), 0, 0, 0


ZIP_TIMESTAMP = version_to_zip_timestamp(VERSION)


def release_title() -> str:
    return f"{RELEASE_TITLE_PREFIX} {VERSION}"
