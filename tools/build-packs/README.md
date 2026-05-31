# Build Packs

该目录用于后续放置 `.vocabpack` 生成脚本。

当前约定：

- 生成结果输出到 `dist/vocabpacks/`。
- `.vocabpack` 不提交 Git。
- `.vocabpack` 只通过 GitHub Releases 发布。
- 发布前必须生成并校验 `latest.json` 中的 `sha256`。
- 发布前必须符合根目录 `PACK_FORMAT.md`。
- 发布前必须通过 `python3 tools/validate_vocabpack.py <package> manifests/latest.json`。

建议输出结构：

```text
dist/vocabpacks/
  ielts-academic-core-2026.06.01.vocabpack
  toefl-academic-core-2026.06.01.vocabpack
  latest.json
  latest.json.sha256
```

校验示例：

```bash
python3 tools/validate_vocabpack.py \
  dist/vocabpacks/ielts-academic-core-2026.06.01.vocabpack \
  manifests/latest.json
```
