await check("metacharacters", () => {
  for (const s of ["a.b", "[draft]", "x+y", "(foo)", "$5", "\\"])
    assert.equal(answer.literalPattern(s).test(s), true);
  assert.equal(answer.literalPattern("a.b").test("axb"), false);
});
await check("anchored", () => {
  assert.equal(answer.literalPattern("cat").test("cats"), false);
  assert.equal(answer.literalPattern("cat").test("bobcat"), false);
});
await check("empty", () => {
  assert.equal(answer.literalPattern("").test(""), true);
  assert.equal(answer.literalPattern("").test("x"), false);
});
