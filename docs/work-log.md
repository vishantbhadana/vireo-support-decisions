# AI use and actual iteration record

## Prompt used (verbatim excerpt from the candidate's request)

“Remember when you are doing the assignment l want you to take care of each and every point they mentioned and be very very specific about each and everything.”

“We dont need to be very exhaustive but smart. I want you to first analyze everything smartly and once done with that then i want you to build something very very optimized so that there would not be too much complexities.”

This was one Codex coding-assistant session, with the supplied assignment/pack as context. No separate chat-model prompt chain or inference API was used. The assistant read the brief, generated and ran Python/HTML, interpreted the blind sample, wrote the memo and performed checks. It would be misleading to present this as independently human-written or human-validated work. Codex is a GPT-6-based coding assistant; an exact deployed model variant or account billing total was not supplied to the task.

## Actual changes (29 September 2026, started about 19:00 IST)

1. Read policy, email and raw files. Narrowed the hiring request to charts plus a routing pilot. Rejected elapsed-resolution-hours × wage as staffing cost, and did not guess the legacy currency scale.
2. Built local character TF-IDF/logistic regression with closing-note weak labels and opening-only features. Held out Q2, excluded repeated exact normalized texts from the secondary temporal test. Kept a 0.70 review threshold.
3. Drew 60 Q2 openings, assigned labels without seeing predictions, then joined predictions. Four category mismatches were all below threshold. Did not tune the threshold on those results. Discarded a possible headline “99% accurate”: that number measures agreement with weak labels, not independent correctness.
4. Replaced repeated roster DataFrame filtering with an agent-ID lookup. Replaced the initial Python 3.14/NumPy 2.5 environment after excessive pandas datetime warnings with pinned Python 3.12-compatible dependencies.
5. Corrected a real scope bug: refund-plus-replacement had been checked within one ticket, yielding zero. The policy is per order; grouping matched Q2 tickets found 15 affected orders. Added a regression test and a separate goodwill-cap review. Neither was added to the routing savings.
6. Added reconciliation tests, fail-fast duplicate/date handling, accessible monthly CSVs, local request validation and a concise handoff. Tested the dashboard in the browser: Billing chart selection, a connectivity message and empty-input rejection.

## Discarded vs never built

Actually discarded/replaced: the incompatible runtime, slow roster lookup, same-ticket-only Finance check, and the misleading weak-label-accuracy interpretation. Not built at all: hosted LLM/RAG, automated helpdesk actions, staffing optimiser and causal savings model. These are scope decisions, not imaginary earlier prototypes.

## Cost and time honesty

No paid runtime calls or external customer-data uploads. Development used existing Codex access; its billing was not available. Run/month arithmetic is in decisions.md. Final elapsed working time is entered after packaging; it is not automatically set to the five-hour cap. The walkthrough records the actual local app and this process log, not a recreated chat or slides.

## Optional public demo — 1 October 2026

User requested: “still i would prefer to deploy it somewhere as that would look more professional”. Added a free GitHub Pages demonstration after the original local implementation and recording. The public dashboard uses an explicit aggregate-field allowlist. A separate classifier is trained only on 88 authored fictional phrases and runs inside the browser. The original customer-trained model stays local; its 56/60 audit is not claimed for the public sample model.

Considered exporting hashed character n-grams from the original model, then rejected it: short n-grams can be enumerated, so hashes do not establish anonymization. Published synthetic training examples and reproducible Python/JavaScript parity tests instead. Automated implementation parity covers 110 fixtures plus invalid input, loading failure and scores on both sides of the review threshold before rounding. This does not establish unseen-complaint accuracy.
