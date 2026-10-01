# Submission — Vireo Audio / Set E

These answers follow the live portal's questions; no downloadable submission-form.md was listed. Prepared with substantial AI assistance, disclosed below.

## What did you build, and what business outcome does it move? State the number and the money.

A local Python tool with monthly inferred-category, intake-team and resolving-team charts, CSV exports, opening-message classification and a human-review path. I narrowed the decision to a routing pilot: 101 Q2 Billing tickets have clear delivery evidence and 134 recorded transfers. Target reducing comparable tickets from 1.33 to 0.66 transfers each. 134 × Rs 305 × 50% = Rs 20,435/quarter in released capacity at unchanged volume, not guaranteed cash. The export cannot prove which team needs two hires; it lacks active effort and staffed capacity. Closing notes establish the retrospective cohort; new suggestions use opening text only and require human confirmation. Public demo: https://vishantbhadana.github.io/vireo-support-decisions/ (synthetic demo classifier, separate from the evaluated local model). One-page memo: https://github.com/vishantbhadana/vireo-support-decisions/blob/main/docs/Priya-Memo.pdf

## What does one run cost, and what would a month cost at roughly 650 tickets a week? Show arithmetic.

No paid model calls. Full-pack analysis took about 13–15 seconds locally; API cost Rs 0/run. 650 × 52/12 = 2,816.7 tickets/month; × Rs 0/inference = Rs 0/month API cost. This is not total operating cost. Illustratively, an unmetered 30-second run at 30 W and Rs 10/kWh costs (30/3600) × 0.030 × 10 = Rs 0.0025/run, or Rs 0.075 for 30 monthly runs, excluding idle server, hardware, labour and hosting. Existing Codex access helped development; its billing was unavailable, so no invented cost. Q2 export volume is only about 182/week; savings were not scaled to the 650/week planning figure.

## How do you know it works? Sample size, checking, error rate and failures.

Uniformly sampled 60 Q2 opening messages with seed 928, assigned labels blind to model output/old tag/closing note, then joined predictions. This was AI-assisted annotation, not independent human gold labels. 56/60 category matches (93.3%); 4/60 errors (6.7%); all four flagged for review. Eight total review cases; 52/52 accepted suggestions matched this small sample, not proof of zero production error. Errors were two coupon/payment interpretations and two touchscreen cases outside the taxonomy. Separate 1,632-message unseen-text temporal check had 99.02% agreement with weak labels, explicitly not an accuracy claim. Eight regression tests passed; browser tests verified chart changes, confident/uncertain messages and empty-input rejection. Human domain validation remains a pilot gate.

## Did you change, narrow, or push back on the client's ask? What, when and why.

Before implementation, after reading the policy/email, I retained monthly charts but rejected “largest first-assigned queue gets both hires”. Intake is not workload; Billing has misroutes, Logistics elapsed time includes waiting, and Tier 2 is not comparable to Tier 1 volume. Q2 Chat Frontline is actually larger than Billing. I proposed a four-week routing pilot plus staffed-hour/active-effort evidence before a Rs 9 lakh/year allocation. I did not pretend a small capacity opportunity proves two jobs are unnecessary.

## What is wrong with the handoff? Specific bugs, shortcuts and known limitations.

The 11-class classifier uses heuristic weak labels and an uncalibrated .70 threshold. The 60-case audit was annotated by the same assistant, is small and not class-balanced; near-duplicate templates may inflate results. The pilot counts all transfers in an eligible cohort because transfer destinations are absent. A real initial bug checked refund/replacement per ticket; corrected to per order and regression-tested. Remaining order checks cover matched Q2 contacts only: 845 lack exact order linkage, and cross-quarter conflicts may be missed. No precise FCR or active handling utilisation is claimed. Legacy money units remain unresolved and are excluded from the primary case. The server is loopback-only, single-user, without production auth or live integration.

## What did you deliberately leave out, and why?

No hosted LLM/RAG/vector database/agent chain: a small local model is sufficient and avoids external customer-data disclosure and per-ticket fees. No automatic ticket movement or workforce optimiser: evidence is insufficient for a safe operational decision. No guessed currency conversion, exact FCR, product-lot failure rate or recovered-refund estimate. Customer names/demographics are not needed, so customers.csv is not loaded. Effort went to reconciliation, a measurable pilot, error inspection and a reproducible handoff.

## Anything you built or found that nobody asked for?

Corrected 2,575 negative legacy resolution intervals using the policy's UTC→IST exception; excluded 139 out-of-window rows; preserved 3,913 unknown transfer counts. Fifteen Q2 orders show refund and replacement across separate tickets; seven goodwill-coded refunds exceed Rs 500. These are Finance review flags, not fraud/loss claims or additional savings. Added channel/creation-shift response-credit exposure and surfaced the 182 versus 650 tickets/week volume mismatch.

## What did you use AI for? Tools/models, help, wasted effort, discarded work. Video link.

Used Codex, a GPT-6-based coding assistant, to read the pack, generate Python/HTML, inspect data, annotate the blind sample, write/test the tool and draft the memo. No separately called LLM inference API. Exact deployed variant and account billing were not supplied. AI helped simplify scope and find data issues; the first runtime choice wasted time through pandas/NumPy warnings. Replaced that runtime, a slow roster lookup and a same-ticket-only refund check. Discarded the misleading “99% accuracy” interpretation of weak-label agreement. The local runtime classifier is scikit-learn TF-IDF + logistic regression. Actual prompt excerpts and iterations are in docs/work-log.md; no invented prompt history. The final captioned screen recording is an actual browser capture of the prompt/iteration log, original local app and public demo, with no slides.

Public Google Drive video: https://drive.google.com/file/d/1VP9CjSd_xVwCxyG2zL_TCapyK6uIWuaD/view?usp=sharing

## Monday handover: the three things needed.

1. Use Python 3.12, copy the original private CSVs into data/raw, and follow README exactly; no API key needed. Keep all raw/generated data private.
2. Never use intake volume or elapsed resolution as a staffing verdict. Treat Rs 20,435 as a 50% transfer-reduction hypothesis; Neha owns the pilot, Arjun validates costs and Sameer reconciles coverage/effort.
3. Keep human review on; run tests/evaluation, inspect same-order Finance flags, and obtain independent labels before live routing. Scores are not calibrated confidence and there is no zero-error claim.

## Honest hours spent — one number

1.3

## Public GitHub repository

https://github.com/vishantbhadana/vireo-support-decisions

## Optional public demonstration

https://vishantbhadana.github.io/vireo-support-decisions/

Free GitHub Pages hosts the aggregate dashboard and a separate synthetic-only classifier that runs in the visitor’s browser. Raw customer records and the customer-trained model remain private. The 56/60 audit measures the original local application only; the final walkthrough explicitly distinguishes it from the public sample classifier. The original can be reproduced using the supplied pack and README. Public hosting and inference API charges: Rs 0 under GitHub Pages’ free public-repository plan; developer time and device/network costs remain separate.
