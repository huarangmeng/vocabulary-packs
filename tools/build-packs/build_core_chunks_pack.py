#!/usr/bin/env python3
from __future__ import annotations

from trainpack_builder import build_trainpack


UNIT_SPECS = [
    {
        "key": "clarify-001",
        "title": "请对方重复",
        "communicativeGoal": "没听清时礼貌请对方重复",
        "scene": "DailyConversation",
        "register": "Neutral",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Low",
            "pronunciationRisk": "Low",
        },
        "tags": ["Clarify", "Repair", "Listening"],
        "activationPrompts": [
            "你没听清对方最后一句话",
            "你想请对方说慢一点",
        ],
        "pronunciationFocus": ["didn't catch that", "again"],
        "items": [
            {
                "type": "Chunk",
                "englishText": "Could you say that again?",
                "chinesePrompt": "你能再说一遍吗？",
                "variants": ["Sorry, could you say that again?", "Could you repeat that?"],
                "notes": ["适合大多数日常和工作场景", "比 What? 更礼貌"],
                "pronunciationTargets": ["could you", "again"],
                "commonMistakes": ["What? say again.", "Repeat again."],
                "tags": ["Clarify", "Chunk"],
            },
            {
                "type": "Chunk",
                "englishText": "Sorry, I didn't catch that.",
                "chinesePrompt": "抱歉，我刚才没听清。",
                "variants": ["Sorry, I didn't catch the last part."],
                "notes": ["先道歉再请求重复更自然"],
                "pronunciationTargets": ["didn't catch that"],
                "commonMistakes": ["I don't hear clearly."],
                "tags": ["Clarify", "Chunk"],
            },
            {
                "type": "SentencePattern",
                "englishText": "Could you say that again a bit more slowly?",
                "chinesePrompt": "你能再说一遍并稍微说慢一点吗？",
                "variants": ["Could you say that a little more slowly?"],
                "notes": ["适合对方语速较快时"],
                "pronunciationTargets": ["a bit more slowly"],
                "commonMistakes": ["Say again slowly."],
                "tags": ["Clarify", "SentencePattern"],
                "slots": ["again", "a bit more slowly"],
                "sampleOutputs": ["Could you say that again a bit more slowly?"],
            },
            {
                "type": "DialogueTurn",
                "englishText": "Sorry, I didn't catch the last part.",
                "chinesePrompt": "抱歉，我最后那部分没听清。",
                "variants": [],
                "notes": ["适合会议或通话中使用"],
                "pronunciationTargets": ["the last part"],
                "commonMistakes": ["Last part I didn't hear."],
                "tags": ["Clarify", "DialogueTurn"],
                "contextText": "The deadline has been moved to next Thursday.",
                "responseRole": "Listener",
            },
        ],
    },
    {
        "key": "buy-time-001",
        "title": "争取思考时间",
        "communicativeGoal": "还没想好时先用保底表达稳住对话",
        "scene": "WorkConversation",
        "register": "Neutral",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Medium",
            "pronunciationRisk": "Low",
        },
        "tags": ["Repair", "ThinkingTime", "Chunk"],
        "activationPrompts": [
            "你需要几秒钟组织语言",
            "你还没完全想好答案",
        ],
        "pronunciationFocus": ["let me think", "for a second"],
        "items": [
            {
                "type": "RepairStrategy",
                "englishText": "Let me think for a second.",
                "chinesePrompt": "让我想一下。",
                "variants": ["Give me a second to think."],
                "notes": ["先稳住节奏，再继续说"],
                "pronunciationTargets": ["let me", "for a second"],
                "commonMistakes": ["I need think."],
                "tags": ["Repair", "ThinkingTime"],
                "repairType": "BuyTime",
            },
            {
                "type": "Chunk",
                "englishText": "That's a good question.",
                "chinesePrompt": "这是个好问题。",
                "variants": ["That's actually a really good question."],
                "notes": ["适合先接住问题，再组织回答"],
                "pronunciationTargets": ["good question"],
                "commonMistakes": ["Your question is good."],
                "tags": ["Repair", "Chunk"],
            },
            {
                "type": "SentencePattern",
                "englishText": "I think there are a couple of ways to look at it.",
                "chinesePrompt": "我觉得这件事可以从几个角度来看。",
                "variants": ["There are probably a few ways to think about it."],
                "notes": ["适合展开观点前做缓冲"],
                "pronunciationTargets": ["a couple of", "look at it"],
                "commonMistakes": ["There have several angles."],
                "tags": ["Repair", "SentencePattern"],
                "slots": ["a couple of ways", "look at it"],
                "sampleOutputs": ["I think there are a couple of ways to look at it."],
            },
            {
                "type": "DialogueTurn",
                "englishText": "Let me think for a second. I would probably start with the budget.",
                "chinesePrompt": "让我想一下。我可能会先从预算开始。",
                "variants": [],
                "notes": ["把争取时间和正式回答接起来"],
                "pronunciationTargets": ["probably start", "the budget"],
                "commonMistakes": ["Wait, I answer budget first."],
                "tags": ["Repair", "DialogueTurn"],
                "contextText": "How would you improve this project plan?",
                "responseRole": "Speaker",
            },
        ],
    },
    {
        "key": "opinion-001",
        "title": "表达个人看法",
        "communicativeGoal": "自然表达个人观点并保留一定弹性",
        "scene": "Meeting",
        "register": "Neutral",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Medium",
            "pronunciationRisk": "Medium",
        },
        "tags": ["Opinion", "Meeting", "Chunk"],
        "activationPrompts": [
            "你想表达自己的看法",
            "你想给出较为温和的意见",
        ],
        "pronunciationFocus": ["I think", "to be honest"],
        "items": [
            {
                "type": "Chunk",
                "englishText": "I think we should start with the customer problem.",
                "chinesePrompt": "我觉得我们应该先从用户问题开始。",
                "variants": ["I think the customer problem should come first."],
                "notes": ["简单直接，适合大多数会议场景"],
                "pronunciationTargets": ["I think we should", "customer problem"],
                "commonMistakes": ["I think should start from customer problem."],
                "tags": ["Opinion", "Chunk"],
            },
            {
                "type": "SentencePattern",
                "englishText": "To be honest, I'm not sure that's the best place to start.",
                "chinesePrompt": "说实话，我不确定那是不是最好的起点。",
                "variants": ["Honestly, I'm not sure that's the best starting point."],
                "notes": ["适合表达保留意见"],
                "pronunciationTargets": ["to be honest", "best place to start"],
                "commonMistakes": ["I am not sure that is best start."],
                "tags": ["Opinion", "SentencePattern"],
                "slots": ["to be honest", "best place to start"],
                "sampleOutputs": ["To be honest, I'm not sure that's the best place to start."],
            },
            {
                "type": "DialogueTurn",
                "englishText": "I see your point, but I think the timeline is still too tight.",
                "chinesePrompt": "我理解你的意思，但我觉得时间线还是太紧了。",
                "variants": [],
                "notes": ["先认可，再提出不同意见"],
                "pronunciationTargets": ["I see your point", "too tight"],
                "commonMistakes": ["I know your meaning but timeline is tight."],
                "tags": ["Opinion", "DialogueTurn"],
                "contextText": "We can probably finish this by Friday.",
                "responseRole": "Participant",
            },
            {
                "type": "PronunciationTarget",
                "englishText": "to be honest",
                "chinesePrompt": "说实话",
                "variants": [],
                "notes": ["重点关注弱读和连读"],
                "pronunciationTargets": ["to be honest"],
                "commonMistakes": [],
                "tags": ["Opinion", "PronunciationTarget"],
                "focusText": "to be honest",
                "focusType": "ChunkStress",
            },
        ],
    },
]
def build():
    return build_trainpack(
        pack_id="core-chunks-1",
        title="高频口语表达块 1",
        description="面向日常交流与工作沟通的高频英文表达块训练包。",
        pack_type="CoreChunks",
        level_hint="A2-B1",
        estimated_minutes=45,
        tags=["Speaking", "Chunks", "A2-B1"],
        training_modes=["Recall", "Shadow", "Respond"],
        unit_specs=UNIT_SPECS,
    )


def main() -> None:
    result = build()
    print(f"Generated: {result.package_path}")
    print(f"Units: {result.unit_count}")
    print(f"Items: {result.item_count}")
    print(f"Size: {result.size_bytes} bytes")
    print(f"SHA-256: {result.sha256}")


if __name__ == "__main__":
    main()
