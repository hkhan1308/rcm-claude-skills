"""
Reference parser for a simplified 271 eligibility response representation.

This is NOT a full X12 271 parser (real X12 is segment/element delimited
EDI, not JSON). It's a reference implementation showing the decision logic
the skill applies once a 271 has been parsed into structured fields by an
upstream EDI translator (e.g. Availity, Change Healthcare, a clearinghouse
SDK). Feed it the structured dict such a translator would already give you.

Usage:
    python parse_271.py sample_271.json
"""

import json
import sys
from dataclasses import dataclass, field


# AAA reject reason codes -> (plain meaning, next step)
REJECT_REASONS = {
    "42": ("Unable to respond at current time", "Retry later; payer system issue, not a coverage denial"),
    "43": ("Invalid/missing subscriber/member ID", "Re-verify member ID against current insurance card"),
    "58": ("Invalid/missing date of birth", "Confirm DOB against government ID, check for transposition"),
    "71": ("Patient name mismatch", "Confirm legal name matches payer records, not a nickname"),
    "72": ("Invalid/missing subscriber/member name", "Resubmit with full legal name"),
    "73": ("Invalid/missing subscriber/member ID", "Verify ID digit-by-digit against the card"),
    "75": ("Subscriber/insured not found", "Confirm payer ID is correct; patient may be with a different payer"),
}


@dataclass
class EligibilityResult:
    status: str  # "active" | "inactive" | "rejected" | "not_found"
    plan_name: str | None = None
    effective_date: str | None = None
    service_covered: bool | None = None
    limitations: list[str] = field(default_factory=list)
    reject_code: str | None = None
    reject_reason: str | None = None
    next_step: str | None = None

    def summary(self) -> str:
        if self.status == "rejected":
            return (
                f"REJECTED (code {self.reject_code}): {self.reject_reason}\n"
                f"Next step: {self.next_step}"
            )
        if self.status != "active":
            return f"Status: {self.status.upper()} — no active coverage found"
        lines = [f"Status: ACTIVE — {self.plan_name or 'plan name not returned'}"]
        if self.effective_date:
            lines.append(f"Effective: {self.effective_date}")
        if self.service_covered is not None:
            lines.append(f"Requested service covered: {'yes' if self.service_covered else 'no'}")
        if self.limitations:
            lines.append("Limitations: " + "; ".join(self.limitations))
        return "\n".join(lines)


def parse_271(response: dict) -> EligibilityResult:
    """Apply the skill's interpretation rules to a structured 271 response."""
    if response.get("aaa_reject_code"):
        code = str(response["aaa_reject_code"])
        reason, next_step = REJECT_REASONS.get(
            code, ("Unrecognized reject code", "Escalate to clearinghouse/payer support with raw response")
        )
        return EligibilityResult(
            status="rejected", reject_code=code, reject_reason=reason, next_step=next_step
        )

    eb_status = response.get("eligibility_status", "").lower()
    if eb_status not in ("1", "active", "6", "inactive"):
        return EligibilityResult(status="not_found")

    status = "active" if eb_status in ("1", "active") else "inactive"
    limitations = []
    if response.get("prior_auth_required"):
        limitations.append("prior authorization required for this service")
    if response.get("visit_limit"):
        limitations.append(f"visit limit: {response['visit_limit']}")
    if response.get("network_restriction"):
        limitations.append(f"network restriction: {response['network_restriction']}")

    return EligibilityResult(
        status=status,
        plan_name=response.get("plan_name"),
        effective_date=response.get("effective_date"),
        service_covered=response.get("service_covered"),
        limitations=limitations,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_271.py <response.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        data = json.load(f)
    result = parse_271(data)
    print(result.summary())
