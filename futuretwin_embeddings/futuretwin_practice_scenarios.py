"""Locally authored illustrative exercises; no inference, network calls or scoring."""
from __future__ import annotations


def _scenario(
    occupation_id: str, occupation_label: str, skill_id: str, skill_label: str,
    slug: str, title: str, summary: str, context: str, question: str,
    answers: list[tuple[str, str, bool]], activity: dict | None = None,
) -> dict:
    return {
        "occupation_uri": "http://data.europa.eu/esco/occupation/" + occupation_id,
        "occupation_label": occupation_label,
        "skill_uri": "http://data.europa.eu/esco/skill/" + skill_id,
        "skill_label": skill_label,
        "id": slug,
        "title": title,
        "summary": summary,
        "activity": activity or {"type": "scenario", "context": context},
        "question": question,
        "choices": [
            {"id": f"option-{i + 1}", "label": label, "feedback": feedback,
             "supported": supported}
            for i, (label, feedback, supported) in enumerate(answers)
        ],
        "basis": (
            "The career and skill are linked by an exact ESCO identifier pair, "
            "checked against the local catalog before release. The scenario, "
            "sample data, answers and feedback are locally authored illustrations, "
            "not observed workplace tasks, a professional assessment or evidence "
            "of proficiency. No AI service is called and no answer is saved."
        ),
    }


PRACTICE_SCENARIOS = [
    _scenario(
        "c40a2919-48a9-40ea-b506-1f34f693496d", "web developer",
        "2522a6ce-3202-4ac8-9f5b-b9cb5a3a83a1", "debug software",
        "web-debug-boundary", "Find a boundary bug",
        "Compare a requirement with a small piece of code.",
        "A shop offers free shipping on orders of at least 50 credits. "
        "The current check is: return total > 50. An order of exactly 50 is charged shipping.",
        "Which change and check best address this bug?",
        [
            ("Change the threshold to total > 49 and test only 51.",
             "That changes the threshold for decimal amounts too. Check the stated boundary, not just one larger value.", False),
            ("Use total >= 50, then test 49, 50 and 51.",
             "Yes. The inclusive comparison matches 'at least', and tests on both sides help check the boundary.", True),
            ("Remove the condition and give every order free shipping.",
             "This avoids the symptom but no longer implements the stated requirement.", False),
        ],
    ),
    _scenario(
        "69bcbb0a-8d80-4ecd-b0a4-9adea2a40de2", "graphic designer",
        "25f4c955-e429-44a6-98a7-7d8cb3b6b690", "follow a brief",
        "design-check-brief", "Check a design against its brief",
        "Separate design preferences from required information.",
        "A poster brief requires a readable event date, venue and registration link. "
        "The draft has an attractive illustration and date, but the supplied brief does not state a venue.",
        "What should you do before signing off the poster?",
        [
            ("Keep the illustration and publish without the venue.",
             "An attractive design does not replace information explicitly required by the brief.", False),
            ("Invent a likely venue so the poster looks finished.",
             "Do not fabricate event details. Obtain the missing information from the responsible person.", False),
            ("Ask the client for the venue and check all required information is readable.",
             "Yes. Resolve missing requirements and check readability before approval.", True),
        ],
    ),
    _scenario(
        "8b6388a4-4904-471b-9331-d3b1211f5525", "ICT project manager",
        "22902bf9-cc3f-495b-811a-c441e28e23f6", "manage project information",
        "project-version-check", "Resolve conflicting project information",
        "Decide how to handle two different delivery dates.",
        "A shared plan says delivery is Friday. A newer meeting note says Monday, "
        "but has no approval record. Two teams are following different dates.",
        "What is the most useful next step?",
        [
            ("Confirm the authorised date with the accountable owner, update the controlled plan and notify both teams.",
             "Yes. Establish the approved information, record the change and make the same version available to everyone.", True),
            ("Assume the newest file is approved and delete the older plan.",
             "A newer timestamp alone does not establish approval, and deleting the record loses useful history.", False),
            ("Let each team choose whichever date is easier.",
             "That leaves the conflict unresolved and makes coordination harder.", False),
        ],
    ),
    _scenario(
        "dc97adbe-f807-4ad8-8f3c-c24b3416cdef", "digital marketing manager",
        "9c6e951f-aa88-4890-983d-e7a6ee49f5bb", "plan marketing campaigns",
        "marketing-plan-objective", "Plan a campaign around its objective",
        "Choose a measurable plan rather than chasing views alone.",
        "A community workshop wants 30 registrations from local adults within two weeks. "
        "The campaign has a fixed budget of 500 credits.",
        "Which plan most directly supports that brief?",
        [
            ("Spend the whole budget on the channel with the most views, without tracking registrations.",
             "Views alone cannot tell you whether the registration objective is being met.", False),
            ("Define the local audience, choose relevant channels, set a spending limit and track completed registrations.",
             "Yes. Audience, channels, budget and a registration measure connect the plan to its objective.", True),
            ("Post identical messages everywhere and report likes as completed registrations.",
             "Likes and registrations are different actions. Do not substitute one measure for the other.", False),
        ],
    ),
    _scenario(
        "d3e32e5e-7f24-48e3-b939-e4f800eb62fb", "human resources officer",
        "e1f09038-b493-4771-ae29-a2d3e7ea013a", "document interviews",
        "hr-interview-notes", "Write useful interview notes",
        "Record job-relevant evidence without turning impressions into facts.",
        "A candidate explains how they tracked deadlines in a previous project. "
        "You need notes for a panel that uses the same job-related criteria for every candidate.",
        "Which note is most useful for the panel?",
        [
            ("They seemed like someone I would enjoy spending time with.",
             "A personal impression is not evidence against the agreed job criteria.", False),
            ("Include unrelated personal details to make the notes more memorable.",
             "Keep records relevant to the role and avoid unnecessary personal information.", False),
            ("Record the specific deadline-tracking example and identify which job criterion it relates to.",
             "Yes. Separate factual evidence from interpretation and apply consistent, job-related criteria.", True),
        ],
    ),
    _scenario(
        "51cd3a7a-eae6-4dc6-9f24-179d7ec6d230", "logistics analyst",
        "8029637c-00eb-4764-ae88-387611176c4b", "analyse logistic needs",
        "logistics-capacity-gap", "Spot a delivery capacity gap",
        "Check capacity and timing before promising a shipment.",
        "",
        "What should you establish before confirming today's dispatch plan?",
        [
            ("Assume the existing pickup can carry all 20 parcels.",
             "The confirmed capacity is only 10. An assumption does not resolve the shortfall.", False),
            ("Confirm capacity for the remaining 10 parcels and a pickup that meets the dispatch cutoff.",
             "Yes. Both capacity and timing must meet the stated need before a plan is confirmed.", True),
            ("Change the recorded parcel count to 10 so it matches the booking.",
             "Do not change the actual requirement to make a capacity problem disappear.", False),
        ],
        activity={
            "type": "table", "caption": "Synthetic dispatch requirements",
            "headers": ["Item", "Confirmed value"],
            "rows": [["Parcels ready", "20"], ["Booked pickup capacity", "10 parcels"],
                     ["Dispatch cutoff", "16:00"], ["Booked pickup time", "15:00"]],
        },
    ),
    _scenario(
        "ac1fc6a9-70d2-475c-8fa0-82ef83830968", "environmental engineer",
        "4e87c852-602a-4a0e-b8d8-20709ce14ac5", "assess the life cycle of resources",
        "environment-life-cycle", "Compare products over their life cycle",
        "Identify the information needed before making an environmental claim.",
        "A team wants to compare a reusable cup with a disposable cup for the same beverage service. "
        "They have not measured production, washing, transport, number of reuses or disposal.",
        "What would make the comparison more defensible?",
        [
            ("Choose a shared service basis and collect production, use, washing, transport and end-of-life data.",
             "Yes. A common comparison basis and explicit boundaries help identify the evidence needed. The result still depends on the data and assumptions.", True),
            ("Declare the reusable cup better solely because its label says reusable.",
             "A label alone does not establish the impacts over the full life cycle.", False),
            ("Count only disposal and ignore all other stages.",
             "That incomplete boundary could miss important impacts. State and justify the stages included.", False),
        ],
    ),
    _scenario(
        "a47f82d3-4cf7-4abf-bb36-2c8cbad28234", "journalist",
        "525046fb-3e1a-4083-88e7-5db7e88bc4f7", "check correctness of information",
        "journalism-verify-source", "Verify a claim before publishing",
        "Check the source, timing and scope of a circulating claim.",
        "An undated screenshot claims a local bridge closes tomorrow. "
        "It does not identify the issuing authority or link to an original notice.",
        "What is the strongest next verification step?",
        [
            ("Publish it as confirmed because many accounts shared it.",
             "Repeated sharing is not independent confirmation of a claim.", False),
            ("Add a plausible quote from an official to make the report clearer.",
             "Never invent a quote or attribute words to a source you have not consulted.", False),
            ("Find the original dated notice, confirm it with the responsible authority and state any remaining uncertainty.",
             "Yes. Verify the primary source, date and scope before presenting the closure as fact.", True),
        ],
    ),
    _scenario(
        "60082a99-d8ef-4e84-9290-78902681b6ed", "business analyst",
        "43d1d56b-ce62-4fe8-8f18-35d92ec73023", "identify undetected organisational needs",
        "business-find-underlying-need", "Find the need behind a feature request",
        "Explore the workflow before choosing a solution.",
        "A team requests a new dashboard because reports arrive late. "
        "Early conversations suggest staff re-enter the same figures in three systems, but this has not been checked.",
        "What should you do before recommending a solution?",
        [
            ("Map the reporting process with users, check where delays occur and agree the underlying need.",
             "Yes. Validate the suspected bottleneck and the desired outcome before deciding whether a dashboard is the right response.", True),
            ("Buy a dashboard immediately because it was the first request.",
             "The requested feature may not solve the underlying delay.", False),
            ("Assume staff are careless and remove their access without investigation.",
             "That is an unsupported explanation and does not establish the organisational need.", False),
        ],
    ),
    _scenario(
        "8d9ec84d-cf2d-4179-87bc-335cda54a427", "database designer",
        "6c08403c-a5bb-4868-b8c2-b7d039c0e511", "design database scheme",
        "database-customer-orders", "Model customers and orders",
        "Choose a structure for a one-to-many relationship.",
        "Each customer can place several orders. Each order belongs to one customer. "
        "Customer contact details should have one maintained record.",
        "Which design best represents these requirements?",
        [
            ("Store all order numbers as a comma-separated value in each customer's name field.",
             "Mixing unrelated values into a name field makes relationships difficult to validate and query.", False),
            ("Use separate Customers and Orders tables, with Orders referring to a stable customer ID.",
             "Yes. This represents the one-to-many relationship while keeping one maintained customer record.", True),
            ("Use one shared customer record for everyone to avoid duplicates.",
             "That loses customer identity and does not represent the stated relationship.", False),
        ],
    ),
    _scenario(
        "eda0d957-3c3c-4139-b89a-a18bc9e18897", "accountant",
        "5f1ebff6-98ec-411f-a1d4-0bf04bd03bdf", "check accounting records",
        "accounting-source-check", "Investigate a record discrepancy",
        "Check the supporting records before correcting an amount.",
        "",
        "What should you do about the different amounts for the same invoice?",
        [
            ("Alter the invoice so it matches the ledger without documenting the change.",
             "Do not alter source evidence to hide a difference.", False),
            ("Ignore the difference because the amounts are close.",
             "A discrepancy still needs to be checked against the supporting records and the applicable procedure.", False),
            ("Compare the original invoice, entry and supporting records, then document any authorised correction.",
             "Yes. Establish the cause using source evidence and follow the correction procedure. This sample is not professional accounting advice.", True),
        ],
        activity={
            "type": "table", "caption": "Synthetic invoice check, amounts in credits",
            "headers": ["Record", "Invoice ID", "Amount"],
            "rows": [["Original invoice", "INV-104", "120"],
                     ["Ledger entry", "INV-104", "102"]],
        },
    ),
    _scenario(
        "1a07bd7d-2e1d-4930-a84a-1a442b8f2a44", "translator",
        "637ca2e2-0624-48b1-be6e-9ff4580344ac", "proofread text",
        "translation-check-details", "Check details in a translated notice",
        "Compare dates and times with the source, not appearance alone.",
        "A source notice states that a meeting is on 10 June at 09:00. "
        "The translated draft reads 11 June at 09:00 and has consistent formatting.",
        "What should you check before approving the draft?",
        [
            ("Leave the date because the formatting is consistent.",
             "Consistent presentation does not establish that the translated information is correct.", False),
            ("Verify the date against the source, correct the mismatch and check the other details for consistency.",
             "Yes. Check factual details against the source and resolve discrepancies rather than guessing.", True),
            ("Replace both dates with an unspecified later date.",
             "That removes information from the source and invents a new meaning.", False),
        ],
    ),
]
