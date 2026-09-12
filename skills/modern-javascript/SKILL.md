---
name: modern-javascript
description: Write, modernize, or review JavaScript language features and async code. Use for ECMAScript semantics, runtime compatibility, or polyfill/transform decisions; not unrelated framework or TypeScript type design.
---

# Modern JavaScript

Keep specification status, runtime support, and toolchain support separate. The user's explicit instructions take precedence over this skill's guidelines.

## Work against the target

Use the relevant JavaScript, required behavior, and declared runtime as input. Inspect `engines`, browser targets, lockfiles, and build configuration as needed for the feature. Do not invent a baseline or upgrade runtimes merely to use newer syntax.

Prefer a supported standardized feature. A proposal can fit when the user/project chooses it and a maintained transform or polyfill implements the required revision. Bundled edition and support tables are dated snapshots; verify changing status against the sources below.

## Preserve semantics

- Keep mutation, property access, iterator consumption, evaluation order, error propagation, and concurrency behavior intact when modernizing.
- Distinguish syntax transforms from runtime polyfills. TypeScript declarations do not supply missing runtime APIs.
- Treat iterator helpers as lazy and single-pass; `Array.fromAsync` consumes sequentially, while `Promise.all` observes already-started work concurrently.
- Do not use `forEach(async ...)` when completion must be awaited. Rejection and timeouts do not cancel underlying work by themselves.
- Distinguish host APIs such as `fetch` and `structuredClone` from ECMA-262 features, and `Intl` from the separate ECMA-402 standard.
- Do not introduce withdrawn Records & Tuples syntax or silently switch between legacy and standard-style decorator semantics.

Deliver the requested code or explanation, noting a required compatibility path when relevant. Verify changed behavior and any fallback that ships; select checks proportional to the change rather than requiring every project check for a syntax answer.

## References

Load the semantic or compatibility topic needed, not every edition.

| Task | Reference |
|---|---|
| Runtime targets, Babel, TypeScript, polyfills | [COMPATIBILITY.md](references/COMPATIBILITY.md) |
| Async functions and early annual additions | [ES2016-ES2017.md](references/ES2016-ES2017.md) |
| Object spread, async iteration, RegExp, flattening | [ES2018-ES2019.md](references/ES2018-ES2019.md) |
| Classes, property checks, change-by-copy | [ES2022-ES2023.md](references/ES2022-ES2023.md) |
| Grouping, promise resolvers, buffers, Unicode sets | [ES2024.md](references/ES2024.md) |
| Set/iterator helpers, import attributes, RegExp | [ES2025.md](references/ES2025.md) |
| ES2026 additions such as `Array.fromAsync` | [ES2026.md](references/ES2026.md) |
| Temporal, resource management, proposals, withdrawn syntax | [UPCOMING.md](references/UPCOMING.md) |
| Promise combinators and error behavior | [PROMISES.md](references/PROMISES.md) |
| Pools, retries, cancellation, async iteration | [CONCURRENCY.md](references/CONCURRENCY.md) |
| Compact syntax lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |

Use [frozen ECMA-262 editions](https://262.ecma-international.org/) for edition membership, [TC39 proposals](https://github.com/tc39/proposals) for proposal status, and official runtime/toolchain documentation for availability.
