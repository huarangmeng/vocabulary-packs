#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import pronouncing
except Exception:  # pragma: no cover - build dependency is checked at runtime.
    pronouncing = None


DIALECTS = ("en-US", "en-GB")
TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / "content" / "pronunciation-cache"
REPORT_DIR = ROOT / "dist" / "reports"
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
USER_AGENT = "VocabularyTrainpackBuilder/1.0"


@dataclass(frozen=True)
class PronunciationBuildResult:
    references: list[dict[str, Any]]
    review_entries: list[dict[str, Any]]
    target_count: int
    reference_coverage: float
    verified_coverage: float


CURATED_LEXICON: dict[str, dict[str, Any]] = {
    "a": {"phonemes": ["ə"], "sourceUrl": "https://en.wiktionary.org/wiki/a#Pronunciation"},
    "i": {"phonemes": ["aɪ"], "sourceUrl": "https://en.wiktionary.org/wiki/I#Pronunciation"},
    "i'm": {"phonemes": ["aɪ", "m"], "sourceUrl": "https://en.wiktionary.org/wiki/I'm#Pronunciation"},
    "i'd": {"phonemes": ["aɪ", "d"], "sourceUrl": "https://en.wiktionary.org/wiki/I'd#Pronunciation"},
    "i'll": {"phonemes": ["aɪ", "l"], "sourceUrl": "https://en.wiktionary.org/wiki/I'll#Pronunciation"},
    "i've": {"phonemes": ["aɪ", "v"], "sourceUrl": "https://en.wiktionary.org/wiki/I've#Pronunciation"},
    "we're": {"phonemes": ["w", "ɪ", "ɹ"], "sourceUrl": "https://en.wiktionary.org/wiki/we're#Pronunciation"},
    "we've": {"phonemes": ["w", "i", "v"], "sourceUrl": "https://en.wiktionary.org/wiki/we've#Pronunciation"},
    "you're": {"phonemes": ["j", "ʊ", "ɹ"], "sourceUrl": "https://en.wiktionary.org/wiki/you're#Pronunciation"},
    "that's": {"phonemes": ["ð", "æ", "t", "s"], "sourceUrl": "https://en.wiktionary.org/wiki/that's#Pronunciation"},
    "what's": {"phonemes": ["w", "ʌ", "t", "s"], "sourceUrl": "https://en.wiktionary.org/wiki/what's#Pronunciation"},
    "how's": {"phonemes": ["h", "aʊ", "z"], "sourceUrl": "https://en.wiktionary.org/wiki/how's#Pronunciation"},
    "it's": {"phonemes": ["ɪ", "t", "s"], "sourceUrl": "https://en.wiktionary.org/wiki/it's#Pronunciation"},
    "let's": {"phonemes": ["l", "ɛ", "t", "s"], "sourceUrl": "https://en.wiktionary.org/wiki/let's#Pronunciation"},
    "don't": {"phonemes": ["d", "oʊ", "n", "t"], "sourceUrl": "https://en.wiktionary.org/wiki/don't#Pronunciation"},
    "didn't": {"phonemes": ["d", "ɪ", "d", "ə", "n", "t"], "sourceUrl": "https://en.wiktionary.org/wiki/didn't#Pronunciation"},
    "can't": {"phonemes": ["k", "æ", "n", "t"], "sourceUrl": "https://en.wiktionary.org/wiki/can't#Pronunciation"},
    "isn't": {"phonemes": ["ɪ", "z", "ə", "n", "t"], "sourceUrl": "https://en.wiktionary.org/wiki/isn't#Pronunciation"},
    "aren't": {"phonemes": ["ɑ", "ɹ", "ə", "n", "t"], "sourceUrl": "https://en.wiktionary.org/wiki/aren't#Pronunciation"},
    "api": {"phonemes": ["eɪ", "p", "i", "aɪ"], "sourceUrl": "https://en.wiktionary.org/wiki/API#Pronunciation"},
    "b": {"phonemes": ["b", "i"], "sourceUrl": "https://en.wiktionary.org/wiki/B#Pronunciation"},
    "prioritise": {"phonemes": ["p", "ɹ", "aɪ", "ɔ", "ɹ", "ə", "t", "aɪ", "z"], "sourceUrl": "https://en.wiktionary.org/wiki/prioritise#Pronunciation"},
    "overpromise": {"phonemes": ["oʊ", "v", "ɚ", "p", "ɹ", "ɑ", "m", "ɪ", "s"], "sourceUrl": "https://en.wiktionary.org/wiki/overpromise#Pronunciation"},
    "summarise": {"phonemes": ["s", "ʌ", "m", "ə", "ɹ", "aɪ", "z"], "sourceUrl": "https://en.wiktionary.org/wiki/summarise#Pronunciation"},
    "shippable": {"phonemes": ["ʃ", "ɪ", "p", "ə", "b", "ə", "l"], "sourceUrl": "https://en.wiktionary.org/wiki/shippable#Pronunciation"},
}

ARPABET_TO_IPA = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ",
    "B": "b", "CH": "t͡ʃ", "D": "d", "DH": "ð", "EH": "ɛ", "ER": "ɚ", "EY": "eɪ",
    "F": "f", "G": "g", "HH": "h", "IH": "ɪ", "IY": "i", "JH": "d͡ʒ", "K": "k",
    "L": "l", "M": "m", "N": "n", "NG": "ŋ", "OW": "oʊ", "OY": "ɔɪ", "P": "p",
    "R": "ɹ", "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "UH": "ʊ", "UW": "u",
    "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ",
}

IPA_SYMBOLS = sorted(
    [
        "t͡ʃ", "d͡ʒ", "aʊ", "aɪ", "eɪ", "oʊ", "ɔɪ", "ɪə", "eə", "ʊə",
        "i", "ɪ", "e", "ɛ", "æ", "ɑ", "ɒ", "ɔ", "ʊ", "u", "ʌ", "ə", "ɚ", "ɝ",
        "p", "b", "t", "d", "k", "g", "f", "v", "θ", "ð", "s", "z", "ʃ", "ʒ",
        "h", "m", "n", "ŋ", "l", "ɹ", "r", "j", "w", "ɾ",
    ],
    key=len,
    reverse=True,
)

VOWELS = {"i", "ɪ", "ɛ", "æ", "ɑ", "ɒ", "ɔ", "ʊ", "u", "ʌ", "ə", "ɚ", "ɝ", "eɪ", "aɪ", "aʊ", "ɔɪ", "oʊ"}
BATH_SET = {"bath", "dance", "chance", "ask", "last", "past", "after", "fast", "half", "class"}
LOT_SET = {"hot", "lot", "not", "got", "stop", "shop", "box", "clock"}


def build_pronunciation_references(pack_id: str, units: list[dict[str, Any]], items: list[dict[str, Any]]) -> PronunciationBuildResult:
    if pronouncing is None:
        raise RuntimeError(
            "pronouncing is required to build official pronunciation references. "
            "Run: python -m pip install -r tools/build-packs/requirements-pronunciation.txt"
        )
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    unit_titles = {unit["unitId"]: unit["title"] for unit in units}
    references: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    sequence = 1
    target_count = 0

    for item in items:
        for target in _targets_for_item(item):
            for dialect in DIALECTS:
                target_count += 1
                tokens = _tokenize(target["targetText"])
                word_refs: list[dict[str, Any]] = []
                missing: list[str] = []
                for token in tokens:
                    word_ref = _verified_word_reference(token, dialect)
                    if word_ref is None:
                        missing.append(token)
                    else:
                        word_refs.append(word_ref)
                if missing or not word_refs:
                    review_entries.append(
                        {
                            "packId": pack_id,
                            "itemId": item["id"],
                            "unitId": item["unitId"],
                            "targetType": target["targetType"],
                            "targetText": target["targetText"],
                            "dialect": dialect,
                            "missingWords": missing,
                            "reason": "No verified online/local pronunciation source for all words.",
                        }
                    )
                    continue
                reference = {
                    "id": f"{pack_id}:pron-{sequence:05d}",
                    "itemId": item["id"],
                    "unitId": item["unitId"],
                    "unitTitle": unit_titles[item["unitId"]],
                    "targetType": target["targetType"],
                    "targetText": target["targetText"],
                    "dialect": dialect,
                    "phonemes": [phoneme for word in word_refs for phoneme in word["phonemes"]],
                    "words": word_refs,
                    "lexicalStress": _merge_lexical_stress(word_refs),
                    "sentenceStress": _sentence_stress_targets(target["targetText"], word_refs),
                    "source": "PackVerifiedOnline",
                    "confidence": "High",
                    "reviewStatus": "PackVerified",
                    "provenance": _merge_provenance(word_refs),
                }
                references.append(reference)
                sequence += 1

    reference_coverage = round(len(references) / target_count, 4) if target_count else 0.0
    verified_coverage = reference_coverage
    return PronunciationBuildResult(
        references=references,
        review_entries=review_entries,
        target_count=target_count,
        reference_coverage=reference_coverage,
        verified_coverage=verified_coverage,
    )


def write_pronunciation_review_report(pack_id: str, result: PronunciationBuildResult) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{pack_id}-pronunciation-review.json"
    report = {
        "packId": pack_id,
        "targetCount": result.target_count,
        "referenceCount": len(result.references),
        "referenceCoverage": result.reference_coverage,
        "verifiedCoverage": result.verified_coverage,
        "reviewCount": len(result.review_entries),
        "reviewEntries": result.review_entries,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report_path


def _targets_for_item(item: dict[str, Any]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    targets: list[dict[str, str]] = []

    def add(target_type: str, text: str) -> None:
        normalized = " ".join(text.strip().split())
        if not normalized:
            return
        key = (target_type, normalized.lower())
        if key in seen:
            return
        seen.add(key)
        targets.append({"targetType": target_type, "targetText": normalized})

    add("EnglishText", item["englishText"])
    for variant in item.get("variants", []):
        add("Variant", variant)
    for target in item.get("pronunciationTargets", []):
        add("PronunciationTarget", target)
    return targets


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def _verified_word_reference(token: str, dialect: str) -> dict[str, Any] | None:
    if token in CURATED_LEXICON:
        entry = CURATED_LEXICON[token]
        return _word(
            token,
            _apply_dialect(token, entry["phonemes"], dialect),
            "CuratedLexicon",
            dialect,
            entry["sourceUrl"],
            license_name="source-provided",
        )

    online = _dictionary_api_reference(token, dialect)
    if online is not None:
        return online

    inflected = _inflected_reference(token, dialect)
    if inflected is not None:
        return inflected

    cmu = _cmudict_reference(token, dialect)
    if cmu is not None:
        return cmu

    return None


def _word(text: str, phonemes: list[str], source: str, dialect: str, source_url: str, *, license_name: str = "source-provided") -> dict[str, Any]:
    return {
        "text": text,
        "phonemes": phonemes,
        "lexicalStress": _infer_lexical_stress(phonemes),
        "source": source,
        "confidence": "High",
        "sourceUrl": source_url,
        "license": license_name,
        "dialect": dialect,
    }


def _dictionary_api_reference(token: str, dialect: str) -> dict[str, Any] | None:
    data = _dictionary_api_lookup(token)
    if not data:
        return None
    candidates: list[dict[str, Any]] = []
    for entry in data if isinstance(data, list) else []:
        source_urls = entry.get("sourceUrls") or []
        entry_license = (entry.get("license") or {}).get("name") or "source-provided"
        for phonetic in entry.get("phonetics") or []:
            text = phonetic.get("text")
            if not isinstance(text, str) or not text.strip():
                continue
            phonemes = _ipa_to_phonemes(text)
            if not phonemes:
                continue
            audio = phonetic.get("audio") or ""
            source_url = phonetic.get("sourceUrl") or (source_urls[0] if source_urls else DICTIONARY_API.format(word=urllib.parse.quote(token)))
            license_name = ((phonetic.get("license") or {}).get("name") or entry_license)
            candidates.append(
                {
                    "phonemes": phonemes,
                    "audio": audio,
                    "sourceUrl": source_url,
                    "license": license_name,
                    "score": _dialect_score(audio, dialect),
                }
            )
        phonetic_text = entry.get("phonetic")
        if isinstance(phonetic_text, str):
            phonemes = _ipa_to_phonemes(phonetic_text)
            if phonemes:
                candidates.append(
                    {
                        "phonemes": phonemes,
                        "audio": "",
                        "sourceUrl": source_urls[0] if source_urls else DICTIONARY_API.format(word=urllib.parse.quote(token)),
                        "license": entry_license,
                        "score": 0,
                    }
                )
    if not candidates:
        return None
    best = sorted(candidates, key=lambda value: value["score"], reverse=True)[0]
    phonemes = _apply_dialect(token, best["phonemes"], dialect) if best["score"] == 0 else best["phonemes"]
    return _word(token, phonemes, "DictionaryApi", dialect, best["sourceUrl"], license_name=best["license"])


def _dictionary_api_lookup(token: str) -> Any | None:
    cache_path = CACHE_DIR / f"dictionaryapi-{_safe_cache_name(token)}.json"
    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        return cached.get("data")
    url = DICTIONARY_API.format(word=urllib.parse.quote(token))
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            data = None
        else:
            raise
    except urllib.error.URLError:
        data = None
    cache_path.write_text(
        json.dumps({"word": token, "url": url, "retrievedAt": int(time.time()), "data": data}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data


def _safe_cache_name(token: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", token.lower()).strip("_") or "word"


def _dialect_score(audio: str, dialect: str) -> int:
    lowered = audio.lower()
    if dialect == "en-US" and ("-us." in lowered or "_us." in lowered or "/us/" in lowered):
        return 3
    if dialect == "en-GB" and ("-uk." in lowered or "_uk." in lowered or "-gb." in lowered or "/uk/" in lowered):
        return 3
    if dialect == "en-GB" and ("-au." in lowered or "_au." in lowered):
        return 2
    return 1 if audio else 0


def _inflected_reference(token: str, dialect: str) -> dict[str, Any] | None:
    candidates: list[tuple[str, str]] = []
    if token.endswith("'s") and len(token) > 2:
        candidates.append((token[:-2], "s"))
    if token.endswith("s") and len(token) > 2 and not token.endswith("'s"):
        candidates.append((token[:-1], "s"))
    if token.endswith("ed") and len(token) > 3:
        candidates.extend([(token[:-1], "ed"), (token[:-2], "ed")])
    if token.endswith("ing") and len(token) > 5:
        stem = token[:-3]
        candidates.extend([(stem, "ing"), (stem + "e", "ing")])
        if len(stem) > 2 and stem[-1] == stem[-2]:
            candidates.append((stem[:-1], "ing"))
    for base, suffix in candidates:
        base_ref = _verified_word_reference(base, dialect)
        if base_ref is None:
            continue
        base_phonemes = list(base_ref["phonemes"])
        if suffix == "s":
            phonemes = base_phonemes + _s_suffix(base_phonemes[-1])
        elif suffix == "ed":
            phonemes = base_phonemes + _ed_suffix(base_phonemes[-1])
        else:
            phonemes = base_phonemes + ["ɪ", "ŋ"]
        return _word(token, phonemes, "InflectionRule", dialect, base_ref["sourceUrl"], license_name=base_ref["license"])
    return None


def _cmudict_reference(token: str, dialect: str) -> dict[str, Any] | None:
    phones = pronouncing.phones_for_word(token) if pronouncing is not None else []
    if not phones:
        return None
    phonemes = _arpabet_to_phonemes(phones[0])
    if not phonemes:
        return None
    return _word(token, _apply_dialect(token, phonemes, dialect), "Cmudict", dialect, "cmudict://pronouncing", license_name="cmudict")


def _arpabet_to_phonemes(phones: str) -> list[str]:
    result: list[str] = []
    for arpabet in phones.split():
        symbol = re.sub(r"\d", "", arpabet)
        ipa = ARPABET_TO_IPA.get(symbol)
        if ipa:
            result.append(ipa)
    return result


def _ipa_to_phonemes(raw_ipa: str) -> list[str]:
    text = raw_ipa.strip().strip("/[]")
    text = re.sub(r"[ˈˌ.()ːˑ̩̯̥̬̃ʰᵊ]", "", text)
    text = text.replace("ɡ", "g").replace("ɝ", "ɚ").replace("r", "ɹ").replace("ɫ", "l")
    phonemes: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace() or char in {",", ";"}:
            index += 1
            continue
        match = next((symbol for symbol in IPA_SYMBOLS if text.startswith(symbol, index)), None)
        if match is None:
            index += 1
            continue
        phonemes.append("ɹ" if match == "r" else match)
        index += len(match)
    return phonemes


def _apply_dialect(word: str, phonemes: list[str], dialect: str) -> list[str]:
    if dialect == "en-US":
        return phonemes
    result = list(phonemes)
    if word in BATH_SET and "æ" in result:
        result[result.index("æ")] = "ɑ"
    if word in LOT_SET and "ɑ" in result:
        result[result.index("ɑ")] = "ɒ"
    non_rhotic: list[str] = []
    for index, phoneme in enumerate(result):
        previous_is_vowel = index > 0 and result[index - 1] in VOWELS
        next_is_vowel = index + 1 < len(result) and result[index + 1] in VOWELS
        if phoneme == "ɹ" and previous_is_vowel and not next_is_vowel:
            continue
        non_rhotic.append(phoneme)
    return non_rhotic


def _s_suffix(last_phoneme: str) -> list[str]:
    if last_phoneme in {"s", "z", "ʃ", "ʒ", "t͡ʃ", "d͡ʒ"}:
        return ["ɪ", "z"]
    if last_phoneme in {"p", "t", "k", "f", "θ"}:
        return ["s"]
    return ["z"]


def _ed_suffix(last_phoneme: str) -> list[str]:
    if last_phoneme in {"t", "d"}:
        return ["ɪ", "d"]
    if last_phoneme in {"p", "k", "f", "θ", "s", "ʃ", "t͡ʃ"}:
        return ["t"]
    return ["d"]


def _infer_lexical_stress(phonemes: list[str]) -> list[int]:
    stress: list[int] = []
    stressed = False
    for phoneme in phonemes:
        if phoneme not in VOWELS:
            continue
        if not stressed and phoneme not in {"ə", "ɚ", "ɝ"}:
            stress.append(1)
            stressed = True
        else:
            stress.append(0)
    return stress


def _merge_lexical_stress(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"word": word["text"], "stress": word.get("lexicalStress", [])}
        for word in words
        if word.get("lexicalStress")
    ]


def _sentence_stress_targets(target_text: str, words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    content_words = [
        word["text"]
        for word in words
        if word["text"] not in {"a", "an", "the", "to", "of", "for", "and", "or", "but", "in", "on", "at", "that"}
    ]
    if not content_words:
        return []
    return [
        {
            "pattern": target_text,
            "primaryWords": content_words[-2:] if len(content_words) > 1 else content_words,
            "note": "Default official-pack cue: keep function words light and make the final content word clear.",
        }
    ]


def _merge_provenance(words: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    provenance: list[dict[str, str]] = []
    for word in words:
        key = (word["source"], word["sourceUrl"], word["license"])
        if key in seen:
            continue
        seen.add(key)
        provenance.append({"source": word["source"], "sourceUrl": word["sourceUrl"], "license": word["license"]})
    return provenance
