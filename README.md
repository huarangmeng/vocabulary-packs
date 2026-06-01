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

版本入口：

- 当前发布版本、Release tag、catalog 时间戳和 zip 时间戳统一由 [release_config.py](file:///Users/bytedance/AndroidStudioProjects/vocabulary-packs/tools/build-packs/release_config.py) 管理。
- 如需切换版本，优先修改 `tools/build-packs/release_config.py`，不要在各个构建脚本里单独改常量。

## 仓库结构

```text
vocabulary-packs/
  README.md
  TRAINPACK_FORMAT.md
  content/
    packs/
      core-chunks-1.json
      small-talk-1.json
      meeting-communication-1.json
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
    release_trainpacks.py
    build-packs/
      README.md
      build_from_content.py
      trainpack_builder.py
  .github/
    workflows/
      release-packs.yml
```

## 存储规则

提交到 Git：

- `README.md`：仓库说明。
- `TRAINPACK_FORMAT.md`：`.trainpack` 固定格式契约。
- `content/packs/*.json`：官方训练包内容源文件。
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

当前仓库内置六份官方训练包内容文件：

- `content/packs/core-chunks-1.json`：高频口语表达块 1。
- `content/packs/core-chunks-2.json`：高频口语表达块 2。
- `content/packs/small-talk-1.json`：Small Talk 1。
- `content/packs/small-talk-2.json`：Small Talk 2。
- `content/packs/meeting-communication-1.json`：会议沟通 1。
- `content/packs/meeting-communication-2.json`：会议沟通 2。

这些 JSON 文件是首批正式发布候选的源内容；Python 只负责读取内容、构建 `.trainpack`、生成 catalog 并执行校验。

## 手动发布

生成训练包后放到本地 `dist/trainpacks/`，该目录内容默认不提交 Git。

推荐直接执行统一发布辅助脚本：

```bash
python3 tools/release_trainpacks.py
```

这会：

- 构建全部官方训练包。
- 生成聚合后的 `manifests/latest.json`。
- 生成 `dist/trainpacks/latest.json` 和 `latest.json.sha256`。
- 逐个校验所有 `.trainpack`。

如需单独调试某一个训练包，也可以直接传入对应 JSON：


```bash
python3 tools/build-packs/build_from_content.py content/packs/core-chunks-2.json
python3 tools/build-packs/build_from_content.py content/packs/small-talk-2.json
python3 tools/build-packs/build_from_content.py content/packs/meeting-communication-2.json
python3 tools/build-packs/build_from_content.py content/packs/small-talk-1.json
python3 tools/build-packs/build_from_content.py content/packs/meeting-communication-1.json
python3 tools/build-packs/build_from_content.py content/packs/core-chunks-1.json
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
python3 tools/print_release_command.py
```

如果你已经执行过 `python3 tools/release_trainpacks.py`，上面的脚本会直接打印当前版本对应的两条命令：

- `gh release create ...`
- `gh release upload ...`

这样发布命令里的 `tag`、`title`、`notes` 和 asset 路径都会从统一配置自动推导，不需要手写版本号。

只想看覆盖上传命令时，也可以直接复制脚本输出中的第二段：

```bash
python3 tools/print_release_command.py
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

## 包联动规则

当前“包联动”统一定义在 `catalog manifest`，而不是 `.trainpack` 包内。这样做的原则是：

- `.trainpack` 继续只承载稳定内容结构，不承担学习路径编排职责。
- 包联动属于“目录层元数据”，便于后续只改 catalog 就能调整推荐顺序和展示策略。
- App 读取 `latest.json` 后，可直接利用联动字段做“先学什么、后学什么、一起学什么”的展示与激活引导。

当前支持的联动字段：

- `seriesId`
- `seriesTitle`
- `seriesOrder`
- `learningPath`
- `prerequisitePackIds`
- `recommendedNextPackIds`
- `companionPackIds`

建议用法：

- `seriesId + seriesOrder`：把 `core-chunks-1`、`core-chunks-2` 这类同系列包串成稳定序列。
- `prerequisitePackIds`：表达“建议先完成基础包，再进入当前包”。
- `recommendedNextPackIds`：表达当前包学完后的下一步推荐。
- `companionPackIds`：表达可并行或互补训练的包。

首批三包的建议联动：

- `core-chunks-1`：作为基础入口，推荐后续进入 `small-talk-1` 和 `meeting-communication-1`。
- `small-talk-1`：前置建议为 `core-chunks-1`，并与 `core-chunks-1` 形成互补学习。
- `meeting-communication-1`：前置建议为 `core-chunks-1`，并与 `small-talk-1`、`core-chunks-1` 形成互补学习。

## 下载地址格式

```text
https://github.com/huarangmeng/vocabulary-packs/releases/download/<tag>/<asset-name>
```

示例：

```text
https://github.com/huarangmeng/vocabulary-packs/releases/download/trainpack-2026.06.02/core-chunks-1-2026.06.02.trainpack
```

另外两包示例：

```text
https://github.com/huarangmeng/vocabulary-packs/releases/download/trainpack-2026.06.02/small-talk-1-2026.06.02.trainpack
https://github.com/huarangmeng/vocabulary-packs/releases/download/trainpack-2026.06.02/meeting-communication-1-2026.06.02.trainpack
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
