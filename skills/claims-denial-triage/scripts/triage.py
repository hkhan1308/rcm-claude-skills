"""
Reference implementation of the CARC-code -> category -> action mapping
described in SKILL.md. Deterministic lookup logic only — the skill itself
does the plain-language translation and checklist generation; this script
is the machine-checkable backbone so that mapping stays consistent.

Usage:
    python triage.py CO-16
    python triage.py --batch denials.json
"""

import argparse
import json
from collections import Counter
from dataclasses import dataclass

CARC_MAP = {
    "CO-16": ("missing_invalid_info", "correctable"),
    "CO-125": ("missing_invalid_info", "correctable"),
    "CO-97": ("bundling", "appealable"),
    "CO-B15": ("bundling", "appealable"),
    "CO-50": ("medical_necessity", "appealable"),
    "CO-N115": ("medical_necessity", "appealable"),
    "CO-29": ("timely_filing", "write_off"),
    "CO-22": ("coordination_of_benefits", "correctable"),
    "CO-23": ("coordination_of_benefits", "correctable"),
    "CO-96": ("non_covered_service", "appealable"),
    "CO-18": ("duplicate_claim", "correctable"),
    "CO-197": ("authorization", "appealable"),
}

CHECKLISTS = {
    "missing_invalid_info": [
        "Identify the specific missing/invalid field from the remit detail",
        "Correct in the billing system",
        "Resubmit as a corrected claim, not a new claim",
    ],
    "bundling": [
        "Check NCCI edit pairs for the billed CPT combination",
        "If clinically distinct, gather documentation supporting modifier use (e.g. -59)",
        "File appeal with supporting documentation",
    ],
    "medical_necessity": [
        "Pull clinical documentation supporting the service",
        "Compare against payer's published medical policy for this service",
        "File appeal with documentation; do not plain-resubmit",
    ],
    "timely_filing": [
        "Check original submission date against payer's filing deadline",
        "Look for a timely-filing exception (retroactive eligibility, COB delay)",
        "If no exception applies, route to write-off",
    ],
    "coordination_of_benefits": [
        "Confirm primary payer via patient/COB records",
        "Rebill correct payer as primary",
        "Attach primary EOB if secondary payer requires it",
    ],
    "non_covered_service": [
        "Confirm exclusion against the plan's covered-services list",
        "If exclusion is disputed, file appeal citing plan language",
        "If confirmed, bill patient per plan terms or write off per policy",
    ],
    "duplicate_claim": [
        "Check remit history for the original claim's processed status",
        "If genuinely not a duplicate, resubmit with a note explaining the distinction",
        "If duplicate, no action — closed",
    ],
    "authorization": [
        "Check payer portal for retro-authorization eligibility",
        "If retro-auth unavailable, determine appeal-worthiness with clinical documentation",
        "Update intake workflow to prevent recurrence for this service type",
    ],
}

VERDICT_LABELS = {
    "correctable": "Correctable — resubmit",
    "appealable": "Appealable — needs documentation",
    "write_off": "Likely write-off",
}


@dataclass
class TriageResult:
    code: str
    category: str
    verdict: str
    checklist: list[str]

    def summary(self) -> str:
        lines = [
            f"Code: {self.code}",
            f"Category: {self.category.replace('_', ' ')}",
            f"Verdict: {VERDICT_LABELS[self.verdict]}",
            "Checklist:",
        ]
        lines += [f"  {i+1}. {step}" for i, step in enumerate(self.checklist)]
        return "\n".join(lines)


def triage(code: str) -> TriageResult:
    code = code.upper().strip()
    if code not in CARC_MAP:
        return TriageResult(
            code=code,
            category="unmapped",
            verdict="appealable",
            checklist=[
                "Code not in reference table — confirm code against current CMS CARC list",
                "Route to coding/billing SME for manual categorization",
            ],
        )
    category, verdict = CARC_MAP[code]
    return TriageResult(code=code, category=category, verdict=verdict, checklist=CHECKLISTS[category])


def batch_triage(codes: list[str]) -> None:
    results = [triage(c) for c in codes]
    counts = Counter(r.category for r in results)
    total = len(results)
    print(f"Batch of {total} denials — category breakdown:")
    for category, count in counts.most_common():
        pct = 100 * count / total
        print(f"  {category.replace('_', ' '):<28} {count:>3}  ({pct:.0f}%)")
    print()
    for r in results:
        print(r.summary())
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("code", nargs="?", help="Single CARC code, e.g. CO-16")
    parser.add_argument("--batch", help="Path to JSON file: a list of CARC codes")
    args = parser.parse_args()

    if args.batch:
        with open(args.batch) as f:
            codes = json.load(f)
        batch_triage(codes)
    elif args.code:
        print(triage(args.code).summary())
    else:
        parser.print_help()
