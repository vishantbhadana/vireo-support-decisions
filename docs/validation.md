# Validation, without inflated accuracy

**Audit before prediction inspection:** uniformly draw 60 Q2 opening messages with pandas random_state=928, assign one issue label and a rationale, then join model outputs. `evaluation/make_labels.py` preserves the label sequence and reproduces the draw. All are after the training cutoff, excluded by ID too; threshold was not tuned on the sample. Annotation was AI-assisted manual interpretation by the same coding assistant—not independent human adjudication. Training uses closing-note rules; inference does not see notes.

- Category match: 56/60 = 93.3%; error 4/60 = 6.7%.
- Human review: 8/60 = 13.3%; all 4 category errors were flagged.
- Accepted subset: 52/52 matches; small sample, **not proof of zero risk**. Approximate 95% Wilson accuracy interval is 93.1–100% for this subset and 84.1–97.4% overall. These describe sample uncertainty only, not annotator bias or production drift.
- Original bot tag: 38/60 matches (63.3%) against the same annotations.
- Two touchscreen cases sit outside the 11-class taxonomy; abstaining is appropriate. Counting them as safe review outcomes gives 58/60, but this is explicitly **not category accuracy**.
- Four errors: discount not applied → Returns (score .527); invalid coupon → Connectivity (.167); unresponsive touchscreens → App (.543) / Charging (.368). All below .70. Two other annotations are context-dependent; a domain reviewer may disagree.

Secondary check: 1,632 Q2 note-labeled messages absent as exact normalized strings from pre-Q2 training, 99.02% agreement with weak labels. This is a consistency check, **not gold accuracy**. Near-duplicate/synthetic-like templates remain, and weak-label rules exclude ambiguous examples. No class-balanced or multilingual benchmark, calibration study, or independent review was done. Exact-text exclusion is not semantic decontamination.

Eight automated tests verify accounting totals, timestamp fix/missingness, independent cost calculation, same-order cross-ticket detection, rejection of duplicate IDs/invalid dates, multi-issue label abstention, and identifier removal. A clean Python 3.12 environment was used. The earlier Python 3.14/NumPy 2.5 environment produced excessive pandas datetime deprecation warnings; it was discarded in favour of pinned compatible packages.

Before operational use: have Billing/Logistics leads independently label at least 100 fresh arrivals, include low-confidence/multi-issue/out-of-taxonomy cases, measure accepted-error and review rates with intervals, and keep human approval until the pilot passes. Never evaluate an agent's performance from inherited first-response breaches or compare Tier 2 attendance with Tier 1.
