/* Public synthetic-phrase demo. All inference stays in this browser. */
(function (global) {
  'use strict';
  let model = null;
  const whitespace = /[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+/gu;

  function cleanText(value) {
    return value.normalize('NFKC').toLowerCase().replace(/\\n/g, ' ')
      .replace(/(?<![a-z0-9_])(?:vr|tk)[- ]?[0-9]+(?![a-z0-9_])/g, ' ')
      .replace(/[a-z0-9_.+\-]+@[a-z0-9_.\-]+/g, ' ')
      .replace(/[0-9]+/g, ' ').replace(whitespace, ' ').replace(/^ +| +$/g, '');
  }

  function validate(payload) {
    const finiteVector = array => Array.isArray(array) && array.every(Number.isFinite);
    if (!payload || payload.schema_version !== 1 || !Array.isArray(payload.classes) ||
        payload.classes.length !== 11 || !payload.classes.every(x => typeof x === 'string') ||
        !finiteVector(payload.idf) || !payload.idf.length || !payload.idf.every(x => x > 0) ||
        !finiteVector(payload.intercept) || payload.intercept.length !== payload.classes.length ||
        !Array.isArray(payload.coefficients) || payload.coefficients.length !== payload.classes.length ||
        !payload.coefficients.every(row => finiteVector(row) && row.length === payload.idf.length) ||
        !payload.vocabulary || typeof payload.vocabulary !== 'object' || Array.isArray(payload.vocabulary) ||
        Object.keys(payload.vocabulary).length !== payload.idf.length ||
        !Object.values(payload.vocabulary).every(x => Number.isInteger(x) && x >= 0 && x < payload.idf.length) ||
        new Set(Object.values(payload.vocabulary)).size !== payload.idf.length ||
        payload.max_input_chars !== 5000 || payload.review_threshold !== 0.70 ||
        JSON.stringify(payload.ngram_range) !== '[3,5]') {
      throw new Error('Unsupported demonstration model');
    }
    return payload;
  }

  async function load(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Could not load the demonstration model');
    const candidate = validate(await response.json());
    model = candidate;
    return {classes: [...model.classes], trainingRows: model.training_rows,
      purpose: model.purpose, reviewThreshold: model.review_threshold};
  }

  async function classify(message) {
    if (typeof message !== 'string') throw new Error('Enter a customer message');
    // Unicode code-point length matches Python len, including astral characters.
    if (Array.from(message).length > 5000) throw new Error('Message is too long (maximum 5000 characters)');
    const text = cleanText(message);
    if (!text) throw new Error('Enter a customer message containing words');
    if (!model) throw new Error('Demonstration model is not loaded yet');
    const counts = new Map();
    function count(gram) {
      if (!Object.prototype.hasOwnProperty.call(model.vocabulary, gram)) return;
      const index = model.vocabulary[gram];
      counts.set(index, (counts.get(index) || 0) + 1);
    }
    for (const word of text.split(' ')) {
      const padded = Array.from(' ' + word + ' ');
      for (let n = 3; n <= 5; n++) {
        let offset = 0;
        count(padded.slice(0, n).join(''));
        while (offset + n < padded.length) {
          offset++;
          count(padded.slice(offset, offset + n).join(''));
        }
        // sklearn emits a short word once, instead of once for every n.
        if (offset === 0) break;
      }
    }
    const features = [];
    let squaredNorm = 0;
    for (const [index, countValue] of counts) {
      const value = (1 + Math.log(countValue)) * model.idf[index];
      features.push([index, value]);
      squaredNorm += value * value;
    }
    const norm = Math.sqrt(squaredNorm) || 1;
    const logits = model.intercept.map((intercept, category) => {
      let score = intercept;
      for (const [index, value] of features) score += model.coefficients[category][index] * value / norm;
      return score;
    });
    const maximum = Math.max(...logits);
    const exponents = logits.map(value => Math.exp(value - maximum));
    const denominator = exponents.reduce((total, value) => total + value, 0);
    const probabilities = exponents.map(value => value / denominator);
    const order = probabilities.map((_, index) => index)
      .sort((a, b) => probabilities[b] - probabilities[a] || a - b).slice(0, 3);
    const best = order[0];
    const rounded = value => Math.round(value * 1000) / 1000;
    return {
      category: model.classes[best],
      score: rounded(probabilities[best]),
      review: probabilities[best] < model.review_threshold,
      alternatives: order.map(index => ({category: model.classes[index], score: rounded(probabilities[index])})),
    };
  }

  global.VireoDemo = Object.freeze({load, classify});
})(globalThis);
