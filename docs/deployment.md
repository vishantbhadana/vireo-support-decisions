# Public demonstration

Live URL: https://vishantbhadana.github.io/vireo-support-decisions/

GitHub Pages serves the static `docs/` directory from `main`. It is a free public-repository demonstration, with no paid API, server account, database, signup or visitor tracking. Normal GitHub Pages usage limits apply.

The historical charts, business calculation and audit summary are an aggregate snapshot of the original assignment analysis. The original customer-trained classifier runs locally with the supplied pack. The public input box is deliberately separate: a small classifier trained only on 88 authored fictional examples, with its training phrases and source in `public-demo/`. The 56/60 audit does not measure that sample model. Neither model should route real support tickets without independent human validation.

`build_public.py` constructs an explicit field allowlist. It excludes raw messages, names, ticket/order/customer/agent identifiers, individual review/routing rows, source-file hashes and evaluation failure IDs. It checks aggregate chart totals before writing. No customer-trained vocabulary or weights are published. The public model needs one static asset download; subsequent classification happens in the browser with no submission, storage or inference service.

## Reproduce

1. Follow the root README to generate the original private analysis and audit.
2. Run `python public-demo/train_demo.py` and `node public-demo/test_model.mjs`.
3. Run `python build_public.py`.
4. Publish only Git-tracked safe files. **Do not upload the local docs directory wholesale**: the locally saved assignment brief is private and ignored.
5. In repository Settings → Pages, choose Deploy from a branch → main → /docs.

The public model's 110 Python/JavaScript reference fixtures, malformed input handling, and pre-round 0.70 threshold checks passed. These are implementation checks, not evidence of accuracy on unseen customer complaints. Browser checks cover chart changes, a delivery suggestion, empty input handling, and no classification network request.

The final captioned screen recording covers the actual prompt log, changes and discarded work, the original local model and the public synthetic demo. It distinguishes the two models and stays within the three-minute limit. The Google Drive URL is retained by uploading a new file version.
