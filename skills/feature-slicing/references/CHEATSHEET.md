# FSD Quick Reference

> **Sources:** [Layers](https://feature-sliced.design/docs/reference/layers) | [Slices & Segments](https://feature-sliced.design/docs/reference/slices-segments) | [Public API](https://feature-sliced.design/docs/reference/public-api)

## Layer Hierarchy

```
app/      → Providers, routing, global styles          [segments only, REQUIRED]
pages/    → Route screens; default home for code       [slices, REQUIRED]
widgets/  → Reused UI blocks, may own logic/data       [slices, optional]
features/ → Reused user interactions                   [slices, optional]
entities/ → Reused business domain models              [slices, optional]
shared/   → Infrastructure: UI kit, API client, utils  [segments only, REQUIRED]
```

**Import Rule:** only import from layers BELOW. Never sideways or up.
**Deprecated:** `processes/` — move contents to `features/` and `app/`.

---

## Import Matrix

| can import → | app | pages | widgets | features | entities | shared |
|--------------|-----|-------|---------|----------|----------|--------|
| **app** | ✅¹ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **pages** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **widgets** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **features** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **entities** | ❌ | ❌ | ❌ | ❌ | @x² | ✅ |
| **shared** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅¹ |

¹ `app/` and `shared/` have no slices — their segments import each other freely
² Cross-entity references only via `@x` notation

---

## "Where does this code go?" (pages-first, v2.1)

```
├─ Used by exactly ONE page              → that page's slice (even forms/logic)
├─ App-wide config, providers, routing   → app/
├─ Infra with no domain knowledge        → shared/
├─ Reused across pages:
│  ├─ Large UI block (may own logic)     → widgets/
│  ├─ User action (verb)                 → features/
│  └─ Domain model/data (noun)           → entities/
```

### Feature or Entity?

| Entity (noun) | Feature (verb) |
|---------------|----------------|
| `user` | `auth` (login/logout) |
| `product` | `add-to-cart` |
| `comment` | `write-comment` |
| `order` | `checkout` |

**Entities:** THINGS with identity, displayed in lists.
**Features:** ACTIONS with side effects, triggered by the user — and only if reused; single-page interactions stay in the page.

---

## Segments

| Segment | Purpose | Examples |
|---------|---------|----------|
| `ui/` | Components, styles, formatters | `UserCard.tsx` |
| `api/` | Backend calls, DTOs, mappers | `getUser()`, `createOrder()` |
| `model/` | Types, schemas, stores, logic | `User`, `userSchema`, `useUserStore` |
| `lib/` | Slice-internal utilities | `formatUserName()` |
| `config/` | Configuration, feature flags | constants |

Purpose-driven names only — never `hooks/`, `components/`, `types/`, `utils/`.

---

## File Structure Templates

### Entity / Feature slice (one index, no segment indexes)
```
entities/{name}/            features/{name}/
├── ui/                     ├── ui/
│   └── {Name}Card.tsx      │   └── {Name}Form.tsx
├── api/                    ├── api/
│   └── {name}Api.ts        │   └── {name}Api.ts
├── model/                  ├── model/
│   ├── types.ts            │   ├── schema.ts
│   └── schema.ts           │   └── store.ts
└── index.ts                └── index.ts
```

### Page slice
```
pages/{name}/
├── ui/
│   ├── {Name}Page.tsx
│   └── (page-local blocks live here too)
├── api/
│   └── loader.ts
└── index.ts
```

---

## Public API Rules

```typescript
// entities/user/index.ts — explicit named exports only
export { UserCard } from './ui/UserCard';
export { getUser, updateUser } from './api/userApi';
export type { User, UserRole } from './model/types';
```

```typescript
// ✅ Consume via public API
import { UserCard, type User } from '@/entities/user';

// ❌ Deep import
import { UserCard } from '@/entities/user/ui/UserCard';

// ✅ Inside the slice: relative imports (never your own index.ts)
import { userSchema } from '../model/schema';
```

- One `index.ts` per slice — no segment indexes on sliced layers
- No root `shared/index.ts` — per segment (`shared/api/index.ts`), per component for `shared/ui` (`@/shared/ui/button`)
- No `export *`

---

## Cross-Entity References (@x)

Entities layer only:

```typescript
// entities/product/@x/order.ts — exports intended for the order entity
export type { ProductId } from '../model/types';

// entities/order/model/types.ts
import type { ProductId } from '@/entities/product/@x/order';
```

---

## Tooling

```bash
npm i -D steiger @feature-sliced/steiger-plugin
npx steiger ./src          # official FSD linter; --watch during refactors
```

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Import from a higher layer | Import from lower layers only |
| Cross-slice import (same layer) | Move code down, `@x` (entities), or compose above |
| Business logic in `shared/` | Domain rules live in entities/features/pages |
| Extract single-use code to features/widgets | Keep it in the page slice (pages-first) |
| Scaffold all 6 layers for a small app | Start with `app` + `pages` + `shared` |
| Generic segments: `components/`, `hooks/` | Purpose segments: `ui/`, `model/`, `lib/` |
| Wildcard exports: `export *` | Explicit named exports |
| Deep imports into slices | Import the slice `index.ts` |

---

## Minimal FSD Setup

```
src/
├── app/
├── pages/
└── shared/
```

Add `entities/`, `features/`, `widgets/` only when something is reused by 2+ pages.

---

## Resources

| Resource | Link |
|----------|------|
| Official docs | https://feature-sliced.design |
| Examples | https://github.com/feature-sliced/examples |
| Steiger linter | https://github.com/feature-sliced/steiger |
| v2.1 notes ("Pages first") | https://github.com/feature-sliced/documentation/releases/tag/v2.1 |
