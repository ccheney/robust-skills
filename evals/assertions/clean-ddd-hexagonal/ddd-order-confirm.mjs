await check("empty-rejected", () =>
  assert.throws(() => new answer.Order("o", []).confirm()),
);
await check("single-transition", () => {
  const o = new answer.Order("o", [{ quantity: 1, priceCents: 0 }]);
  o.confirm();
  assert.throws(() => o.confirm());
  assert.equal(o.events.length, 1);
});
await check("records-fact", () => {
  const o = new answer.Order("o-42", [{ quantity: 2, priceCents: 350 }]);
  o.confirm();
  assert.equal(o.status, "CONFIRMED");
  assert.deepEqual(o.events, [{ type: "OrderConfirmed", orderId: "o-42" }]);
});
await check("valid-items", () => {
  assert.throws(() => new answer.Order("o", [{ quantity: 0, priceCents: 1 }]));
  assert.throws(() => new answer.Order("o", [{ quantity: 1, priceCents: -1 }]));
});
await check("total", () => {
  const item = { quantity: 2, priceCents: 350 };
  const o = new answer.Order("o", [item]);
  item.priceCents = 1;
  assert.equal(o.totalCents, 700);
});
await check("input-isolation", () => {
  const items = [{ quantity: 1, priceCents: 1 }];
  const o = new answer.Order("o", items);
  items.length = 0;
  o.confirm();
  assert.equal(o.status, "CONFIRMED");
});
