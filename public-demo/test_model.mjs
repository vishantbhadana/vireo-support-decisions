// Only localhost serves test fixtures; this is not browser automation.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import './model.js';

const modelBytes = await readFile(new URL('./model.json', import.meta.url));
const fixtures = JSON.parse(await readFile(new URL('./reference-tests.json', import.meta.url), 'utf8'));
function thresholdFixture(probability) {
  const payload = JSON.parse(modelBytes);
  payload.coefficients = payload.coefficients.map(row => row.map(() => 0));
  payload.intercept = payload.intercept.map(() => 0);
  payload.intercept[0] = Math.log(probability * (payload.classes.length - 1) / (1 - probability));
  return JSON.stringify(payload);
}
const server = createServer((request, response) => {
  if (request.url === '/model.json') {
    response.writeHead(200, {'Content-Type': 'application/json'}).end(modelBytes);
  } else if (request.url === '/invalid.json') {
    response.writeHead(200, {'Content-Type': 'application/json'}).end('{}');
  } else if (request.url === '/below-threshold.json') {
    response.writeHead(200, {'Content-Type': 'application/json'}).end(thresholdFixture(0.6996));
  } else if (request.url === '/above-threshold.json') {
    response.writeHead(200, {'Content-Type': 'application/json'}).end(thresholdFixture(0.7004));
  } else response.writeHead(404).end();
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
try {
  const base = `http://127.0.0.1:${server.address().port}`;
  await assert.rejects(VireoDemo.classify('my parcel is late'), /not loaded/);
  await assert.rejects(VireoDemo.load(base + '/missing.json'), /Could not load/);
  await assert.rejects(VireoDemo.load(base + '/invalid.json'), /Unsupported/);
  const summary = await VireoDemo.load(base + '/model.json');
  assert.equal(summary.trainingRows, 88);
  assert.equal(summary.classes.length, 11);
  let reviewCount = 0;
  let acceptedCount = 0;
  for (const fixture of fixtures.tests) {
    if (fixture.error) {
      await assert.rejects(VireoDemo.classify(fixture.message), error => error.message === fixture.error, fixture.name);
    } else {
      const result = await VireoDemo.classify(fixture.message);
      assert.deepEqual(result, fixture.expected, fixture.name);
      if (result.review) reviewCount++; else acceptedCount++;
    }
  }
  assert.ok(reviewCount > 0 && acceptedCount > 0, 'Exercise both review decisions');
  // Code points, not UTF-16 code units, define the input cap.
  assert.equal((await VireoDemo.classify('🧪'.repeat(5000))).review, true);
  await assert.rejects(VireoDemo.classify('🧪'.repeat(5001)), /maximum 5000/);
  // Both scores display as 0.700; review must depend on the unrounded value.
  await VireoDemo.load(base + '/below-threshold.json');
  assert.equal((await VireoDemo.classify('parcel')).score, 0.7);
  assert.equal((await VireoDemo.classify('parcel')).review, true);
  await VireoDemo.load(base + '/above-threshold.json');
  assert.equal((await VireoDemo.classify('parcel')).score, 0.7);
  assert.equal((await VireoDemo.classify('parcel')).review, false);
  console.log(`PASS: ${fixtures.tests.length} Python/JavaScript parity fixtures; ${acceptedCount} accepted, ${reviewCount} review; loading, malformed model, Unicode length and pre-round threshold checks.`);
  console.log('These tests establish implementation parity, not predictive quality.');
} finally {
  server.closeAllConnections();
  await new Promise(resolve => server.close(resolve));
}
