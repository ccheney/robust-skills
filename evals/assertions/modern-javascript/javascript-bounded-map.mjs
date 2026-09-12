await check("bounded", async () => {
  let active = 0,
    max = 0;
  const r = await answer.mapLimit([1, 2, 3, 4], 2, async (x) => {
    active++;
    max = Math.max(max, active);
    await new Promise((r) => setTimeout(r, 2));
    active--;
    return x * 2;
  });
  assert.equal(max, 2);
  assert.deepEqual(r, [2, 4, 6, 8]);
});
await check("uses-concurrency", async () => {
  let count = 0;
  const pending = [];
  const p = answer.mapLimit([1, 2], 2, () => {
    count++;
    return new Promise((r) => pending.push(r));
  });
  assert.equal(count, 2);
  pending.forEach((r) => r(1));
  await p;
});
await check("invalid-limit", async () => {
  for (const n of [0, -1, 1.5])
    await assert.rejects(answer.mapLimit([], n, async () => {}));
});
await check("empty", async () =>
  assert.deepEqual(await answer.mapLimit([], 2, async () => {}), []),
);
await check("errors", async () => {
  const e = new Error("failed");
  await assert.rejects(
    answer.mapLimit([1], 1, async () => {
      throw e;
    }),
    (x) => x === e,
  );
});
