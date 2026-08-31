# RCM Claude Skills

Two [Claude Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) built from real healthcare Revenue Cycle Management (RCM) workflows: EDI 270/271 eligibility verification and payer claims-denial triage.

Both are distilled from patterns used in production RCM automation — eligibility checks that fed a 300K/year verification pipeline, and denial-triage logic behind a $99M claims recovery effort. The skills package that domain logic so Claude can apply it consistently: read a request or a denial, classify it correctly, and produce the right next action.

## What's here

| Skill | Does |
|---|---|
| [`eligibility-verification-270-271`](skills/eligibility-verification-270-271/) | Validates a 270 eligibility inquiry before submission, and interprets a 271 response — coverage status, plan details, rejection reason, and next step |
| [`claims-denial-triage`](skills/claims-denial-triage/) | Classifies a payer denial by CARC/RARC code, determines whether it's correctable or appealable, and drafts a resubmission checklist |

## Why skills, not just prompts

Both workflows have real structure: fixed code sets (CARC/RARC, HIPAA 270/271 segments), decision rules that don't change per-request, and outputs that downstream systems depend on being consistent. A skill packages that structure once — field requirements, code tables, decision logic — instead of re-explaining it in every prompt. That's the same reason these were originally built as reusable rule sets in the automation pipelines they came from, not as one-off scripts.

## Using these skills

Drop a skill folder into your Claude Skills directory (or point Claude at this repo) and reference it by name, e.g. "use claims-denial-triage on this EOB." Each `SKILL.md` documents its own trigger conditions and expected input format.

## Disclaimer

Code tables (CARC/RARC) are the public CMS/X12 reference sets. Sample requests, denials, and policy text throughout are synthetic — no real patient, claim, or PHI data is used anywhere in this repo.

## Author

Built by [Hamza Naeem](https://linkedin.com/in/hamza-shahbaz-naeem-98325968) — TPM background in healthcare RCM automation (EDI eligibility, claims denial recovery, HIPAA-regulated AI agent delivery).
