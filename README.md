# Vocabulary Packs

`Vocabulary Packs` 是 `Vocabulary` App 的外部词库分发仓库。仓库本身只维护 manifest、来源说明、许可证说明和发布流程；实际 `.vocabpack` 文件通过 GitHub Releases 的 Release Assets 分发。

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
  LICENSES.md
  manifests/
    latest.json
    2026.06.01.json
  sources/
    ielts-academic-core.md
    toefl-academic-core.md
  tools/
    build-packs/
  .github/
    workflows/
      release-packs.yml
```

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
