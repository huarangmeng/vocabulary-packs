# Vocabulary Trainpacks

`Vocabulary Trainpacks` 是 `Vocabulary` App 的官方口语训练包分发仓库。

这个仓库只负责四件事：

- 维护官方训练包目录文件 `catalog manifest`。
- 维护 `.trainpack` 固定格式契约和 schema。
- 维护训练包构建与校验脚本。
- 通过 GitHub Releases 发布 `.trainpack` 官方训练包。

## 当前决策

- 主分发源：GitHub Releases。
- 不需要个人域名。
- 不需要对象存储账号。
- 不需要绑定支付方式。
- App 通过 `latest.json` 获取训练包列表，再下载 `.trainpack`。
- 所有下载文件必须通过 `sha256` 校验后才能导入。
- 官方训练包不直接写入用户自建 `study_items`。

## 仓库结构

```text
vocabulary-packs/
  README.md
  TRAINPACK_FORMAT.md
  manifests/
    latest.json
    2026.06.02.json
  schemas/
    catalog.schema.json
    trainpack-manifest.schema.json
    unit.schema.json
    item.schema.json
  tools/
    validate_trainpack.py
    build-packs/
      README.md
      build_core_chunks_pack.py
  .github/
    workflows/
      release-packs.yml
```

## 存储规则

提交到 Git：

- `README.md`：仓库说明。
- `TRAINPACK_FORMAT.md`：`.trainpack` 固定格式契约。
- `manifests/*.json`：训练包目录文件。
- `schemas/*.json`：格式约束 schema。
- `tools/`：训练包构建和校验脚本。
- `.github/workflows/`：Release 发布流程。

不提交到 Git：

- `.trainpack` 训练包。
- 构建过程中的临时文件。
- 本地下载或测试产生的数据。

`.trainpack` 文件只作为 GitHub Release Asset 上传，避免二进制文件进入 Git 历史。

## 格式规则

所有训练包必须遵守 [TRAINPACK_FORMAT.md](TRAINPACK_FORMAT.md)。

固定规则：

- `.trainpack` 必须是 zip 文件。
- 包内只能有 `manifest.json`、`units.json` 和 `items.jsonl`。
- `manifest.json` 必须符合 `schemas/trainpack-manifest.schema.json`。
- `units.json` 中的每个单元必须符合 `schemas/unit.schema.json`。
- `items.jsonl` 每一行必须符合 `schemas/item.schema.json`。
- 外部 catalog 必须符合 `schemas/catalog.schema.json`。
- 发布前必须通过 `tools/validate_trainpack.py` 校验。

## Release 规则

Release tag 使用日期版本：

```text
trainpack-2026.06.02
trainpack-2026.06.15
trainpack-2026.07.01
```

Release Asset 命名规则：

```text
core-chunks-1-2026.06.02.trainpack
small-talk-1-2026.06.02.trainpack
latest.json
latest.json.sha256
```

## 当前示例训练包

当前仓库内置一个最小可用示例构建脚本：

- `core-chunks-1`：高频口语表达块 1。

它用于固定 `.trainpack` 结构、校验流程和 App 接入边界，不代表最终内容规模。

## 手动发布

生成训练包后放到本地 `dist/trainpacks/`，该目录内容默认不提交 Git。

构建示例训练包：

```bash
python3 tools/build-packs/build_core_chunks_pack.py
```

校验训练包格式：

```bash
python3 tools/validate_trainpack.py \
  dist/trainpacks/core-chunks-1-2026.06.02.trainpack \
  manifests/latest.json
```

计算校验值：

```bash
shasum -a 256 dist/trainpacks/*.trainpack
shasum -a 256 dist/trainpacks/latest.json
```

创建 Release 并上传：

```bash
gh release create trainpack-2026.06.02 \
  --repo huarangmeng/vocabulary-packs \
  --title "Vocabulary Trainpacks 2026.06.02" \
  --notes "Initial official speaking trainpacks." \
  dist/trainpacks/*.trainpack \
  dist/trainpacks/latest.json \
  dist/trainpacks/latest.json.sha256
```

追加或覆盖 manifest：

```bash
gh release upload trainpack-2026.06.02 \
  --repo huarangmeng/vocabulary-packs \
  dist/trainpacks/latest.json \
  dist/trainpacks/latest.json.sha256 \
  --clobber
```

GitHub Actions 中的 `Release Vocabulary Trainpack Manifests` 只负责发布 `manifests/*.json`。真实 `.trainpack` 文件按设计不提交 Git，需要在本地生成后用 `gh release upload` 上传为 Release Asset。

## Manifest 规则

App 读取 `latest.json` 后展示“官方训练包”列表。

`latest.json` 基本结构：

```json
{
  "schemaVersion": 1,
  "catalogVersion": "2026.06.02",
  "generatedAt": "2026-06-02T00:00:00Z",
  "minAppVersion": "1.1.0",
  "packs": []
}
```

每个训练包条目至少包含：

- `id`：稳定训练包 ID。
- `title`：展示名称。
- `description`：展示描述。
- `packType`：训练包类型。
- `version`：训练包版本。
- `unitCount`：单元数量。
- `itemCount`：内容项数量。
- `estimatedMinutes`：预计学习时长。
- `sizeBytes`：下载大小。
- `sha256`：文件校验值。
- `fileName`：Release asset 文件名。
- `trainingModes`：支持的训练模式。
- `urls`：下载地址列表。

## 下载地址格式

```text
https://github.com/huarangmeng/vocabulary-packs/releases/download/<tag>/<asset-name>
```

示例：

```text
https://github.com/huarangmeng/vocabulary-packs/releases/download/trainpack-2026.06.02/core-chunks-1-2026.06.02.trainpack
```

## App 接入规则

- App 先拉取 catalog，再展示“官方训练包”。
- App 下载 `.trainpack` 到临时文件。
- App 校验 catalog 中声明的 `sha256`。
- App 解包并校验包内 `manifest.json`、`units.json` 和 `items.jsonl`。
- 官方训练包只进入官方内容层，不自动加入用户自建内容。
- 用户手动选择“加入训练计划”后，才创建单元级激活记录。

## 访问量边界

GitHub Releases 官方边界：单个 Release 最多 `1000` 个 assets；单个 asset 必须小于 `2 GiB`；Release 资产没有官方声明的总大小和带宽限制。

工程上建议：

- 常规训练包尽量控制在 `1-10 MB`。
- 单个训练包建议不超过 `50 MB`。
- 如果超过 `50 MB`，应优先拆成多个主题包。
