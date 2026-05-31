#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any


ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ENTRY_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_PATTERN = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
FILE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-\d{4}\.\d{2}\.\d{2}\.vocabpack$")
ALLOWED_ENTRY_TYPES = {"WordOrPhrase", "Sentence", "Logic"}
PACKAGE_FILES = {"manifest.json", "entries.jsonl"}


def fail(message: str) -> None:
    raise ValueError(message)


def require_keys(obj: dict[str, Any], keys: set[str], label: str) -> None:
    missing = keys - obj.keys()
    extra = obj.keys() - keys
    if missing:
        fail(f"{label} missing keys: {sorted(missing)}")
    if extra:
        fail(f"{label} has extra keys: {sorted(extra)}")


def require_string(value: Any, label: str, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty string")
    if pattern and not pattern.match(value):
        fail(f"{label} has invalid format: {value}")
    return value


def require_int(value: Any, label: str, *, minimum: int = 1) -> int:
    if not isinstance(value, int) or value < minimum:
        fail(f"{label} must be an integer >= {minimum}")
    return value


def require_string_list(value: Any, label: str, *, min_items: int = 0) -> list[str]:
    if not isinstance(value, list) or len(value) < min_items:
        fail(f"{label} must be a list with at least {min_items} item(s)")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{label}[{index}] must be a non-empty string")
    return value


def validate_package_manifest(manifest: dict[str, Any]) -> None:
    require_keys(
        manifest,
        {"schemaVersion", "bookId", "bookVersion", "title", "description", "itemCount", "createdAt", "entryFile"},
        "package manifest",
    )
    if manifest["schemaVersion"] != 1:
        fail("package manifest schemaVersion must be 1")
    require_string(manifest["bookId"], "package manifest bookId", pattern=ID_PATTERN)
    require_string(manifest["bookVersion"], "package manifest bookVersion", pattern=VERSION_PATTERN)
    require_string(manifest["title"], "package manifest title")
    require_string(manifest["description"], "package manifest description")
    require_int(manifest["itemCount"], "package manifest itemCount")
    require_string(manifest["createdAt"], "package manifest createdAt", pattern=UTC_PATTERN)
    if manifest["entryFile"] != "entries.jsonl":
        fail("package manifest entryFile must be entries.jsonl")


def validate_entry(entry: dict[str, Any], expected_order: int, book_id: str) -> None:
    require_keys(
        entry,
        {
            "id",
            "order",
            "type",
            "englishText",
            "chinesePrompt",
            "partOfSpeech",
            "definitionEn",
            "exampleEn",
            "exampleZh",
            "synonyms",
            "wordFamily",
            "difficulty",
            "tags",
        },
        f"entry #{expected_order}",
    )
    entry_id = require_string(entry["id"], f"entry #{expected_order} id", pattern=ENTRY_ID_PATTERN)
    if not entry_id.startswith(f"{book_id}:"):
        fail(f"entry #{expected_order} id must start with {book_id}:")
    order = require_int(entry["order"], f"entry #{expected_order} order")
    if order != expected_order:
        fail(f"entry order must be continuous: expected {expected_order}, got {order}")
    if entry["type"] not in ALLOWED_ENTRY_TYPES:
        fail(f"entry #{expected_order} type is invalid: {entry['type']}")
    require_string(entry["englishText"], f"entry #{expected_order} englishText")
    require_string(entry["chinesePrompt"], f"entry #{expected_order} chinesePrompt")
    require_string(entry["partOfSpeech"], f"entry #{expected_order} partOfSpeech")
    require_string(entry["definitionEn"], f"entry #{expected_order} definitionEn")
    require_string(entry["exampleEn"], f"entry #{expected_order} exampleEn")
    require_string(entry["exampleZh"], f"entry #{expected_order} exampleZh")
    require_string_list(entry["synonyms"], f"entry #{expected_order} synonyms")
    require_string_list(entry["wordFamily"], f"entry #{expected_order} wordFamily")
    require_string(entry["difficulty"], f"entry #{expected_order} difficulty")
    require_string_list(entry["tags"], f"entry #{expected_order} tags", min_items=1)


def read_package(package_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not package_path.is_file():
        fail(f"package does not exist: {package_path}")
    with zipfile.ZipFile(package_path) as package:
        names = set(package.namelist())
        if names != PACKAGE_FILES:
            fail(f"package files must be exactly {sorted(PACKAGE_FILES)}, got {sorted(names)}")
        manifest = json.loads(package.read("manifest.json").decode("utf-8"))
        entries_text = package.read("entries.jsonl").decode("utf-8")
    if not isinstance(manifest, dict):
        fail("package manifest must be a JSON object")
    entries = []
    for line_number, line in enumerate(entries_text.splitlines(), start=1):
        if not line.strip():
            fail(f"entries.jsonl line {line_number} is blank")
        entry = json.loads(line)
        if not isinstance(entry, dict):
            fail(f"entries.jsonl line {line_number} must be a JSON object")
        entries.append(entry)
    return manifest, entries


def validate_catalog(catalog_path: Path, package_path: Path, package_manifest: dict[str, Any], entries: list[dict[str, Any]]) -> None:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(catalog, dict):
        fail("catalog must be a JSON object")
    require_keys(catalog, {"schemaVersion", "catalogVersion", "generatedAt", "minAppVersion", "books"}, "catalog")
    if catalog["schemaVersion"] != 1:
        fail("catalog schemaVersion must be 1")
    require_string(catalog["catalogVersion"], "catalog catalogVersion", pattern=VERSION_PATTERN)
    require_string(catalog["generatedAt"], "catalog generatedAt", pattern=UTC_PATTERN)
    require_string(catalog["minAppVersion"], "catalog minAppVersion")
    if not isinstance(catalog["books"], list) or not catalog["books"]:
        fail("catalog books must be a non-empty list")

    book_id = package_manifest["bookId"]
    book_version = package_manifest["bookVersion"]
    matches = [book for book in catalog["books"] if isinstance(book, dict) and book.get("id") == book_id and book.get("version") == book_version]
    if len(matches) != 1:
        fail(f"catalog must contain exactly one book for {book_id}@{book_version}")
    book = matches[0]
    require_keys(
        book,
        {"id", "title", "description", "version", "itemCount", "sizeBytes", "sha256", "fileName", "tags", "urls"},
        "catalog book",
    )
    require_string(book["id"], "catalog book id", pattern=ID_PATTERN)
    require_string(book["title"], "catalog book title")
    require_string(book["description"], "catalog book description")
    require_string(book["version"], "catalog book version", pattern=VERSION_PATTERN)
    require_int(book["itemCount"], "catalog book itemCount")
    require_int(book["sizeBytes"], "catalog book sizeBytes")
    require_string(book["sha256"], "catalog book sha256", pattern=SHA256_PATTERN)
    require_string(book["fileName"], "catalog book fileName", pattern=FILE_NAME_PATTERN)
    require_string_list(book["tags"], "catalog book tags", min_items=1)
    require_string_list(book["urls"], "catalog book urls", min_items=1)

    if book["title"] != package_manifest["title"]:
        fail("catalog book title must match package manifest title")
    if book["itemCount"] != len(entries) or book["itemCount"] != package_manifest["itemCount"]:
        fail("catalog book itemCount must match package manifest and actual entries")
    if book["sizeBytes"] != package_path.stat().st_size:
        fail("catalog book sizeBytes must match package file size")
    digest = hashlib.sha256(package_path.read_bytes()).hexdigest()
    if book["sha256"] != digest:
        fail("catalog book sha256 must match package file")
    if book["fileName"] != package_path.name:
        fail("catalog book fileName must match package file name")
    if not all(url.startswith("https://") for url in book["urls"]):
        fail("catalog book urls must all be https")


def validate(package_path: Path, catalog_path: Path) -> None:
    package_manifest, entries = read_package(package_path)
    validate_package_manifest(package_manifest)
    if package_manifest["itemCount"] != len(entries):
        fail("package manifest itemCount must match actual entries")

    seen_ids = set()
    for index, entry in enumerate(entries, start=1):
        validate_entry(entry, index, package_manifest["bookId"])
        if entry["id"] in seen_ids:
            fail(f"duplicate entry id: {entry['id']}")
        seen_ids.add(entry["id"])

    validate_catalog(catalog_path, package_path, package_manifest, entries)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python3 tools/validate_vocabpack.py <package.vocabpack> <catalog.json>", file=sys.stderr)
        return 2
    try:
        validate(Path(argv[1]), Path(argv[2]))
    except Exception as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {argv[1]} against {argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
