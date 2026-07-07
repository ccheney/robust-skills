---
name: feature-slicing
description: Proactively apply when creating new features/components/pages or setting up frontend project structure. Triggers on FSD, feature slicing, Feature-Sliced Design, frontend architecture, layer structure, module boundaries, scalable frontend, slice organization, public API, barrel exports, import rules, Steiger. Use when restructuring React/Next.js/Vue/Remix projects, organizing frontend code, fixing import violations, deciding where code belongs (entity vs feature vs widget vs shared), or migrating legacy codebases. Feature-Sliced Design (FSD) architecture for frontend projects.
---

# Feature-Sliced Design Architecture

Frontend architecture methodology (spec v2.1) with a strict layer hierarchy and one import rule. FSD organizes code by **business domain** rather than technical role.

> **Official Docs:** [feature-sliced.design](https://feature-sliced.design) | **GitHub:** [feature-sliced](https://github.com/feature-sliced)

---

## THE IMPORT RULE (Critical)

**A module in a slice may only import slices from layers strictly below. Never sideways or upward.** This is what keeps slices replaceable and dependencies traceable — every violation you allow becomes an invisible coupling someone else trips over.

```
app → pages → widgets → features → entities → shared
 ↓      ↓        ↓          ↓          ↓         ✓
 ✓      ✓        ✓          ✓          ✓      (external only)
```

| Violation | Example | Fix |
|-----------|---------|-----|
| Cross-slice (same layer) | `features/auth` → `features/user-profile` | Move shared code to a lower layer, or compose both in the page/widget above |
| Upward import | `entities/user` → `features/auth` | Move the needed code down |
| Shared importing up | `shared/` → `entities/` | Shared depends only on external packages |
| Cross-entity | `entities/order` → `entities/product` internals | Use `@x` notation (entities layer only) |

**Exception:** `app/` and `shared/` are each "a layer and a slice at the same time" — they divide directly into segments, and their segments may freely import each other.

---

## Layer Hierarchy

| Layer | Purpose | Has Slices | Required |
|-------|---------|------------|----------|
| `app/` | Initialization, routing, providers, global styles | No (segments only) | Yes |
| `pages/` | Route-based screens — **the default home for most code** | Yes | Yes |
| `widgets/` | Large self-sufficient UI blocks reused across pages; may own their data fetching and logic | Yes | No |
| `features/` | User interactions reused across pages (login, add-to-cart) | Yes | No |
| `entities/` | Business domain models reused across pages (user, product) | Yes | No |
| `shared/` | Reused infrastructure: UI kit, API client, route constants, utilities. No knowledge of domain slices — but it may be app-aware (your backend's client, your route paths) | No (segments only) | Yes |

The `processes/` layer is **deprecated** — move its contents to `features/` and `app/`.

**Minimal setup:** `app/`, `pages/`, `shared/`. A small app with 5 routes does not need entities, features, or widgets — adding them "for completeness" spreads single-use code across the tree and negates FSD's cohesion benefit. Add a layer only when something is genuinely reused by 2+ pages.

---

## Pages First (v2.1 default)

When unsure where code goes, **put it in the page slice that uses it** — including forms, data logic, and large UI blocks. Extract downward only when a second page needs it. Why: page-local code is found instantly by newcomers; premature entities/features force jumping through several folders to change one user flow.

```
Where does this code go?
├─ Used by exactly ONE page              → that page's slice (even logic/forms)
├─ App-wide config, providers, routing   → app/
├─ Domain-agnostic or infra code         → shared/
├─ Reused across pages:
│  ├─ Large UI block with own logic      → widgets/
│  ├─ User action (verb)                 → features/
│  └─ Domain model/data (noun)           → entities/
```

### "Feature or Entity?"

| Entity (noun) | Feature (verb) |
|---------------|----------------|
| `user` — user data model | `auth` — login/logout actions |
| `product` — product info | `add-to-cart` — adding to cart |
| `comment` — comment data | `write-comment` — creating comments |

Entities represent THINGS with identity. Features represent ACTIONS with side effects. Not everything is a feature — an interaction used on one page stays in that page.

### "Which segment?"

Segments divide a slice by technical purpose:

```
├─ ui/      → components, styles, formatters
├─ api/     → backend calls, DTOs, mappers
├─ model/   → types, schemas, stores, business logic
├─ lib/     → slice-internal utilities
└─ config/  → feature flags, constants
```

Name segments by **purpose**, not essence: `api/`, `model/`, `lib/` — never `hooks/`, `components/`, `types/`, `utils/`. Purpose names tell a reader what the code is *for*; essence names just restate the file extension.

---

## Directory Structure

```
src/
├── app/                    # Layer + slice: segments only
│   ├── providers/          # React context, QueryClient, theme
│   ├── routes/             # Router configuration
│   └── styles/             # Global CSS, theme tokens
├── pages/
│   └── {page-name}/
│       ├── ui/             # Page component + page-local blocks
│       ├── api/            # Loaders, server actions
│       ├── model/          # Page-specific state
│       └── index.ts        # Public API
├── widgets/
│   └── {widget-name}/
│       ├── ui/
│       ├── api/            # Widgets may fetch their own data (v2.1)
│       └── index.ts
├── features/
│   └── {feature-name}/
│       ├── ui/
│       ├── api/
│       ├── model/
│       └── index.ts
├── entities/
│   └── {entity-name}/
│       ├── ui/             # Entity UI (Card, Avatar)
│       ├── api/            # CRUD operations
│       ├── model/          # Types, mappers, validation
│       └── index.ts
└── shared/                 # Layer + slice: segments only, no root index
    ├── ui/                 # Design system (index per component)
    ├── api/                # API client, interceptors
    ├── lib/                # Utilities (dates, validation)
    ├── config/             # Environment, constants
    ├── routes/             # Route path constants
    └── i18n/               # Translations
```

---

## Public API Pattern

Every slice exposes ONE public API via `index.ts`. External code imports only from it — the index is the contract that lets a slice refactor its internals freely.

```typescript
// entities/user/index.ts
export { UserCard } from './ui/UserCard';
export { getUser, updateUser } from './api/userApi';
export type { User, UserRole } from './model/types';
```

```typescript
// ✅ Correct
import { UserCard, type User } from '@/entities/user';

// ❌ Wrong — reaches into internals
import { UserCard } from '@/entities/user/ui/UserCard';
```

Three rules that prevent the common failure modes:

1. **Explicit named exports, no wildcards.** `export * from './ui'` hides the contract, leaks internals, and harms tree-shaking.
2. **No segment-level index files on sliced layers.** If `features/comments/index.ts` exists, don't also create `features/comments/ui/index.ts` — extra barrels slow bundlers and invite circular imports. Inside a slice, use relative imports; never import your own `index.ts`.
3. **On `shared/`, the public API lives per segment** (`shared/api/index.ts`), and for `shared/ui`/`shared/lib`, per component (`shared/ui/button/index.ts`) — one giant barrel bundles a syntax highlighter into every page.

Details and edge cases: [references/PUBLIC-API.md](references/PUBLIC-API.md).

---

## Cross-Entity References (@x Notation)

Entities sometimes genuinely contain each other (an order contains products). Instead of a hidden cross-import, make it explicit with `@x` — used **only on the entities layer**:

```
entities/
├── product/
│   ├── @x/
│   │   └── order.ts    # exports intended specifically for the order entity
│   └── index.ts
└── order/
    └── model/types.ts  # imports from product/@x/order
```

```typescript
// entities/product/@x/order.ts
export type { ProductId } from '../model/types';

// entities/order/model/types.ts
import type { ProductId } from '@/entities/product/@x/order';
```

Keep `@x` files tiny (usually type re-exports). If two entities cross-reference extensively, merge them.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Business logic in `shared/` | `shared/lib/calculateDiscount.ts` knows domain rules | Move to the entity/feature/page that owns it; shared holds infra only |
| Cross-slice import (same layer) | Invisible coupling between siblings | Extract down, use `@x` (entities), or compose in the layer above |
| Over-slicing a small app | 6 layers, 20 slices, every slice used once | Pages-first: keep code in page slices; layers earn their existence via reuse |
| Everything is a feature | `features/close-modal` | Only reused, business-meaningful interactions |
| Single-use widgets | Widget used by one page | Keep in that page's `ui/` |
| Generic segments | `components/`, `hooks/`, `utils/` | Purpose names: `ui/`, `model/`, `lib/` |
| Wildcard exports | `export * from './ui'` | Explicit named exports |
| Bypassing public API | Deep imports into a slice | Import from the slice `index.ts` |

---

## Tooling

Verify architecture automatically with **Steiger**, the official FSD linter:

```bash
npm i -D steiger @feature-sliced/steiger-plugin
npx steiger ./src            # add --watch during refactors
```

It catches cross-imports, missing public APIs, and single-use slices (`fsd/insignificant-slice`). ESLint alternative: `@feature-sliced/eslint-config`.

**Path alias** (required for `@/entities/user`-style imports):

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

---

## Reference Documentation

| Read this | When |
|-----------|------|
| [references/LAYERS.md](references/LAYERS.md) | Deciding which layer code belongs to; full layer specs and flowchart |
| [references/PUBLIC-API.md](references/PUBLIC-API.md) | Writing index files, fixing circular imports, tree-shaking, `@x` details |
| [references/IMPLEMENTATION.md](references/IMPLEMENTATION.md) | Writing actual code: complete entity/feature/widget/page examples with React Query, Zustand, Zod |
| [references/NEXTJS.md](references/NEXTJS.md) | Any Next.js project — the `app`/`pages` folder conflict, `_app`/`_pages` renaming, server/client public APIs |
| [references/MIGRATION.md](references/MIGRATION.md) | Restructuring an existing codebase to FSD incrementally |
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Quick lookup: import matrix, structure templates |

## Resources

- **Official documentation:** https://feature-sliced.design
- **Specification:** https://feature-sliced.design/docs/reference
- **GitHub organization:** https://github.com/feature-sliced
- **Examples:** https://github.com/feature-sliced/examples
- **Steiger linter:** https://github.com/feature-sliced/steiger
- **Awesome FSD:** https://github.com/feature-sliced/awesome
