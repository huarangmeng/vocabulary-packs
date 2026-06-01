#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from release_config import CREATED_AT, MIN_APP_VERSION, TAG, VERSION, ZIP_TIMESTAMP


ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT / "content" / "packs"
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
    "items",
]

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
    size_bytes: int
    sha256: str
    tags: list[str]
    training_modes: list[str]

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
        return {
            "id": self.pack_id,
            "title": self.title,
            "description": self.description,
            "packType": self.pack_type,
            "version": VERSION,
            "levelHint": self.level_hint,
            "unitCount": self.unit_count,
            "itemCount": self.item_count,
            "estimatedMinutes": self.estimated_minutes,
            "sizeBytes": self.size_bytes,
            "sha256": self.sha256,
            "fileName": self.file_name,
            "tags": self.tags,
            "trainingModes": self.training_modes,
            "urls": [self.download_url],
        }


def _write_deterministic_text(zf: zipfile.ZipFile, name: str, text: str) -> None:
    info = zipfile.ZipInfo(filename=name, date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    zf.writestr(info, text.encode("utf-8"))


def _ensure_keys(data: dict[str, Any], keys: list[str], context: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{context} missing required keys: {', '.join(missing)}")


def discover_content_paths() -> list[Path]:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(CONTENT_DIR.glob("*.json"))


def load_pack_definition(content_path: Path) -> dict[str, Any]:
    data = json.loads(content_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{content_path} must contain a JSON object")

    _ensure_keys(data, REQUIRED_PACK_KEYS, str(content_path))
    if not isinstance(data["units"], list) or not data["units"]:
        raise ValueError(f"{content_path} must contain a non-empty units array")

    for unit_index, unit in enumerate(data["units"], start=1):
        if not isinstance(unit, dict):
            raise ValueError(f"{content_path} unit #{unit_index} must be an object")
        _ensure_keys(unit, REQUIRED_UNIT_KEYS, f"{content_path} unit #{unit_index}")
        if not isinstance(unit["items"], list) or not unit["items"]:
            raise ValueError(f"{content_path} unit #{unit_index} must contain a non-empty items array")
        for item_index, item in enumerate(unit["items"], start=1):
            if not isinstance(item, dict):
                raise ValueError(f"{content_path} unit #{unit_index} item #{item_index} must be an object")
            _ensure_keys(item, REQUIRED_ITEM_KEYS, f"{content_path} unit #{unit_index} item #{item_index}")

    return data


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
            }
        )
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
) -> PackageBuildResult:
    units, items = _build_units_and_items(pack_id, unit_specs)
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
        "estimatedMinutes": estimated_minutes,
        "createdAt": CREATED_AT,
        "unitsFile": "units.json",
        "itemsFile": "items.jsonl",
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
        size_bytes=size_bytes,
        sha256=sha256,
        tags=tags,
        training_modes=training_modes,
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
