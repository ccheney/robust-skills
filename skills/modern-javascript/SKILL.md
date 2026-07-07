---
name: modern-javascript
description: Proactively apply when creating web applications, Node.js services, or any JavaScript project. Triggers on JavaScript, ES6, ES2020, ES2022, ES2024, ES2025, ES2026, modern JS, refactor legacy, array methods, async/await, optional chaining, nullish coalescing, destructuring, spread, rest, template literals, arrow functions, toSorted, toReversed, at, groupBy, iterator helpers, Set union intersection difference, Promise, Promise.try, RegExp.escape, Array.fromAsync, using await using, Temporal, functional programming. Use when writing new JavaScript code, refactoring legacy code, modernizing codebases, implementing functional patterns, checking which ECMAScript edition or runtime supports a feature, or reviewing JS for performance and readability. Modern JavaScript (ES6-ES2026) patterns and best practices.
---

# Modern JavaScript (ES6-ES2026)

Write clean, performant, maintainable JavaScript using modern language features. This skill covers ES6 through ES2026, emphasizing immutability, functional patterns, and expressive syntax — and it pins each feature to the ECMAScript edition and runtimes that actually support it, because misattributed versions are the most common way modern-JS advice breaks.

## Quick Decision Trees

### "Which array method should I use?"

```
What do I need?
├─ Transform each element           → .map()
├─ Keep some elements               → .filter()
├─ Find one element                 → .find() / .findLast()
├─ Check if condition met           → .some() / .every()
├─ Reduce to single value           → .reduce()
├─ Get last element                 → .at(-1)
├─ Sort without mutating            → .toSorted()
├─ Reverse without mutating         → .toReversed()
├─ Group by property                → Object.groupBy() / Map.groupBy()
├─ Collect an async iterable        → Array.fromAsync()
└─ Flatten nested arrays            → .flat() / .flatMap()
```

### "How do I handle nullish values?"

```
Nullish handling?
├─ Safe property access              → obj?.prop / obj?.[key]
├─ Safe method call                  → obj?.method?.()
├─ Default for null/undefined only   → value ?? 'default'
├─ Default for any falsy             → value || 'default'
├─ Assign if null/undefined          → obj.prop ??= 'default'
└─ Check property exists             → Object.hasOwn(obj, 'key')
```

### "Should I mutate or copy?"

```
Always prefer non-mutating methods:
├─ Sort array      → .toSorted()    (not .sort())
├─ Reverse array   → .toReversed()  (not .reverse())
├─ Splice array    → .toSpliced()   (not .splice())
├─ Update element  → .with(i, val)  (not arr[i] = val)
├─ Add to array    → [...arr, item] (not .push())
└─ Merge objects   → {...obj, key}  (not Object.assign())
```

## ES Version Quick Reference

Editions are set by which proposals reach TC39 Stage 4 before the spring cutoff, so a feature's edition often lags its browser availability (e.g. `Array.fromAsync` shipped in browsers in 2023-24 but is spec'd in ES2026). Cite editions from this table, not from memory.

| Version | Year | Key Features |
|---------|------|--------------|
| ES6 | 2015 | let/const, arrow functions, classes, destructuring, spread, Promises, modules, Symbol, Map/Set, Proxy, generators |
| ES2016 | 2016 | Array.includes(), exponentiation operator ** |
| ES2017 | 2017 | async/await, Object.values/entries, padStart/padEnd, trailing commas, SharedArrayBuffer, Atomics |
| ES2018 | 2018 | Rest/spread for objects, for await...of, Promise.finally(), RegExp named groups, lookbehind, dotAll flag |
| ES2019 | 2019 | .flat(), .flatMap(), Object.fromEntries(), trimStart/End(), optional catch binding, stable Array.sort() |
| ES2020 | 2020 | Optional chaining ?., nullish coalescing ??, BigInt, Promise.allSettled(), globalThis, dynamic import(), matchAll |
| ES2021 | 2021 | String.replaceAll(), Promise.any(), logical assignment ??= \|\|= &&=, numeric separators 1_000_000, WeakRef |
| ES2022 | 2022 | .at(), Object.hasOwn(), top-level await, private class fields #field, static blocks, Error cause, /d flag |
| ES2023 | 2023 | .toSorted(), .toReversed(), .toSpliced(), .with(), .findLast(), .findLastIndex(), hashbang grammar |
| ES2024 | 2024 | Object.groupBy(), Map.groupBy(), Promise.withResolvers(), RegExp /v flag, resizable ArrayBuffer + transfer(), Atomics.waitAsync(), isWellFormed() |
| ES2025 | 2025 | Set methods (.union, .intersection, ...), iterator helpers (.map, .filter, .take), RegExp.escape(), Promise.try(), import attributes + JSON modules, duplicate named capture groups, RegExp inline modifiers, Float16Array |
| ES2026 | 2026 | Array.fromAsync(), Error.isError(), Math.sumPrecise(), Uint8Array.fromBase64()/toBase64(), Iterator.concat(), Map.getOrInsert(), JSON.parse source access |

Already Stage 4 and slated for ES2027: **Temporal**, **explicit resource management (`using`/`await using`)**, `Atomics.pause()`, `Iterator.zip()`. Decorators remain Stage 3 (transpiler only). Records & Tuples (`#{}`/`#[]`) was **withdrawn** — never emit that syntax. See [references/UPCOMING.md](references/UPCOMING.md).

## Runtime Support Rules of Thumb

State the baseline when reaching for newer features; suggesting `.toSorted()` to someone on Node 18 produces a runtime `TypeError: arr.toSorted is not a function`.

- **Safe almost everywhere (Baseline widely available)**: everything through ES2023, plus ES2024 grouping/`Promise.withResolvers` and `Array.fromAsync` (Node 21-22+, Safari 16.4-17.4+).
- **Needs a modern baseline (2024-2025 browsers, Node 22-23+)**: Set methods, iterator helpers, import attributes, Promise.try, duplicate named capture groups.
- **Cutting edge (Node 24+, 2025+ browsers; Safari partly behind flags)**: RegExp.escape, Float16Array, `using`/`await using`, Error.isError, Uint8Array base64.
- **Native but not universal**: Temporal (Firefox 139+, Chrome 144+, Node 26+; polyfill elsewhere). Decorators always need Babel or TypeScript.

Per-feature version tables live at the end of [references/ES2024.md](references/ES2024.md), [references/ES2025.md](references/ES2025.md), and [references/ES2026.md](references/ES2026.md).

## Modernization Patterns

### Array Access

```javascript
// ❌ Legacy
const last = arr[arr.length - 1];
const secondLast = arr[arr.length - 2];
```

```javascript
// ✅ Modern (ES2022)
const last = arr.at(-1);
const secondLast = arr.at(-2);
```

### Non-Mutating Array Operations

```javascript
// ❌ Mutates original array (and returns the same reference)
const sorted = arr.sort((a, b) => a - b);
const reversed = arr.reverse();
```

```javascript
// ✅ Returns new array (ES2023)
const sorted = arr.toSorted((a, b) => a - b);
const reversed = arr.toReversed();
const updated = arr.with(2, 'new value');
const removed = arr.toSpliced(1, 1);
```

### String Replacement

```javascript
// ❌ Legacy with regex
const result = str.replace(/foo/g, 'bar');
```

```javascript
// ✅ Modern (ES2021) — no escaping worries for literal strings
const result = str.replaceAll('foo', 'bar');
```

### Grouping Data

```javascript
// ❌ Manual grouping
const grouped = items.reduce((acc, item) => {
  const key = item.category;
  acc[key] = acc[key] || [];
  acc[key].push(item);
  return acc;
}, {});
```

```javascript
// ✅ Modern (ES2024)
const grouped = Object.groupBy(items, item => item.category);
```

Gotcha: `Object.groupBy` returns a **null-prototype object** — property access and destructuring work, but `grouped.hasOwnProperty(...)` throws. Use `Object.hasOwn()`. Use `Map.groupBy` when keys are objects or non-strings. There is no `Array.prototype.group()` — that earlier shape of the proposal never shipped.

### Nullish Handling

```javascript
// ❌ Falsy check (0, '', false are valid values)
const value = input || 'default';
const name = user && user.profile && user.profile.name;
```

```javascript
// ✅ Nullish check (only null/undefined)
const value = input ?? 'default';
const name = user?.profile?.name;
```

### Property Existence

```javascript
// ❌ Can be fooled by prototype or overwritten hasOwnProperty
if (obj.hasOwnProperty('key')) { }
```

```javascript
// ✅ Modern (ES2022) — also works on null-prototype objects
if (Object.hasOwn(obj, 'key')) { }
```

### Logical Assignment

```javascript
// ❌ Verbose assignment
if (obj.prop === null || obj.prop === undefined) {
  obj.prop = 'default';
}
```

```javascript
// ✅ Modern (ES2021)
obj.prop ??= 'default';  // Assign if null/undefined
obj.count ||= 0;         // Assign if falsy
obj.enabled &&= check(); // Assign if truthy
```

## Async Patterns

### Promise Combinators

```javascript
// Wait for all, fail if any fails
const [users, posts] = await Promise.all([fetchUsers(), fetchPosts()]);

// Wait for all, get status of each
const results = await Promise.allSettled([fetchA(), fetchB()]);
results.forEach(r => {
  if (r.status === 'fulfilled') console.log(r.value);
  else console.error(r.reason);
});

// First to succeed
const fastest = await Promise.any([fetchFromCDN1(), fetchFromCDN2()]);

// First to settle
const winner = await Promise.race([fetchData(), timeout(5000)]);
```

### Promise.withResolvers (ES2024)

```javascript
// ❌ Legacy pattern
let resolve, reject;
const promise = new Promise((res, rej) => {
  resolve = res;
  reject = rej;
});
```

```javascript
// ✅ Modern (ES2024)
const { promise, resolve, reject } = Promise.withResolvers();
```

### Top-Level Await (ES2022)

```javascript
// In ES modules, await at top level
const config = await fetch('/config.json').then(r => r.json());
const db = await connectDatabase(config);

export { db };
```

## Functional Patterns

### Immutable Object Updates

```javascript
// Add/update property
const updated = { ...user, age: 31 };

// Remove property
const { password, ...userWithoutPassword } = user;

// Nested update
const newState = {
  ...state,
  user: { ...state.user, name: 'New Name' }
};
```

### Array Transformations

```javascript
// Chain transformations (ES2023)
const result = users
  .filter(u => u.active)
  .map(u => u.name)
  .toSorted();

// Using flatMap for filter+map (single pass)
const activeNames = users.flatMap(u => u.active ? [u.name] : []);

// ES2024: Group then process
const byStatus = Object.groupBy(users, u => u.active ? 'active' : 'inactive');
const activeUserNames = byStatus.active?.map(u => u.name) ?? [];
```

### Composition

```javascript
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);
const compose = (...fns) => x => fns.reduceRight((v, f) => f(v), x);

const processUser = pipe(
  user => ({ ...user, name: user.name.trim() }),
  user => ({ ...user, email: user.email.toLowerCase() }),
  user => ({ ...user, createdAt: new Date() })
);
```

## Destructuring Patterns

### Object Destructuring

```javascript
// Basic with rename and default
const { name: userName, age = 18 } = user;

// Nested
const { address: { city, country } } = user;

// Rest
const { id, ...userData } = user;
```

### Array Destructuring

```javascript
// Skip elements
const [first, , third] = array;

// Rest
const [head, ...tail] = array;

// Swap variables
[a, b] = [b, a];

// Function returns
const [x, y] = getCoordinates();
```

## Anti-Patterns

| Anti-Pattern | Problem | Modern Solution |
|--------------|---------|-----------------|
| `arr[arr.length-1]` | Verbose, error-prone | `arr.at(-1)` |
| `.sort()` on original | Mutates array | `.toSorted()` |
| `.replace(/x/g)` for literal strings | Needs regex escaping | `.replaceAll()` |
| `obj.hasOwnProperty()` | Can be overwritten; throws on null-prototype objects | `Object.hasOwn()` |
| `value \|\| default` | 0, '', false treated as falsy | `value ?? default` |
| `obj && obj.prop && obj.prop.method()` | Verbose null checks | `obj?.prop?.method?.()` |
| `for (let i = 0; ...)` | Index bugs, verbose | `.map()`, `.filter()`, `for...of` |
| `items.forEach(async item => ...)` | forEach ignores promises; nothing is awaited | `for...of` + await, or `Promise.all(items.map(...))` |
| `let resolve; new Promise(r => ...)` | Boilerplate, escape-hatch closures | `Promise.withResolvers()` |
| Manual array grouping with reduce | Verbose, error-prone | `Object.groupBy()` / `Map.groupBy()` |
| `#{ }` / `#[ ]` record/tuple literals | Proposal withdrawn April 2025; never valid syntax | Plain frozen objects, or Maps keyed manually |

## Best Practices

1. **Use `const` by default** — Only use `let` when reassignment is needed
2. **Prefer arrow functions** — Especially for callbacks and short functions
3. **Use template literals** — Instead of string concatenation
4. **Destructure early** — Extract what you need at function start
5. **Avoid mutations** — Use `.toSorted()`, `.toReversed()`, spread operator
6. **Use optional chaining** — Prevent "Cannot read property of undefined"
7. **Use nullish coalescing** — `??` for defaults, not `||` (unless intentional)
8. **Prefer array methods** — `.map()`, `.filter()`, `.find()` over loops
9. **Use `async/await`** — Instead of `.then()` chains
10. **State the runtime baseline** — Note the Node/browser floor when using post-ES2023 features

## Reference Documentation

Open the reference that matches the task; SKILL.md alone is enough for everyday syntax choices.

### ES Version References

| Read this | When |
|------|---------|
| [references/ES2016-ES2017.md](references/ES2016-ES2017.md) | async/await fundamentals, Object.values/entries, string padding |
| [references/ES2018-ES2019.md](references/ES2018-ES2019.md) | Object rest/spread, flat/flatMap, regex named groups/lookbehind/dotAll |
| [references/ES2022-ES2023.md](references/ES2022-ES2023.md) | .at(), change-by-copy methods, private fields, static blocks, error cause |
| [references/ES2024.md](references/ES2024.md) | Grouping data, Promise.withResolvers, /v regex, ArrayBuffer resize/transfer |
| [references/ES2025.md](references/ES2025.md) | Set operations, iterator helpers, RegExp.escape, Promise.try, import attributes |
| [references/ES2026.md](references/ES2026.md) | Array.fromAsync, Error.isError, base64 bytes, Math.sumPrecise, Map.getOrInsert |
| [references/UPCOMING.md](references/UPCOMING.md) | Temporal, using/await using, decorators, proposal status questions |

### Pattern References

| Read this | When |
|------|---------|
| [references/PROMISES.md](references/PROMISES.md) | Writing async flows, choosing combinators, fixing promise anti-patterns |
| [references/CONCURRENCY.md](references/CONCURRENCY.md) | Rate limiting, pools, retry/backoff, timeouts, cancellation, async iteration |
| [references/IMMUTABILITY.md](references/IMMUTABILITY.md) | State updates (React/Redux), pure functions, deep clone decisions |
| [references/COMPOSITION.md](references/COMPOSITION.md) | Higher-order functions, currying, memoization, Maybe/Result patterns |
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Quick syntax lookup across all editions |

## Resources

### Specifications
- **ECMAScript Specification**: https://tc39.es/ecma262/ (living standard)
- **TC39 Proposals**: https://github.com/tc39/proposals (stage status; finished-proposals.md maps features to editions)
- **TC39 Process**: https://tc39.es/process-document/ (how features are added)

### Documentation
- **MDN Web Docs**: https://developer.mozilla.org/en-US/docs/Web/JavaScript
- **JavaScript.info**: https://javascript.info/

### Compatibility
- **Can I Use**: https://caniuse.com (browser support tables)
- **Node.js ES Compatibility**: https://node.green/
