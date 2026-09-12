await check("seconds", () =>
  assert.equal(
    answer.dateToken(new Date(1750000000999), "2025-06-15 UTC"),
    "<!date^1750000000^{date_num} {time}|2025-06-15 UTC>",
  ),
);
await check("fallback", () =>
  assert.ok(
    answer
      .dateToken(new Date(0), "Jan 1 1970 00:00 UTC")
      .endsWith("|Jan 1 1970 00:00 UTC>"),
  ),
);
await check("negative-time", () =>
  assert.equal(
    answer.dateToken(new Date(-1), "1969 UTC"),
    "<!date^-1^{date_num} {time}|1969 UTC>",
  ),
);
