# Vireo support decisions

A small, local tool for monthly category/team reporting and opening-message triage. It challenges a volume-only hiring decision with an auditable routing pilot. No hosted LLM, API key, database, build step or network access at runtime.

## Open the public demo

[Live dashboard](https://vishantbhadana.github.io/vireo-support-decisions/) · [1:40 original app walkthrough](https://drive.google.com/file/d/1VP9CjSd_xVwCxyG2zL_TCapyK6uIWuaD/view?usp=sharing)

The public site contains aggregate findings and a **separate, synthetic-only demonstration classifier** that runs in the visitor's browser. It does not contain customer messages, individual ticket/order records or the model trained on the supplied pack. The **56/60 audit applies only to the original local model**, not the public sample classifier. Use the local instructions below to reproduce the full assignment results. GitHub Pages hosts this static demonstration for free; no API or paid backend is required. Entered sample text is not transmitted or saved.

To rebuild the public copy after running the local analysis: `python public-demo/train_demo.py`, then `python build_public.py`. JavaScript/Python inference parity checks: `node public-demo/test_model.mjs`. The public build constructs an explicit aggregate allowlist and checks chart totals; it never copies raw input or row-level outputs. Publish `main` → `/docs` using GitHub Pages. See [deployment notes](docs/deployment.md).

## Run on a clean machine

Python **3.12** recommended (tested on 3.12.14). Use the supplied assignment pack; customer data is intentionally **not** in this repository.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p data/raw
# Copy tickets.csv, agents.csv, orders.csv and products.csv from the supplied pack into data/raw/.
python evaluation/make_labels.py
python analyze.py
python evaluate.py
python server.py
```

Open **http://127.0.0.1:8765**. Windows activation: `.venv\Scripts\activate`. Stop with Ctrl-C. Startup re-trains locally; allow roughly 15–30 seconds on a laptop. `python server.py --port 8766 --data-dir /path/to/pack` supports a different port/input directory. Evaluation scripts use `data/raw`.

The four CSVs must retain the original column names/schema. The policy and email were reviewed when making assumptions; the program does not need PDF extraction. `customers.csv` is deliberately not loaded: names, cities and membership are unnecessary for this decision. Missing input files fail with their filenames; duplicate ticket IDs and invalid creation dates fail rather than silently changing the population.

## Use

- Choose inferred category, first-assigned team or resolving team, then a series. Each chart includes all 18 months, an accessible table and CSV download.
- Try a customer opening message. Scores below 0.70 are sent for human review. Even higher scores are suggestions, not authority to move a live ticket.
- Inspect Q2 queues, first-response coverage and Finance review flags. No individual productivity ranking.
- Reproducible detailed outputs are in `output/`, including `ticket-results.csv`, `routing-opportunity.csv`, `same-order-refund-replacement.csv` and `goodwill-review.csv`. These files are private and ignored by Git.

## Verify

```sh
python tests.py
python evaluate.py
```

Eight regression tests cover denominator reconciliation, timezone/missingness, money arithmetic, cross-ticket same-order policy, invalid inputs and ambiguous training labels. Pack-dependent tests skip if inputs are absent. Evaluation recreates a 60-ticket Q2 sample (seed 928), annotated from opening messages before inspecting predictions. Labels were assigned by the coding assistant, **not independent human experts**. The full audit is regenerated privately in `evaluation/report.json` and `evaluation/audit-results.csv`.

Observed: 56/60 category matches (93.3%); 4/60 errors (6.7%), all four routed to review. Eight total abstentions; 52/52 accepted suggestions matched this small audit. Do not infer zero production error. See [validation](docs/validation.md).

## Decision and scope

Q2: 101 of 450 Billing intake tickets satisfy a conservative delivery-misroute review definition, with 134 recorded transfers. Halving those transfers gives **134 × Rs 305 × 50% = Rs 20,435 per quarter** in capacity value at unchanged volume. This is a pilot target, not booked cash or a reason to eliminate jobs. The historical eligibility definition uses closing-note evidence; deployment uses opening-message suggestions plus human confirmation.

See [Priya memo](docs/memo-priya.md), [decisions/costs](docs/decisions.md), [AI work log](docs/work-log.md), and [submission answers](submission-form.md). Memo PDF is a private handoff artifact, generated separately.

## Architecture and privacy

`analyze.py` → timestamp/roster reconciliation → weak labels from unambiguous closing notes → character TF-IDF + logistic regression trained before Q2 → monthly exports + business case. `server.py` uses Python's standard HTTP server, listening on **loopback only**; `web/index.html` is plain HTML/CSS/JS. No telemetry, CDN assets or external requests. Inference messages are not logged or persisted. This is a single-user prototype, not an authenticated production service. Do not expose its port publicly.

No bundled customer records, private links, customer-trained model, credentials or raw screenshots. To reproduce the supplied-pack figures, the reviewer supplies the original CSVs. The separately labelled public classifier uses authored synthetic examples and is never substituted in the assignment evaluation.
