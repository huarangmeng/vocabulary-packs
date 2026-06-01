# Vocabulary Trainpack Format

本文档是 `.trainpack` 的固定格式契约。后续所有官方训练包都必须遵守该格式，不允许每个训练包自行增加不同的顶层结构。

## 文件格式

`.trainpack` 必须是 zip 文件，且根目录只允许包含：

```text
manifest.json
units.json
items.jsonl
```

要求：

- `manifest.json` 必须是 UTF-8 JSON。
- `units.json` 必须是 UTF-8 JSON。
- `items.jsonl` 必须是 UTF-8 JSON Lines。
- `items.jsonl` 每一行必须是一个完整 JSON 内容项。
- zip 内不允许目录、不允许嵌套路径、不允许额外文件。
- zip 内文件名必须完全匹配，区分大小写。

## 包内 Manifest

`manifest.json` 必须包含：

```json
{
  "schemaVersion": 1,
  "packId": "core-chunks-1",
  "packVersion": "2026.06.02",
  "title": "高频口语表达块 1",
  "description": "面向日常交流与工作沟通的高频英文表达块训练包。",
  "packType": "CoreChunks",
  "locale": "en-US",
  "unitCount": 3,
  "itemCount": 12,
  "estimatedMinutes": 45,
  "createdAt": "2026-06-02T00:00:00Z",
  "unitsFile": "units.json",
  "itemsFile": "items.jsonl"
}
```

字段约束：

- `schemaVersion`：固定为 `1`。
- `packId`：小写字母、数字和连字符，例如 `core-chunks-1`。
- `packVersion`：日期版本，例如 `2026.06.02`。
- `title`：展示名称。
- `description`：展示描述。
- `packType`：训练包类型，例如 `CoreChunks`、`Scenario`、`Function`、`Repair`。
- `locale`：语言区域，例如 `en-US`。
- `unitCount`：必须等于 `units.json` 实际单元数。
- `itemCount`：必须等于 `items.jsonl` 实际行数。
- `estimatedMinutes`：包级预计学习时长，必须大于 `0`。
- `createdAt`：UTC ISO-8601 时间，必须以 `Z` 结尾。
- `unitsFile`：固定为 `units.json`。
- `itemsFile`：固定为 `items.jsonl`。

## 训练单元 Unit

`units.json` 中每个单元必须包含：

```json
{
  "unitId": "core-chunks-1:clarify-001",
  "order": 1,
  "title": "请对方重复",
  "communicativeGoal": "没听清时礼貌请对方重复",
  "scene": "DailyConversation",
  "register": "Neutral",
  "difficulty": {
    "lexical": "A2-B1",
    "interactionPressure": "Low",
    "pronunciationRisk": "Low"
  },
  "tags": ["Clarify", "Repair", "Listening"],
  "activationPrompts": [
    "你没听清对方最后一句话",
    "你想请对方说慢一点"
  ],
  "itemIds": [
    "core-chunks-1:item-0001",
    "core-chunks-1:item-0002"
  ],
  "pronunciationFocus": ["didn't catch that", "again"]
}
```

字段约束：

- `unitId`：全局稳定 ID，格式为 `{packId}:{unitKey}`。
- `order`：从 `1` 开始连续递增。
- `title`：单元标题，不能为空。
- `communicativeGoal`：本单元训练目标，不能为空。
- `scene`：场景标签，例如 `DailyConversation`、`Meeting`、`Travel`。
- `register`：语域，例如 `Casual`、`Neutral`、`Formal`。
- `difficulty`：多维难度对象，不能缺字段。
- `tags`：至少一个标签。
- `activationPrompts`：至少一个提示语。
- `itemIds`：单元下所有内容项 ID，不能为空。
- `pronunciationFocus`：发音重点短语，可以为空数组。

## 原子内容项 Item

`items.jsonl` 中每行必须包含一个完整内容项。

支持类型：

- `Chunk`
- `SentencePattern`
- `DialogueTurn`
- `RepairStrategy`
- `PronunciationTarget`

示例：

```json
{
  "id": "core-chunks-1:item-0001",
  "unitId": "core-chunks-1:clarify-001",
  "order": 1,
  "type": "Chunk",
  "englishText": "Could you say that again?",
  "chinesePrompt": "你能再说一遍吗？",
  "variants": [
    "Sorry, could you say that again?",
    "Could you repeat that?"
  ],
  "notes": [
    "适合大多数日常和工作场景",
    "比 What? 更礼貌"
  ],
  "pronunciationTargets": ["could you", "again"],
  "commonMistakes": ["What? say again.", "Repeat again."],
  "tags": ["Clarify", "Chunk"]
}
```

字段约束：

- `id`：全局稳定 ID。
- `unitId`：必须指向 `units.json` 中现有单元。
- `order`：在单元内连续递增。
- `type`：固定枚举，必须属于允许类型。
- `englishText`：英文表达，不能为空。
- `chinesePrompt`：中文提示，不能为空。
- `variants`：有限替换表达，可以为空数组。
- `notes`：用户可见提示，可以为空数组。
- `pronunciationTargets`：发音关注片段，可以为空数组。
- `commonMistakes`：常见错误或不自然表达，可以为空数组。
- `tags`：至少一个标签。

可选字段：

- `contextText`
- `responseRole`
- `repairType`
- `slots`
- `sampleOutputs`
- `focusText`
- `focusType`

## 外部 Catalog

`manifests/latest.json` 和版本化 catalog 必须包含：

```json
{
  "schemaVersion": 1,
  "catalogVersion": "2026.06.02",
  "generatedAt": "2026-06-02T00:00:00Z",
  "minAppVersion": "1.1.0",
  "packs": [
    {
      "id": "core-chunks-1",
      "title": "高频口语表达块 1",
      "description": "面向日常交流与工作沟通的高频英文表达块训练包。",
      "packType": "CoreChunks",
      "version": "2026.06.02",
      "levelHint": "A2-B1",
      "unitCount": 3,
      "itemCount": 12,
      "estimatedMinutes": 45,
      "sizeBytes": 12345,
      "sha256": "replace-with-real-sha256",
      "fileName": "core-chunks-1-2026.06.02.trainpack",
      "tags": ["Speaking", "Chunks", "A2-B1"],
      "trainingModes": ["Recall", "Shadow", "Respond"],
      "urls": [
        "https://github.com/huarangmeng/vocabulary-packs/releases/download/trainpack-2026.06.02/core-chunks-1-2026.06.02.trainpack"
      ]
    }
  ]
}
```

Catalog 中的 `packs[].id`、`packs[].version`、`packs[].unitCount`、`packs[].itemCount` 必须和 `.trainpack` 包内 `manifest.json` 对齐。

## 校验命令

生成或发布前必须执行：

```bash
python3 tools/validate_trainpack.py dist/trainpacks/core-chunks-1-2026.06.02.trainpack manifests/latest.json
```

该命令会检查：

- zip 包结构。
- 包内 manifest 字段。
- units JSON 字段。
- items JSONL 字段。
- `unitCount` 和 `itemCount` 是否一致。
- `Unit.order` 是否连续。
- `Item.order` 是否在各自单元内连续。
- `itemIds` 与 `unitId` 引用关系是否正确。
- catalog 中的 `sha256`、大小、URL、文件名和包内容是否匹配。
