---
name: modern-javascript
description: Write, modernize, and review JavaScript against real ECMAScript language features and explicit runtime targets. Use for JavaScript or Node.js code, ES edition attribution (ES2015-ES2026), compatibility and polyfill/transpile decisions, array/iterator/Set/Map/Promise/RegExp/TypedArray APIs, modules, async code, Temporal, explicit resource management, decorators, or replacing stale and withdrawn proposal syntax. Prefer standardized features, while permitting mature proposals when the required maintained transform or polyfill is stated.
---

# Modern JavaScript

Use current JavaScript without confusing specification status, runtime support, and toolchain support. Treat these as three separate questions:

1. **Is it standardized?** Check the frozen annual ECMA-262 edition or TC39's current proposal tracker.
2. **Does the target run it?** Check the project's declared Node/browser targets and current compatibility data.
3. **Can tooling bridge the gap?** Syntax may need a transform; built-ins need a polyfill. One does not imply the other.

## Workflow

1. Inspect `package.json` (`engines`, `browserslist`, dependencies), runtime/deployment config, `tsconfig.json`, and Babel/bundler config. Do not invent a baseline.
2. Select the simplest standardized feature supported by that baseline.
3. For a newer standard or mature proposal, state the required runtime, transform, or polyfill in the implementation or handoff.
4. Preserve observable behavior while modernizing: mutation, evaluation order, iterator consumption, concurrency, cancellation, property descriptors, and error propagation matter more than shorter syntax.
5. Run the project's formatter, type-checker, linter, and tests. Exercise both the native path and compatibility path when both ship.

Read [references/COMPATIBILITY.md](references/COMPATIBILITY.md) whenever support is uncertain, the feature is newer than ES2023, or a proposal is involved.

## Status Rules

- Use the [frozen ECMAScript 2026 specification](https://262.ecma-international.org/17.0/) for ES2026 attribution and the [living draft](https://tc39.es/ecma262/) for already-integrated future features.
- Use TC39's [finished-proposals table](https://github.com/tc39/proposals/blob/main/finished-proposals.md) for Stage 4 publication-year mapping and its [active tracker](https://github.com/tc39/proposals) for current stages.
- Do not infer an edition from the year a browser shipped a feature. `Array.fromAsync`, for example, shipped before its ES2026 publication.
- Do not describe Stage 3 or 2.7 syntax as standard JavaScript. It can still be a sound project choice when a maintained toolchain implements the selected proposal revision.
- Do not emit withdrawn Records & Tuples syntax (`#{}` / `#[]`).

## Edition Map

This is a routing index, not a substitute for the detailed references.

| Edition | Representative additions |
|---|---|
| ES2015 | `let`/`const`, classes, modules, arrow functions, destructuring, promises, generators, `Map`/`Set`, `Proxy` |
| ES2016 | exponentiation, `Array.prototype.includes` |
| ES2017 | async functions, `Object.values`/`entries`, string padding, shared memory and Atomics |
| ES2018 | object rest/spread, async iteration, `Promise.prototype.finally`, major RegExp additions |
| ES2019 | `flat`/`flatMap`, `Object.fromEntries`, optional catch binding, stable sort |
| ES2020 | optional chaining, nullish coalescing, `BigInt`, `Promise.allSettled`, dynamic `import()`, `globalThis` |
| ES2021 | logical assignment, `Promise.any`, `replaceAll`, numeric separators, `WeakRef` |
| ES2022 | `.at`, `Object.hasOwn`, top-level `await`, class fields/private elements/static blocks, error cause, RegExp indices |
| ES2023 | array change-by-copy methods, `findLast`/`findLastIndex`, hashbang grammar, symbols as weak keys |
| ES2024 | grouping, `Promise.withResolvers`, well-formed strings, RegExp `v`, resizable/transferable buffers, `Atomics.waitAsync` |
| ES2025 | Set methods, sync iterator helpers, `RegExp.escape`, `Promise.try`, import attributes/JSON modules, RegExp modifiers, Float16 |
| ES2026 | `Array.fromAsync`, `Error.isError`, `Math.sumPrecise`, Uint8Array base64/hex, `Iterator.concat`, Map/WeakMap upsert, JSON source access |

Already Stage 4 with publication expected in ES2027: Temporal, explicit resource management (`using` / `await using`), `Atomics.pause`, and `Iterator.zip` / `zipKeyed`. See [references/UPCOMING.md](references/UPCOMING.md).

## Choose by Semantics

### Collections

| Need | Prefer | Important behavior |
|---|---|---|
| Transform/filter an array | `map`, `filter`, `flatMap` | Eager; creates arrays |
| Process a large/infinite sync source | iterator helpers | Lazy; consumes the iterator |
| Find from the end | `findLast`, `findLastIndex` | Does not reverse or copy |
| Change without mutating the source | `toSorted`, `toReversed`, `toSpliced`, `with` | Shallow copy |
| Group under string/symbol keys | `Object.groupBy` | Returns a null-prototype object |
| Group under identity keys | `Map.groupBy` | Preserves key identity |
| Collect an async iterable | `Array.fromAsync` | Pulls and awaits sequentially |
| Run already-created work concurrently | `Promise.all` | Rejects early; does not cancel inputs |

Do not replace mutation mechanically. A private, newly allocated array can be mutated efficiently without exposing mutable shared state. Use change-by-copy methods when preserving the source is part of the contract.

```javascript
const ranked = scores.toSorted((a, b) => b.points - a.points);

const byTeam = Object.groupBy(players, player => player.team);
if (Object.hasOwn(byTeam, requestedTeam)) {
  render(byTeam[requestedTeam]);
}
```

### Nullish and Property Checks

```javascript
const city = user?.address?.city ?? 'Unknown';

// `??` preserves 0, false, and ''. Use `||` only when all falsy values mean absent.
settings.timeout ??= 5_000;

// Safe for overwritten or null-prototype objects.
if (Object.hasOwn(record, 'id')) use(record.id);
```

### Async Work

```javascript
// Independent work: concurrent.
const [user, permissions] = await Promise.all([
  fetchUser(id),
  fetchPermissions(id),
]);

// Ordered source: sequential consumption.
const pages = await Array.fromAsync(fetchPages());

// A loop is correct when each step depends on the previous one.
for (const migration of migrations) {
  await migration.run();
}
```

Never use `forEach(async () => ...)` when completion must be awaited. Read [references/PROMISES.md](references/PROMISES.md) for combinators and [references/CONCURRENCY.md](references/CONCURRENCY.md) for bounded concurrency and cancellation.

### Modules

Use `with` for import attributes; the older `assert` spelling is not current ECMAScript.

```javascript
import config from './config.json' with { type: 'json' };

const locale = await import(`./locales/${language}.js`);
```

Import attributes and JSON modules are ES2025, but module loading remains host-sensitive. Verify Node, browser, bundler, and test-runner support together.

### Exact API Boundaries

- `structuredClone`, `fetch`, streams, `AbortController`, and DOM APIs are host/web APIs, not ECMA-262 language features.
- `Intl.*` is standardized in ECMA-402, not ECMA-262.
- TypeScript syntax and types are not JavaScript runtime features.
- A TypeScript `lib` entry supplies type declarations, not a runtime implementation.
- Babel syntax transforms do not automatically install missing globals or prototype methods.

## Compatibility Paths

Prefer native support when the target has it. Otherwise choose deliberately:

| Feature kind | Compatibility mechanism |
|---|---|
| Syntax (`using`, decorators) | Babel/TypeScript transform that matches the selected proposal revision |
| Built-in (`Iterator.concat`, `Map#getOrInsert`) | Runtime upgrade or maintained polyfill such as current core-js |
| Namespace API (Temporal) | Runtime upgrade or a maintained Temporal polyfill |
| Shared-memory primitive (`Atomics.pause`) | Native support only; feature-detect and keep a fallback algorithm |

TypeScript 7.0 is released, but it is not a polyfill and 7.0 has no stable programmatic compiler API. Projects whose framework/linter embeds TypeScript may need TypeScript 6 alongside it. See [references/COMPATIBILITY.md](references/COMPATIBILITY.md).

## Review Traps

- `.sort()`, `.reverse()`, `.splice()`, `Map#set`, `Set#add`, and most TypedArray methods mutate. That is not automatically wrong; make it intentional.
- Object/array spread is shallow and invokes ordinary property access; it does not preserve prototypes or descriptors.
- `structuredClone` is a host API and cannot clone functions, weak collections, or every platform object.
- `Object.groupBy` has no inherited `hasOwnProperty` or `toString`.
- Iterator helpers are lazy and single-pass; arrays are reusable and eager.
- `Promise.all` does not cancel remaining operations after rejection. Pass `AbortSignal` when cancellation is required.
- `Math.sumPrecise` accurately sums the binary Number inputs; it does not make decimal money exact.
- `Error.isError` is cross-realm-safe for ECMAScript Error objects; host error types can have runtime-specific behavior.
- `Temporal` is not part of ES2026. Its Stage 4 publication target is ES2027.
- Standard decorators are not legacy TypeScript `experimentalDecorators`.

## References

Load only what the task needs.

| Reference | Use for |
|---|---|
| [ES2016-ES2017.md](references/ES2016-ES2017.md) | early annual additions, async functions, shared memory |
| [ES2018-ES2019.md](references/ES2018-ES2019.md) | async iteration, object spread, RegExp, flattening |
| [ES2022-ES2023.md](references/ES2022-ES2023.md) | classes, `.at`, change-by-copy, weak symbol keys |
| [ES2024.md](references/ES2024.md) | grouping, resolvers, Unicode sets, buffers |
| [ES2025.md](references/ES2025.md) | Set/iterator helpers, modules, RegExp, Float16 |
| [ES2026.md](references/ES2026.md) | all seven finalized ES2026 feature proposals |
| [UPCOMING.md](references/UPCOMING.md) | Stage 4 ES2027 set, selected mature proposals, withdrawn syntax |
| [COMPATIBILITY.md](references/COMPATIBILITY.md) | runtime matrices, Babel/TypeScript/core-js/polyfill decisions |
| [PROMISES.md](references/PROMISES.md) | promise semantics and anti-patterns |
| [CONCURRENCY.md](references/CONCURRENCY.md) | pools, retries, cancellation, async iteration |
| [CHEATSHEET.md](references/CHEATSHEET.md) | compact syntax lookup |

## Authority Order

1. Frozen annual ECMA-262 editions for edition membership
2. Living ECMA-262 plus TC39 proposal tracker/spec repositories for future status and semantics
3. Test262 for conformance cases
4. MDN Browser Compatibility Data and official engine/runtime releases for availability
5. Official TypeScript, Babel, and polyfill documentation for compatibility paths
