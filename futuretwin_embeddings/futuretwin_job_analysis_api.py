"""FutureTwin: evidence-aware job posting analysis, for Replit.

Place alongside futuretwin_skill_api.py under futuretwin_embeddings/.

Run:
    python futuretwin_embeddings/futuretwin_job_analysis_api.py --demo
    python futuretwin_embeddings/futuretwin_job_analysis_api.py --serve

POST /api/analyze-job with {"text": "...", "top_k": 20}.

The two outputs are purposefully separate:
  explicit_mentions: literal job-ad text evidence, from a modest curated vocabulary
  semantic_candidates: ESCO skills retrieved by MiniLM, NOT proven requirements

This prototype DOES NOT comprehensively extract skills or produce labor-market counts.
Expand and independently validate the explicit vocabulary before any trend study.
"""
from __future__ import annotations

import argparse
import os
import re

from flask import jsonify, request

# Reuse the *same* Flask app, trained model, and ESCO embedding cache.
from futuretwin_skill_api import app, load_index, match_skills

# These are only spelling/wording detectors, NOT independent proof that a skill
# maps to a particular ESCO identifier. Missing terms do not mean no skill exists.
PATTERNS = {
    "SQL": [r"\bSQL\b", r"\bstructured query language\b"],
    "Python": [r"\bPython\b"],
    "R programming": [r"\bR programming\b", r"\bR language\b"],
    "Microsoft Excel": [r"\b(?:Microsoft\s+)?Excel\b"],
    "Power BI": [r"\bPower\s*BI\b"],
    "Tableau": [r"\bTableau\b"],
    "JavaScript": [r"\bJavaScript\b"],
    "statistical analysis": [r"\bstatistical analys[ie]s\b"],
    "data visualisation": [r"\bdata visuali[sz]ation\b", r"\bvisuali[sz]e data\b"],
    "dashboard development": [
        r"\bdashboard (?:development|creation|design)\b",
        r"\b(?:build|create|develop|design)(?:ing|s|ed)? dashboards?\b",
    ],
    "data cleaning": [r"\bdata cleaning\b", r"\bclean(?:ing)? data\b"],
    "machine learning": [r"\bmachine learning\b"],
    "Git": [r"\bGit\b"],
}
COMPILED = {
    skill: [re.compile(p, flags=re.IGNORECASE) for p in patterns]
    for skill, patterns in PATTERNS.items()
}


def explicit_mentions(text: str) -> list[dict]:
    """Return literal spans as evidence. No ontology link is assumed."""
    found = []
    for skill, patterns in COMPILED.items():
        hits = []
        seen_spans = set()
        for pattern in patterns:
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                if span not in seen_spans:
                    seen_spans.add(span)
                    hits.append({
                        "quote": text[match.start():match.end()],
                        "start": match.start(),
                        "end": match.end(),
                    })
        if hits:
            found.append({"term": skill, "evidence": sorted(hits, key=lambda h: h["start"])})
    return sorted(found, key=lambda item: item["evidence"][0]["start"])


def analyze_job(text: str, top_k: int = 20) -> dict:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("'text' must be a non-empty string")
    if len(text) > 15000:
        raise ValueError("'text' must be at most 15,000 characters")
    if not isinstance(top_k, int) or isinstance(top_k, bool) or not (1 <= top_k <= 50):
        raise ValueError("'top_k' must be an integer between 1 and 50")

    mentions = explicit_mentions(text)
    candidates = match_skills(text, top_k=top_k)
    # Critically, cosine similarity alone is not evidence that an ad named a skill.
    for candidate in candidates:
        candidate["evidence_status"] = "semantic_suggestion_only"
    return {
        "input": text,
        "explicit_mentions": mentions,
        "semantic_candidates": candidates,
        "method": {
            "explicit_mentions": "rule-based detection with verbatim spans; limited vocabulary",
            "semantic_candidates": "fine-tuned MiniLM occupation-skill similarity",
            "esco_uri_mapping": "not asserted for explicit mentions; requires a validated normalization step",
        },
        "warning": (
            "Do not count semantic candidates as employer-requested skills. "
            "Explicit matcher coverage is incomplete and must be validated on real advertisements."
        ),
    }


@app.post("/api/analyze-job")
def api_analyze_job():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send a JSON object"}), 400
    try:
        result = analyze_job(payload.get("text"), payload.get("top_k", 20))
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true")
    mode.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    if args.demo:
        sample = (
            "Data analyst responsible for SQL queries, data visualization, "
            "statistical analysis and dashboard development."
        )
        from pprint import pprint
        pprint(analyze_job(sample, top_k=5))
    else:
        load_index()
        port = int(os.getenv("PORT", "5000"))
        app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
