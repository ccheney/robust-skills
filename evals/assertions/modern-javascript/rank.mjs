await check("descending", () =>
  assert.deepEqual(
    answer.rank([{ points: 2 }, { points: 8 }]).map((x) => x.points),
    [8, 2],
  ),
);
await check("nonmutating", () => {
  const a = [{ points: 1 }, { points: 2 }];
  const before = [...a];
  const r = answer.rank(a);
  assert.notEqual(r, a);
  assert.deepEqual(a, before);
});
await check("identity", () => {
  const a = { points: 2 };
  assert.equal(answer.rank([a])[0], a);
});
await check("stable-ties", () => {
  const a = { points: 2, id: "a" },
    b = { points: 2, id: "b" };
  assert.deepEqual(answer.rank([a, b]), [a, b]);
});
await check("empty", () => assert.deepEqual(answer.rank([]), []));
