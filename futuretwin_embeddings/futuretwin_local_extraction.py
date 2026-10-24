"""Conservative source-span extraction, using only the bundled ESCO vocabulary.

This is not an LLM. Literal mentions and a small set of activity rules produce
unconfirmed evidence; the existing local MiniLM suggests ESCO candidates later.
"""
from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path

_TOKENS = re.compile(r"(?u)\w+(?:[+#]+)?")
_SKILLS = Path(__file__).resolve().parent / "skills_en.csv"
_ACTIVITY = re.compile(
    r"\b(?:built|build|developed|develop|managed|manage|analysed|analyse|analyzed|"
    r"analyze|created|create|supported|support|tested|test|designed|design|"
    r"implemented|implement|maintained|maintain|organised|organise|organized|"
    r"organize|coordinated|coordinate|prepared|prepare|trained|train|"
    r"resolved|resolve|processed|process|reviewed|review|translated|translate|"
    r"assisted|assist|monitored|monitor|repaired|repair)\b", re.I,
)
_PRIVATE = re.compile(
    r"@|https?://|\b(?:university|college|school|gpa|cgpa|passport|"
    r"address|phone|email|born|salary)\b|\+?\d[\d ()-]{7,}", re.I,
)
_NEGATED = re.compile(
    r"\b(?:not|no|never|without|lack|lacking)\b[^.;!?\n]{0,65}$", re.I,
)
_ASPIRATION = re.compile(
    r"\b(?:want to|would like to|hope to|plan to|interested in|wish to|"
    r"ignore instructions|ignore previous|extract|system prompt)\b", re.I,
)
_STOP = {"a", "an", "the", "and", "or", "as", "at", "by", "for", "in",
         "is", "it", "of", "on", "to", "be", "can", "may", "will", "i"}


@lru_cache(maxsize=1)
def _vocabulary() -> dict:
    trie: dict = {}
    with _SKILLS.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            for label in [row["preferredLabel"], *row.get("altLabels", "").splitlines()]:
                words = [m.group().casefold() for m in _TOKENS.finditer(label)]
                if not words or len(words) > 12 or len(label) > 200:
                    continue
                if len(words) == 1 and (words[0] in _STOP or len(words[0]) < 3):
                    # Avoid treating ordinary words / single letters as skills.
                    continue
                node = trie
                for word in words:
                    node = node.setdefault(word, {})
                node[""] = True
    return trie


def extract_local_skills(text: str, source_kind: str = "resume") -> dict:
    """Return exact source spans only; never persist or send source text."""
    if source_kind not in {"resume", "experience"} or not isinstance(text, str):
        raise ValueError("Choose a supported source.")
    if len(text) > 30_000:
        raise ValueError("Source text exceeds the local extraction limit.")
    trie = _vocabulary()
    mentions, activities, seen = [], [], set()
    tokens = list(_TOKENS.finditer(text))
    i = 0
    while i < len(tokens) and len(mentions) < 40:
        node, best, j = trie, None, i
        while j < min(len(tokens), i + 12):
            # Do not join separate bullet points or sentences into a skill.
            if j > i and not re.fullmatch(r"[ \t/-]*", text[tokens[j-1].end():tokens[j].start()]):
                break
            word = tokens[j].group().casefold()
            if word not in node:
                break
            node = node[word]
            if "" in node:
                best = j
            j += 1
        if best is not None:
            start, end = tokens[i].start(), tokens[best].end()
            value = text[start:end]
            preceding = text[max(0, start - 70):start]
            key = value.casefold()
            if key not in seen and not _NEGATED.search(preceding):
                mentions.append({"value": value, "evidence": value})
                seen.add(key)
            i = best + 1
        else:
            i += 1

    for sentence in re.split(r"[\n;.!?]+", text):
        sentence = sentence.strip(" \t-*•")
        if not sentence or _PRIVATE.search(sentence) or _ASPIRATION.search(sentence):
            continue
        verb = _ACTIVITY.search(sentence)
        if not verb or verb.start() > 35 or _NEGATED.search(sentence[:verb.start()]):
            continue
        value = sentence[verb.start():].strip()
        if not 12 <= len(value) <= 200 or value.casefold() in seen:
            continue
        activities.append({"value": value, "evidence": value})
        seen.add(value.casefold())
        if len(activities) >= 20:
            break
    return {"explicit_skills": mentions, "work_activities": activities}
