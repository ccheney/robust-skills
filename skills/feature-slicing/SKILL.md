---
name: feature-slicing
description: Organize frontend code with Feature-Sliced Design (FSD). Use when adopting FSD, placing code in an existing FSD project, or fixing slice imports and public APIs; not for every new component or page.
---

# Feature-Sliced Design

Apply FSD v2.1 to the requested module-boundary decision. The user's explicit instructions take precedence over this skill's guidelines; an ordinary frontend edit is not permission to migrate its architecture.

## Work within the project

Use the affected files, imports, framework/router, and requested behavior as input. Determine whether the repository already uses FSD or the user is asking to adopt it. If neither is true, preserve the existing structure.

Prefer page-local ownership until shared use or a distinct responsibility justifies extraction:

| Layer | Responsibility |
|---|---|
| `app` | Initialization, providers, routing |
| `pages` | Screens and their local UI, data, and logic |
| `widgets` | Self-contained UI blocks |
| `features` | Reusable user interactions |
| `entities` | Shared business concepts |
| `shared` | Infrastructure and domain-independent utilities/UI |

Use only the layers needed. Preserve framework-reserved directories and server/client boundaries, particularly in Next.js.

## Maintain the import contract

- A slice imports other slices from lower layers, not sideways or upward. Explicit `@x` APIs are the documented cross-entity exception.
- `app` and `shared` have segments rather than slices; their segments can import one another.
- Expose deliberate public APIs. Use internal relative imports to avoid importing a slice's own barrel; keep server-only exports out of client entrypoints.
- Name FSD segments by purpose (`ui`, `api`, `model`, `lib`, `config`). Do not rename unrelated folders merely to match an example.

Deliver the requested placement, refactor, or review with the resulting import paths. For code changes, verify affected imports and use existing architecture checks when available. Install Steiger or rewrite path aliases only when the task calls for tooling setup.

## References

Choose the reference that resolves the current decision.

| Task | Reference |
|---|---|
| Layer ownership and extraction | [LAYERS.md](references/LAYERS.md) |
| Public APIs, barrels, cycles, `@x` | [PUBLIC-API.md](references/PUBLIC-API.md) |
| Concrete entity/feature/widget/page examples | [IMPLEMENTATION.md](references/IMPLEMENTATION.md) |
| Next.js route directories and server/client exports | [NEXTJS.md](references/NEXTJS.md) |
| Requested migration of existing code | [MIGRATION.md](references/MIGRATION.md) |
| Import matrix or compact structure lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |

Use the [official FSD documentation](https://feature-sliced.design/docs/reference) for specification questions. Adapt example libraries and aliases to the installed stack.
