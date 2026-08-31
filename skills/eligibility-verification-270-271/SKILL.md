---
name: eligibility-verification-270-271
description: Use this skill when validating a patient eligibility inquiry before it's sent as an EDI 270 transaction, or when interpreting an EDI 271 eligibility response (or a plain-language summary of one). Triggers include mentions of "270", "271", "eligibility verification", "eligibility check", "coverage verification", or a payer response that needs to be read for coverage status, plan details, or a rejection reason. Also use when someone pastes a raw or semi-structured eligibility response and asks whether a patient is covered, what their benefits are, or why a check failed.
---

# EDI 270/271 Eligibility Verification

## What this skill does

1. **Pre-submission (270) validation** — checks that a proposed eligibility inquiry has the fields a payer needs to return a usable answer, and flags anything that will cause a rejection before it's sent.
2. **Response (271) interpretation** — reads a 271 response (or a description of one) and produces a clear verdict: is the patient covered for the requested service, what are the plan specifics, and if it failed, exactly why and what to do next.

## Required fields for a 270 inquiry

A request is submission-ready only if all of these are present and correctly formatted:

| Field | Format notes |
|---|---|
| Subscriber/Member ID | Payer-specific format — do not guess a format, ask if uncertain |
| Patient name (first, last) | Must match payer records; nicknames commonly cause false rejections |
| Date of birth | YYYYMMDD |
| Payer ID | Not the payer's marketing name — the EDI-specific ID |
| Provider NPI | 10 digits |
| Service type code | e.g. "30" (health benefit plan coverage), "98" (professional physician visit) — match to the actual service being verified, not a generic default |
| Date of service | YYYYMMDD; future-dated for a pre-visit check |

If a field is missing, say so plainly and name which field — don't submit or simulate a request with placeholder data standing in for a real field.

## Interpreting a 271 response

Extract and report, in this order:
1. **Eligibility status** — active coverage / inactive / not found
2. **Plan details** — plan name/type, effective dates, relevant copay/coinsurance/deductible if present in the response
3. **Service-specific coverage** — whether the specific service type inquired about is covered, and any limitations (prior auth required, visit caps, network restrictions)
4. **Rejection handling** — if the response is a rejection (AAA segment), state the specific reject reason code and its plain-language meaning, and the corrective action (e.g., "subscriber ID not found — verify against the insurance card, common cause is a transposed digit or an outdated card")

## Common rejection reasons and next steps

| Reason (plain language) | Typical cause | Next step |
|---|---|---|
| Subscriber/member ID not found | Typo, outdated card, wrong payer | Re-verify ID against current insurance card |
| Patient name/DOB mismatch | Name formatting, nickname, DOB transposition | Confirm against government ID, resubmit |
| Invalid/missing NPI | Wrong provider submitted, NPI typo | Confirm rendering vs. billing provider NPI |
| Service type not covered under this inquiry | Wrong service type code used | Resubmit with correct service type code for the actual service |
| Payer system unavailable | Payer-side outage | Retry after a delay; do not treat as a coverage denial |

## Output format

Give a short structured summary: status, plan/coverage summary, any limitations, and — if rejected — the reason and fix. Don't restate the entire raw 271 segment-by-segment; translate it.

## Boundaries

This skill interprets and validates eligibility data it's given. It does not fabricate coverage details that aren't present in the input, and it does not use or store real patient identifiers — work with de-identified or synthetic data unless the user has their own compliant data pipeline.
