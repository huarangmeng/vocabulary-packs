# Build Packs

该目录用于后续放置 `.vocabpack` 生成脚本。

当前约定：

- 生成结果输出到 `dist/vocabpacks/`。
- `.vocabpack` 不提交 Git。
- `.vocabpack` 只通过 GitHub Releases 发布。
- 发布前必须生成并校验 `latest.json` 中的 `sha256`。

建议输出结构：

```text
dist/vocabpacks/
  ielts-academic-core-2026.06.01.vocabpack
  toefl-academic-core-2026.06.01.vocabpack
  latest.json
  latest.json.sha256
```
