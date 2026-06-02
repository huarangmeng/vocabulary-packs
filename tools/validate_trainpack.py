#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
UNIT_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*$")
ITEM_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*:item-\d{4}$")
VERSION_PATTERN = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
FILE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-\d{4}\.\d{2}\.\d{2}\.trainpack$")
ALLOWED_PACK_TYPES = {"CoreChunks", "Scenario", "Function", "Repair", "PronunciationFocus", "ExamSpeaking"}
ALLOWED_TRAINING_MODES = {"Recall", "Shadow", "Respond", "Repair"}
ALLOWED_ITEM_TYPES = {"Chunk", "SentencePattern", "DialogueTurn", "RepairStrategy", "PronunciationTarget"}
ALLOWED_REGISTERS = {"Casual", "Neutral", "Formal"}
ALLOWED_LEVELS = {"Low", "Medium", "High"}
ALLOWED_PRONUNCIATION_DIALECTS = {"en-US", "en-GB"}
ALLOWED_PRONUNCIATION_TARGET_TYPES = {"EnglishText", "Variant", "PronunciationTarget"}
ALLOWED_PRONUNCIATION_SOURCES = {"PackVerifiedOnline"}
ALLOWED_WORD_PRONUNCIATION_SOURCES = {"CuratedLexicon", "DictionaryApi", "Cmudict", "InflectionRule"}
ALLOWED_PRONUNCIATION_REVIEW_STATUS = {"PackVerified"}
ALLOWED_TASK_ROLES = {"WarmUp", "Main", "Challenge", "Review"}
ALLOWED_CORRECTION_FOCUS = {
    "Naturalness",
    "SpokenRegister",
    "Completeness",
    "Clarification",
    "TurnTaking",
    "Softening",
    "Pronunciation",
    "ScenarioFit",
    "Fluency",
    "Decision",
    "FollowUp",
    "Repair",
}
PACKAGE_FILES = {"manifest.json", "units.json", "items.jsonl", "pronunciation_references.jsonl"}
ITEM_REQUIRED_KEYS = {
    "id",
    "unitId",
    "order",
    "type",
    "englishText",
    "chinesePrompt",
    "variants",
    "notes",
    "pronunciationTargets",
    "commonMistakes",
    "tags",
}
ITEM_OPTIONAL_KEYS = {
    "contextText",
    "responseRole",
    "repairType",
    "slots",
    "sampleOutputs",
    "focusText",
    "focusType",
}
CATALOG_PACK_REQUIRED_KEYS = {
    "id",
    "title",
    "description",
    "packType",
    "version",
    "levelHint",
    "unitCount",
    "itemCount",
    "pronunciationReferenceCount",
    "referenceCoverage",
    "verifiedCoverage",
    "estimatedMinutes",
    "sizeBytes",
    "sha256",
    "fileName",
    "tags",
    "trainingModes",
    "urls",
}
CATALOG_PACK_OPTIONAL_KEYS = {
    "seriesId",
    "seriesTitle",
    "seriesOrder",
    "learningPath",
    "prerequisitePackIds",
    "recommendedNextPackIds",
    "companionPackIds",
}


def fail(message: str) -> None:
    raise ValueError(message)


def require_exact_keys(obj: dict[str, Any], keys: set[str], label: str) -> None:
    missing = keys - obj.keys()
    extra = obj.keys() - keys
    if missing:
        fail(f"{label} missing keys: {sorted(missing)}")
    if extra:
        fail(f"{label} has extra keys: {sorted(extra)}")


def require_allowed_keys(obj: dict[str, Any], required: set[str], optional: set[str], label: str) -> None:
    missing = required - obj.keys()
    extra = obj.keys() - (required | optional)
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


def validate_manifest(manifest: dict[str, Any]) -> None:
    require_exact_keys(
        manifest,
        {
            "schemaVersion",
            "packId",
            "packVersion",
            "title",
            "description",
            "packType",
            "locale",
            "unitCount",
            "itemCount",
            "pronunciationReferenceCount",
            "referenceCoverage",
            "verifiedCoverage",
            "estimatedMinutes",
            "createdAt",
            "unitsFile",
            "itemsFile",
            "pronunciationReferencesFile",
        },
        "trainpack manifest",
    )
    if manifest["schemaVersion"] != 1:
        fail("trainpack manifest schemaVersion must be 1")
    require_string(manifest["packId"], "trainpack manifest packId", pattern=ID_PATTERN)
    require_string(manifest["packVersion"], "trainpack manifest packVersion", pattern=VERSION_PATTERN)
    require_string(manifest["title"], "trainpack manifest title")
    require_string(manifest["description"], "trainpack manifest description")
    if manifest["packType"] not in ALLOWED_PACK_TYPES:
        fail(f"trainpack manifest packType is invalid: {manifest['packType']}")
    require_string(manifest["locale"], "trainpack manifest locale", pattern=re.compile(r"^[a-z]{2}-[A-Z]{2}$"))
    require_int(manifest["unitCount"], "trainpack manifest unitCount")
    require_int(manifest["itemCount"], "trainpack manifest itemCount")
    require_int(manifest["pronunciationReferenceCount"], "trainpack manifest pronunciationReferenceCount")
    require_float_ratio(manifest["referenceCoverage"], "trainpack manifest referenceCoverage")
    require_float_ratio(manifest["verifiedCoverage"], "trainpack manifest verifiedCoverage")
    require_int(manifest["estimatedMinutes"], "trainpack manifest estimatedMinutes")
    require_string(manifest["createdAt"], "trainpack manifest createdAt", pattern=UTC_PATTERN)
    if manifest["unitsFile"] != "units.json":
        fail("trainpack manifest unitsFile must be units.json")
    if manifest["itemsFile"] != "items.jsonl":
        fail("trainpack manifest itemsFile must be items.jsonl")
    if manifest["pronunciationReferencesFile"] != "pronunciation_references.jsonl":
        fail("trainpack manifest pronunciationReferencesFile must be pronunciation_references.jsonl")


def validate_unit(unit: dict[str, Any], expected_order: int, pack_id: str) -> None:
    require_exact_keys(
        unit,
        {
            "unitId",
            "order",
            "title",
            "communicativeGoal",
            "scene",
            "register",
            "difficulty",
            "tags",
            "activationPrompts",
            "itemIds",
            "pronunciationFocus",
            "taskHints",
        },
        f"unit #{expected_order}",
    )
    unit_id = require_string(unit["unitId"], f"unit #{expected_order} unitId", pattern=UNIT_ID_PATTERN)
    if not unit_id.startswith(f"{pack_id}:"):
        fail(f"unit #{expected_order} unitId must start with {pack_id}:")
    order = require_int(unit["order"], f"unit #{expected_order} order")
    if order != expected_order:
        fail(f"unit order must be continuous: expected {expected_order}, got {order}")
    require_string(unit["title"], f"unit #{expected_order} title")
    require_string(unit["communicativeGoal"], f"unit #{expected_order} communicativeGoal")
    require_string(unit["scene"], f"unit #{expected_order} scene")
    if unit["register"] not in ALLOWED_REGISTERS:
        fail(f"unit #{expected_order} register is invalid: {unit['register']}")
    difficulty = unit["difficulty"]
    if not isinstance(difficulty, dict):
        fail(f"unit #{expected_order} difficulty must be an object")
    require_exact_keys(difficulty, {"lexical", "interactionPressure", "pronunciationRisk"}, f"unit #{expected_order} difficulty")
    require_string(difficulty["lexical"], f"unit #{expected_order} difficulty.lexical")
    if difficulty["interactionPressure"] not in ALLOWED_LEVELS:
        fail(f"unit #{expected_order} difficulty.interactionPressure is invalid")
    if difficulty["pronunciationRisk"] not in ALLOWED_LEVELS:
        fail(f"unit #{expected_order} difficulty.pronunciationRisk is invalid")
    require_string_list(unit["tags"], f"unit #{expected_order} tags", min_items=1)
    item_ids = require_string_list(unit["itemIds"], f"unit #{expected_order} itemIds", min_items=1)
    for item_id in item_ids:
        if not ITEM_ID_PATTERN.match(item_id):
            fail(f"unit #{expected_order} itemIds contains invalid item id: {item_id}")
    require_string_list(unit["activationPrompts"], f"unit #{expected_order} activationPrompts", min_items=1)
    require_string_list(unit["pronunciationFocus"], f"unit #{expected_order} pronunciationFocus")
    validate_task_hints(unit["taskHints"], f"unit #{expected_order} taskHints")


def validate_task_hints(task_hints: Any, label: str) -> None:
    if not isinstance(task_hints, dict):
        fail(f"{label} must be an object")
    require_exact_keys(
        task_hints,
        {
            "defaultRole",
            "successCriteria",
            "correctionFocus",
            "retryPrompts",
            "variantPrompts",
        },
        label,
    )
    if task_hints["defaultRole"] not in ALLOWED_TASK_ROLES:
        fail(f"{label}.defaultRole is invalid: {task_hints['defaultRole']}")
    require_string_list(task_hints["successCriteria"], f"{label}.successCriteria", min_items=1)
    correction_focus = require_string_list(task_hints["correctionFocus"], f"{label}.correctionFocus", min_items=1)
    for focus in correction_focus:
        if focus not in ALLOWED_CORRECTION_FOCUS:
            fail(f"{label}.correctionFocus contains invalid value: {focus}")
    require_string_list(task_hints["retryPrompts"], f"{label}.retryPrompts", min_items=1)
    require_string_list(task_hints["variantPrompts"], f"{label}.variantPrompts", min_items=1)


def validate_item(item: dict[str, Any], expected_pack_id: str, item_index: int) -> None:
    require_allowed_keys(item, ITEM_REQUIRED_KEYS, ITEM_OPTIONAL_KEYS, f"item #{item_index}")
    item_id = require_string(item["id"], f"item #{item_index} id", pattern=ITEM_ID_PATTERN)
    if not item_id.startswith(f"{expected_pack_id}:"):
        fail(f"item #{item_index} id must start with {expected_pack_id}:")
    unit_id = require_string(item["unitId"], f"item #{item_index} unitId", pattern=UNIT_ID_PATTERN)
    if not unit_id.startswith(f"{expected_pack_id}:"):
        fail(f"item #{item_index} unitId must start with {expected_pack_id}:")
    require_int(item["order"], f"item #{item_index} order")
    if item["type"] not in ALLOWED_ITEM_TYPES:
        fail(f"item #{item_index} type is invalid: {item['type']}")
    require_string(item["englishText"], f"item #{item_index} englishText")
    require_string(item["chinesePrompt"], f"item #{item_index} chinesePrompt")
    require_string_list(item["variants"], f"item #{item_index} variants")
    require_string_list(item["notes"], f"item #{item_index} notes")
    require_string_list(item["pronunciationTargets"], f"item #{item_index} pronunciationTargets")
    require_string_list(item["commonMistakes"], f"item #{item_index} commonMistakes")
    require_string_list(item["tags"], f"item #{item_index} tags", min_items=1)
    for optional_key in ITEM_OPTIONAL_KEYS:
        if optional_key in item:
            if optional_key in {"slots", "sampleOutputs"}:
                require_string_list(item[optional_key], f"item #{item_index} {optional_key}")
            else:
                require_string(item[optional_key], f"item #{item_index} {optional_key}")


def require_float_ratio(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or value < 0 or value > 1:
        fail(f"{label} must be a number between 0 and 1")
    return float(value)


def validate_pronunciation_reference(
    reference: dict[str, Any],
    expected_pack_id: str,
    reference_index: int,
    item_ids: set[str],
    unit_ids: set[str],
) -> None:
    require_exact_keys(
        reference,
        {
            "id",
            "itemId",
            "unitId",
            "unitTitle",
            "targetType",
            "targetText",
            "dialect",
            "phonemes",
            "words",
            "source",
            "confidence",
            "reviewStatus",
            "provenance",
        },
        f"pronunciation reference #{reference_index}",
    )
    reference_id = require_string(reference["id"], f"pronunciation reference #{reference_index} id")
    if not reference_id.startswith(f"{expected_pack_id}:pron-"):
        fail(f"pronunciation reference #{reference_index} id must start with {expected_pack_id}:pron-")
    item_id = require_string(reference["itemId"], f"pronunciation reference #{reference_index} itemId", pattern=ITEM_ID_PATTERN)
    if item_id not in item_ids:
        fail(f"pronunciation reference {reference_id} references unknown itemId: {item_id}")
    unit_id = require_string(reference["unitId"], f"pronunciation reference #{reference_index} unitId", pattern=UNIT_ID_PATTERN)
    if unit_id not in unit_ids:
        fail(f"pronunciation reference {reference_id} references unknown unitId: {unit_id}")
    require_string(reference["unitTitle"], f"pronunciation reference #{reference_index} unitTitle")
    if reference["targetType"] not in ALLOWED_PRONUNCIATION_TARGET_TYPES:
        fail(f"pronunciation reference {reference_id} has invalid targetType: {reference['targetType']}")
    require_string(reference["targetText"], f"pronunciation reference #{reference_index} targetText")
    if reference["dialect"] not in ALLOWED_PRONUNCIATION_DIALECTS:
        fail(f"pronunciation reference {reference_id} has invalid dialect: {reference['dialect']}")
    require_string_list(reference["phonemes"], f"pronunciation reference #{reference_index} phonemes", min_items=1)
    words = reference["words"]
    if not isinstance(words, list) or not words:
        fail(f"pronunciation reference {reference_id} words must be a non-empty list")
    flattened: list[str] = []
    for word_index, word in enumerate(words, start=1):
        if not isinstance(word, dict):
            fail(f"pronunciation reference {reference_id} word #{word_index} must be an object")
        require_exact_keys(
            word,
            {"text", "phonemes", "source", "confidence", "sourceUrl", "license", "dialect"},
            f"pronunciation reference {reference_id} word #{word_index}",
        )
        require_string(word["text"], f"pronunciation reference {reference_id} word #{word_index} text")
        flattened.extend(require_string_list(word["phonemes"], f"pronunciation reference {reference_id} word #{word_index} phonemes", min_items=1))
        if word["source"] not in ALLOWED_WORD_PRONUNCIATION_SOURCES:
            fail(f"pronunciation reference {reference_id} word #{word_index} source is invalid: {word['source']}")
        if word["confidence"] not in ALLOWED_LEVELS:
            fail(f"pronunciation reference {reference_id} word #{word_index} confidence is invalid: {word['confidence']}")
        require_string(word["sourceUrl"], f"pronunciation reference {reference_id} word #{word_index} sourceUrl")
        require_string(word["license"], f"pronunciation reference {reference_id} word #{word_index} license")
        if word["dialect"] not in ALLOWED_PRONUNCIATION_DIALECTS:
            fail(f"pronunciation reference {reference_id} word #{word_index} dialect is invalid: {word['dialect']}")
    if flattened != reference["phonemes"]:
        fail(f"pronunciation reference {reference_id} phonemes must equal flattened word phonemes")
    if reference["source"] not in ALLOWED_PRONUNCIATION_SOURCES:
        fail(f"pronunciation reference {reference_id} source is invalid: {reference['source']}")
    if reference["confidence"] not in ALLOWED_LEVELS:
        fail(f"pronunciation reference {reference_id} confidence is invalid: {reference['confidence']}")
    if reference["reviewStatus"] not in ALLOWED_PRONUNCIATION_REVIEW_STATUS:
        fail(f"pronunciation reference {reference_id} reviewStatus is invalid: {reference['reviewStatus']}")
    provenance = reference["provenance"]
    if not isinstance(provenance, list) or not provenance:
        fail(f"pronunciation reference {reference_id} provenance must be a non-empty list")
    for provenance_index, item in enumerate(provenance, start=1):
        if not isinstance(item, dict):
            fail(f"pronunciation reference {reference_id} provenance #{provenance_index} must be an object")
        require_exact_keys(item, {"source", "sourceUrl", "license"}, f"pronunciation reference {reference_id} provenance #{provenance_index}")
        require_string(item["source"], f"pronunciation reference {reference_id} provenance #{provenance_index} source")
        require_string(item["sourceUrl"], f"pronunciation reference {reference_id} provenance #{provenance_index} sourceUrl")
        require_string(item["license"], f"pronunciation reference {reference_id} provenance #{provenance_index} license")


def read_package(package_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if not package_path.is_file():
        fail(f"package does not exist: {package_path}")
    with zipfile.ZipFile(package_path) as package:
        names = set(package.namelist())
        if names != PACKAGE_FILES:
            fail(f"package files must be exactly {sorted(PACKAGE_FILES)}, got {sorted(names)}")
        manifest = json.loads(package.read("manifest.json").decode("utf-8"))
        units = json.loads(package.read("units.json").decode("utf-8"))
        items_text = package.read("items.jsonl").decode("utf-8")
        pronunciation_references_text = package.read("pronunciation_references.jsonl").decode("utf-8")
    if not isinstance(manifest, dict):
        fail("package manifest must be a JSON object")
    if not isinstance(units, list):
        fail("units.json must be a JSON array")
    items: list[dict[str, Any]] = []
    for line_number, line in enumerate(items_text.splitlines(), start=1):
        if not line.strip():
            fail(f"items.jsonl line {line_number} is blank")
        item = json.loads(line)
        if not isinstance(item, dict):
            fail(f"items.jsonl line {line_number} must be a JSON object")
        items.append(item)
    pronunciation_references: list[dict[str, Any]] = []
    for line_number, line in enumerate(pronunciation_references_text.splitlines(), start=1):
        if not line.strip():
            fail(f"pronunciation_references.jsonl line {line_number} is blank")
        reference = json.loads(line)
        if not isinstance(reference, dict):
            fail(f"pronunciation_references.jsonl line {line_number} must be a JSON object")
        pronunciation_references.append(reference)
    return manifest, units, items, pronunciation_references


def validate_catalog(
    catalog_path: Path,
    package_path: Path,
    manifest: dict[str, Any],
    units: list[dict[str, Any]],
    items: list[dict[str, Any]],
    pronunciation_references: list[dict[str, Any]],
) -> None:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(catalog, dict):
        fail("catalog must be a JSON object")
    require_exact_keys(catalog, {"schemaVersion", "catalogVersion", "generatedAt", "minAppVersion", "packs"}, "catalog")
    if catalog["schemaVersion"] != 1:
        fail("catalog schemaVersion must be 1")
    require_string(catalog["catalogVersion"], "catalog catalogVersion", pattern=VERSION_PATTERN)
    require_string(catalog["generatedAt"], "catalog generatedAt", pattern=UTC_PATTERN)
    require_string(catalog["minAppVersion"], "catalog minAppVersion")
    if not isinstance(catalog["packs"], list) or not catalog["packs"]:
        fail("catalog packs must be a non-empty list")

    pack_id = manifest["packId"]
    pack_version = manifest["packVersion"]
    matches = [pack for pack in catalog["packs"] if isinstance(pack, dict) and pack.get("id") == pack_id and pack.get("version") == pack_version]
    if len(matches) != 1:
        fail(f"catalog must contain exactly one pack for {pack_id}@{pack_version}")
    pack = matches[0]
    require_allowed_keys(pack, CATALOG_PACK_REQUIRED_KEYS, CATALOG_PACK_OPTIONAL_KEYS, "catalog pack")
    require_string(pack["id"], "catalog pack id", pattern=ID_PATTERN)
    require_string(pack["title"], "catalog pack title")
    require_string(pack["description"], "catalog pack description")
    if pack["packType"] not in ALLOWED_PACK_TYPES:
        fail(f"catalog pack packType is invalid: {pack['packType']}")
    require_string(pack["version"], "catalog pack version", pattern=VERSION_PATTERN)
    require_string(pack["levelHint"], "catalog pack levelHint")
    require_int(pack["unitCount"], "catalog pack unitCount")
    require_int(pack["itemCount"], "catalog pack itemCount")
    require_int(pack["pronunciationReferenceCount"], "catalog pack pronunciationReferenceCount")
    require_float_ratio(pack["referenceCoverage"], "catalog pack referenceCoverage")
    require_float_ratio(pack["verifiedCoverage"], "catalog pack verifiedCoverage")
    require_int(pack["estimatedMinutes"], "catalog pack estimatedMinutes")
    require_int(pack["sizeBytes"], "catalog pack sizeBytes")
    require_string(pack["sha256"], "catalog pack sha256", pattern=SHA256_PATTERN)
    require_string(pack["fileName"], "catalog pack fileName", pattern=FILE_NAME_PATTERN)
    require_string_list(pack["tags"], "catalog pack tags", min_items=1)
    modes = require_string_list(pack["trainingModes"], "catalog pack trainingModes", min_items=1)
    for mode in modes:
        if mode not in ALLOWED_TRAINING_MODES:
            fail(f"catalog pack trainingModes contains invalid mode: {mode}")
    urls = require_string_list(pack["urls"], "catalog pack urls", min_items=1)
    if not all(url.startswith("https://") for url in urls):
        fail("catalog pack urls must all be https")

    series_fields = [field for field in ("seriesId", "seriesTitle", "seriesOrder") if field in pack]
    if series_fields and len(series_fields) != 3:
        fail("catalog pack seriesId, seriesTitle and seriesOrder must appear together")
    if "seriesId" in pack:
        require_string(pack["seriesId"], "catalog pack seriesId", pattern=ID_PATTERN)
        require_string(pack["seriesTitle"], "catalog pack seriesTitle")
        require_int(pack["seriesOrder"], "catalog pack seriesOrder")
    if "learningPath" in pack:
        require_string(pack["learningPath"], "catalog pack learningPath")
    for linkage_key in ("prerequisitePackIds", "recommendedNextPackIds", "companionPackIds"):
        if linkage_key in pack:
            ids = require_string_list(pack[linkage_key], f"catalog pack {linkage_key}", min_items=1)
            for linked_pack_id in ids:
                if not ID_PATTERN.match(linked_pack_id):
                    fail(f"catalog pack {linkage_key} contains invalid pack id: {linked_pack_id}")

    if pack["title"] != manifest["title"]:
        fail("catalog pack title must match trainpack manifest title")
    if pack["description"] != manifest["description"]:
        fail("catalog pack description must match trainpack manifest description")
    if pack["packType"] != manifest["packType"]:
        fail("catalog pack packType must match trainpack manifest packType")
    if pack["unitCount"] != len(units) or pack["unitCount"] != manifest["unitCount"]:
        fail("catalog pack unitCount must match trainpack manifest and actual units")
    if pack["itemCount"] != len(items) or pack["itemCount"] != manifest["itemCount"]:
        fail("catalog pack itemCount must match trainpack manifest and actual items")
    if (
        pack["pronunciationReferenceCount"] != len(pronunciation_references)
        or pack["pronunciationReferenceCount"] != manifest["pronunciationReferenceCount"]
    ):
        fail("catalog pack pronunciationReferenceCount must match trainpack manifest and actual references")
    if pack["referenceCoverage"] != manifest["referenceCoverage"]:
        fail("catalog pack referenceCoverage must match trainpack manifest")
    if pack["verifiedCoverage"] != manifest["verifiedCoverage"]:
        fail("catalog pack verifiedCoverage must match trainpack manifest")
    if pack["estimatedMinutes"] != manifest["estimatedMinutes"]:
        fail("catalog pack estimatedMinutes must match trainpack manifest")
    if pack["sizeBytes"] != package_path.stat().st_size:
        fail("catalog pack sizeBytes must match package file size")
    digest = hashlib.sha256(package_path.read_bytes()).hexdigest()
    if pack["sha256"] != digest:
        fail("catalog pack sha256 must match package file")
    if pack["fileName"] != package_path.name:
        fail("catalog pack fileName must match package file name")


def validate(package_path: Path, catalog_path: Path) -> None:
    manifest, units, items, pronunciation_references = read_package(package_path)
    validate_manifest(manifest)
    if manifest["unitCount"] != len(units):
        fail("trainpack manifest unitCount must match actual units")
    if manifest["itemCount"] != len(items):
        fail("trainpack manifest itemCount must match actual items")
    if manifest["pronunciationReferenceCount"] != len(pronunciation_references):
        fail("trainpack manifest pronunciationReferenceCount must match actual pronunciation references")

    seen_unit_ids: set[str] = set()
    unit_id_to_item_ids: dict[str, list[str]] = {}
    for index, unit in enumerate(units, start=1):
        validate_unit(unit, index, manifest["packId"])
        unit_id = unit["unitId"]
        if unit_id in seen_unit_ids:
            fail(f"duplicate unit id: {unit_id}")
        seen_unit_ids.add(unit_id)
        item_ids = list(unit["itemIds"])
        if len(item_ids) != len(set(item_ids)):
            fail(f"unit {unit_id} itemIds contains duplicates")
        unit_id_to_item_ids[unit_id] = item_ids

    seen_item_ids: set[str] = set()
    items_by_unit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, item in enumerate(items, start=1):
        validate_item(item, manifest["packId"], index)
        item_id = item["id"]
        if item_id in seen_item_ids:
            fail(f"duplicate item id: {item_id}")
        seen_item_ids.add(item_id)
        unit_id = item["unitId"]
        if unit_id not in seen_unit_ids:
            fail(f"item {item_id} references unknown unitId: {unit_id}")
        items_by_unit[unit_id].append(item)

    referenced_item_ids = {item_id for item_ids in unit_id_to_item_ids.values() for item_id in item_ids}
    if referenced_item_ids != seen_item_ids:
        missing_in_units = sorted(seen_item_ids - referenced_item_ids)
        missing_in_items = sorted(referenced_item_ids - seen_item_ids)
        if missing_in_units:
            fail(f"items not referenced by any unit: {missing_in_units}")
        if missing_in_items:
            fail(f"unit itemIds reference missing items: {missing_in_items}")

    for unit_id, unit_items in items_by_unit.items():
        unit_items.sort(key=lambda value: value["order"])
        expected_ids = unit_id_to_item_ids[unit_id]
        actual_ids = [item["id"] for item in unit_items]
        if expected_ids != actual_ids:
            fail(f"unit {unit_id} itemIds order must match actual item order")
        for expected_order, item in enumerate(unit_items, start=1):
            if item["order"] != expected_order:
                fail(f"item order must be continuous inside unit {unit_id}: expected {expected_order}, got {item['order']}")

    seen_reference_ids: set[str] = set()
    for index, reference in enumerate(pronunciation_references, start=1):
        validate_pronunciation_reference(reference, manifest["packId"], index, seen_item_ids, seen_unit_ids)
        reference_id = reference["id"]
        if reference_id in seen_reference_ids:
            fail(f"duplicate pronunciation reference id: {reference_id}")
        seen_reference_ids.add(reference_id)

    validate_catalog(catalog_path, package_path, manifest, units, items, pronunciation_references)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python3 tools/validate_trainpack.py <package.trainpack> <catalog.json>", file=sys.stderr)
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
