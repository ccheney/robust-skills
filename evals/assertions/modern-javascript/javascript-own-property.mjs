await check("own", () => assert.equal(answer.owns({ id: 1 }, "id"), true));
await check("inherited-excluded", () =>
  assert.equal(answer.owns(Object.create({ id: 1 }), "id"), false),
);
await check("null-prototype", () => {
  const r = Object.create(null);
  r.id = 0;
  assert.equal(answer.owns(r, "id"), true);
});
await check("shadowed", () =>
  assert.equal(answer.owns({ id: 1, hasOwnProperty: null }, "id"), true),
);
