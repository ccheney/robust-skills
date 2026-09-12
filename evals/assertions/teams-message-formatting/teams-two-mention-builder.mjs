const users = [
  { id: "uid-b", name: "R&D <ops>" },
  { id: "uid-a", name: "Ada" },
];
const saved = structuredClone(users),
  out = answer.buildMentions(users);
await check("indexes", () =>
  assert.deepEqual(out.body, {
    contentType: "html",
    content: '<at id="0">R&amp;D &lt;ops&gt;</at>, <at id="1">Ada</at>',
  }),
);
await check("identities", () =>
  assert.deepEqual(
    out.mentions,
    users.map((u, i) => ({
      id: i,
      mentionText: u.name,
      mentioned: {
        user: { id: u.id, displayName: u.name, userIdentityType: "aadUser" },
      },
    })),
  ),
);
await check("input-unchanged", () => assert.deepEqual(users, saved));
await check("empty", () =>
  assert.deepEqual(answer.buildMentions([]), {
    body: { contentType: "html", content: "" },
    mentions: [],
  }),
);
await check("duplicates", () =>
  assert.equal(answer.buildMentions([users[1], users[1]]).mentions.length, 2),
);
