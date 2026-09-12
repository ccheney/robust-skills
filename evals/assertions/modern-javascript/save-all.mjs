await check("concurrent-start", async () => {
  const started = [];
  const pending = [];
  const op = answer.saveAll([1, 2, 3], (x) => {
    started.push(x);
    return new Promise((r) => pending.push(r));
  });
  assert.deepEqual(started, [1, 2, 3]);
  pending.forEach((r, i) => r(i));
  await op;
});
await check("resolved-values", async () =>
  assert.deepEqual(await answer.saveAll([3, 1], async (x) => x * 2), [6, 2]),
);
await check("input-order", async () => {
  const pending = new Map();
  const op = answer.saveAll(
    ["a", "b"],
    (x) => new Promise((r) => pending.set(x, r)),
  );
  pending.get("b")("B");
  pending.get("a")("A");
  assert.deepEqual(await op, ["A", "B"]);
});
await check("rejection", async () => {
  const error = new Error("storage unavailable");
  await assert.rejects(
    answer.saveAll([1], async () => {
      throw error;
    }),
    (e) => e === error,
  );
});
await check("empty", async () =>
  assert.deepEqual(await answer.saveAll([], async () => {}), []),
);
