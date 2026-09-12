await check("identity-keys", () => {
  const a = { id: 1 },
    b = { id: 1 };
  const rows = [
    { owner: a, n: 1 },
    { owner: b, n: 2 },
    { owner: a, n: 3 },
  ];
  const r = answer.groupByOwner(rows);
  assert.ok(r instanceof Map);
  assert.deepEqual([...r.keys()], [a, b]);
  assert.deepEqual(r.get(a), [rows[0], rows[2]]);
});
await check("row-identity", () => {
  const a = { id: 1 };
  const row = { owner: a };
  assert.equal(answer.groupByOwner([row]).get(a)[0], row);
});
await check("empty-map", () => assert.equal(answer.groupByOwner([]).size, 0));
