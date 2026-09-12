await check("intended-assignee", () =>
  assert.equal(
    answer.assignment("U234", "ready"),
    "Assigned to <@U234>: ready",
  ),
);
await check("untrusted-note", () =>
  assert.equal(
    answer.assignment("U234", "<@U999> & <!here>"),
    "Assigned to <@U234>: &lt;@U999&gt; &amp; &lt;!here&gt;",
  ),
);
await check("alternate-id", () =>
  assert.equal(answer.assignment("UABC", "😀"), "Assigned to <@UABC>: 😀"),
);
