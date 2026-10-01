"""Build the separate public demonstration model from authored phrases only.

This script never imports analyze.py or opens any supplied assignment data.
Run with the existing Python requirements from the repository root.
"""
from pathlib import Path
import json
import re
import unicodedata

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

HERE = Path(__file__).resolve().parent
MAX_INPUT_CHARS = 5000
THRESHOLD = 0.70
WHITESPACE = r"[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]"


def clean_text(message):
    # Deliberately specified for the browser port; this demo has no personal data.
    value = unicodedata.normalize("NFKC", message).lower().replace("\\n", " ")
    value = re.sub(r"(?<![a-z0-9_])(?:vr|tk)[- ]?[0-9]+(?![a-z0-9_])", " ", value)
    value = re.sub(r"[a-z0-9_.+\-]+@[a-z0-9_.\-]+", " ", value)
    value = re.sub(r"[0-9]+", " ", value)
    return re.sub(WHITESPACE + "+", " ", value).strip(" ")


def response(model, message):
    if not isinstance(message, str):
        raise ValueError("Enter a customer message")
    if len(message) > MAX_INPUT_CHARS:
        raise ValueError(f"Message is too long (maximum {MAX_INPUT_CHARS} characters)")
    clean = clean_text(message)
    if not clean:
        raise ValueError("Enter a customer message containing words")
    probabilities = model.predict_proba([clean])[0]
    # Stable class-index tie break is shared with the browser implementation.
    order = sorted(range(len(probabilities)), key=lambda i: (-probabilities[i], i))[:3]
    best = order[0]
    return {
        "category": str(model.classes_[best]),
        "score": round(float(probabilities[best]), 3),
        "review": bool(probabilities[best] < THRESHOLD),
        "alternatives": [
            {"category": str(model.classes_[i]), "score": round(float(probabilities[i]), 3)}
            for i in order
        ],
    }


def main():
    phrases = json.loads((HERE / "phrases.json").read_text())
    if len(phrases) != 11 or any(len(examples) != 8 for examples in phrases.values()):
        raise ValueError("Expected eleven categories with eight authored phrases each")
    messages = [clean_text(text) for examples in phrases.values() for text in examples]
    labels = [category for category, examples in phrases.items() for _ in examples]
    if len(messages) != len(set(messages)):
        raise ValueError("Training phrases must be distinct")
    model = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                min_df=1, max_features=35000, sublinear_tf=True,
                                lowercase=False)),
        ("clf", LogisticRegression(C=4, class_weight="balanced", max_iter=500,
                                   random_state=42)),
    ])
    model.fit(messages, labels)
    vectorizer, classifier = model["tfidf"], model["clf"]
    exported = {
        "schema_version": 1,
        "purpose": "synthetic-phrase demonstration only; not the audited local model",
        "training_source": "public-demo/phrases.json; 88 explicitly authored fictional phrases",
        "training_rows": len(messages),
        "max_input_chars": MAX_INPUT_CHARS,
        "review_threshold": THRESHOLD,
        "ngram_range": [3, 5],
        "classes": model.classes_.tolist(),
        "vocabulary": {k: int(v) for k, v in vectorizer.vocabulary_.items()},
        "idf": vectorizer.idf_.tolist(),
        "coefficients": classifier.coef_.tolist(),
        "intercept": classifier.intercept_.tolist(),
    }
    (HERE / "model.json").write_text(json.dumps(exported, ensure_ascii=False, separators=(",", ":")) + "\n")
    # These are implementation-parity fixtures, not a held-out quality evaluation.
    fixtures = [
        (f"authored-example-{i + 1}", text)
        for i, text in enumerate([text for examples in phrases.values() for text in examples])
    ]
    fixtures += [
        ("delivery-paraphrase", "My parcel hasn't arrived. Could you check the delivery status?"),
        ("connectivity-paraphrase", "Bluetooth keeps disconnecting from my laptop."),
        ("short-one-letter", "a"),
        ("short-two-letters", "hi"),
        ("unknown", "zyxqv zyxqv"),
        ("repeated", "refund refund refund refund refund"),
        ("literal-newline", r"my parcel\nhas not arrived"),
        ("actual-newline", "my parcel\nhas not arrived"),
        ("email-and-identifiers", "My parcel VR12345 TK-999 is late; contact invented@example.test"),
        ("unicode-accent", "Café headphones have a Bluetooth connexion problem."),
        ("unicode-emoji", "My earbuds 🔋 will not charge 😟"),
        ("unicode-only", "こんにちは 世界"),
        ("unicode-whitespace", "My\u00a0parcel\u2003has\u202fnot arrived"),
        ("compatibility-normalization", "Ｍｙ ｐａｒｃｅｌ ｈａｓ ｎｏｔ ａｒｒｉｖｅｄ"),
        ("punctuation", "Bluetooth??? Pairing!!! Failed..."),
        ("unknown-hardware", "The touchscreen is unresponsive."),
        ("max-length-valid", "x" * MAX_INPUT_CHARS),
    ]
    tests = []
    for name, message in fixtures:
        result = response(model, message)
        tests.append({"name": name, "message": message, "expected": result})
    for name, message in [("empty", ""), ("spaces", " \n\t "),
                          ("identifiers-only", "VR1234 TK567 invented@example.test"),
                          ("over-limit", "x" * (MAX_INPUT_CHARS + 1)),
                          ("non-string", None)]:
        try:
            response(model, message)
        except ValueError as error:
            tests.append({"name": name, "message": message, "error": str(error)})
        else:
            raise AssertionError(f"Invalid fixture unexpectedly accepted: {name}")
    (HERE / "reference-tests.json").write_text(json.dumps({
        "purpose": "Python/JavaScript implementation parity; not classification accuracy",
        "tests": tests,
    }, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"training_rows": len(messages), "classes": len(model.classes_),
                      "features": len(vectorizer.vocabulary_), "parity_fixtures": len(tests),
                      "review_fixtures": sum(t.get("expected", {}).get("review", False) for t in tests),
                      "model_bytes": (HERE / "model.json").stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
