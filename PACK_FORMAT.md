# Vocabulary Pack Format

本文档是 `.vocabpack` 的固定格式契约。后续所有词库都必须遵守该格式，不允许每个词库自行增加不同的顶层结构。

## 文件格式

`.vocabpack` 必须是 zip 文件，且根目录只允许包含：

```text
manifest.json
entries.jsonl
```

要求：

- `manifest.json` 必须是 UTF-8 JSON。
- `entries.jsonl` 必须是 UTF-8 JSON Lines。
- `entries.jsonl` 每一行必须是一个完整词条 JSON。
- zip 内不允许目录、不允许嵌套路径、不允许额外文件。
- zip 内文件名必须完全匹配，区分大小写。

## 包内 Manifest

`manifest.json` 必须包含：

```json
{
  "schemaVersion": 1,
  "bookId": "ielts-academic-core",
  "bookVersion": "2026.06.01",
  "title": "雅思学术核心词库",
  "description": "面向 IELTS Academic 阅读、写作和口语场景的核心学术词汇。",
  "itemCount": 54,
  "createdAt": "2026-06-01T00:00:00Z",
  "entryFile": "entries.jsonl"
}
```

字段约束：

- `schemaVersion`：固定为 `1`。
- `bookId`：小写字母、数字和连字符，例如 `ielts-academic-core`。
- `bookVersion`：日期版本，例如 `2026.06.01`。
- `title`：展示名称。
- `description`：展示描述。
- `itemCount`：必须等于 `entries.jsonl` 实际行数。
- `createdAt`：UTC ISO-8601 时间，必须以 `Z` 结尾。
- `entryFile`：固定为 `entries.jsonl`。

## 词条 Entry

`entries.jsonl` 中每行必须包含：

```json
{
  "id": "ielts-academic-core:analyse",
  "order": 1,
  "type": "WordOrPhrase",
  "englishText": "analyse",
  "chinesePrompt": "分析；剖析",
  "partOfSpeech": "verb",
  "definitionEn": "to examine information carefully in order to understand patterns, causes, or meaning",
  "exampleEn": "Researchers analyse survey responses before drawing conclusions.",
  "exampleZh": "研究人员在得出结论前会分析问卷回答。",
  "synonyms": ["examine", "study", "evaluate"],
  "wordFamily": ["analysis", "analyst", "analytical"],
  "difficulty": "B2-C1",
  "tags": ["IELTS", "Academic", "Core"]
}
```

字段约束：

- `id`：全局稳定 ID，格式为 `{bookId}:{entryKey}`。
- `order`：从 `1` 开始连续递增。
- `type`：固定枚举，目前支持 `WordOrPhrase`、`Sentence`、`Logic`。
- `englishText`：英文表达，不能为空。
- `chinesePrompt`：中文提示，不能为空。
- `partOfSpeech`：词性或类型标记，不能为空；句子类可用 `sentence`。
- `definitionEn`：英文释义，不能为空。
- `exampleEn`：英文例句，不能为空。
- `exampleZh`：中文例句，不能为空。
- `synonyms`：字符串数组，可以为空数组。
- `wordFamily`：字符串数组，可以为空数组。
- `difficulty`：难度标记，例如 `A2-B1`、`B2-C1`。
- `tags`：字符串数组，至少包含一个标签。

## 外部 Catalog

`manifests/latest.json` 和版本化 catalog 必须包含：

```json
{
  "schemaVersion": 1,
  "catalogVersion": "2026.06.01",
  "generatedAt": "2026-06-01T00:00:00Z",
  "minAppVersion": "1.0.0",
  "books": [
    {
      "id": "ielts-academic-core",
      "title": "雅思学术核心词库",
      "description": "面向 IELTS Academic 阅读、写作和口语场景的核心学术词汇。",
      "version": "2026.06.01",
      "itemCount": 54,
      "sizeBytes": 8108,
      "sha256": "75d601f0c9633e992cb3e2ada20dd6cf81d8e3785a6a1c6994b348d582a06126",
      "fileName": "ielts-academic-core-2026.06.01.vocabpack",
      "tags": ["IELTS", "Academic", "B2-C1"],
      "urls": [
        "https://github.com/huarangmeng/vocabulary-packs/releases/download/vocab-2026.06.01/ielts-academic-core-2026.06.01.vocabpack"
      ]
    }
  ]
}
```

Catalog 中的 `books[].id`、`books[].version`、`books[].itemCount` 必须和 `.vocabpack` 包内 `manifest.json` 对齐。

## 校验命令

生成或发布前必须执行：

```bash
python3 tools/validate_vocabpack.py dist/vocabpacks/ielts-academic-core-2026.06.01.vocabpack manifests/latest.json
```

该命令会检查：

- zip 包结构。
- 包内 manifest 字段。
- entries JSONL 字段。
- `itemCount` 是否一致。
- `order` 是否连续。
- entry id 是否唯一。
- catalog 中的 `sha256`、大小、URL、文件名和包内容是否匹配。
