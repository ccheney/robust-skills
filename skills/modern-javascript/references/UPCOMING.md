# Post-ES2026 JavaScript

Status snapshot: 2026-08-13. The latest TC39 plenary ran 2026-07-20 through 2026-07-23; use the current [TC39 proposal tracker](https://github.com/tc39/proposals) for outcomes even when detailed meeting notes have not yet been published.

The Stage 4 proposals currently mapped to ES2027 are Temporal, explicit resource management, `Atomics.pause`, and joint iteration (`Iterator.zip` / `zipKeyed`). They are finished proposals and can be used with an explicit runtime/polyfill plan; they are not part of ES2026.

## Contents

- [Stage 4 for ES2027](#stage-4-for-es2027)
- [Temporal](#temporal)
- [Explicit resource management](#explicit-resource-management)
- [Atomics.pause](#atomicspause)
- [Joint iteration](#joint-iteration)
- [Selected mature proposals](#selected-mature-proposals)
- [Decorators and metadata](#decorators-and-metadata)
- [Withdrawn Records and Tuples](#withdrawn-records-and-tuples)
- [Sources](#sources)

## Stage 4 for ES2027

| Feature | Reached Stage 4 | Native support snapshot | Compatibility route |
|---|---:|---|---|
| Temporal | 2026-03-11 | Firefox 139, Chrome 144, official Node 26 binaries; Safari preview | Dedicated Temporal polyfill |
| Explicit resource management | 2026-05-19 | Chrome 134, Firefox 141, Node 24; no stable Safari support recorded | Babel/TypeScript transform plus disposal built-ins as needed |
| `Atomics.pause` | 2026-05-19 | Chrome 133, Firefox 137, Safari 18.4; no Node support recorded | No faithful polyfill; feature-detect a fallback |
| `Iterator.zip` / `zipKeyed` | 2026-05-19 | Limited native support | current core-js modules |

The dates come from the TC39 proposal-tracker commits and linked meeting records. Older articles and tool documentation may show earlier stages or different edition labels.

## Temporal

Temporal provides immutable, explicit date/time types. Choose the type that matches the domain instead of defaulting every value to an instant:

```javascript
const birthday = Temporal.PlainDate.from('1990-05-15');
const appointment = Temporal.PlainDateTime.from('2026-08-13T14:30');
const flight = Temporal.ZonedDateTime.from(
  '2026-08-13T14:30-04:00[America/New_York]',
);
const receivedAt = Temporal.Now.instant();
const timeout = Temporal.Duration.from({ seconds: 30 });
```

Calendar and timezone arithmetic remain explicit and return new values:

```javascript
const date = Temporal.PlainDate.from('2024-01-31');
date.add({ months: 1 }).toString(); // '2024-02-29'

const london = flight.withTimeZone('Europe/London');
```

Do not mechanically replace every `Date`:

- Keep `Date` where a platform API requires it.
- Use `Temporal.Instant` for an exact timeline point.
- Use plain types for calendar values without a timezone.
- Use `Temporal.ZonedDateTime` when timezone rules are part of the value.

For unsupported targets, use a maintained implementation listed by the [Temporal proposal](https://github.com/tc39/proposal-temporal#polyfills). As of 2026-08-13, its table labels `temporal-polyfill` stable, `temporal-polyfill-lite` release candidate, and `@js-temporal/polyfill` alpha; recheck those labels and choose according to the project's stability and bundle requirements. A TypeScript `esnext.temporal` lib supplies types only.

Node 26's official binaries enable Temporal by default, but custom/distributor builds may omit it when Node is built without the required Rust toolchain. Detect `globalThis.Temporal` at runtime instead of relying only on the Node version.

## Explicit resource management

`using` and `await using` guarantee LIFO cleanup on normal and abrupt scope exit.

```javascript
{
  using file = openFile('data.txt');
  process(file);
} // file[Symbol.dispose]() runs

async function runQuery() {
  await using connection = await connect();
  return connection.query('SELECT 1');
} // awaits connection[Symbol.asyncDispose]()
```

The feature group includes:

- `Symbol.dispose` and `Symbol.asyncDispose`
- `DisposableStack` and `AsyncDisposableStack`
- `SuppressedError`
- `using` / `await using`, including loop forms

`null` and `undefined` initializers require no disposal. Other non-disposable values throw when registered. Resources are disposed in reverse acquisition order, and disposal still runs on `throw`, `return`, or `break`.

Babel's explicit-resource-management transform and TypeScript 5.2+ provide compatibility emit. Add current core-js protocol built-ins when the target lacks the symbols/stacks used by the code or emitted helpers. Test thrown-body plus thrown-disposer behavior; `SuppressedError` preserves both failures.

## Atomics.pause

`Atomics.pause()` is a zero-argument hint for spin-wait loops. It is not a sleep, timer, yield, synchronization operation, or configurable-duration pause. TC39 removed the proposal's unused optional iteration hint when it advanced to Stage 4.

```javascript
function tryBoundedSpin(view, index, expected, spinLimit = 64) {
  for (let attempt = 0; attempt < spinLimit; attempt++) {
    if (Atomics.load(view, index) !== expected) return true;
    if (typeof Atomics.pause === 'function') Atomics.pause();
  }
  return false; // Caller switches to Atomics.wait/waitAsync or another strategy.
}
```

Prefer `Atomics.wait`, `Atomics.waitAsync`, messaging, or a higher-level synchronization design when actual blocking/wakeup semantics are needed. A library cannot faithfully polyfill an engine CPU-pause hint.

## Joint iteration

`Iterator.zip` synchronizes positional iterables; `Iterator.zipKeyed` preserves an object's enumerable keys.

```javascript
Iterator.zip([
  [0, 1, 2],
  [3, 4, 5],
]).toArray();
// [[0, 3], [1, 4], [2, 5]]

Iterator.zipKeyed({
  name: ['Ada', 'Grace'],
  role: ['engineer', 'admiral'],
}).toArray();
// [{ name: 'Ada', role: 'engineer' }, ...]
```

The options `mode: 'shortest'` (default), `'longest'`, and `'strict'` control unequal lengths. Longest mode accepts per-input padding. Use current core-js when native support is outside the project's baseline.

## Selected mature proposals

These are **not standard JavaScript yet**. Recommend one only when its exact implementation path is already supported and tested by the project's toolchain.

| Proposal | Current stage | Current practical position |
|---|---:|---|
| Await Dictionary (`Promise.allKeyed`, `allSettledKeyed`) | 3 (advanced 2026-07-20) | Proposal reports no native or polyfill implementation; do not ship without owning one |
| Deferring Module Evaluation (`import defer`) | 3 | Syntax/tooling support is host- and bundler-specific; no universal runtime path |
| Source Phase Imports | 3 | Requires host integration; check the exact Wasm/JS host and bundler |
| Import Text | 3 | Requires host integration; do not confuse it with bundler raw-loader syntax |
| Iterator chunking / includes / join | 3 | Feature-detect or use a maintained library with equivalent semantics |
| Error Stack Accessor | 3 | Existing `Error.prototype.stack` behavior remains engine-sensitive until standardized and shipped |
| RegExp Buffer Boundaries | 3 | New regex syntax requires parser/engine support; avoid untransformed use |

Stage 3 means the design is mature, not that the platform provides it. A stable library with equivalent behavior can be a compatibility route for methods; new grammar and host integration usually require the actual compiler/host to participate.

## Decorators and metadata

TC39's current tracker places both Decorators and Decorator Metadata at **Stage 2.7** as of the May 2026 plenary. Some Babel, TypeScript, and proposal pages still say Stage 3; use the tracker for current status.

They remain reasonable in projects that deliberately adopt a maintained transform:

```javascript
function logged(method, context) {
  return function (...args) {
    console.log(`Calling ${String(context.name)}`);
    return method.apply(this, args);
  };
}

class Calculator {
  @logged
  add(a, b) {
    return a + b;
  }
}
```

Compatibility requirements:

- Babel: pin `@babel/plugin-proposal-decorators` to `version: '2023-11'`.
- TypeScript: use standard decorators (supported since 5.0), not `experimentalDecorators` legacy semantics.
- Metadata: provide a compatible `Symbol.metadata` polyfill before decorated code when the runtime lacks it.
- Lock compiler/transform versions and test decorator order, initializers, inheritance, and metadata. Stage 2.7 can still change.

Standard decorators do not support legacy TypeScript parameter decorators, and legacy `emitDecoratorMetadata` expectations are not the standard metadata proposal.

## Withdrawn Records and Tuples

The Records & Tuples proposal was withdrawn in April 2025. The literal forms below were never standard JavaScript and must not be emitted:

```javascript
// Invalid and withdrawn:
// const point = #{ x: 1, y: 2 };
// const pair = #[1, 2];
```

Use ordinary objects/arrays, `Object.freeze` when shallow freezing is actually needed, and explicit structural comparison/keying. The successor Composites work is early-stage and is not a production compatibility target.

## Sources

- [TC39 finished proposals](https://github.com/tc39/proposals/blob/main/finished-proposals.md)
- [TC39 active proposal tracker](https://github.com/tc39/proposals)
- [July 2026 plenary agenda](https://github.com/tc39/agendas/blob/main/2026/07.md)
- [May 2026 plenary notes](https://github.com/tc39/notes/blob/main/meetings/2026-05/may-19.md)
- [Temporal proposal](https://github.com/tc39/proposal-temporal)
- [Node.js 26.0.0 release](https://nodejs.org/en/blog/release/v26.0.0)
- [Node.js Temporal build requirements](https://github.com/nodejs/node/blob/main/BUILDING.md#building-nodejs-with-temporal-support)
- [Explicit resource management proposal](https://github.com/tc39/proposal-explicit-resource-management)
- [Atomics.pause proposal](https://github.com/tc39/proposal-atomics-microwait)
- [Joint iteration proposal](https://github.com/tc39/proposal-joint-iteration)
- [Decorators proposal](https://github.com/tc39/proposal-decorators)
- [Await Dictionary proposal](https://github.com/tc39/proposal-await-dictionary)
