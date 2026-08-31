---
name: claims-denial-triage
description: Use this skill when triaging a payer claim denial or an EOB (Explanation of Benefits) line showing a denial. Triggers include mentions of a CARC or RARC code, "denial", "denied claim", "EOB", "rejection reason", or someone pasting denial text and asking why a claim was denied, whether it's worth appealing, or what to do next. Also use for batches of denials that need categorizing by root cause for a denial-trend report.
---

# Claims Denial Triage

## What this skill does

Given a denial (a CARC code, a RARC code, free-text denial reason, or a pasted EOB line), this skill:
1. Identifies the denial category (the *root cause type*, not just the code)
2. States whether it's a **correctable/resubmittable** denial, an **appealable** denial, or a **write-off** candidate
3. Produces a short resubmission or appeal checklist

## Denial category reference

CARC (Claim Adjustment Reason Codes) map to root-cause categories. The category — not the raw code — determines the correct action:

| Category | Example CARCs | Typical cause | Action |
|---|---|---|---|
| **Missing/invalid information** | CO-16, CO-125 | Missing modifier, invalid ID, incomplete claim | Correct and resubmit — usually same-day fixable |
| **Bundling / unbundling** | CO-97, CO-B15 | Service considered included in another billed procedure | Review NCCI edits; appeal only if unbundling is clinically justified |
| **Medical necessity** | CO-50, CO-N115 | Payer's clinical criteria not met per documentation submitted | Appeal with additional clinical documentation, not a plain resubmission |
| **Timely filing** | CO-29 | Claim submitted after payer's filing deadline | Usually not correctable — check for a timely-filing exception (e.g. retroactive eligibility) before writing off |
| **Coordination of benefits** | CO-22, CO-23 | Another payer is primary | Rebill correct payer as primary, or submit COB documentation |
| **Non-covered service** | CO-96 | Plan excludes the service entirely | Appeal only if coverage exclusion is disputed; otherwise bill patient per plan terms or write off |
| **Duplicate claim** | CO-18 | Same claim already processed | Verify against remit history before resubmitting — do not blind-resubmit |
| **Authorization** | CO-197 | Prior auth missing or doesn't match services billed | Check if retro-auth is available from payer; if not, likely appeal or write-off |

## Triage output format

For each denial, give:
- **Category** (from the table above, or closest match)
- **Root cause** in plain language
- **Correctable / Appealable / Write-off** verdict
- **Checklist** — 2–4 concrete next steps, in order

Don't just restate the CARC code's official description — translate it into what the biller actually needs to do next.

## Batch triage

For multiple denials at once, group by category first and give a per-category count before triaging individually — this is what turns a denial list into a trend report a revenue cycle team can act on (e.g. "40% of this batch is CO-16 missing-modifier — that's a front-end coding fix, not a payer issue").

## Boundaries

This skill classifies and routes denials based on stated codes/reasons — it does not have access to the actual claim, payer contract, or medical record, so appeal-worthiness calls involving clinical judgment should be flagged for coding/clinical review rather than decided outright. Treat all example claim, patient, or provider data as synthetic; do not process real PHI through this skill.
