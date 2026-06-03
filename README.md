# Vocabulary Official Speaking Packs

This repository is the external official content source for Vocabulary V2. It is intentionally clean because no previous trainpack release has shipped.

## Product Boundary

- Formal learning content is only authored official content or user-created content inside the app.
- This repository only produces official speaking-action packs.
- The app must not use this repository to provide open-ended AI generation, automatic translation, automatic correction, or a free content platform.
- AI can only help the app choose or explain the next in-task action inside official pack boundaries.

## V2 Content Model

```text
Catalog
-> Pack
-> Unit / SpeakingAct
-> Item / Move
-> PackVerified pronunciation reference
-> Today speaking queue
```

All source packs use `packType = SpeakingActs`. The physical `.trainpack` format remains:

```text
manifest.json
units.json
items.jsonl
pronunciation_references.jsonl
```

## Current Source Packs

| Pack | Goal | Units | Items | Path |
| --- | --- | ---: | ---: | --- |
| `core-repair-1` | 核心修复口语动作 1 | 5 | 20 | Foundation |
| `small-talk-actions-1` | 闲聊口语动作 1 | 6 | 24 | SocialConversation |
| `meeting-actions-1` | 会议口语动作 1 | 6 | 24 | WorkplaceCommunication |
| `opinion-builder-1` | 观点表达口语动作 1 | 5 | 20 | OpinionBuilder |
| `pronunciation-risk-1` | 发音与重音风险口语动作 1 | 5 | 20 | PronunciationRisk |

## Daily Queue Metadata

Catalog entries include `dailyQueueRoles`:

- `Review`
- `New`
- `Transfer`
- `WeakPoint`
- `Challenge`

The app uses those roles to build a daily queue of 4-12 short tasks. It should not show a fixed three-scene routine or a training-mode lobby.

## Pronunciation And Stress

The builder generates `pronunciation_references.jsonl` for `englishText`, `variants`, and `pronunciationTargets` in `en-US` and `en-GB`.

Generated references include:

- `phonemes`
- `words[].phonemes`
- `words[].lexicalStress`
- top-level `lexicalStress`
- top-level `sentenceStress`
- source URL, license, dialect, confidence, and provenance

Only `PackVerified` official references can trigger high-confidence pronunciation or stress feedback in the app. Missing or unverified references must fail release validation instead of silently becoming generated guesses.

## Build

```bash
cd /Users/bytedance/AndroidStudioProjects/vocabulary-packs
.venv-pronunciation/bin/python tools/release_trainpacks.py
```

The command writes:

```text
dist/trainpacks/*-2026.06.03.trainpack
dist/trainpacks/latest.json
dist/trainpacks/latest.json.sha256
manifests/latest.json
manifests/2026.06.03.json
content/generated-pronunciation-references/*.jsonl
```

## Release

Use the command printed by `tools/release_trainpacks.py`. It filters assets to the current version only.
