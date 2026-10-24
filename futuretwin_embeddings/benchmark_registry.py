"""FutureTwin multi-source benchmark registry.

Single source of truth for every benchmark we track: where results come from,
what the benchmark measures (task descriptions preserved for the fine-tuned
MiniLM skill matcher), score direction/unit, and attribution.

No network or database access here — pure metadata.
"""
from __future__ import annotations

# =====================================
# SOURCES (verified 2026-10-21)
# =====================================
# access: "connected"   -> machine-readable results fetched automatically
#         "paid"        -> results exist but not on our current tier
#         "local_only"  -> no machine-readable results feed; evaluation must
#                          be run locally or extracted manually from reports

SOURCES = {
    "artificial_analysis": {
        "name": "Artificial Analysis",
        "access": "connected",
        "url": "https://artificialanalysis.ai/",
        "api": "https://artificialanalysis.ai/api/v2/language/models/free",
        "attribution": "Artificial Analysis Intelligence Index™ results. Free API tier.",
        "note": (
            "Free tier exposes composite indexes only (Intelligence + 8 domain "
            "indexes). Individual benchmark results (e.g. per-benchmark scores) "
            "are NOT included in the free tier."
        ),
    },
    "swebench": {
        "name": "SWE-bench",
        "access": "connected",
        "url": "https://www.swebench.com/",
        "data": "https://raw.githubusercontent.com/SWE-bench/swe-bench.github.io/master/data/leaderboards.json",
        "attribution": "SWE-bench official leaderboard data (SWE-bench team).",
        "note": "Official machine-readable leaderboard JSON, dated entries with resolved %.",
    },
    "livebench": {
        "name": "LiveBench",
        "access": "connected",
        "url": "https://livebench.ai/",
        "data": "https://raw.githubusercontent.com/LiveBench/livebench.github.io/main/public/",
        "attribution": "LiveBench (Abacus.AI / Yann LeCun et al.), contamination-free benchmark.",
        "note": (
            "Per-release score tables (table_<date>.csv) plus category mapping "
            "(categories_<date>.json). Subcategory-level scores 0-100."
        ),
    },
    "metr": {
        "name": "METR",
        "access": "local_only",
        "url": "https://metr.org/",
        "attribution": "METR research reports.",
        "note": (
            "No stable machine-readable results feed. Public eval data lives in "
            "DVC-tracked repos (eval-analysis-public) requiring their analysis "
            "pipeline; headline results are published in reports. Connecting "
            "means running HCAST/RE-Bench locally or manual extraction."
        ),
    },
    "osworld": {
        "name": "OSWorld",
        "access": "local_only",
        "url": "https://os-world.github.io/",
        "attribution": "OSWorld (XLANG Lab), NeurIPS 2024.",
        "note": (
            "No official results API. The leaderboard is published as web "
            "content; the benchmark is designed to be run locally against real "
            "VM environments. A connector would need unofficial scraping or a "
            "local evaluation harness."
        ),
    },
}

# =====================================
# BENCHMARK METADATA
# =====================================
# Task descriptions are preserved verbatim here and mirrored into PostgreSQL
# (benchmark_task_descriptions) so the fine-tuned MiniLM can map them to ESCO
# skills. They describe what the benchmark measures, not what AI will do to
# jobs.

AA_INDEXES = {
    # AA field name -> (display benchmark name, domain, task description)
    "artificial_analysis_intelligence_index": (
        "Artificial Analysis Intelligence Index",
        "General",
        "Answer questions and solve problems across mathematics, science, "
        "reasoning and coding in a composite evaluation.",
    ),
    "artificial_analysis_coding_index": (
        "Artificial Analysis Coding Index",
        "Coding",
        "Solve programming problems: write, complete, debug and explain "
        "computer code across coding evaluation suites.",
    ),
    "artificial_analysis_agentic_index": (
        "Artificial Analysis Agentic Index",
        "Agentic",
        "Plan and execute multi-step tasks using digital tools, terminal "
        "commands and web browsing in agentic evaluation harnesses.",
    ),
    "artificial_analysis_economics_index": (
        "Artificial Analysis Economics Index",
        "Economics",
        "Answer economics questions, interpret economic indicators and reason "
        "about markets and policy.",
    ),
    "artificial_analysis_engineering_index": (
        "Artificial Analysis Engineering Index",
        "Engineering",
        "Solve engineering problems, analyze technical systems and evaluate "
        "designs across engineering disciplines.",
    ),
    "artificial_analysis_finance_and_accounting_index": (
        "Artificial Analysis Finance & Accounting Index",
        "Finance",
        "Analyze financial statements, apply accounting standards and "
        "interpret financial data.",
    ),
    "artificial_analysis_healthcare_and_medical_index": (
        "Artificial Analysis Healthcare & Medical Index",
        "Healthcare",
        "Answer medical questions, interpret clinical information and reason "
        "about diagnoses and treatments.",
    ),
    "artificial_analysis_legal_index": (
        "Artificial Analysis Legal Index",
        "Legal",
        "Analyze legal documents, apply statutes and case law, and draft "
        "legal reasoning.",
    ),
    "artificial_analysis_strategy_and_ops_index": (
        "Artificial Analysis Strategy & Ops Index",
        "Strategy",
        "Analyze business operations, develop strategies and plan "
        "organizational activities.",
    ),
}

SWEBENCH_LEADERBOARDS = {
    # leaderboard key in leaderboards.json -> task description
    "Verified": (
        "Resolve real, human-validated GitHub issues in open-source Python "
        "repositories: read the issue report, navigate the codebase, locate "
        "the defect and generate a correct code patch.",
    ),
    "Lite": (
        "Resolve real GitHub issues (lite subset) in open-source Python "
        "repositories by generating code patches.",
    ),
    "Multimodal": (
        "Resolve GitHub issues that include screenshots or other visual "
        "artifacts, combining image understanding with code patching.",
    ),
    "Multilingual": (
        "Resolve real GitHub issues across multiple programming languages, "
        "not only Python, by generating code patches.",
    ),
    "Test": (
        "Resolve GitHub issues in the SWE-bench test split by generating "
        "code patches.",
    ),
}

LIVEBENCH_TASKS = {
    # LiveBench subcategory -> task description
    "code_generation": "Generate correct programs from problem statements under time-limited, contamination-free conditions.",
    "code_completion": "Complete partial source code so it passes hidden tests.",
    "javascript": "Write and repair JavaScript code in multi-step agentic coding tasks.",
    "typescript": "Write and repair TypeScript code in multi-step agentic coding tasks.",
    "python": "Write and repair Python code in multi-step agentic coding tasks.",
    "AMPS_Hard": "Solve hard competition-style mathematics problems.",
    "math_comp": "Solve mathematics competition problems.",
    "olympiad": "Solve olympiad-level mathematics problems requiring multi-step proofs.",
    "integrals_with_game": "Compute integrals and solve quantitative puzzles.",
    "connections": "Find latent connections between words or concepts.",
    "consecutive_events": "Reason about sequences of events in structured data.",
    "tablejoin": "Join and reconcile data tables to answer questions.",
    "tablereformat": "Reformat and transform tabular data accurately.",
    "paraphrase": "Paraphrase text while preserving meaning.",
    "simplify": "Simplify text while preserving meaning.",
    "story_generation": "Write coherent stories following constraints.",
    "summarize": "Summarize documents accurately.",
    "plot_unscrambling": "Reconstruct the order of scrambled plot or logic statements.",
    "spatial": "Solve spatial reasoning problems.",
    "theory_of_mind": "Reason about beliefs and intentions of others.",
    "zebra_puzzle": "Solve logic grid (zebra) puzzles.",
    "typos": "Detect and correct typographical errors in text.",
    "logic_with_navigation": "Follow logical instructions involving navigation steps.",
}

LIVEBENCH_DOMAINS = {
    # suite name -> our domain bucket (suites come from categories_<date>.json)
    "Coding": "Coding",
    "Agentic Coding": "Coding",
    "Reasoning": "Reasoning",
    "Mathematics": "Mathematics",
    "Data Analysis": "Data Analysis",
    "Language": "Language",
    "IF": "Instruction Following",
}


def task_descriptions() -> list[dict]:
    """Flatten all preserved task descriptions for DB mirroring."""
    rows = []
    for field, (bench, _domain, text) in AA_INDEXES.items():
        rows.append({"benchmark_name": bench, "task": "", "task_text": text,
                     "source": "artificial_analysis"})
    for key, text in SWEBENCH_LEADERBOARDS.items():
        rows.append({"benchmark_name": f"SWE-bench {key}", "task": "",
                     "task_text": text, "source": "swebench"})
    for sub, text in LIVEBENCH_TASKS.items():
        rows.append({"benchmark_name": "LiveBench", "task": sub,
                     "task_text": text, "source": "livebench"})
    return rows
