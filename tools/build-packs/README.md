# Build Trainpacks

该目录用于放置 `.trainpack` 生成脚本。

当前约定：

- 生成结果输出到 `dist/trainpacks/`。
- `.trainpack` 不提交 Git。
- `.trainpack` 只通过 GitHub Releases 发布。
- 版本号、Release tag、`createdAt` 和 zip 时间戳统一来自 `release_config.py`。
- 发布前必须生成并校验 `latest.json` 中的 `sha256`。
- 发布前必须符合根目录 `TRAINPACK_FORMAT.md`。
- 发布前必须通过 `python3 tools/validate_trainpack.py <package> manifests/latest.json`。

建议输出结构：

```text
dist/trainpacks/
  core-chunks-1-2026.06.02.trainpack
  small-talk-1-2026.06.02.trainpack
  meeting-communication-1-2026.06.02.trainpack
  latest.json
  latest.json.sha256
```

当前脚本：

- `build_core_chunks_pack.py`：生成 `core-chunks-1` 示例训练包。
- `build_small_talk_pack.py`：生成 `small-talk-1` 训练包。
- `build_meeting_communication_pack.py`：生成 `meeting-communication-1` 训练包。
- `trainpack_builder.py`：提供共用的 trainpack 打包与 catalog 写出逻辑。

推荐统一执行：

```bash
python3 tools/release_trainpacks.py
```

如需单独调试：

```bash
python3 tools/build-packs/build_core_chunks_pack.py
python3 tools/build-packs/build_small_talk_pack.py
python3 tools/build-packs/build_meeting_communication_pack.py
```

校验示例：

```bash
python3 tools/validate_trainpack.py \
  dist/trainpacks/core-chunks-1-2026.06.02.trainpack \
  manifests/latest.json
```
