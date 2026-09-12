await check("single-encoding", () =>
  assert.equal(answer.escapeMrkdwn("R&D <ops>"), "R&amp;D &lt;ops&gt;"),
);
await check("mention-neutralized", () =>
  assert.equal(
    answer.escapeMrkdwn("<!channel> <@U999>"),
    "&lt;!channel&gt; &lt;@U999&gt;",
  ),
);
await check("link-neutralized", () =>
  assert.equal(
    answer.escapeMrkdwn("<https://evil.example|click>"),
    "&lt;https://evil.example|click&gt;",
  ),
);
await check("raw-ampersands", () =>
  assert.equal(answer.escapeMrkdwn("&lt; &amp;"), "&amp;lt; &amp;amp;"),
);
await check("preserves-content", () =>
  assert.equal(
    answer.escapeMrkdwn(`"a" 'b' café 😀 *bold*`),
    `"a" 'b' café 😀 *bold*`,
  ),
);
await check("empty", () => assert.equal(answer.escapeMrkdwn(""), ""));
