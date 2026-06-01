#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERSION = "2026.06.02"
TAG = f"trainpack-{VERSION}"
PACK_ID = "core-chunks-1"
FILE_NAME = f"{PACK_ID}-{VERSION}.trainpack"
DOWNLOAD_URL = (
    "https://github.com/huarangmeng/vocabulary-packs/releases/download/"
    f"{TAG}/{FILE_NAME}"
)
CREATED_AT = "2026-06-02T00:00:00Z"
ZIP_TIMESTAMP = (2026, 6, 2, 0, 0, 0)


UNIT_SPECS = [
    {
        "key": "clarify-001",
        "title": "请对方重复",
        "communicativeGoal": "没听清时礼貌请对方重复",
        "scene": "DailyConversation",
        "register": "Neutral",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Low",
            "pronunciationRisk": "Low",
        },
        "tags": ["Clarify", "Repair", "Listening"],
        "activationPrompts": [
            "你没听清对方最后一句话",
            "你想请对方说慢一点",
        ],
        "pronunciationFocus": ["didn't catch that", "again"],
        "items": [
            {
                "type": "Chunk",
                "englishText": "Could you say that again?",
                "chinesePrompt": "你能再说一遍吗？",
                "variants": ["Sorry, could you say that again?", "Could you repeat that?"],
                "notes": ["适合大多数日常和工作场景", "比 What? 更礼貌"],
                "pronunciationTargets": ["could you", "again"],
                "commonMistakes": ["What? say again.", "Repeat again."],
                "tags": ["Clarify", "Chunk"],
            },
            {
                "type": "Chunk",
                "englishText": "Sorry, I didn't catch that.",
                "chinesePrompt": "抱歉，我刚才没听清。",
                "variants": ["Sorry, I didn't catch the last part."],
                "notes": ["先道歉再请求重复更自然"],
                "pronunciationTargets": ["didn't catch that"],
                "commonMistakes": ["I don't hear clearly."],
                "tags": ["Clarify", "Chunk"],
            },
            {
                "type": "SentencePattern",
                "englishText": "Could you say that again a bit more slowly?",
                "chinesePrompt": "你能再说一遍并稍微说慢一点吗？",
                "variants": ["Could you say that a little more slowly?"],
                "notes": ["适合对方语速较快时"],
                "pronunciationTargets": ["a bit more slowly"],
                "commonMistakes": ["Say again slowly."],
                "tags": ["Clarify", "SentencePattern"],
                "slots": ["again", "a bit more slowly"],
                "sampleOutputs": ["Could you say that again a bit more slowly?"],
            },
            {
                "type": "DialogueTurn",
                "englishText": "Sorry, I didn't catch the last part.",
                "chinesePrompt": "抱歉，我最后那部分没听清。",
                "variants": [],
                "notes": ["适合会议或通话中使用"],
                "pronunciationTargets": ["the last part"],
                "commonMistakes": ["Last part I didn't hear."],
                "tags": ["Clarify", "DialogueTurn"],
                "contextText": "The deadline has been moved to next Thursday.",
                "responseRole": "Listener",
            },
        ],
    },
    {
        "key": "buy-time-001",
        "title": "争取思考时间",
        "communicativeGoal": "还没想好时先用保底表达稳住对话",
        "scene": "WorkConversation",
        "register": "Neutral",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Medium",
            "pronunciationRisk": "Low",
        },
        "tags": ["Repair", "ThinkingTime", "Chunk"],
        "activationPrompts": [
            "你需要几秒钟组织语言",
            "你还没完全想好答案",
        ],
        "pronunciationFocus": ["let me think", "for a second"],
        "items": [
            {
                "type": "RepairStrategy",
                "englishText": "Let me think for a second.",
                "chinesePrompt": "让我想一下。",
                "variants": ["Give me a second to think."],
                "notes": ["先稳住节奏，再继续说"],
                "pronunciationTargets": ["let me", "for a second"],
                "commonMistakes": ["I need think."],
                "tags": ["Repair", "ThinkingTime"],
                "repairType": "BuyTime",
            },
            {
                "type": "Chunk",
                "englishText": "That's a good question.",
                "chinesePrompt": "这是个好问题。",
                "variants": ["That's actually a really good question."],
                "notes": ["适合先接住问题，再组织回答"],
                "pronunciationTargets": ["good question"],
                "commonMistakes": ["Your question is good."],
                "tags": ["Repair", "Chunk"],
            },
            {
                "type": "SentencePattern",
                "englishText": "I think there are a couple of ways to look at it.",
                "chinesePrompt": "我觉得这件事可以从几个角度来看。",
                "variants": ["There are probably a few ways to think about it."],
                "notes": ["适合展开观点前做缓冲"],
                "pronunciationTargets": ["a couple of", "look at it"],
                "commonMistakes": ["There have several angles."],
                "tags": ["Repair", "SentencePattern"],
                "slots": ["a couple of ways", "look at it"],
                "sampleOutputs": ["I think there are a couple of ways to look at it."],
            },
            {
                "type": "DialogueTurn",
                "englishText": "Let me think for a second. I would probably start with the budget.",
                "chinesePrompt": "让我想一下。我可能会先从预算开始。",
                "variants": [],
                "notes": ["把争取时间和正式回答接起来"],
                "pronunciationTargets": ["probably start", "the budget"],
                "commonMistakes": ["Wait, I answer budget first."],
                "tags": ["Repair", "DialogueTurn"],
                "contextText": "How would you improve this project plan?",
                "responseRole": "Speaker",
            },
        ],
    },
    {
        "key": "opinion-001",
        "title": "表达个人看法",
        "communicativeGoal": "自然表达个人观点并保留一定弹性",
        "scene": "Meeting",
        "register": "Neutral",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Medium",
            "pronunciationRisk": "Medium",
        },
        "tags": ["Opinion", "Meeting", "Chunk"],
        "activationPrompts": [
            "你想表达自己的看法",
            "你想给出较为温和的意见",
        ],
        "pronunciationFocus": ["I think", "to be honest"],
        "items": [
            {
                "type": "Chunk",
                "englishText": "I think we should start with the customer problem.",
                "chinesePrompt": "我觉得我们应该先从用户问题开始。",
                "variants": ["I think the customer problem should come first."],
                "notes": ["简单直接，适合大多数会议场景"],
                "pronunciationTargets": ["I think we should", "customer problem"],
                "commonMistakes": ["I think should start from customer problem."],
                "tags": ["Opinion", "Chunk"],
            },
            {
                "type": "SentencePattern",
                "englishText": "To be honest, I'm not sure that's the best place to start.",
                "chinesePrompt": "说实话，我不确定那是不是最好的起点。",
                "variants": ["Honestly, I'm not sure that's the best starting point."],
                "notes": ["适合表达保留意见"],
                "pronunciationTargets": ["to be honest", "best place to start"],
                "commonMistakes": ["I am not sure that is best start."],
                "tags": ["Opinion", "SentencePattern"],
                "slots": ["to be honest", "best place to start"],
                "sampleOutputs": ["To be honest, I'm not sure that's the best place to start."],
            },
            {
                "type": "DialogueTurn",
                "englishText": "I see your point, but I think the timeline is still too tight.",
                "chinesePrompt": "我理解你的意思，但我觉得时间线还是太紧了。",
                "variants": [],
                "notes": ["先认可，再提出不同意见"],
                "pronunciationTargets": ["I see your point", "too tight"],
                "commonMistakes": ["I know your meaning but timeline is tight."],
                "tags": ["Opinion", "DialogueTurn"],
                "contextText": "We can probably finish this by Friday.",
                "responseRole": "Participant",
            },
            {
                "type": "PronunciationTarget",
                "englishText": "to be honest",
                "chinesePrompt": "说实话",
                "variants": [],
                "notes": ["重点关注弱读和连读"],
                "pronunciationTargets": ["to be honest"],
                "commonMistakes": [],
                "tags": ["Opinion", "PronunciationTarget"],
                "focusText": "to be honest",
                "focusType": "ChunkStress",
            },
        ],
    },
]


def write_deterministic_text(zf: zipfile.ZipFile, name: str, text: str) -> None:
    info = zipfile.ZipInfo(filename=name, date_time=ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    zf.writestr(info, text.encode("utf-8"))


def build_units_and_items() -> tuple[list[dict], list[dict]]:
    units: list[dict] = []
    items: list[dict] = []
    item_index = 1
    for unit_order, spec in enumerate(UNIT_SPECS, start=1):
        unit_id = f"{PACK_ID}:{spec['key']}"
        unit_item_ids: list[str] = []
        for order_in_unit, item_spec in enumerate(spec["items"], start=1):
            item_id = f"{PACK_ID}:item-{item_index:04d}"
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
            for optional_key in ["contextText", "responseRole", "repairType", "slots", "sampleOutputs", "focusText", "focusType"]:
                if optional_key in item_spec:
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


def main() -> None:
    units, items = build_units_and_items()
    package_manifest = {
        "schemaVersion": 1,
        "packId": PACK_ID,
        "packVersion": VERSION,
        "title": "高频口语表达块 1",
        "description": "面向日常交流与工作沟通的高频英文表达块训练包。",
        "packType": "CoreChunks",
        "locale": "en-US",
        "unitCount": len(units),
        "itemCount": len(items),
        "estimatedMinutes": 45,
        "createdAt": CREATED_AT,
        "unitsFile": "units.json",
        "itemsFile": "items.jsonl",
    }

    output_dir = ROOT / "dist" / "trainpacks"
    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / FILE_NAME
    with zipfile.ZipFile(package_path, "w") as package:
        write_deterministic_text(package, "manifest.json", json.dumps(package_manifest, ensure_ascii=False, indent=2) + "\n")
        write_deterministic_text(package, "units.json", json.dumps(units, ensure_ascii=False, indent=2) + "\n")
        write_deterministic_text(
            package,
            "items.jsonl",
            "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in items) + "\n",
        )

    digest = hashlib.sha256(package_path.read_bytes()).hexdigest()
    size_bytes = package_path.stat().st_size

    catalog = {
        "schemaVersion": 1,
        "catalogVersion": VERSION,
        "generatedAt": CREATED_AT,
        "minAppVersion": "1.1.0",
        "packs": [
            {
                "id": PACK_ID,
                "title": "高频口语表达块 1",
                "description": "面向日常交流与工作沟通的高频英文表达块训练包。",
                "packType": "CoreChunks",
                "version": VERSION,
                "levelHint": "A2-B1",
                "unitCount": len(units),
                "itemCount": len(items),
                "estimatedMinutes": 45,
                "sizeBytes": size_bytes,
                "sha256": digest,
                "fileName": FILE_NAME,
                "tags": ["Speaking", "Chunks", "A2-B1"],
                "trainingModes": ["Recall", "Shadow", "Respond"],
                "urls": [DOWNLOAD_URL],
            }
        ],
    }

    manifest_dir = ROOT / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    catalog_text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    (manifest_dir / "latest.json").write_text(catalog_text, encoding="utf-8")
    (manifest_dir / f"{VERSION}.json").write_text(catalog_text, encoding="utf-8")
    (output_dir / "latest.json").write_text(catalog_text, encoding="utf-8")
    latest_digest = hashlib.sha256((output_dir / "latest.json").read_bytes()).hexdigest()
    (output_dir / "latest.json.sha256").write_text(f"{latest_digest}  latest.json\n", encoding="utf-8")

    print(f"Generated: {package_path}")
    print(f"Units: {len(units)}")
    print(f"Items: {len(items)}")
    print(f"Size: {size_bytes} bytes")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
