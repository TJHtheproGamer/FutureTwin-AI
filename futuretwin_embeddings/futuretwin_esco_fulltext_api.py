"""FutureTwin v3: evidence-aware ESCO glossary matching over job advertisements.

Place beside these existing Replit files:
  futuretwin_skill_api.py
  futuretwin_job_analysis_api.py
  futuretwin_esco_normalized_api.py

Only the Python standard library is used for the glossary matcher. The existing
API still requires its original Flask, pandas and sentence-transformers deps.

Examples:
  python futuretwin_embeddings/futuretwin_esco_fulltext_api.py --self-test
  python futuretwin_embeddings/futuretwin_esco_fulltext_api.py --demo
  python futuretwin_embeddings/futuretwin_esco_fulltext_api.py --serve

POST /api/analyze-job-v3 with {"text": "...", "top_k": 5}

CAUTIONS:
 * Exact text mention != confirmed skill requirement; negation and preferred-only
   descriptions are NOT classified here.
 * Unique glossary match != correctness of the underlying ESCO ontology mapping.
 * The output is candidate evidence, NOT suitable for automatic demand counting
   without contextual validation and held-out real job-ad evaluations.
 * Unmatched curated mentions remain explicit and unlinked.
"""
from __future__ import annotations

import argparse
import os
import re
import unicodedata
from functools import lru_cache
from typing import Any

# Match words while supporting common programming-language punctuation.
# Nonword separators (spaces, commas, parentheses) remain between tokens;
# matching terms must have the same token sequence as the actual text.
TOKEN_RE = re.compile(r"(?u)[^\W_]+(?:[+#./-][^\W_]+)*[+#]*")
END = "\0"


def _tokens(s: str) -> list[tuple[str, int, int]]:
    return [
        (unicodedata.normalize("NFKC", m.group()).casefold(), m.start(), m.end())
        for m in TOKEN_RE.finditer(s)
    ]


def _safe_for_auto_matching(term: str) -> bool:
    """Avoid the riskiest single-letter and very short glossary entries.

    Conservative, not a relevance test. Short exact terms may still be caught by
    the curated detector (e.g. SQL, R, C, Go) with domain-aware regex.
    """
    words = _tokens(term)
    if not words:
        return False
    if len(words) == 1 and len(words[0][0]) < 5:
        return False
    if len(term.strip()) > 140:  # avoid long pseudo-sentences in alias files
        return False
    return True


def make_glossary(preferred: dict, aliases: dict) -> tuple[dict, dict]:
    """Return a token trie and simple diagnostics for official ESCO labels.

    Leaves hold the full normalized official term, never a guess made by MiniLM.
    """
    tree: dict = {}
    terms = set(preferred) | set(aliases)
    included = 0
    skipped = 0
    for term in sorted(terms):
        if not _safe_for_auto_matching(term):
            skipped += 1
            continue
        words = _tokens(term)
        node = tree
        for word, _, _ in words:
            node = node.setdefault(word, {})
        node[END] = term
        included += 1
    return tree, {"indexed_terms": included, "excluded_short_or_long_terms": skipped}


def _mapping(term: str, preferred: dict, aliases: dict, names: dict) -> dict:
    """Conservatively map a detected official phrase; any collision is ambiguous."""
    uris = set(preferred.get(term, set())) | set(aliases.get(term, set()))
    if len(uris) != 1:
        return {
            "status": "ambiguous" if uris else "unmatched",
            "skill_uri": None,
            "label": None,
            "candidate_count": len(uris),
        }
    uri = next(iter(uris))
    source = "preferred_label_exact" if uri in preferred.get(term, set()) else "official_alternate_label_exact"
    return {"status": "matched", "skill_uri": uri, "label": names.get(uri, ""), "source": source}


def extract_glossary_mentions(text: str, trie: dict, preferred: dict, aliases: dict, names: dict) -> list[dict]:
    """Longest nonoverlapping official glossary matches with literal evidence spans."""
    words = _tokens(text)
    results = []
    i = 0
    while i < len(words):
        node = trie
        longest: tuple[int, str] | None = None
        j = i
        while j < len(words) and words[j][0] in node:
            node = node[words[j][0]]
            if END in node:
                longest = (j, node[END])
            j += 1
        if longest is None:
            i += 1
            continue
        end_i, phrase = longest
        start, end = words[i][1], words[end_i][2]
        results.append({
            "term": phrase,
            "evidence": [{"quote": text[start:end], "start": start, "end": end}],
            "esco_mapping": _mapping(phrase, preferred, aliases, names),
            "detector": "official_esco_label_or_alias_exact_tokens",
            "requirement_status": "context_not_verified",
        })
        i = end_i + 1
    return results


def _overlaps(a: dict, b: dict) -> bool:
    return any(x["start"] < y["end"] and y["start"] < x["end"]
               for x in a["evidence"] for y in b["evidence"])


@lru_cache(maxsize=1)
def get_glossary():
    # Imported lazily so the pure matcher can be unit-tested without loading
    # torch/Flask/embeddings. This uses the SAME validated ESCO files as v2.
    from futuretwin_esco_normalized_api import load_esco_registry
    registry, stats, path = load_esco_registry()
    trie, trie_stats = make_glossary(registry["preferred"], registry["aliases"])
    return trie, registry, {**stats, **trie_stats, "alias_file": path}


def analyze_job_v3(text: str, top_k: int = 5) -> dict:
    from futuretwin_esco_normalized_api import analyze_job_v2
    result = analyze_job_v2(text, top_k)
    trie, registry, info = get_glossary()
    existing = result["explicit_mentions"]
    for mention in existing:
        mention["detector"] = "curated_regex"
        mention["requirement_status"] = "context_not_verified"

    found = extract_glossary_mentions(
        text, trie, registry["preferred"], registry["aliases"], registry["names"]
    )
    # Keep curated exact spans (even unmatched); don't emit duplicate or
    # overlapping claims merely because a longer synonym contains a term.
    # If a broader glossary match is more informative, inspect in a separate
    # audit rather than overriding the curated term automatically.
    new = [m for m in found if not any(_overlaps(m, old) for old in existing)]
    result["explicit_mentions"] = sorted(existing + new, key=lambda x: x["evidence"][0]["start"])
    result["method"]["explicit_mentions"] = (
        "Curated phrase rules plus automatic exact token matching against ESCO "
        "preferred/alternate labels; longest glossary match at each position."
    )
    result["method"]["esco_auto_extractor"] = info
    result["method"]["requirements"] = "Not classified: mentions may be negated, preferred-only, or historical."
    result["warning"] = (
        "Matches are text evidence and ESCO mapping candidates, not proven job requirements. "
        "Unknown and ambiguous links stay unresolved. Do not count semantic "
        "suggestions as employer requests. Validate extraction on real ads."
    )
    return result


def _self_test() -> None:
    preferred = {
        "sql": {"esco/sql"},
        "machine learning": {"esco/ml"},
        "develop dashboards": {"esco/dashboards"},
        "computer programming": {"esco/programming"},
    }
    aliases = {"machine learning": {"esco/ml"}, "dashboards": {"esco/dash"}}
    names = {"esco/ml": "machine learning", "esco/dashboards": "develop dashboards", "esco/dash": "dashboard"}
    trie, meta = make_glossary(preferred, aliases)
    text = "Experience with SQL and machine learning; develop dashboards."
    result = extract_glossary_mentions(text, trie, preferred, aliases, names)
    assert [r["evidence"][0]["quote"] for r in result] == ["machine learning", "develop dashboards"], result
    assert all(text[r["evidence"][0]["start"]:r["evidence"][0]["end"]] == r["evidence"][0]["quote"] for r in result)
    assert result[0]["esco_mapping"]["skill_uri"] == "esco/ml"
    assert result[1]["esco_mapping"]["skill_uri"] == "esco/dashboards"
    print("SELF-TEST PASSED", meta, "| matches:", [r["term"] for r in result])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--demo", action="store_true")
    group.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return

    from futuretwin_esco_normalized_api import app
    from flask import jsonify, request

    @app.post("/api/analyze-job-v3")
    def api_analyze_job_v3():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Send a JSON object"}), 400
        try:
            result = analyze_job_v3(payload.get("text"), payload.get("top_k", 5))
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(result)

    if args.demo:
        sample = "Data analyst responsible for SQL queries, data visualization, statistical analysis and dashboard development."
        result = analyze_job_v3(sample)
        for match in result["explicit_mentions"]:
            print(f"{match['evidence'][0]['quote']} => {match['esco_mapping']['status']}: "
                  f"{match['esco_mapping'].get('label')} ({match['detector']})")
        print("ESCO glossary:", result["method"]["esco_auto_extractor"])
    else:
        get_glossary()  # build trie once at startup, not once per request
        print("FutureTwin v3 ESCO text matcher ready.", flush=True)
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)


if __name__ == "__main__":
    main()
