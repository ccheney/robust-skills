await check("eventual-success", async () => {
  let n = 0;
  assert.equal(
    await answer.retry(
      async () => {
        if (++n < 3) throw Error("temporary");
        return 42;
      },
      3,
      () => true,
    ),
    42,
  );
  assert.equal(n, 3);
});
await check("attempt-count", async () => {
  let n = 0;
  await assert.rejects(
    answer.retry(
      async () => {
        n++;
        throw Error("down");
      },
      2,
      () => true,
    ),
  );
  assert.equal(n, 2);
});
await check("non-retryable", async () => {
  let n = 0;
  const e = Error("auth");
  await assert.rejects(
    answer.retry(
      async () => {
        n++;
        throw e;
      },
      4,
      () => false,
    ),
    (x) => x === e,
  );
  assert.equal(n, 1);
});
await check("identity", async () => {
  const e = Error("down");
  await assert.rejects(
    answer.retry(
      async () => {
        throw e;
      },
      1,
      () => true,
    ),
    (x) => x === e,
  );
});
