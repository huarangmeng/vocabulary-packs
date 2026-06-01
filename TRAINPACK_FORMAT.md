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
  "pronunciationFocus": ["didn't catch that", "again"],
  "taskHints": {
    "defaultRole": "WarmUp",
    "successCriteria": [
      "完成“请对方重复”对应的沟通动作",
      "没听清时礼貌请对方重复",
      "语气自然清楚，适合中性日常或工作场景"
    ],
    "correctionFocus": ["Clarification", "SpokenRegister"],
    "retryPrompts": [
      "只重说关键一句：你没听清对方最后一句话",
      "这次先放慢语速，把沟通目标说完整。"
    ],
    "variantPrompts": [
      "你想请对方说慢一点",
      "换一个相近场景，再完成“请对方重复”这个口语动作。"
    ]
  }
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
- `taskHints`：任务流编排提示，不能为空。

`taskHints` 字段约束：

- `defaultRole`：建议默认任务角色，固定为 `WarmUp`、`Main`、`Challenge` 或 `Review`。
- `successCriteria`：任务成功标准，至少一条。
- `correctionFocus`：优先纠偏方向，至少一条。
- `retryPrompts`：首次输出不理想时的重说提示，至少一条。
- `variantPrompts`：达到 `Spoken` 后用于判断 `Ready` 的变体场景，至少一条。

允许的 `correctionFocus`：

- `Naturalness`
- `SpokenRegister`
- `Completeness`
- `Clarification`
- `TurnTaking`
- `Softening`
- `Pronunciation`
- `ScenarioFit`
- `Fluency`
- `Decision`
- `FollowUp`
- `Repair`

设计约束：

- `taskHints` 是包内正式结构，不是 App 私有推导字段。
- `taskHints` 不直接等同于当天的运行时任务；App 仍可根据用户状态把同一个单元编排成复习、热身、主训练或挑战。
- App 生成运行时 `SpeakingTask` 时，应优先使用 `taskHints`，再结合 catalog 联动和用户历史表现。

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

## 包联动元数据

`.trainpack` 包内固定格式仍然只包含：

- `manifest.json`
- `units.json`
- `items.jsonl`

包与包之间的联动关系不写入 `.trainpack` 内部，而统一写入外部 `catalog manifest`。原因是：

- 联动关系属于分发编排和学习路径，不属于包内原子训练内容本身。
- 保持 `.trainpack` 三文件结构稳定，避免后续每次调整推荐路径都重定义包内格式。
- 允许同一份包内容在不同 App 版本或不同发布阶段使用不同学习路径编排。

Catalog 中允许为每个 `packs[]` 条目补充以下联动字段：

- `seriesId`：系列稳定 ID，例如 `core-speaking-foundations`。
- `seriesTitle`：系列展示名称，例如“核心口语基础”。
- `seriesOrder`：该包在系列中的顺序，从 `1` 开始。
- `learningPath`：该包所属学习路径，例如 `Foundation`、`SocialConversation`、`WorkplaceCommunication`。
- `prerequisitePackIds`：建议先完成的前置包列表。
- `recommendedNextPackIds`：建议后续继续学习的下一包列表。
- `companionPackIds`：推荐并行学习或互补学习的包列表。

约束：

- `seriesId`、`seriesTitle`、`seriesOrder` 要么同时出现，要么同时不出现。
- `prerequisitePackIds`、`recommendedNextPackIds`、`companionPackIds` 中的每个值都必须是现有 `packId`。
- App 不应把这些字段视为强制业务约束，而应视为“推荐学习路径”和“展示编排”元数据。

一个带联动字段的 catalog 条目示例：

```json
{
  "id": "small-talk-1",
  "title": "Small Talk 1",
  "description": "面向日常寒暄、轻松开场、活动现场、工作近况、周末、天气、兴趣追问和自然收尾的高频 small talk 训练包。",
  "packType": "Scenario",
  "version": "2026.06.02",
  "levelHint": "A2-B1",
  "unitCount": 8,
  "itemCount": 32,
  "estimatedMinutes": 120,
  "sizeBytes": 6457,
  "sha256": "9e107b2a9e8256dfc6ab7d0e635f2085f363fe8940f027b8c366539c1b27ae5e",
  "fileName": "small-talk-1-2026.06.02.trainpack",
  "tags": ["Speaking", "SmallTalk", "Core", "A2-B1"],
  "trainingModes": ["Recall", "Shadow", "Respond"],
  "urls": [
    "https://github.com/huarangmeng/vocabulary-packs/releases/download/trainpack-2026.06.02/small-talk-1-2026.06.02.trainpack"
  ],
  "seriesId": "social-speaking-path",
  "seriesTitle": "社交口语路径",
  "seriesOrder": 1,
  "learningPath": "SocialConversation",
  "prerequisitePackIds": ["core-chunks-1"],
  "recommendedNextPackIds": ["meeting-communication-1"],
  "companionPackIds": ["core-chunks-1"]
}
```

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
