# Build Trainpacks

该目录用于放置 `.trainpack` 通用构建脚本。

当前约定：

- 生成结果输出到 `dist/trainpacks/`。
- `.trainpack` 不提交 Git。
- `.trainpack` 只通过 GitHub Releases 发布。
- 版本号、Release tag、`createdAt` 和 zip 时间戳统一来自 `release_config.py`。
- 发音参考由 `pronunciation_reference_builder.py` 离线生成，随包写入 `pronunciation_references.jsonl`。
- 发布前必须生成并校验 `latest.json` 中的 `sha256`。
- 发布前必须符合根目录 `TRAINPACK_FORMAT.md`。
- 发布前必须通过 `python3 tools/validate_trainpack.py <package> manifests/latest.json`。

建议输出结构：

```text
dist/trainpacks/
  core-repair-1-2026.06.03.trainpack
  small-talk-actions-1-2026.06.03.trainpack
  meeting-actions-1-2026.06.03.trainpack
  opinion-builder-1-2026.06.03.trainpack
  pronunciation-risk-1-2026.06.03.trainpack
  latest.json
  latest.json.sha256
```

当前结构：

- `build_from_content.py`：读取 `content/packs/*.json` 并构建一个或多个 trainpack。
- `trainpack_builder.py`：提供内容加载、trainpack 打包与 catalog 写出逻辑。
- `pronunciation_reference_builder.py`：生成 `en-US` 和 `en-GB` 双方言发音参考索引。
- `release_config.py`：统一管理版本、tag、createdAt 和 zip 时间戳。
- `requirements-pronunciation.txt`：可选离线词典依赖，当前用于引入 CMUdict 质量的词级音素候选。

内容源文件不放在这个目录，而是统一放在仓库根目录的 `content/packs/` 下。

推荐统一执行：

```bash
python3 -m venv .venv-pronunciation
. .venv-pronunciation/bin/activate
python -m pip install -r tools/build-packs/requirements-pronunciation.txt
python3 tools/release_trainpacks.py
```

如需单独调试：

```bash
python3 tools/build-packs/build_from_content.py content/packs/core-repair-1.json
python3 tools/build-packs/build_from_content.py content/packs/small-talk-actions-1.json
python3 tools/build-packs/build_from_content.py content/packs/meeting-actions-1.json
```

校验示例：

```bash
python3 tools/validate_trainpack.py \
  dist/trainpacks/core-repair-1-2026.06.03.trainpack \
  manifests/latest.json
```
