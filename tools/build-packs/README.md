# Build Trainpacks

该目录用于放置 `.trainpack` 生成脚本。

当前约定：

- 生成结果输出到 `dist/trainpacks/`。
- `.trainpack` 不提交 Git。
- `.trainpack` 只通过 GitHub Releases 发布。
- 发布前必须生成并校验 `latest.json` 中的 `sha256`。
- 发布前必须符合根目录 `TRAINPACK_FORMAT.md`。
- 发布前必须通过 `python3 tools/validate_trainpack.py <package> manifests/latest.json`。

建议输出结构：

```text
dist/trainpacks/
  core-chunks-1-2026.06.02.trainpack
  latest.json
  latest.json.sha256
```

当前示例脚本：

- `build_core_chunks_pack.py`：生成 `core-chunks-1` 示例训练包。

校验示例：

```bash
python3 tools/validate_trainpack.py \
  dist/trainpacks/core-chunks-1-2026.06.02.trainpack \
  manifests/latest.json
```
