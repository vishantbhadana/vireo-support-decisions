# Separate public demonstration classifier

This directory contains a small browser-only demonstration trained on **88 explicitly authored fictional phrases** in `phrases.json` (eight per category). No supplied customer messages, customer identifiers, order details or private trained vocabulary are read or exported by `train_demo.py`.

This is **not the audited local classifier**. The 56/60 result, routing-cohort selection and historical category charts belong to the original private-data analysis described in the main repository. They do not measure the quality of this public phrase-trained model. The public model has no independently measured predictive accuracy and must not be used to make real support-routing decisions. Its review threshold is a fixed 0.70 demonstration rule; scores are not calibrated confidence.

## Browser interface

```html
<script src="public-demo/model.js"></script>
<script type="module">
  await VireoDemo.load('public-demo/model.json');
  const suggestion = await VireoDemo.classify('My parcel has not arrived.');
  // {category, score, review, alternatives: [{category, score}, ...]}
</script>
```

Call `load` once; inference runs entirely in the browser, without network requests, storage, telemetry or external libraries. Loading the static model itself requires one same-origin asset request. The maximum input is 5,000 Unicode code points. Empty inputs and inputs reduced to only stripped identifiers are rejected. Unknown vocabulary yields an uncertain suggestion and must be reviewed.

The pipeline applies the explicitly shared text normalization, character-boundary 3–5-gram TF-IDF with sublinear term frequency and L2 normalization, then multiclass logistic regression. The model includes readable n-grams only from the published fictional phrases. Nothing here purports to anonymize privately trained model features.

## Rebuild and verify

From the repository root, with its Python requirements installed and Node.js available:

```sh
python public-demo/train_demo.py
node public-demo/test_model.mjs
```

The generator opens only `phrases.json` and writes `model.json` and `reference-tests.json` in this directory. The tests compare browser JavaScript output with Python sklearn reference output for all 88 phrases and edge cases: one/two-character tokens, unseen words, repetition, actual/literal newlines, fictional email/IDs, Unicode, invalid input and size limits. An independent controlled-model check confirms that 0.6996 and 0.7004 both display as 0.700 but receive different review decisions. These tests check implementation parity, not held-out model quality.
