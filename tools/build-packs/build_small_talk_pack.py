#!/usr/bin/env python3
from __future__ import annotations

from trainpack_builder import build_trainpack


UNIT_SPECS = [
    {
        "key": "greet-001",
        "title": "开启轻松寒暄",
        "communicativeGoal": "在见面或会前自然开启一段轻松对话",
        "scene": "SmallTalk",
        "register": "Casual",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Low",
            "pronunciationRisk": "Low",
        },
        "tags": ["SmallTalk", "Greeting", "WarmUp"],
        "activationPrompts": [
            "你刚到办公室，想和同事自然打个招呼",
            "你想在正式话题前先聊两句",
        ],
        "pronunciationFocus": ["how's it going", "been up to"],
        "items": [
            {
                "type": "Chunk",
                "englishText": "Hey, how's it going?",
                "chinesePrompt": "嗨，最近怎么样？",
                "variants": ["Hi, how are things going?"],
                "notes": ["适合熟悉但不太正式的场景"],
                "pronunciationTargets": ["how's it going"],
                "commonMistakes": ["How are you recently?"],
                "tags": ["SmallTalk", "Chunk"],
            },
            {
                "type": "Chunk",
                "englishText": "What have you been up to lately?",
                "chinesePrompt": "你最近都在忙什么？",
                "variants": ["What have you been up to these days?"],
                "notes": ["比 How are you 更容易引出内容"],
                "pronunciationTargets": ["been up to", "lately"],
                "commonMistakes": ["What are you busy these days?"],
                "tags": ["SmallTalk", "Chunk"],
            },
            {
                "type": "DialogueTurn",
                "englishText": "Hey, how's it going? You look busy today.",
                "chinesePrompt": "嗨，最近怎么样？你今天看起来挺忙的。",
                "variants": [],
                "notes": ["先寒暄，再自然带出观察"],
                "pronunciationTargets": ["you look busy"],
                "commonMistakes": ["You seem very busied today."],
                "tags": ["SmallTalk", "DialogueTurn"],
                "contextText": "你在茶水间遇到一位熟悉同事。",
                "responseRole": "Speaker",
            },
            {
                "type": "PronunciationTarget",
                "englishText": "How's it going?",
                "chinesePrompt": "最近怎么样？",
                "variants": [],
                "notes": ["关注连读和弱读，避免逐词顿开"],
                "pronunciationTargets": ["how's it going"],
                "commonMistakes": [],
                "tags": ["SmallTalk", "PronunciationTarget"],
                "focusText": "How's it going?",
                "focusType": "Linking",
            },
        ],
    },
    {
        "key": "weekend-001",
        "title": "聊周末和近况",
        "communicativeGoal": "围绕周末安排和最近生活自然延展寒暄",
        "scene": "SmallTalk",
        "register": "Casual",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Medium",
            "pronunciationRisk": "Low",
        },
        "tags": ["SmallTalk", "Weekend", "FollowUp"],
        "activationPrompts": [
            "你想问问对方周末过得怎么样",
            "你想顺着对方近况继续聊下去",
        ],
        "pronunciationFocus": ["did you get up to", "pretty low-key"],
        "items": [
            {
                "type": "Chunk",
                "englishText": "Did you do anything fun over the weekend?",
                "chinesePrompt": "你周末有做什么好玩的事吗？",
                "variants": ["Did you get up to anything fun over the weekend?"],
                "notes": ["很适合办公室和朋友间轻松寒暄"],
                "pronunciationTargets": ["anything fun", "over the weekend"],
                "commonMistakes": ["Did you play something fun in weekend?"],
                "tags": ["SmallTalk", "Chunk"],
            },
            {
                "type": "Chunk",
                "englishText": "It was pretty low-key, actually.",
                "chinesePrompt": "其实挺平淡的。",
                "variants": ["It was pretty quiet, actually."],
                "notes": ["适合回应自己周末没干什么大事"],
                "pronunciationTargets": ["pretty low-key"],
                "commonMistakes": ["It was very normal."],
                "tags": ["SmallTalk", "Chunk"],
            },
            {
                "type": "SentencePattern",
                "englishText": "I mostly stayed in and caught up on some rest.",
                "chinesePrompt": "我大多待在家里补了补觉。",
                "variants": ["I mostly stayed home and got some rest."],
                "notes": ["适合给出自然但简单的近况描述"],
                "pronunciationTargets": ["mostly stayed in", "caught up on"],
                "commonMistakes": ["I stayed at home for rest."],
                "tags": ["SmallTalk", "SentencePattern"],
                "slots": ["stayed in", "caught up on some rest"],
                "sampleOutputs": ["I mostly stayed in and caught up on some rest."],
            },
            {
                "type": "DialogueTurn",
                "englishText": "Did you do anything fun over the weekend, or did you mostly relax?",
                "chinesePrompt": "你周末有做什么好玩的事吗，还是主要都在休息？",
                "variants": [],
                "notes": ["给对方一个更容易接的回答范围"],
                "pronunciationTargets": ["mostly relax"],
                "commonMistakes": ["Weekend you did anything fun or relax?"],
                "tags": ["SmallTalk", "DialogueTurn"],
                "contextText": "周一早上，你在工位旁和同事聊天。",
                "responseRole": "Speaker",
            },
        ],
    },
    {
        "key": "weather-001",
        "title": "用天气和环境接话",
        "communicativeGoal": "用天气、通勤或环境话题自然接话，不让寒暄断掉",
        "scene": "SmallTalk",
        "register": "Casual",
        "difficulty": {
            "lexical": "A2-B1",
            "interactionPressure": "Medium",
            "pronunciationRisk": "Medium",
        },
        "tags": ["SmallTalk", "Weather", "Continuation"],
        "activationPrompts": [
            "你想用天气接一两句，不让对话突然结束",
            "你想抱怨一下天气或通勤，再自然转到别的话题",
        ],
        "pronunciationFocus": ["it's been", "on my way in"],
        "items": [
            {
                "type": "Chunk",
                "englishText": "The weather's been all over the place lately.",
                "chinesePrompt": "最近天气真是变化特别大。",
                "variants": ["The weather's been kind of all over the place lately."],
                "notes": ["很适合轻松抱怨或开话题"],
                "pronunciationTargets": ["weather's been", "all over the place"],
                "commonMistakes": ["The weather changes very much recently."],
                "tags": ["SmallTalk", "Chunk"],
            },
            {
                "type": "Chunk",
                "englishText": "It was pouring on my way in this morning.",
                "chinesePrompt": "我今天早上来的路上下大雨了。",
                "variants": ["It was absolutely pouring this morning on my way in."],
                "notes": ["适合带出通勤体验"],
                "pronunciationTargets": ["pouring", "on my way in"],
                "commonMistakes": ["I was in big rain on the way."],
                "tags": ["SmallTalk", "Chunk"],
            },
            {
                "type": "RepairStrategy",
                "englishText": "I don't know about you, but I'm ready for some sunshine.",
                "chinesePrompt": "不知道你怎么想，反正我是想见点太阳了。",
                "variants": ["I don't know about you, but I'm definitely ready for some sunshine."],
                "notes": ["适合表达个人感受，又能邀请对方接话"],
                "pronunciationTargets": ["I don't know about you", "ready for some sunshine"],
                "commonMistakes": ["I want sunshine now."],
                "tags": ["SmallTalk", "RepairStrategy"],
                "repairType": "BridgeToOpinion",
            },
            {
                "type": "DialogueTurn",
                "englishText": "The weather's been all over the place lately. I had no idea what to wear this morning.",
                "chinesePrompt": "最近天气变化太大了，我今早都不知道该穿什么。",
                "variants": [],
                "notes": ["先说环境，再补一条轻松个人经历"],
                "pronunciationTargets": ["what to wear"],
                "commonMistakes": ["I don't know wear what this morning."],
                "tags": ["SmallTalk", "DialogueTurn"],
                "contextText": "你和同事一起等电梯。",
                "responseRole": "Speaker",
            },
        ],
    },
]


def build():
    return build_trainpack(
        pack_id="small-talk-1",
        title="Small Talk 1",
        description="面向日常寒暄、轻松开场和跟进近况的口语训练包。",
        pack_type="Scenario",
        level_hint="A2-B1",
        estimated_minutes=50,
        tags=["Speaking", "SmallTalk", "A2-B1"],
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
