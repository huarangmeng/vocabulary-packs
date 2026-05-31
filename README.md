# Vocabulary Packs

`Vocabulary Packs` 是 `Vocabulary` App 的外部词库包分发仓库。

这个仓库只负责三件事：

- 维护词库目录文件 `manifest`。
- 通过 GitHub Releases 发布 `.vocabpack` 词库包。
- 给 App 提供稳定的下载地址和完整性校验信息。

## 当前决策

- 主分发源：GitHub Releases。
- 不需要个人域名。
- 不需要对象存储账号。
- 不需要绑定支付方式。
- App 通过 `latest.json` 获取词库列表，再下载 `.vocabpack`。
- 所有下载文件必须通过 `sha256` 校验后才能导入。

## 仓库结构

```text
vocabulary-packs/
  README.md
  PACK_FORMAT.md
  manifests/
    latest.json
    2026.06.01.json
  schemas/
    catalog.schema.json
    package-manifest.schema.json
    entry.schema.json
  tools/
    validate_vocabpack.py
    build-packs/
  .github/
    workflows/
      release-packs.yml
```

## 存储规则

提交到 Git：

- `README.md`：仓库说明。
- `PACK_FORMAT.md`：`.vocabpack` 固定格式契约。
- `manifests/*.json`：词库目录文件。
- `schemas/*.json`：格式约束 schema。
- `tools/`：后续词库包构建脚本。
- `.github/workflows/`：Release 发布流程。

不提交到 Git：

- `.vocabpack` 词库包。
- 构建过程中的临时文件。
- 本地下载或测试产生的数据。

`.vocabpack` 文件只作为 GitHub Release Asset 上传，避免二进制文件进入 Git 历史。

## 格式规则

所有词库包必须遵守 [PACK_FORMAT.md](PACK_FORMAT.md)。

固定规则：

- `.vocabpack` 必须是 zip 文件。
- 包内只能有 `manifest.json` 和 `entries.jsonl`。
- `manifest.json` 必须符合 `schemas/package-manifest.schema.json`。
- `entries.jsonl` 每行必须符合 `schemas/entry.schema.json`。
- 外部 catalog 必须符合 `schemas/catalog.schema.json`。
- 发布前必须通过 `tools/validate_vocabpack.py` 校验。

## Release 规则

Release tag 使用日期版本：

```text
vocab-2026.06.01
vocab-2026.06.15
vocab-2026.07.01
```

Release Asset 命名规则：

```text
ielts-academic-core-2026.06.01.vocabpack
toefl-academic-core-2026.06.01.vocabpack
latest.json
latest.json.sha256
```

## 手动发布

生成词库包后放到本地 `dist/vocabpacks/`，该目录内容默认不提交 Git。

计算校验值：

```bash
shasum -a 256 dist/vocabpacks/*.vocabpack
shasum -a 256 dist/vocabpacks/latest.json
```

校验词库格式：

```bash
python3 tools/validate_vocabpack.py \
  dist/vocabpacks/ielts-academic-core-2026.06.01.vocabpack \
  manifests/latest.json
```

创建 Release 并上传：

```bash
gh release create vocab-2026.06.01 \
  --repo huarangmeng/vocabulary-packs \
  --title "Vocabulary Packs 2026.06.01" \
  --notes "Initial vocabulary packs." \
  dist/vocabpacks/*.vocabpack \
  dist/vocabpacks/latest.json
```

追加或覆盖 manifest：

```bash
gh release upload vocab-2026.06.01 \
  --repo huarangmeng/vocabulary-packs \
  dist/vocabpacks/latest.json \
  --clobber
```

GitHub Actions 中的 `Release Vocabulary Manifests` 只负责发布 `manifests/*.json`。真实 `.vocabpack` 文件按设计不提交 Git，需要在本地生成后用 `gh release upload` 上传为 Release Asset。

## Manifest 规则

App 读取 `latest.json` 后展示“其他词库”列表。

`latest.json` 基本结构：

```json
{
  "schemaVersion": 1,
  "catalogVersion": "2026.06.01",
  "generatedAt": "2026-06-01T00:00:00Z",
  "minAppVersion": "1.0.0",
  "books": []
}
```

每个词库条目后续至少包含：

- `id`：稳定词库 ID。
- `title`：展示名称。
- `version`：词库版本。
- `itemCount`：条目数量。
- `sizeBytes`：下载大小。
- `sha256`：文件校验值。
- `urls`：下载地址列表。

## 下载地址格式

```text
https://github.com/huarangmeng/vocabulary-packs/releases/download/<tag>/<asset-name>
```

示例：

```text
https://github.com/huarangmeng/vocabulary-packs/releases/download/vocab-2026.06.01/ielts-academic-core-2026.06.01.vocabpack
```

## App 接入规则

- App 先拉取 manifest，再展示“其他词库”。
- App 下载 `.vocabpack` 到临时文件。
- App 校验 manifest 中声明的 `sha256`。
- App 解包并校验包内 `manifest.json`。
- 外部词库只进入“其他词库”，不自动加入“我的词库”。
- 用户手动选择加入后，才复制为本地学习内容。

## 访问量边界

GitHub Releases 官方边界：单个 Release 最多 `1000` 个 assets；单个 asset 必须小于 `2 GiB`；Release 资产没有官方声明的总大小和带宽限制。

工程上仍建议单个词库包控制在 `200 MB` 以内，常规词库尽量控制在 `2-20 MB`。
