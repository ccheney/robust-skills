await check("validates-minor-units", () => {
  for (const n of [-1, 0.1, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1])
    assert.throws(() => new answer.Money(n, "USD"));
});
await check("currency", () =>
  assert.throws(() =>
    new answer.Money(1, "USD").add(new answer.Money(1, "EUR")),
  ),
);
await check("immutable", () => {
  const m = new answer.Money(100, "USD");
  try {
    m.cents = 900;
  } catch {}
  assert.equal(m.cents, 100);
});
await check("nonmutating-add", () => {
  const a = new answer.Money(125, "USD"),
    b = new answer.Money(75, "USD");
  const c = a.add(b);
  assert.equal(c.cents, 200);
  assert.notEqual(c, a);
  assert.equal(a.cents, 125);
  assert.equal(b.cents, 75);
});
await check("overflow", () =>
  assert.throws(() =>
    new answer.Money(Number.MAX_SAFE_INTEGER, "USD").add(
      new answer.Money(1, "USD"),
    ),
  ),
);
