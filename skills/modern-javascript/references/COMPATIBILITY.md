# Compatibility and Toolchains

Use this reference when a feature is newer than the deployment baseline or is not yet in a frozen ECMAScript edition.

## Contents

- [Decide the compatibility path](#decide-the-compatibility-path)
- [Transforms are not polyfills](#transforms-are-not-polyfills)
- [Babel](#babel)
- [TypeScript 7 and TypeScript 6](#typescript-7-and-typescript-6)
- [Runtime polyfills](#runtime-polyfills)
- [Current support snapshot](#current-support-snapshot)
- [Feature detection](#feature-detection)
- [Authoritative sources](#authoritative-sources)

## Decide the compatibility path

1. Read the project's actual targets: `engines`, `browserslist`, deployment images, Electron/runtime versions, and bundler/test configuration.
2. Classify the feature as syntax, a built-in API, a host API, or a combination.
3. Prefer a native standardized feature when every supported target has it.
4. Otherwise choose and document a runtime upgrade, syntax transform, polyfill, or fallback algorithm.
5. Test the oldest supported target. A modern development machine proves very little about production compatibility.

Do not use an edition label as a runtime guarantee. Engines ship features before and after annual ECMA-262 publication.

## Transforms are not polyfills

| Kind | Example | What is required |
|---|---|---|
| Syntax only | decorators | Babel/TypeScript must parse and emit compatible JavaScript |
| Syntax plus protocol built-ins | `using` / `await using` | Transform plus `Symbol.dispose`, stacks, and related built-ins when the emitted helper/runtime needs them |
| Built-in only | `Map.prototype.getOrInsert` | Runtime support or a polyfill |
| Namespace API | Temporal | Runtime support or a Temporal polyfill |
| Host API | `fetch`, `structuredClone` | Host/runtime package or application-specific fallback; not an ECMAScript polyfill decision |

Raising TypeScript's `target` or adding `lib: ["esnext"]` changes syntax emit and available types. It does **not** install `Iterator.concat`, Temporal, or any other runtime API.

## Babel

Use `@babel/preset-env` with explicit targets for standardized syntax. For proposal syntax, pin the proposal revision instead of accepting an implicit default.

### Standard decorators

TC39 currently tracks decorators at Stage 2.7, but the proposal has a mature transform ecosystem. Babel's current proposal snapshot is selected explicitly:

```json
{
  "plugins": [
    ["@babel/plugin-proposal-decorators", { "version": "2023-11" }]
  ]
}
```

Do not combine this with legacy decorators accidentally. Babel's `legacy` mode and TypeScript's `experimentalDecorators` implement older, incompatible semantics. If decorators use `context.metadata`, load a compatible `Symbol.metadata` polyfill before decorated code.

### Explicit resource management

`@babel/plugin-transform-explicit-resource-management` transforms `using` and `await using` and is included in current preset-env data. The transform does not by itself make every related built-in available. Add a tested runtime/polyfill path when code directly uses `DisposableStack`, `AsyncDisposableStack`, or the well-known disposal symbols.

### Polyfill injection

Babel major versions differ:

- Babel 8 directs users from preset-env's old `useBuiltIns` option to `babel-plugin-polyfill-corejs3`.
- Existing Babel 7 projects may already use `useBuiltIns` with core-js.

Inspect the installed major and its official documentation before changing configuration. Do not add both strategies and duplicate polyfills.

## TypeScript 7 and TypeScript 6

[TypeScript 7.0 was released on 2026-07-08](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/). It is the native compiler port, not a new JavaScript runtime and not a polyfill.

Important 7.0 boundaries:

- It has a production `tsc`, but no stable programmatic compiler API in 7.0.
- Tools that embed the compiler or language service may still require TypeScript 6. The TypeScript team documents side-by-side installation with `@typescript/typescript6`.
- Angular template tooling and Vue/MDX/Astro/Svelte integrations may still require TypeScript 6 until their integrations support the new API.
- TypeScript 7 changed several defaults and removed legacy targets/options. Read the official migration notes before treating it as a drop-in toolchain upgrade.

For syntax compatibility:

- Standard-style decorators are supported by TypeScript 5.0+ without `experimentalDecorators`. The TC39 proposal is now Stage 2.7, so lock tests to the compiler version and do not claim native standard status.
- Explicit resource management was added in TypeScript 5.2. The emitted compatibility code still relies on the disposal protocol; supply the declared libs and runtime support/polyfills that the target requires.
- TypeScript 6 added Temporal type declarations under `esnext` / `esnext.temporal`. Those declarations do not provide Temporal at runtime.

Use Babel or another dedicated emitter when a project's required syntax transform is not supported by its chosen TypeScript 7 path. Keep TypeScript for checking with `noEmit` if that separation is simpler.

## Runtime polyfills

### core-js

Current core-js provides modules for all seven ES2026 feature groups, including:

- `Array.fromAsync`
- `Error.isError`
- `Math.sumPrecise`
- Uint8Array base64/hex conversion
- `Iterator.concat`
- Map/WeakMap `getOrInsert` methods
- JSON source access and raw JSON

It also provides proposal modules for explicit resource management and modules for `Iterator.zip` / `zipKeyed`. Prefer target-driven injection for applications; use selective imports for libraries only when the library's compatibility contract permits global patching.

Examples of selective application imports:

```javascript
import 'core-js/actual/iterator/concat';
import 'core-js/actual/map/get-or-insert';
import 'core-js/actual/typed-array/from-base64';
```

Pin and test the current core-js version in the project. A polyfill can match API behavior but cannot reproduce engine performance characteristics.

### Temporal

Temporal is too large to treat as a casual utility import. Prefer a runtime that ships it. Otherwise choose a maintained implementation listed by the [TC39 Temporal repository](https://github.com/tc39/proposal-temporal#polyfills), such as `@js-temporal/polyfill` or `temporal-polyfill`, and account for bundle cost and timezone/calendar data.

```javascript
import { Temporal } from '@js-temporal/polyfill';

const today = Temporal.Now.plainDateISO();
```

Avoid silently assigning a ponyfill to `globalThis.Temporal` in a library. Let the application own that global policy.

### No faithful polyfill

`Atomics.pause` is an engine/shared-memory primitive. A normal JavaScript library cannot reproduce its execution hint faithfully. Feature-detect it and retain a different backoff strategy when unavailable.

## Current support snapshot

First unflagged versions from [MDN Browser Compatibility Data](https://github.com/mdn/browser-compat-data), checked 2026-08-13. `partial` means the implementation has the BCD caveat described below.

### ES2026

| Feature | Chrome | Firefox | Safari | Node.js |
|---|---:|---:|---:|---:|
| `Array.fromAsync` | 121 | 115 | 16.4 | 22.0.0 |
| `Error.isError` | 134 | 138 | 18.4 partial | 24.3.0 |
| `Math.sumPrecise` | 147 | 137 | 26.2 | No current support recorded |
| Uint8Array base64/hex | 140 | 133 | 18.2 | 25.0.0 |
| `Iterator.concat` | 146 | 147 | 26.4 | 26.0.0 |
| Map/WeakMap upsert | 145 | 144 | 26.2 | 26.0.0 |
| JSON parse source/raw JSON | 114 | 135 | 18.4 | 21.0.0 |

Safari 18.4's `Error.isError` returns `false` for `DOMException`; BCD therefore marks it partial. Node 24.0-24.2 had the same limitation and is complete from 24.3.

### Stage 4, expected ES2027

| Feature | Native position | Compatibility path |
|---|---|---|
| Temporal | Chrome 144, Firefox 139, Node 26; Safari preview | Dedicated Temporal polyfill |
| Explicit resource management | Chrome 134, Firefox 141, Node 24; no stable Safari support recorded | Babel/TypeScript transform plus core-js protocol built-ins as needed |
| `Atomics.pause` | Chrome 133, Firefox 137, Safari 18.4; no Node support recorded | Feature-detected fallback algorithm |
| `Iterator.zip` / `zipKeyed` | Limited native support | current core-js modules |

Do not turn these numbers into a universal baseline. Electron, embedded WebViews, serverless images, test runners, and bundlers may lag their upstream engine.

## Feature detection

Use detection when shipping one artifact across mixed runtimes:

```javascript
const sum = typeof Math.sumPrecise === 'function'
  ? Math.sumPrecise(values)
  : compensatedSum(values);

const pause = typeof Atomics.pause === 'function'
  ? () => Atomics.pause()
  : () => {};
```

Feature detection answers whether a property exists, not whether an old implementation has every current semantic fix. For security- or correctness-sensitive behavior, pin the runtime or run a behavior test.

## Authoritative sources

- [ECMAScript 2026, 17th edition](https://262.ecma-international.org/17.0/)
- [Living ECMA-262 draft](https://tc39.es/ecma262/)
- [TC39 proposal tracker](https://github.com/tc39/proposals)
- [TC39 finished proposals](https://github.com/tc39/proposals/blob/main/finished-proposals.md)
- [MDN Browser Compatibility Data](https://github.com/mdn/browser-compat-data)
- [Babel plugin documentation](https://babeljs.io/docs/plugins-list)
- [Babel 8 migration guide](https://babeljs.io/docs/v8-migration)
- [TypeScript 7.0 release](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/)
- [core-js feature documentation](https://github.com/zloirock/core-js#ecmascript)
