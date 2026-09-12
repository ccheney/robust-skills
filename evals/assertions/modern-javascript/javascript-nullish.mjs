await check("falsy-preserved", () => {
  for (const x of [0, false, ""])
    assert.equal(answer.timeoutOf({ timeout: x }), x);
});
await check("nullish-default", () => {
  assert.equal(answer.timeoutOf({ timeout: null }), 5000);
  assert.equal(answer.timeoutOf({}), 5000);
});
await check("missing-config", () =>
  assert.equal(answer.timeoutOf(undefined), 5000),
);
