await check("lazy", () => {
  let pulls = 0;
  function* source() {
    pulls++;
    yield 1;
  }
  const r = answer.take(source(), 1);
  assert.equal(pulls, 0);
  assert.deepEqual([...r], [1]);
});
await check("bounded-consumption", () => {
  let pulls = 0;
  function* source() {
    for (let i = 0; i < 10; i++) {
      pulls++;
      yield i;
    }
  }
  assert.deepEqual([...answer.take(source(), 2)], [0, 1]);
  assert.equal(pulls, 2);
});
await check("closes-source", () => {
  let closed = false;
  function* s() {
    try {
      yield 1;
      yield 2;
    } finally {
      closed = true;
    }
  }
  [...answer.take(s(), 1)];
  assert.equal(closed, true);
});
await check("zero", () => {
  let pulls = 0;
  function* s() {
    pulls++;
    yield 1;
  }
  assert.deepEqual([...answer.take(s(), 0)], []);
  assert.equal(pulls, 0);
});
