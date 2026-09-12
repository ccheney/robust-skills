import assert from 'node:assert/strict';
import { saveAll, rank } from './exports.mjs';

if (process.argv[2] === 'save-all') {
  const started = [];
  const pending = new Map();
  const save = item => {
    started.push(item);
    return new Promise(resolve => pending.set(item, resolve));
  };
  let completed = false;
  const operation = saveAll(['a', 'b', 'c'], save).then(value => { completed = true; return value; });
  assert.deepEqual(started, ['a', 'b', 'c']);
  pending.get('c')('C');
  pending.get('b')('B');
  await Promise.resolve();
  await Promise.resolve();
  assert.equal(completed, false);
  pending.get('a')('A');
  assert.deepEqual(await operation, ['A', 'B', 'C']);
  assert.deepEqual(await saveAll([], save), []);
  const failure = new Error('write failed');
  await assert.rejects(saveAll([1], () => Promise.reject(failure)), error => error === failure);
} else if (process.argv[2] === 'rank') {
  const input = [{id:'a', points:2}, {id:'b', points:5}, {id:'c', points:2}];
  const original = [...input];
  const result = rank(input);
  assert.notEqual(result, input);
  assert.deepEqual(input, original);
  assert.deepEqual(result, [input[1], input[0], input[2]]);
  assert.equal(result[0], input[1]);
  assert.deepEqual(rank([]), []);
} else {
  throw new Error('Unknown JavaScript case');
}
console.log('Behavior checks passed');
