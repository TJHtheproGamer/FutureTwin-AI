"""Read-only exploration views grounded in the existing ESCO relationships."""
from __future__ import annotations

from typing import Any

from futuretwin_career_insurance import skill_descriptions
from futuretwin_practice_scenarios import PRACTICE_SCENARIOS

CV_OCCUPATION = "http://data.europa.eu/esco/occupation/1c5a45b9-440e-4726-b565-16a952abd341"
IMAGE_PROCESSING = "http://data.europa.eu/esco/skill/945b8655-5577-4c3a-946a-842d4527afa8"
DATA_ANALYST_OCCUPATION = "http://data.europa.eu/esco/occupation/d3edb8f8-3a06-47a0-8fb9-9b212c006aa2"
DATA_QUALITY_ASSESSMENT = "http://data.europa.eu/esco/skill/cc7370dd-69fa-4c67-a96f-d4d135d38700"
CUSTOMER_SERVICE_OCCUPATION = "http://data.europa.eu/esco/occupation/13d1b2b4-99dd-44da-9734-c9f74bae18f7"
IDENTIFY_CUSTOMER_NEEDS = "http://data.europa.eu/esco/skill/68698869-c13c-4563-adc7-118b7644f45d"
PRIMARY_TEACHER_OCCUPATION = "http://data.europa.eu/esco/occupation/03d79393-7b30-4159-945b-01963eddd302"
ASSESS_STUDENTS = "http://data.europa.eu/esco/skill/6fe019dd-027f-45f3-b19c-d27f7ae00980"

SCENARIO_EXPERIENCES = {
    DATA_ANALYST_OCCUPATION: {
        "skill_uri": DATA_QUALITY_ASSESSMENT,
        "id": "data-quality-sample",
        "title": "Check a small data sample",
        "summary": "Spot issues to verify before reporting a total.",
        "activity": {
            "type": "table",
            "caption": "Synthetic order sample",
            "headers": ["Order ID", "Date", "Units"],
            "rows": [
                ["104", "5 Jun", "24"],
                ["105", "6 Jun", "18"],
                ["105", "6 Jun", "18"],
                ["107", "—", "31"],
            ],
        },
        "question": "What should you verify before reporting the monthly total?",
        "choices": [
            {
                "id": "verify-records",
                "label": "Check whether the repeated ID is a duplicate and how missing dates should be handled.",
                "feedback": "Good. Check records against the source and the agreed quality rules before changing or counting them.",
                "supported": True,
            },
            {
                "id": "delete-row",
                "label": "Delete one repeated row and guess the missing date.",
                "feedback": "Do not remove or invent values without checking the source and the data-quality rules.",
                "supported": False,
            },
            {
                "id": "count-all",
                "label": "Count every row as a separate order because the sample is small.",
                "feedback": "The repeated ID is a quality flag to investigate; a small sample still needs validation.",
                "supported": False,
            },
        ],
        "basis": (
            "The skill is explicitly linked to this occupation in ESCO. The table is "
            "synthetic and illustrates checking duplicate and missing values; it is "
            "not an observed workplace task or a proficiency test."
        ),
    },
    CUSTOMER_SERVICE_OCCUPATION: {
        "skill_uri": IDENTIFY_CUSTOMER_NEEDS,
        "id": "clarify-customer-need",
        "title": "Clarify what the customer needs",
        "summary": "Choose a follow-up that helps uncover the customer's actual requirement.",
        "activity": {
            "type": "scenario",
            "context": (
                "A customer says: “The delivery date changed, and I need the item "
                "before my trip next week.”"
            ),
        },
        "question": "Which response best identifies the customer's need?",
        "choices": [
            {
                "id": "clarify-date",
                "label": "Ask what date they need it by and whether an alternative would solve the timing problem.",
                "feedback": "Good. A focused question and active listening clarify the customer's requirement before suggesting a solution.",
                "supported": True,
            },
            {
                "id": "sell-upgrade",
                "label": "Immediately recommend the most expensive delivery upgrade.",
                "feedback": "This assumes what the customer needs without checking their date or acceptable alternatives.",
                "supported": False,
            },
            {
                "id": "recite-policy",
                "label": "Repeat the standard delivery policy without asking how the change affects them.",
                "feedback": "Policy information may help later, but first clarify the customer's actual requirement.",
                "supported": False,
            },
        ],
        "basis": (
            "The skill is explicitly linked to this occupation in ESCO. The dialogue "
            "is an authored illustration of asking questions and listening, not a "
            "recorded customer interaction or service-quality assessment."
        ),
    },
    PRIMARY_TEACHER_OCCUPATION: {
        "skill_uri": ASSESS_STUDENTS,
        "id": "check-student-understanding",
        "title": "Check a learner's understanding",
        "summary": "Choose a next step based on one piece of student work.",
        "activity": {
            "type": "scenario",
            "context": (
                "A pupil gives an incorrect answer to one subtraction question. "
                "The written work does not show how they reached it."
            ),
        },
        "question": "What is a useful next step when assessing the pupil's understanding?",
        "choices": [
            {
                "id": "ask-method",
                "label": "Ask the pupil to explain their method, then use a similar short example to locate the difficult step.",
                "feedback": "Good. Gather more evidence of the learner's reasoning before deciding what support is useful.",
                "supported": True,
            },
            {
                "id": "assign-level",
                "label": "Assign a low ability level based on this one answer.",
                "feedback": "One answer without working is not enough to make a broad judgement about a learner's ability.",
                "supported": False,
            },
            {
                "id": "repeat-unit",
                "label": "Repeat the entire unit without checking which step caused difficulty.",
                "feedback": "First find out what the pupil understood and where the reasoning broke down.",
                "supported": False,
            },
        ],
        "basis": (
            "The skill is explicitly linked to this occupation in ESCO. The pupil's "
            "work and response options are authored practice, not a real student "
            "record or a teaching assessment."
        ),
    },
}
AVAILABLE_EXPERIENCE_EXAMPLES = [
    {
        "occupation_uri": CV_OCCUPATION,
        "occupation_label": "computer vision engineer",
        "skill_uri": IMAGE_PROCESSING,
        "skill_label": "digital image processing",
    },
    {
        "occupation_uri": DATA_ANALYST_OCCUPATION,
        "occupation_label": "data analyst",
        "skill_uri": DATA_QUALITY_ASSESSMENT,
        "skill_label": "data quality assessment",
    },
    {
        "occupation_uri": CUSTOMER_SERVICE_OCCUPATION,
        "occupation_label": "customer service representative",
        "skill_uri": IDENTIFY_CUSTOMER_NEEDS,
        "skill_label": "identify customer's needs",
    },
    {
        "occupation_uri": PRIMARY_TEACHER_OCCUPATION,
        "occupation_label": "primary school teacher",
        "skill_uri": ASSESS_STUDENTS,
        "skill_label": "assess students",
    },
]
SCENARIO_EXPERIENCES.update({
    row["occupation_uri"]: row for row in PRACTICE_SCENARIOS
})
AVAILABLE_EXPERIENCE_EXAMPLES.extend(
    {key: row[key] for key in
     ("occupation_uri", "occupation_label", "skill_uri", "skill_label")}
    for row in PRACTICE_SCENARIOS
)


def _experience_examples() -> list[dict[str, str]]:
    return [dict(row) for row in AVAILABLE_EXPERIENCE_EXAMPLES]


def _relations(rows: dict[str, list[dict[str, str]]]) -> dict[str, dict[str, str]]:
    """Use identity, not labels or similarity; essential wins duplicate rows."""
    result = {}
    for relation in ("optional", "essential"):
        for row in rows.get(relation, []):
            result[row["uri"]] = {**row, "relation": relation}
    return result


def build_career_map(
    detail: dict[str, Any],
    confirmed: dict[str, Any],
    occupations: dict[str, dict[str, Any]],
    relations: dict[str, dict[str, list[dict[str, str]]]],
) -> dict[str, Any]:
    """Expose only exact edges within the career and its chosen comparison set.

    The response includes the complete scoped set for accessible search/list
    exploration. The client limits the initial visual map, not the evidence.
    This function does not change the saved goal, comparisons, or Passport.
    """
    target = detail["occupation"]
    insurance = detail.get("stress_test", {}).get("insurance", {})
    comparison = insurance.get("comparison", {})
    career_uris = [target["uri"]]
    for career in comparison.get("alternatives", []):
        uri = career.get("uri")
        if uri in occupations and uri not in career_uris:
            career_uris.append(uri)
    scoped = {uri: _relations(relations.get(uri, {})) for uri in career_uris}
    target_skills = scoped[target["uri"]]
    # Confirmed alternative-only skills may appear, but unrelated confirmed
    # Passport entries must not acquire invented edges to the selected career.
    pool = dict(target_skills)
    for rows in scoped.values():
        for uri, skill in rows.items():
            if uri in confirmed and uri not in pool:
                pool[uri] = skill
    recommended = {
        row["uri"] for group in ("prepare", "options")
        for row in insurance.get(group, [])
    }
    descriptions = skill_descriptions()
    skills = []
    for uri, skill in pool.items():
        target_relation = target_skills.get(uri, {}).get("relation")
        skills.append({
            "uri": uri,
            "label": skill["label"],
            "confirmed": uri in confirmed,
            "relation": target_relation,
            "recommended": uri in recommended,
            "description": descriptions.get(uri, {}).get("description", ""),
            "connections": [
                {"occupation_uri": career_uri, "relation": rows[uri]["relation"]}
                for career_uri, rows in scoped.items() if uri in rows
            ],
        })
    skills.sort(key=lambda row: (
        not row["confirmed"], not row["recommended"],
        {"essential": 0, "optional": 1}.get(row["relation"], 2),
        row["label"].casefold(), row["uri"],
    ))
    return {
        "occupation": {"uri": target["uri"], "label": target["label"]},
        "occupations": [
            {"uri": uri, "label": occupations[uri]["label"],
             "is_selected": uri == target["uri"]}
            for uri in career_uris
        ],
        "skills": skills,
        "notice": (
            "Exact ESCO links within this career and your comparison set. "
            "Connections are not readiness or hiring predictions."
        ),
    }


def career_experience(
    occupation: dict[str, Any],
    relations: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    """Authored, occupation-linked practice examples, not competency assessments.

    Release only for a verified occupation/skill identity pair. No response or
    score is stored, and no Passport skill is confirmed by playing.
    """
    config = SCENARIO_EXPERIENCES.get(occupation["uri"])
    if config:
        skill = _relations(relations).get(config["skill_uri"])
        if not skill:
            return {
                "status": "unavailable",
                "notice": "The linked skill is not available in the current ESCO data.",
                "available_examples": _experience_examples(),
            }
        official = skill_descriptions().get(config["skill_uri"], {})
        return {
            "status": "available",
            "id": config["id"],
            "title": config["title"],
            "summary": config["summary"],
            "kind": "illustrative_practice",
            "notice": (
                "Synthetic practice only. No competence score, hiring claim, "
                "or Passport confirmation."
            ),
            "activity": config["activity"],
            "question": config["question"],
            "choices": config["choices"],
            "available_examples": _experience_examples(),
            "source": {
                "occupation": {
                    "uri": occupation["uri"],
                    "label": occupation["label"],
                    "description": occupation.get("description", ""),
                },
                "skill": {
                    "uri": config["skill_uri"],
                    "label": skill["label"],
                    "relation": skill["relation"],
                    "description": official.get("description", ""),
                },
                "basis": config["basis"],
            },
        }

    skill = _relations(relations).get(IMAGE_PROCESSING)
    if occupation["uri"] != CV_OCCUPATION or not skill:
        return {
            "status": "unavailable",
            "notice": "No grounded challenge for this career yet.",
            "available_examples": _experience_examples(),
        }
    official = skill_descriptions().get(IMAGE_PROCESSING, {})
    return {
        "status": "available",
        "id": "cv-contrast-stretch",
        "title": "Reveal a hidden shape",
        "summary": "Experiment with image contrast, then review what it tells you.",
        "kind": "illustrative_practice",
        "notice": "Synthetic practice only. No competency score or Passport confirmation.",
        "available_examples": _experience_examples(),
        "source": {
            "occupation": {"uri": occupation["uri"], "label": occupation["label"],
                           "description": occupation.get("description", "")},
            "skill": {"uri": IMAGE_PROCESSING, "label": skill["label"],
                      "relation": skill["relation"],
                      "description": official.get("description", "")},
            "basis": "Official ESCO occupation link and contrast-stretching knowledge. "
                     "Exercise, pixels and feedback are authored illustrations, "
                     "not benchmark measurements or workplace task observations.",
        },
        "image": {
            "width": 4,
            "height": 4,
            "pixels": [118, 118, 118, 118,
                       118, 122, 122, 118,
                       118, 122, 122, 118,
                       118, 118, 118, 118],
            "alt": "A synthetic four-by-four grayscale grid: central two-by-two "
                   "square has value 122, surrounding pixels 118.",
            "formula": "stretched = 255 * (pixel - min) / (max - min); "
                       "display = original + strength * (stretched - original)",
        },
        "question": "What can you conclude from this preview?",
        "choices": [
            {
                "id": "inspect",
                "label": "The shape is easier to inspect, not proof of model accuracy.",
                "feedback": "Yes. Contrast stretching changes visibility. Model accuracy "
                            "still needs representative labelled tests.",
                "supported": True,
            },
            {
                "id": "accuracy",
                "label": "A clearer image guarantees accurate AI predictions.",
                "feedback": "Clarity alone cannot establish prediction accuracy. "
                            "Check representative labelled tests.",
                "supported": False,
            },
            {
                "id": "qualification",
                "label": "This exercise proves professional image-processing skill.",
                "feedback": "This is a small illustrative exercise, not an assessment "
                            "of professional proficiency.",
                "supported": False,
            },
        ],
    }
