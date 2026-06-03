#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pronunciation_reference_builder import build_pronunciation_references, write_pronunciation_review_report
from release_config import CREATED_AT, MIN_APP_VERSION, TAG, VERSION, ZIP_TIMESTAMP


ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT / "content" / "packs"
GENERATED_PRONUNCIATION_DIR = ROOT / "content" / "generated-pronunciation-references"
OUTPUT_DIR = ROOT / "dist" / "trainpacks"
MANIFEST_DIR = ROOT / "manifests"

REQUIRED_PACK_KEYS = [
    "packId",
    "title",
    "description",
    "packType",
    "levelHint",
    "estimatedMinutes",
    "tags",
    "trainingModes",
    "units",
]

OPTIONAL_PACK_KEYS = [
    "catalogMetadata",
    "pronunciationPolicy",
]

OPTIONAL_CATALOG_METADATA_KEYS = {
    "seriesId",
    "seriesTitle",
    "seriesOrder",
    "learningPath",
    "prerequisitePackIds",
    "recommendedNextPackIds",
    "companionPackIds",
    "dailyQueueRoles",
}

REQUIRED_UNIT_KEYS = [
    "key",
    "title",
    "communicativeGoal",
    "scene",
    "register",
    "difficulty",
    "tags",
    "activationPrompts",
    "pronunciationFocus",
    "taskHints",
    "items",
]

REQUIRED_TASK_HINT_KEYS = [
    "defaultRole",
    "successCriteria",
    "correctionFocus",
    "retryPrompts",
    "variantPrompts",
]
OPTIONAL_TASK_HINT_KEYS = [
    "recommendedTaskTypes",
    "transferPrompts",
    "weakPointPrompts",
]

ALLOWED_TASK_ROLES = {"WarmUp", "Main", "Challenge", "Review"}
ALLOWED_DAILY_QUEUE_ROLES = {"Review", "New", "Transfer", "WeakPoint", "Challenge"}
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

REQUIRED_ITEM_KEYS = [
    "type",
    "englishText",
    "chinesePrompt",
]

OPTIONAL_ITEM_KEYS = [
    "variants",
    "notes",
    "pronunciationTargets",
    "commonMistakes",
    "tags",
    "contextText",
    "responseRole",
    "repairType",
    "slots",
    "sampleOutputs",
    "focusText",
    "focusType",
]


@dataclass(frozen=True)
class PackageBuildResult:
    package_path: Path
    pack_id: str
    title: str
    description: str
    pack_type: str
    level_hint: str
    estimated_minutes: int
    unit_count: int
    item_count: int
    pronunciation_reference_count: int
    reference_coverage: float
    verified_coverage: float
    size_bytes: int
    sha256: str
    tags: list[str]
    training_modes: list[str]
    catalog_metadata: dict[str, Any]

    @property
    def file_name(self) -> str:
        return self.package_path.name

    @property
    def download_url(self) -> str:
        return (
            "https://github.com/huarangmeng/vocabulary-packs/releases/download/"
            f"{TAG}/{self.file_name}"
        )

    def to_catalog_entry(self) -> dict[str, Any]:
        entry = {
            "id": self.pack_id,
            "title": self.title,
            "description": self.description,
            "packType": self.pack_type,
            "version": VERSION,
            "levelHint": self.level_hint,
            "unitCount": self.unit_count,
            "itemCount": self.item_count,
            "pronunciationReferenceCount": self.pronunciation_reference_count,
            "referenceCoverage": self.reference_coverage,
            "verifiedCoverage": self.verified_coverage,
            "estimatedMinutes": self.estimated_minutes,
            "sizeBytes": self.size_bytes,
            "sha256": self.sha256,
            "fileName": self.file_name,
            "tags": self.tags,
            "trainingModes": self.training_modes,
            "urls": [self.download_url],
        }
        entry.update(self.catalog_metadata)
        return entry


def _write_deterministic_text(zf: zipfile.ZipFile, name: str, text: str) -> None:
    info = zipfile.ZipInfo(filename=name, date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    zf.writestr(info, text.encode("utf-8"))


def _pronunciation_references_jsonl(pronunciation_references: list[dict[str, Any]]) -> str:
    return "\n".join(
        json.dumps(reference, ensure_ascii=False, separators=(",", ":"))
        for reference in pronunciation_references
    ) + "\n"


def _write_generated_pronunciation_references(pack_id: str, pronunciation_references: list[dict[str, Any]]) -> Path:
    GENERATED_PRONUNCIATION_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GENERATED_PRONUNCIATION_DIR / f"{pack_id}.pronunciation_references.jsonl"
    output_path.write_text(_pronunciation_references_jsonl(pronunciation_references), encoding="utf-8")
    return output_path


def _ensure_keys(data: dict[str, Any], keys: list[str], context: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{context} missing required keys: {', '.join(missing)}")


def _validate_catalog_metadata(catalog_metadata: Any, context: str) -> dict[str, Any]:
    if catalog_metadata is None:
        return {}
    if not isinstance(catalog_metadata, dict):
        raise ValueError(f"{context} catalogMetadata must be an object")

    unknown = sorted(set(catalog_metadata.keys()) - OPTIONAL_CATALOG_METADATA_KEYS)
    if unknown:
        raise ValueError(f"{context} catalogMetadata has unsupported keys: {', '.join(unknown)}")

    linkage_fields = ("seriesId", "seriesTitle", "seriesOrder")
    present_linkage_fields = [field for field in linkage_fields if field in catalog_metadata]
    if present_linkage_fields and len(present_linkage_fields) != len(linkage_fields):
        raise ValueError(
            f"{context} catalogMetadata must provide seriesId, seriesTitle and seriesOrder together"
        )

    for string_key in ("seriesId", "seriesTitle", "learningPath"):
        if string_key in catalog_metadata:
            value = catalog_metadata[string_key]
            if not isinstance(value, str) or not value:
                raise ValueError(f"{context} catalogMetadata.{string_key} must be a non-empty string")

    if "seriesOrder" in catalog_metadata:
        value = catalog_metadata["seriesOrder"]
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"{context} catalogMetadata.seriesOrder must be an integer >= 1")

    for list_key in ("prerequisitePackIds", "recommendedNextPackIds", "companionPackIds"):
        if list_key in catalog_metadata:
            value = catalog_metadata[list_key]
            if not isinstance(value, list) or not value:
                raise ValueError(f"{context} catalogMetadata.{list_key} must be a non-empty array")
            for pack_id in value:
                if not isinstance(pack_id, str) or not pack_id:
                    raise ValueError(f"{context} catalogMetadata.{list_key} must only contain non-empty strings")

    if "dailyQueueRoles" in catalog_metadata:
        roles = _validate_string_list(catalog_metadata["dailyQueueRoles"], f"{context} catalogMetadata.dailyQueueRoles")
        unknown_roles = sorted(set(roles) - ALLOWED_DAILY_QUEUE_ROLES)
        if unknown_roles:
            raise ValueError(f"{context} catalogMetadata.dailyQueueRoles has unsupported values: {', '.join(unknown_roles)}")

    return dict(catalog_metadata)


def _validate_string_list(value: Any, context: str, *, min_items: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < min_items:
        raise ValueError(f"{context} must be an array with at least {min_items} item(s)")
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item:
            raise ValueError(f"{context}[{index}] must be a non-empty string")
    return list(value)


def _validate_task_hints(task_hints: Any, context: str) -> dict[str, Any]:
    if not isinstance(task_hints, dict):
        raise ValueError(f"{context} taskHints must be an object")
    _ensure_keys(task_hints, REQUIRED_TASK_HINT_KEYS, f"{context} taskHints")
    allowed_keys = set(REQUIRED_TASK_HINT_KEYS) | set(OPTIONAL_TASK_HINT_KEYS)
    unknown = sorted(set(task_hints.keys()) - allowed_keys)
    if unknown:
        raise ValueError(f"{context} taskHints has unsupported keys: {', '.join(unknown)}")

    default_role = task_hints["defaultRole"]
    if default_role not in ALLOWED_TASK_ROLES:
        raise ValueError(f"{context} taskHints.defaultRole is invalid: {default_role}")

    correction_focus = _validate_string_list(
        task_hints["correctionFocus"],
        f"{context} taskHints.correctionFocus",
    )
    unknown_focus = sorted(set(correction_focus) - ALLOWED_CORRECTION_FOCUS)
    if unknown_focus:
        raise ValueError(f"{context} taskHints.correctionFocus has unsupported values: {', '.join(unknown_focus)}")

    result = {
        "defaultRole": default_role,
        "successCriteria": _validate_string_list(task_hints["successCriteria"], f"{context} taskHints.successCriteria"),
        "correctionFocus": correction_focus,
        "retryPrompts": _validate_string_list(task_hints["retryPrompts"], f"{context} taskHints.retryPrompts"),
        "variantPrompts": _validate_string_list(task_hints["variantPrompts"], f"{context} taskHints.variantPrompts"),
    }
    for list_key in OPTIONAL_TASK_HINT_KEYS:
        if list_key in task_hints:
            values = _validate_string_list(task_hints[list_key], f"{context} taskHints.{list_key}")
            if list_key == "recommendedTaskTypes":
                unknown_roles = sorted(set(values) - ALLOWED_DAILY_QUEUE_ROLES)
                if unknown_roles:
                    raise ValueError(f"{context} taskHints.{list_key} has unsupported values: {', '.join(unknown_roles)}")
            result[list_key] = values
    return result


def discover_content_paths() -> list[Path]:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(CONTENT_DIR.glob("*.json"))


def load_pack_definition(content_path: Path) -> dict[str, Any]:
    data = json.loads(content_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{content_path} must contain a JSON object")

    _ensure_keys(data, REQUIRED_PACK_KEYS, str(content_path))
    unknown_pack_keys = sorted(set(data.keys()) - (set(REQUIRED_PACK_KEYS) | set(OPTIONAL_PACK_KEYS)))
    if unknown_pack_keys:
        raise ValueError(f"{content_path} has unsupported keys: {', '.join(unknown_pack_keys)}")
    if not isinstance(data["units"], list) or not data["units"]:
        raise ValueError(f"{content_path} must contain a non-empty units array")

    for unit_index, unit in enumerate(data["units"], start=1):
        if not isinstance(unit, dict):
            raise ValueError(f"{content_path} unit #{unit_index} must be an object")
        _ensure_keys(unit, REQUIRED_UNIT_KEYS, f"{content_path} unit #{unit_index}")
        unit["taskHints"] = _validate_task_hints(unit["taskHints"], f"{content_path} unit #{unit_index}")
        if not isinstance(unit["items"], list) or not unit["items"]:
            raise ValueError(f"{content_path} unit #{unit_index} must contain a non-empty items array")
        for item_index, item in enumerate(unit["items"], start=1):
            if not isinstance(item, dict):
                raise ValueError(f"{content_path} unit #{unit_index} item #{item_index} must be an object")
            _ensure_keys(item, REQUIRED_ITEM_KEYS, f"{content_path} unit #{unit_index} item #{item_index}")

    data["catalogMetadata"] = _validate_catalog_metadata(data.get("catalogMetadata"), str(content_path))
    data["pronunciationPolicy"] = _validate_pronunciation_policy(data.get("pronunciationPolicy"), str(content_path))

    return data


def _validate_pronunciation_policy(policy: Any, context: str) -> dict[str, Any]:
    if policy is None:
        return {
            "dialects": ["en-US", "en-GB"],
            "referenceScope": ["EnglishText", "Variant", "PronunciationTarget"],
            "minimumVerifiedCoverage": 0.98,
            "generator": "online-verified-pronunciation-builder-v2",
        }
    if not isinstance(policy, dict):
        raise ValueError(f"{context} pronunciationPolicy must be an object")
    required = {"dialects", "referenceScope", "minimumVerifiedCoverage", "generator"}
    missing = sorted(required - policy.keys())
    if missing:
        raise ValueError(f"{context} pronunciationPolicy missing keys: {', '.join(missing)}")
    unknown = sorted(policy.keys() - required)
    if unknown:
        raise ValueError(f"{context} pronunciationPolicy has unsupported keys: {', '.join(unknown)}")
    dialects = _validate_string_list(policy["dialects"], f"{context} pronunciationPolicy.dialects")
    if dialects != ["en-US", "en-GB"]:
        raise ValueError(f"{context} pronunciationPolicy.dialects must be ['en-US', 'en-GB']")
    reference_scope = _validate_string_list(policy["referenceScope"], f"{context} pronunciationPolicy.referenceScope")
    if reference_scope != ["EnglishText", "Variant", "PronunciationTarget"]:
        raise ValueError(
            f"{context} pronunciationPolicy.referenceScope must be ['EnglishText', 'Variant', 'PronunciationTarget']"
        )
    minimum_verified_coverage = policy["minimumVerifiedCoverage"]
    if (
        not isinstance(minimum_verified_coverage, (int, float))
        or minimum_verified_coverage < 0.98
        or minimum_verified_coverage > 1
    ):
        raise ValueError(f"{context} pronunciationPolicy.minimumVerifiedCoverage must be between 0.98 and 1")
    generator = policy["generator"]
    if not isinstance(generator, str) or not generator:
        raise ValueError(f"{context} pronunciationPolicy.generator must be a non-empty string")
    return {
        "dialects": dialects,
        "referenceScope": reference_scope,
        "minimumVerifiedCoverage": float(minimum_verified_coverage),
        "generator": generator,
    }


def _build_units_and_items(pack_id: str, unit_specs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    units: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    item_index = 1
    for unit_order, spec in enumerate(unit_specs, start=1):
        unit_id = f"{pack_id}:{spec['key']}"
        unit_item_ids: list[str] = []
        for order_in_unit, item_spec in enumerate(spec["items"], start=1):
            item_id = f"{pack_id}:item-{item_index:04d}"
            item_index += 1
            item = {
                "id": item_id,
                "unitId": unit_id,
                "order": order_in_unit,
                "type": item_spec["type"],
                "englishText": item_spec["englishText"],
                "chinesePrompt": item_spec["chinesePrompt"],
                "variants": item_spec.get("variants", []),
                "notes": item_spec.get("notes", []),
                "pronunciationTargets": item_spec.get("pronunciationTargets", []),
                "commonMistakes": item_spec.get("commonMistakes", []),
                "tags": item_spec.get("tags", []),
            }
            for optional_key in OPTIONAL_ITEM_KEYS:
                if optional_key in item_spec and optional_key not in item:
                    item[optional_key] = item_spec[optional_key]
            items.append(item)
            unit_item_ids.append(item_id)
        units.append(
            {
                "unitId": unit_id,
                "order": unit_order,
                "title": spec["title"],
                "communicativeGoal": spec["communicativeGoal"],
                "scene": spec["scene"],
                "register": spec["register"],
                "difficulty": spec["difficulty"],
                "tags": spec["tags"],
                "activationPrompts": spec["activationPrompts"],
                "itemIds": unit_item_ids,
                "pronunciationFocus": spec["pronunciationFocus"],
                "taskHints": spec["taskHints"],
            }
        )
        if "speakingActId" in spec:
            units[-1]["speakingActId"] = spec["speakingActId"]
        if "sceneCoverage" in spec:
            units[-1]["sceneCoverage"] = spec["sceneCoverage"]
    return units, items


def build_trainpack(
    *,
    pack_id: str,
    title: str,
    description: str,
    pack_type: str,
    level_hint: str,
    estimated_minutes: int,
    tags: list[str],
    training_modes: list[str],
    unit_specs: list[dict[str, Any]],
    catalog_metadata: dict[str, Any] | None = None,
    pronunciation_policy: dict[str, Any] | None = None,
) -> PackageBuildResult:
    units, items = _build_units_and_items(pack_id, unit_specs)
    pronunciation_result = build_pronunciation_references(pack_id, units, items)
    pronunciation_references = pronunciation_result.references
    write_pronunciation_review_report(pack_id, pronunciation_result)
    pronunciation_references_text = _pronunciation_references_jsonl(pronunciation_references)
    _write_generated_pronunciation_references(pack_id, pronunciation_references)
    minimum_verified_coverage = (pronunciation_policy or {}).get("minimumVerifiedCoverage", 0.98)
    if pronunciation_result.verified_coverage < minimum_verified_coverage:
        raise ValueError(
            f"{pack_id} verified pronunciation coverage {pronunciation_result.verified_coverage:.2%} "
            f"is below required {minimum_verified_coverage:.2%}; see dist/reports/{pack_id}-pronunciation-review.json"
        )
    package_manifest = {
        "schemaVersion": 1,
        "packId": pack_id,
        "packVersion": VERSION,
        "title": title,
        "description": description,
        "packType": pack_type,
        "locale": "en-US",
        "unitCount": len(units),
        "itemCount": len(items),
        "pronunciationReferenceCount": len(pronunciation_references),
        "referenceCoverage": pronunciation_result.reference_coverage,
        "verifiedCoverage": pronunciation_result.verified_coverage,
        "estimatedMinutes": estimated_minutes,
        "createdAt": CREATED_AT,
        "unitsFile": "units.json",
        "itemsFile": "items.jsonl",
        "pronunciationReferencesFile": "pronunciation_references.jsonl",
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    package_path = OUTPUT_DIR / f"{pack_id}-{VERSION}.trainpack"
    with zipfile.ZipFile(package_path, "w") as package:
        _write_deterministic_text(package, "manifest.json", json.dumps(package_manifest, ensure_ascii=False, indent=2) + "\n")
        _write_deterministic_text(package, "units.json", json.dumps(units, ensure_ascii=False, indent=2) + "\n")
        _write_deterministic_text(
            package,
            "items.jsonl",
            "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in items) + "\n",
        )
        _write_deterministic_text(
            package,
            "pronunciation_references.jsonl",
            pronunciation_references_text,
        )

    size_bytes = package_path.stat().st_size
    sha256 = hashlib.sha256(package_path.read_bytes()).hexdigest()
    return PackageBuildResult(
        package_path=package_path,
        pack_id=pack_id,
        title=title,
        description=description,
        pack_type=pack_type,
        level_hint=level_hint,
        estimated_minutes=estimated_minutes,
        unit_count=len(units),
        item_count=len(items),
        pronunciation_reference_count=len(pronunciation_references),
        reference_coverage=pronunciation_result.reference_coverage,
        verified_coverage=pronunciation_result.verified_coverage,
        size_bytes=size_bytes,
        sha256=sha256,
        tags=tags,
        training_modes=training_modes,
        catalog_metadata=dict(catalog_metadata or {}),
    )


def build_from_definition(definition: dict[str, Any]) -> PackageBuildResult:
    return build_trainpack(
        pack_id=definition["packId"],
        title=definition["title"],
        description=definition["description"],
        pack_type=definition["packType"],
        level_hint=definition["levelHint"],
        estimated_minutes=definition["estimatedMinutes"],
        tags=definition["tags"],
        training_modes=definition["trainingModes"],
        unit_specs=definition["units"],
        catalog_metadata=definition.get("catalogMetadata", {}),
        pronunciation_policy=definition.get("pronunciationPolicy", {}),
    )


def build_from_content_path(content_path: Path) -> PackageBuildResult:
    return build_from_definition(load_pack_definition(content_path))


def write_catalog(results: list[PackageBuildResult]) -> Path:
    catalog = {
        "schemaVersion": 1,
        "catalogVersion": VERSION,
        "generatedAt": CREATED_AT,
        "minAppVersion": MIN_APP_VERSION,
        "packs": [result.to_catalog_entry() for result in sorted(results, key=lambda value: value.pack_id)],
    }
    catalog_text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    latest_manifest = MANIFEST_DIR / "latest.json"
    version_manifest = MANIFEST_DIR / f"{VERSION}.json"
    latest_output = OUTPUT_DIR / "latest.json"
    latest_manifest.write_text(catalog_text, encoding="utf-8")
    version_manifest.write_text(catalog_text, encoding="utf-8")
    latest_output.write_text(catalog_text, encoding="utf-8")
    latest_digest = hashlib.sha256(latest_output.read_bytes()).hexdigest()
    (OUTPUT_DIR / "latest.json.sha256").write_text(f"{latest_digest}  latest.json\n", encoding="utf-8")
    return latest_manifest
