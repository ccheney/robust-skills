await check("special-keys", () => {
  const rows = ["__proto__", "constructor", "toString", "__proto__"].map(
    (name) => ({ name }),
  );
  const r = answer.groupByName(rows);
  assert.deepEqual(r.__proto__, [rows[0], rows[3]]);
  assert.equal(r.constructor[0], rows[1]);
});
await check("null-prototype", () =>
  assert.equal(
    Object.getPrototypeOf(answer.groupByName([{ name: "x" }])),
    null,
  ),
);
await check("empty", () =>
  assert.deepEqual(Object.keys(answer.groupByName([])), []),
);
