await check("neutralize-tags", () =>
  assert.equal(
    answer.escapeHtml('<at id="0">Admin</at>'),
    '&lt;at id="0"&gt;Admin&lt;/at&gt;',
  ),
);
await check("escape-order", () =>
  assert.equal(answer.escapeHtml("R&D <ops>"), "R&amp;D &lt;ops&gt;"),
);
await check("literal-entities", () =>
  assert.equal(answer.escapeHtml("&lt;"), "&amp;lt;"),
);
await check("unicode", () =>
  assert.equal(answer.escapeHtml("café 😀"), "café 😀"),
);
await check("empty", () => assert.equal(answer.escapeHtml(""), ""));
